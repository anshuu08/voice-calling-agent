"""
TakeRemo — Excel Service Layer
Flexible parsing, validation, duplicate checking, and updated Excel workbook generator.
Supports .xlsx, .xls, and .csv with robust column aliases and row tracking.
"""

import os
import re
import io
import json
import secrets
from typing import Dict, Any, List, Tuple, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import pandas as pd

from services.db import get_db_connection, utc_now


COLUMN_SYNONYMS = {
    # Name
    'name': ['name', 'full name', 'candidate name', 'customer name', 'contact name', 'lead name', 'client name', 'person name'],
    # Phone
    'phone': ['phone', 'phone number', 'phonenumber', 'mobile', 'mobile number', 'mobilenumber', 'contact', 'contact number', 'contactno', 'cell', 'cell number', 'telephone'],
    # Email
    'email': ['email', 'email address', 'mail', 'email id'],
    # Preferred language
    'preferred_language': ['preferred language', 'language', 'preferred lang', 'lang'],
    # Notes
    'notes': ['notes', 'remarks', 'comment', 'comments', 'additional notes', 'description'],
    # Recruitment specific
    'job_role': ['job role', 'jobrole', 'role', 'position', 'designation', 'job title', 'target role'],
    'education': ['education', 'qualification', 'educational qualification', 'degree', 'highest degree'],
    'skills': ['skills', 'technical skills', 'key skills', 'skill set', 'technologies'],
    'experience': ['experience', 'total experience', 'years of experience', 'yoe', 'work experience'],
    'location': ['location', 'city', 'current location', 'residence'],
    # Sales specific
    'company': ['company', 'company name', 'organization', 'org name', 'account name', 'firm'],
    'product_or_service': ['product or service', 'product', 'service', 'requirement', 'offering', 'interest'],
    'lead_source': ['lead source', 'source', 'channel', 'campaign source'],
    # Support specific
    'customer_id': ['customer id', 'customerid', 'client id', 'account id', 'cust id', 'ticket id'],
    'issue_or_query': ['issue or query', 'issue', 'query', 'problem', 'concern', 'complaint', 'subject']
}


def normalize_column_name(header: str) -> Optional[str]:
    """Matches a header string to one of our standard keys using synonyms."""
    if not header or not isinstance(header, str):
        return None
    cleaned = re.sub(r'[^a-z0-9]', ' ', header.strip().lower())
    cleaned = ' '.join(cleaned.split())

    for standard_key, aliases in COLUMN_SYNONYMS.items():
        if cleaned in aliases:
            return standard_key
        # Check sub-string match if header clearly contains alias
        for alias in aliases:
            if alias in cleaned:
                return standard_key
    return None


def clean_and_validate_phone(phone_val: Any) -> Tuple[bool, str, str]:
    """
    Validates and normalizes phone numbers to standard E.164.
    Supports 10-digit Indian numbers with optional prefixes (0, 91, +91).
    Returns (is_valid, normalized_e164, error_message).
    """
    if phone_val is None:
        return False, "", "Phone number is empty"

    raw = str(phone_val).strip()
    if not raw:
        return False, "", "Phone number is empty"

    # Remove spaces, hyphens, parentheses, dots
    cleaned = re.sub(r'[\s\-\(\)\.]', '', raw)

    # Check for scientific notation like 9.87654E+09
    if 'e' in cleaned.lower():
        try:
            cleaned = str(int(float(raw)))
        except Exception:
            pass

    # Check if starts with +
    has_plus = cleaned.startswith('+')
    digits = re.sub(r'\D', '', cleaned)

    if not digits:
        return False, "", "No numeric digits found in phone number"

    # Handle standard 10-digit Indian numbers (starting with 6, 7, 8, 9)
    if len(digits) == 10 and digits[0] in '6789':
        return True, f"+91{digits}", ""

    # Handle 11 digits starting with 0
    if len(digits) == 11 and digits.startswith('0') and digits[1] in '6789':
        return True, f"+91{digits[1:]}", ""

    # Handle 12 digits starting with 91
    if len(digits) == 12 and digits.startswith('91') and digits[2] in '6789':
        return True, f"+{digits}", ""

    # Generic international format if length is between 10 and 15
    if 10 <= len(digits) <= 15:
        if has_plus:
            return True, f"+{digits}", ""
        elif digits.startswith('91') and len(digits) == 12:
            return True, f"+{digits}", ""
        elif len(digits) == 10:
            return True, f"+91{digits}", ""
        return True, f"+{digits}", ""

    return False, raw, f"Invalid phone format: must be at least 10 digits (got '{raw}')"


