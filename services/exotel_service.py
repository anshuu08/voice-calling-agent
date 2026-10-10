"""
TakeRemo — Exotel Telephony Gateway Service Layer
Handles real API requests to Exotel for outbound calling, call status inspection,
and webhook event normalization.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, Tuple


class ExotelService:
    @classmethod
    def get_config(cls) -> Dict[str, str]:
        sid = os.environ.get('EXOTEL_ACCOUNT_SID', '').strip()
        key = os.environ.get('EXOTEL_API_KEY', '').strip()
        token = (os.environ.get('EXOTEL_API_TOKEN_PASSWORD') or os.environ.get('EXOTEL_API_TOKEN', '')).strip()
        sub = os.environ.get('EXOTEL_SUBDOMAIN', 'api.exotel.com').strip()
        vn = os.environ.get('EXOTEL_VIRTUAL_NUMBER', '').strip()

        if not (sid and key and token):
            raise ValueError("Exotel credentials (ACCOUNT_SID, API_KEY, API_TOKEN) are incomplete in environment.")

        return {
            "account_sid": sid,
            "api_key": key,
            "api_token": token,
            "subdomain": sub,
            "virtual_number": vn
        }

    @classmethod
    def initiate_outbound_call(
        cls,
        to_phone: str,
        custom_field: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches an outbound phone call via Exotel REST API.
        Returns a dictionary with CallSid, Status, and provider metadata.
        """
        cfg = cls.get_config()
        url = f"https://{cfg['subdomain']}/v1/Accounts/{cfg['account_sid']}/Calls/connect.json"

        # Format CallerId: remove spaces and dashes for Exotel
        caller_id = cfg['virtual_number'].replace('-', '').replace(' ', '')

        app_id = os.environ.get('EXOTEL_APP_ID', '').strip()
        app_url = os.environ.get('EXOTEL_APP_URL', '').strip()

        payload = {
            "From": to_phone,
            "CallerId": caller_id,
            "CustomField": custom_field,
            "TimeLimit": "600"  # 10 minutes max
        }

        if app_url:
            payload["Url"] = app_url
        elif app_id:
            payload["Url"] = f"http://my.exotel.com/{cfg['account_sid']}/exoml/start_voice/{app_id}"
        else:
            # When connecting without an app ID, pass virtual number as To fallback
            payload["To"] = caller_id

        cb = callback_url or os.environ.get('EXOTEL_CALLBACK_URL', '').strip()
        if cb:
            payload["StatusCallback"] = cb

        try:
            res = requests.post(
                url,
                auth=(cfg["api_key"], cfg["api_token"]),
                data=payload,
                timeout=20
            )

            if res.status_code in (200, 201):
                data = res.json()
                call_info = data.get("Call", {})
                return {
                    "success": True,
                    "callSid": call_info.get("Sid") or f"EXO_{custom_field}",
                    "status": call_info.get("Status", "queued"),
                    "provider": "exotel",
                    "raw": call_info
                }
            else:
                print(f"[ExotelService] Error initiating call (HTTP {res.status_code}): {res.text}")
                error_msg = f"Exotel API returned status {res.status_code}: {res.text[:200]}"
                return {
                    "success": False,
                    "error": error_msg,
                    "status": "failed"
                }
        except Exception as e:
            print(f"[ExotelService] Connection failure: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    @classmethod
    def get_call_status(cls, call_sid: str) -> Dict[str, Any]:
        """
        Queries Exotel for the live status of an initiated call.
        """
        cfg = cls.get_config()
        url = f"https://{cfg['subdomain']}/v1/Accounts/{cfg['account_sid']}/Calls/{call_sid}.json"

        try:
            res = requests.get(
                url,
                auth=(cfg["api_key"], cfg["api_token"]),
                timeout=10
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "success": True,
                    "call": data.get("Call", {})
                }
            return {
                "success": False,
                "error": f"HTTP {res.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
