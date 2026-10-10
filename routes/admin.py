"""
TakeRemo — Admin API Blueprint (Python Backend)

Endpoints:
- GET  /api/admin/dashboard
- GET  /api/admin/users
- POST /api/admin/recruitment/upload
- POST /api/admin/recruitment/start
- POST /api/admin/sales/upload
- POST /api/admin/sales/start
- POST /api/admin/support/upload
- POST /api/admin/support/start
- GET  /api/admin/conversations
- GET  /api/admin/conversations/<id>
- GET  /api/admin/calls

All routes protected with @require_admin middleware (Valid JWT + role='admin').
Centralized error handling returns consistent JSON without leaking internal details.
"""

from flask import Blueprint, request, jsonify, g
from middleware.auth import require_admin
from services.admin_service import AdminService
from services.recruitment_service import RecruitmentService, RecruitmentServiceError
from services.sales_service import SalesService, SalesServiceError
from services.support_service import SupportService, SupportServiceError
from services.conversation_service import ConversationService
from services.call_service import CallService

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ============================================================================
# 1. DASHBOARD METRICS: GET /api/admin/dashboard
# ============================================================================
@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def get_dashboard():
    try:
        stats = AdminService.get_dashboard_stats()
        response_data = {
            "success": True,
            **stats
        }
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Unable to load dashboard metrics at this time."
        }), 500


# ============================================================================
# 2. USERS MANAGEMENT: GET /api/admin/users
# ============================================================================
@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)

        result = AdminService.get_users(page=page, limit=limit, search=search, status=status)
        return jsonify({
            "success": True,
            **result
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Unable to retrieve users list."
        }), 500


# ============================================================================
# 3. RECRUITMENT WORKFLOW: UPLOAD & START
# ============================================================================
def _extract_upload_file(req):
    """
    Helper to extract uploaded file from multipart form-data or JSON payload.
    """
    # 1. Check multipart/form-data file upload
    if req.files:
        for key in ['file', 'excel', 'candidates', 'leads', 'data']:
            if key in req.files:
                f = req.files[key]
                if f.filename:
                    return f, f.filename
        # Fallback to first file in request
        for f in req.files.values():
            if f.filename:
                return f, f.filename

    # 2. Fallback to JSON payload (e.g. { "fileName": "candidates.xlsx" })
    data = req.get_json(silent=True) or {}
    filename = data.get('fileName') or data.get('filename')
    if filename:
        return None, filename

    return None, None


@admin_bp.route('/recruitment/upload', methods=['POST'])
@require_admin
def recruitment_upload():
    try:
        file_obj, filename = _extract_upload_file(request)
        if not filename:
            return jsonify({
                "success": False,
                "message": "No file uploaded. Please provide an Excel (.xlsx, .xls) file."
            }), 400

        result = RecruitmentService.validate_and_process_upload(file_obj, filename)
        return jsonify({
            "success": True,
            **result
        }), 200
    except RecruitmentServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to process candidate spreadsheet upload."
        }), 500


@admin_bp.route('/recruitment/start', methods=['POST'])
@require_admin
def recruitment_start():
    try:
        data = request.get_json(silent=True) or {}
        file_id = data.get('fileId') or data.get('file_id')
        if not file_id:
            return jsonify({
                "success": False,
                "message": "Parameter 'fileId' is required to initialize campaign."
            }), 400

        result = RecruitmentService.start_calling_campaign(file_id)
        return jsonify({
            "success": True,
            **result
        }), 200
    except RecruitmentServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to initialize recruitment calling campaign."
        }), 500


# ============================================================================
# 4. SALES WORKFLOW: UPLOAD & START
# ============================================================================
@admin_bp.route('/sales/upload', methods=['POST'])
@require_admin
def sales_upload():
    try:
        file_obj, filename = _extract_upload_file(request)
        if not filename:
            return jsonify({
                "success": False,
                "message": "No file uploaded. Please provide an Excel (.xlsx, .xls) file."
            }), 400

        result = SalesService.validate_and_process_upload(file_obj, filename)
        return jsonify({
            "success": True,
            **result
        }), 200
    except SalesServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to process sales lead spreadsheet upload."
        }), 500


@admin_bp.route('/sales/start', methods=['POST'])
@require_admin
def sales_start():
    try:
        data = request.get_json(silent=True) or {}
        file_id = data.get('fileId') or data.get('file_id')
        if not file_id:
            return jsonify({
                "success": False,
                "message": "Parameter 'fileId' is required to initialize campaign."
            }), 400

        result = SalesService.start_calling_campaign(file_id)
        return jsonify({
            "success": True,
            **result
        }), 200
    except SalesServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to initialize sales calling campaign."
        }), 500