class ExcelService:

    @classmethod
    def parse_and_validate_upload(cls, file_obj, filename: str, service: str) -> Dict[str, Any]:
        """
        Parses the uploaded sheet, maps columns flexibly, validates contacts,
        identifies duplicates, and stores batch and contacts persistently in SQLite.
        """
        service = service.lower().strip()
        if service not in ('recruitment', 'sales', 'support'):
            service = 'recruitment'

        _, ext = os.path.splitext(filename.lower())
        if ext not in ('.xlsx', '.xls', '.csv'):
            raise ValueError(f"Unsupported file format '{ext}'. Please upload .xlsx, .xls, or .csv")

        # Save copy to uploads directory
        uploads_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        batch_id = f"batch_{service[:3]}_{secrets.token_hex(6)}"
        saved_filename = f"{batch_id}_{filename}"
        saved_path = os.path.join(uploads_dir, saved_filename)

        # Read file bytes
        file_bytes = None
        if hasattr(file_obj, 'read'):
            file_bytes = file_obj.read()
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            with open(saved_path, 'wb') as f:
                f.write(file_bytes)
        else:
            raise ValueError("No file content provided")

        # Parse DataFrame using pandas or openpyxl
        try:
            if ext == '.csv':
                df = pd.read_csv(io.BytesIO(file_bytes), dtype=str)
            else:
                df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
        except Exception as e:
            raise ValueError(f"Unable to read spreadsheet: {str(e)}")

        if df.empty:
            raise ValueError("The uploaded spreadsheet contains no data rows.")

        # Map headers
        col_mapping = {}
        for original_col in df.columns:
            std_key = normalize_column_name(str(original_col))
            if std_key:
                col_mapping[original_col] = std_key

        # Validate that essential columns (Name, Phone) can be located
        mapped_std_keys = set(col_mapping.values())
        if 'phone' not in mapped_std_keys:
            raise ValueError("Could not find a 'Phone Number' or 'Mobile' column in the uploaded sheet. Found columns: " + ", ".join(df.columns))

        name_col = None
        phone_col = None
        for orig, std in col_mapping.items():
            if std == 'name' and not name_col:
                name_col = orig
            elif std == 'phone' and not phone_col:
                phone_col = orig

        # If name column was not explicitly matched, fallback to first non-phone column
        if not name_col:
            for c in df.columns:
                if c != phone_col:
                    name_col = c
                    col_mapping[c] = 'name'
                    break

        seen_phones = {}
        valid_records = []
        invalid_records = []

        total_rows = len(df)

        for idx, row in df.iterrows():
            excel_row_num = idx + 2  # 1-indexed, header is row 1
            raw_dict = {str(k): (str(v).strip() if pd.notna(v) else "") for k, v in row.to_dict().items()}

            # Extract standard fields
            name_val = raw_dict.get(name_col, "").strip() if name_col else ""
            phone_val = raw_dict.get(phone_col, "").strip() if phone_col else ""

            row_errors = []

            if not name_val:
                row_errors.append("Contact name is missing")

            is_valid_phone, e164_phone, phone_err = clean_and_validate_phone(phone_val)
            if not is_valid_phone:
                row_errors.append(phone_err)
            else:
                # Duplicate detection within this batch
                if e164_phone in seen_phones:
                    first_row = seen_phones[e164_phone]
                    row_errors.append(f"Duplicate phone number (already seen on row {first_row})")
                else:
                    seen_phones[e164_phone] = excel_row_num

            # Extract extra fields
            extra = {}
            for orig, val in raw_dict.items():
                std = col_mapping.get(orig)
                if std and std not in ('name', 'phone'):
                    extra[std] = val
                elif not std:
                    extra[orig] = val

            pref_lang = extra.get('preferred_language', 'en') or 'en'
            notes = extra.get('notes', '')

            contact_id = f"cnt_{secrets.token_hex(8)}"

            record_info = {
                "id": contact_id,
                "row_index": excel_row_num,
                "name": name_val or f"Contact (Row {excel_row_num})",
                "phone": e164_phone if is_valid_phone else phone_val,
                "preferred_language": pref_lang,
                "notes": notes,
                "extra": extra,
                "raw": raw_dict,
                "valid": len(row_errors) == 0,
                "errors": row_errors
            }

            if len(row_errors) == 0:
                valid_records.append(record_info)
            else:
                invalid_records.append(record_info)

        # Persist Batch & Contacts into SQLite
        conn = get_db_connection()
        now = utc_now()
        try:
            with conn:
                conn.execute("""
                INSERT INTO batches (id, service, filename, original_path, status, total_rows, valid_rows, invalid_rows, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'READY', ?, ?, ?, ?, ?)
                """, (batch_id, service, filename, saved_path, total_rows, len(valid_records), len(invalid_records), now, now))

                for r in valid_records:
                    conn.execute("""
                    INSERT INTO contacts (
                        id, batch_id, service, row_index, raw_data, name, phone, preferred_language, notes, extra_data,
                        validation_status, validation_errors, call_status, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'VALID', '[]', 'PENDING', ?)
                    """, (
                        r['id'], batch_id, service, r['row_index'], json.dumps(r['raw']),
                        r['name'], r['phone'], r['preferred_language'], r['notes'], json.dumps(r['extra']),
                        now
                    ))

                for r in invalid_records:
                    conn.execute("""
                    INSERT INTO contacts (
                        id, batch_id, service, row_index, raw_data, name, phone, preferred_language, notes, extra_data,
                        validation_status, validation_errors, call_status, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'INVALID', ?, 'SKIPPED', ?)
                    """, (
                        r['id'], batch_id, service, r['row_index'], json.dumps(r['raw']),
                        r['name'], r['phone'], r['preferred_language'], r['notes'], json.dumps(r['extra']),
                        json.dumps(r['errors']), now
                    ))
        finally:
            conn.close()

        # Format validation error summaries for UI
        error_summary = []
        for inv in invalid_records[:50]:
            error_summary.append({
                "row": inv["row_index"],
                "name": inv["name"],
                "phone": inv["phone"],
                "errors": inv["errors"]
            })

        # Format preview contacts for UI
        preview_contacts = []
        for val in valid_records[:10]:
            preview_contacts.append({
                "row": val["row_index"],
                "name": val["name"],
                "phone": val["phone"],
                "language": val["preferred_language"],
                "extra": val["extra"]
            })

        return {
            "fileId": batch_id,
            "fileName": filename,
            "service": service,
            "status": "READY",
            "totalRows": total_rows,
            "validRows": len(valid_records),
            "invalidRows": len(invalid_records),
            "errorSummary": error_summary,
            "previewContacts": preview_contacts,
            "columnsDetected": list(df.columns),
            "mappedFields": {orig: std for orig, std in col_mapping.items()}
        }

    @classmethod
    def generate_updated_workbook(cls, service: str, batch_id: Optional[str] = None) -> bytes:
        """
        Creates an updated Excel file containing all contacts for the specified service
        (or specific batch), preserving original columns and adding result columns.
        """
        conn = get_db_connection()
        try:
            query = "SELECT * FROM contacts WHERE service = ?"
            params = [service.lower()]
            if batch_id:
                query += " AND batch_id = ?"
                params.append(batch_id)
            query += " ORDER BY row_index ASC, updated_at DESC"

            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{service.capitalize()} Report"

        # Headers
        base_headers = [
            "Row", "Contact Name", "Phone Number", "Call Status", "Provider Call ID",
            "Attempt Count", "Started At", "Ended At", "Duration (Sec)",
            "Language", "Call Outcome", "Classification", "Extracted Fields",
            "Conversation Summary", "Validation Errors", "Error Details"
        ]

        # Service-specific headers
        if service == 'recruitment':
            headers = base_headers[:12] + [
                "Education", "Skills", "Experience", "Job Role Fit", "Availability"
            ] + base_headers[12:]
        elif service == 'sales':
            headers = base_headers[:12] + [
                "Customer Interest", "Product Discussed", "Objections", "Next Action"
            ] + base_headers[12:]
        else:
            headers = base_headers[:12] + [
                "Issue Category", "Urgency", "Resolution Status", "Escalation Required"
            ] + base_headers[12:]

        # Header styling
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        border_thin = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Fill rows
        for r in rows:
            extracted = {}
            if r["extracted_data"]:
                try:
                    extracted = json.loads(r["extracted_data"])
                except Exception:
                    pass

            val_errors = ""
            if r["validation_errors"]:
                try:
                    err_list = json.loads(r["validation_errors"])
                    val_errors = "; ".join(err_list) if isinstance(err_list, list) else str(err_list)
                except Exception:
                    val_errors = str(r["validation_errors"])

            row_data = [
                r["row_index"],
                r["name"],
                r["phone"],
                r["call_status"],
                r["provider_call_id"] or "",
                r["attempt_count"],
                r["started_at"] or "",
                r["ended_at"] or "",
                r["duration_seconds"] or 0,
                r["detected_language"] or r["preferred_language"] or "en",
                r["call_outcome"] or "",
                r["classification"] or ""
            ]

            if service == 'recruitment':
                row_data += [
                    extracted.get("education", ""),
                    extracted.get("skills", ""),
                    extracted.get("experience", ""),
                    extracted.get("job_role_fit", ""),
                    extracted.get("availability", "")
                ]
            elif service == 'sales':
                row_data += [
                    extracted.get("customer_interest", ""),
                    extracted.get("product_discussed", ""),
                    extracted.get("objections", ""),
                    extracted.get("next_action", "")
                ]
            else:
                row_data += [
                    extracted.get("issue_category", ""),
                    extracted.get("urgency", ""),
                    extracted.get("resolution_status", ""),
                    "Yes" if extracted.get("escalation_required") else "No"
                ]

            row_data += [
                json.dumps(extracted) if extracted else "",
                r["summary"] or "",
                val_errors,
                r["error_details"] or ""
            ]

            ws.append(row_data)

        # Style data cells
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = border_thin
                cell.font = Font(name="Calibri", size=10)

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                val = str(cell.value or '')
                max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
