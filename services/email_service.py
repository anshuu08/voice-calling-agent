"""
TakeRemo — Email Notification Service Layer (SMTP)
Sends non-blocking batch completion summaries to authorized administrator (Reach@takeremo.com).
Safely logs any SMTP connection/handshake errors without blocking the calling pipeline.
"""

import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

from services.db import get_db_connection


class EmailService:
    @classmethod
    def send_batch_completion_summary(cls, batch_id: str):
        """Dispatches an asynchronous thread to send the summary email."""
        thread = threading.Thread(
            target=cls._send_summary_worker,
            args=(batch_id,),
            daemon=True,
            name=f"EmailSummaryWorker-{batch_id}"
        )
        thread.start()

    @classmethod
    def _send_summary_worker(cls, batch_id: str):
        host = os.environ.get('EMAIL_HOST', 'smtp.takeremo.com')
        port = int(os.environ.get('EMAIL_PORT', 587))
        user = os.environ.get('EMAIL_USER', 'Reach@takeremo.com')
        pwd = os.environ.get('EMAIL_PASSWORD', '')

        if not (host and user and pwd):
            print("[EmailService] SMTP credentials missing or incomplete; skipping email delivery.")
            return

        conn = get_db_connection()
        try:
            batch = conn.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
            if not batch:
                return

            stats = conn.execute("""
            SELECT call_status, COUNT(*) as cnt
            FROM contacts
            WHERE batch_id = ?
            GROUP BY call_status
            """, (batch_id,)).fetchall()

            status_counts = {r['call_status']: r['cnt'] for r in stats}
        finally:
            conn.close()

        service_name = batch['service'].capitalize()
        completed = status_counts.get('COMPLETED', 0)
        failed = status_counts.get('FAILED', 0)
        skipped = status_counts.get('SKIPPED', 0)
        total = batch['total_rows']

        subject = f"[TakeRemo Alert] Voice Campaign Completed — {service_name} ({completed}/{total} Completed)"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px;">
                <div style="border-bottom: 2px solid #ef4444; padding-bottom: 12px; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #0f172a;">TakeRemo Voice Campaign Summary</h2>
                    <p style="margin: 4px 0 0; color: #64748b; font-size: 14px;">Automated Report for Score Labs Operations</p>
                </div>

                <p>Hello Administrator,</p>
                <p>The automated AI voice calling campaign for <strong>{service_name}</strong> (Batch: <code>{batch_id}</code>) has finished processing.</p>

                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold;">Service Workflow:</td>
                        <td style="padding: 10px;">{service_name}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold;">File Uploaded:</td>
                        <td style="padding: 10px;">{batch['filename']}</td>
                    </tr>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold;">Total Contacts Processed:</td>
                        <td style="padding: 10px;">{total}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #16a34a;">Successfully Completed Calls:</td>
                        <td style="padding: 10px; font-weight: bold; color: #16a34a;">{completed}</td>
                    </tr>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #dc2626;">Failed / Unanswered Calls:</td>
                        <td style="padding: 10px; color: #dc2626;">{failed}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #eab308;">Skipped / Invalid Rows:</td>
                        <td style="padding: 10px; color: #eab308;">{skipped}</td>
                    </tr>
                </table>

                <p style="margin-top: 24px;">
                    You can inspect all turn-by-turn dialogue transcripts, classifications, and download the updated Excel report directly from the Remo Admin Dashboard.
                </p>

                <div style="margin: 24px 0; text-align: center;">
                    <a href="http://localhost:8080/dashboard" style="background: #ef4444; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                        Open Remo Admin Dashboard
                    </a>
                </div>

                <p style="color: #94a3b8; font-size: 12px; margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
                    TakeRemo Voice AI • Score Labs • Confidential Telephony Notification
                </p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = user
        msg.attach(MIMEText(html_body, 'html'))

        try:
            # Connect via STARTTLS on port 587 or SSL on port 465
            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=12)
            else:
                server = smtplib.SMTP(host, port, timeout=12)
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(user, pwd)
            server.sendmail(user, [user], msg.as_string())
            server.quit()
            print(f"[EmailService] Successfully sent batch summary email to {user} for batch {batch_id}")
        except Exception as e:
            print(f"[EmailService] Notice: Could not deliver SMTP summary email ({e}). The calling pipeline continues unaffected.")