# ============================================================================
# 5. CUSTOMER SUPPORT WORKFLOW: UPLOAD & START
# ============================================================================
@admin_bp.route('/support/upload', methods=['POST'])
@require_admin
def support_upload():
    try:
        file_obj, filename = _extract_upload_file(request)
        if not filename:
            return jsonify({
                "success": False,
                "message": "No file uploaded. Please provide an Excel (.xlsx, .xls) file."
            }), 400

        result = SupportService.validate_and_process_upload(file_obj, filename)
        return jsonify({
            "success": True,
            **result
        }), 200
    except SupportServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to process customer support file upload."
        }), 500


@admin_bp.route('/support/start', methods=['POST'])
@require_admin
def support_start():
    try:
        data = request.get_json(silent=True) or {}
        file_id = data.get('fileId') or data.get('file_id')
        if not file_id:
            return jsonify({
                "success": False,
                "message": "Parameter 'fileId' is required to initialize campaign."
            }), 400

        result = SupportService.start_calling_campaign(file_id)
        return jsonify({
            "success": True,
            **result
        }), 200
    except SupportServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to initialize support calling campaign."
        }), 500


# ============================================================================
# 6. CONVERSATIONS & TRANSCRIPTS: GET /api/admin/conversations
# ============================================================================
@admin_bp.route('/conversations', methods=['GET'])
@require_admin
def get_conversations():
    try:
        service = request.args.get('service', '', type=str)
        user = request.args.get('user', '', type=str)
        status = request.args.get('status', '', type=str)
        date = request.args.get('date', '', type=str)
        search = request.args.get('search', '', type=str)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        result = ConversationService.get_conversations(
            service=service,
            user=user,
            status=status,
            date=date,
            search=search,
            page=page,
            limit=limit
        )
        return jsonify({
            "success": True,
            **result
        }), 200
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to load conversations."
        }), 500


@admin_bp.route('/conversations/<conv_id>', methods=['GET'])
@require_admin
def get_conversation_details(conv_id):
    try:
        conv = ConversationService.get_conversation_by_id(conv_id)
        if not conv:
            return jsonify({
                "success": False,
                "message": f"Conversation with ID '{conv_id}' was not found."
            }), 404

        return jsonify({
            "success": True,
            "conversation": conv,
            **conv
        }), 200
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve conversation details."
        }), 500


@admin_bp.route('/conversations/<conv_id>', methods=['DELETE'])
@require_admin
def delete_conversation(conv_id):
    try:
        from services.db import get_db_connection
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("DELETE FROM transcript_messages WHERE conversation_id = ?", (conv_id,))
                conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        finally:
            conn.close()
        return jsonify({"success": True, "message": "Conversation deleted."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================================================
# 7. CALL HISTORY: GET /api/admin/calls
# ============================================================================
@admin_bp.route('/calls', methods=['GET'])
@require_admin
def get_calls():
    try:
        service = request.args.get('service', '', type=str)
        status = request.args.get('status', '', type=str)
        user = request.args.get('user', '', type=str)
        date = request.args.get('date', '', type=str)
        search = request.args.get('search', '', type=str)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        result = CallService.get_calls(
            service=service,
            status=status,
            user=user,
            date=date,
            search=search,
            page=page,
            limit=limit
        )
        return jsonify({
            "success": True,
            **result
        }), 200
    except Exception:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve call history."
        }), 500


@admin_bp.route('/calls/<call_id>', methods=['DELETE'])
@require_admin
def delete_call(call_id):
    try:
        from services.db import get_db_connection
        conn = get_db_connection()
        
        # ID is either 'call_{contact_id[:8]}' for DB or 'call_101' for sample data
        c_id = call_id.replace("call_", "")
        
        try:
            with conn:
                # Delete any associated conversations to prevent orphaned transcripts
                # (if PRAGMA foreign_keys is OFF, we do it manually)
                conv_ids = [r['id'] for r in conn.execute("SELECT id FROM conversations WHERE contact_id LIKE ?", (f"{c_id}%",)).fetchall()]
                for conv in conv_ids:
                    conn.execute("DELETE FROM transcript_messages WHERE conversation_id = ?", (conv,))
                conn.execute("DELETE FROM conversations WHERE contact_id LIKE ?", (f"{c_id}%",))
                
                # Delete the contact which represents the call log in DB
                conn.execute("DELETE FROM contacts WHERE id LIKE ?", (f"{c_id}%",))
        finally:
            conn.close()
            
        return jsonify({"success": True, "message": "Call log deleted."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================================================
# 8. EXCEL REPORT DOWNLOAD: GET /api/admin/<service>/download
# ============================================================================
@admin_bp.route('/<service>/download', methods=['GET'])
@admin_bp.route('/export/<service>', methods=['GET'])
@require_admin
def download_updated_excel(service):
    """
    Generates and downloads the updated Excel workbook for the specified service.
    Contains original contact fields plus newly populated result columns.
    """
    from flask import Response
    from services.excel_service import ExcelService

    svc = service.lower().strip()
    if svc not in ('recruitment', 'sales', 'support'):
        return jsonify({"success": False, "message": f"Invalid service '{service}'"}), 400

    try:
        batch_id = request.args.get('batchId') or request.args.get('fileId')
        excel_bytes = ExcelService.generate_updated_workbook(svc, batch_id)

        filename = f"{svc}_updated_results.xlsx"
        return Response(
            excel_bytes,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to generate Excel download: {str(e)}"}), 500


# ============================================================================
# 9. QUEUE CONTROLS: PAUSE, RESUME, CANCEL, STATUS
# ============================================================================
@admin_bp.route('/queue/status', methods=['GET'])
@require_admin
def get_queue_status():
    from services.call_queue_worker import CallQueueWorker
    batch_id = request.args.get('batchId')
    status = CallQueueWorker.get_queue_status(batch_id)
    return jsonify({"success": True, **status}), 200


@admin_bp.route('/queue/pause', methods=['POST'])
@require_admin
def pause_queue():
    from services.call_queue_worker import CallQueueWorker
    CallQueueWorker.pause_queue()
    return jsonify({"success": True, "message": "Sequential calling queue paused."}), 200


@admin_bp.route('/queue/resume', methods=['POST'])
@require_admin
def resume_queue():
    from services.call_queue_worker import CallQueueWorker
    CallQueueWorker.resume_queue()
    return jsonify({"success": True, "message": "Sequential calling queue resumed."}), 200


@admin_bp.route('/queue/cancel', methods=['POST'])
@require_admin
def cancel_queue():
    from services.call_queue_worker import CallQueueWorker
    data = request.get_json(silent=True) or {}
    batch_id = data.get('batchId') or data.get('fileId')
    CallQueueWorker.cancel_queue(batch_id)
    return jsonify({"success": True, "message": "Calling queue cancelled."}), 200


# ============================================================================
# 10. TEST CALL TRIGGER: POST /api/admin/test-call
# ============================================================================
@admin_bp.route('/test-call', methods=['POST'])
@require_admin
def test_call():
    """
    Dispatches a single test call to an approved phone number or triggers
    interactive simulation for verification.
    """
    from services.call_queue_worker import CallQueueWorker
    from services.db import get_db_connection, utc_now
    import secrets

    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    name = data.get('name', 'Test Contact').strip()
    service = data.get('service', 'recruitment').strip().lower()

    if not phone:
        return jsonify({"success": False, "message": "Phone number is required for test call."}), 400

    conn = get_db_connection()
    now = utc_now()
    batch_id = f"test_batch_{secrets.token_hex(4)}"
    contact_id = f"test_cnt_{secrets.token_hex(6)}"
    try:
        with conn:
            conn.execute("""
            INSERT INTO batches (id, service, filename, status, total_rows, valid_rows, invalid_rows, created_at, updated_at)
            VALUES (?, ?, 'single_test_call.xlsx', 'IN_PROGRESS', 1, 1, 0, ?, ?)
            """, (batch_id, service, now, now))

            conn.execute("""
            INSERT INTO contacts (id, batch_id, service, row_index, raw_data, name, phone, validation_status, call_status, updated_at)
            VALUES (?, ?, ?, 1, '{}', ?, ?, 'VALID', 'PENDING', ?)
            """, (contact_id, batch_id, service, name, phone, now))
    finally:
        conn.close()

    CallQueueWorker.enqueue_batch(batch_id)
    return jsonify({
        "success": True,
        "message": f"Test call queued for {name} ({phone}) in {service} mode.",
        "batchId": batch_id,
        "contactId": contact_id
    }), 200


# ============================================================================
# 11. EXOTEL WEBHOOK: POST /api/admin/exotel/webhook (and public /api/exotel/callback)
# ============================================================================
@admin_bp.route('/exotel/webhook', methods=['POST', 'GET'])
def exotel_webhook():
    """
    Handles Exotel carrier status callbacks idempotently.
    Updates call status and trigger next sequential turn.
    """
    from services.db import get_db_connection, utc_now
    payload = request.form.to_dict() or request.args.to_dict() or request.get_json(silent=True) or {}
    call_sid = payload.get('CallSid') or payload.get('Sid')
    status = payload.get('Status', '').lower()
    custom_field = payload.get('CustomField')

    if custom_field and call_sid:
        conn = get_db_connection()
        now = utc_now()
        duration = payload.get('CallDuration') or payload.get('Legs[0][Duration]') or 0
        try:
            dur_int = int(duration)
        except Exception:
            dur_int = 0

        try:
            with conn:
                terminal_status = 'COMPLETED' if status in ('completed', 'answered') else 'FAILED'
                conn.execute("""
                UPDATE contacts
                SET provider_call_id = ?, call_status = ?, duration_seconds = ?, updated_at = ?
                WHERE id = ?
                """, (call_sid, terminal_status, dur_int, now, custom_field))

                conn.execute("""
                UPDATE call_queue
                SET status = ?, updated_at = ?
                WHERE contact_id = ?
                """, (terminal_status, now, custom_field))
        finally:
            conn.close()

    return jsonify({"success": True, "received": True}), 200

