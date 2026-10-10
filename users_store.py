"""
Agent Hari — Centralized User Store & Repository (Python Backend)

Clean, decoupled data access layer for authentication.
Stores user records with persistent JSON storage (data/users.json).
"""

import os
import json
import secrets
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')


class UserStoreError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _init_store():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)


def read_users():
    _init_store()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[USER_STORE] Error reading users file: {e}")
        return []


def write_users(users):
    _init_store()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def find_user_by_email(email):
    if not email:
        return None
    normalized = email.strip().lower()
    users = read_users()
    for u in users:
        if u.get('email', '').strip().lower() == normalized:
            return u
    return None


def find_user_by_id(user_id):
    if not user_id:
        return None
    users = read_users()
    for u in users:
        if u.get('id') == user_id:
            return u
    return None


def create_user(name, email, password_hash):
    users = read_users()
    normalized = email.strip().lower()

    for u in users:
        if u.get('email', '').strip().lower() == normalized:
            raise UserStoreError("An account with this email already exists.", status_code=409)

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    user_id = 'usr_' + secrets.token_hex(12)

    new_user = {
        "id": user_id,
        "name": name.strip(),
        "email": normalized,
        "phone": "",
        "companyName": "",
        "jobTitle": "",
        "companySize": "",
        "industry": "",
        "profileCompleted": False,
        "passwordHash": password_hash,
        "createdAt": now,
        "updatedAt": now,
        "resetToken": None,
        "resetTokenExpires": None
    }

    users.append(new_user)
    write_users(users)

    return {
        "id": new_user["id"],
        "name": new_user["name"],
        "email": new_user["email"],
        "phone": new_user["phone"],
        "companyName": new_user["companyName"],
        "jobTitle": new_user["jobTitle"],
        "companySize": new_user["companySize"],
        "industry": new_user["industry"],
        "profileCompleted": new_user["profileCompleted"],
        "createdAt": new_user["createdAt"]
    }


def set_reset_token(email, token, expires_at_ms):
    if not email:
        return False
    users = read_users()
    normalized = email.strip().lower()
    user = None
    for u in users:
        if u.get('email', '').strip().lower() == normalized:
            user = u
            break

    if not user:
        return False

    user["resetToken"] = token
    user["resetTokenExpires"] = expires_at_ms
    user["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    write_users(users)
    return True


def find_user_by_reset_token(token):
    if not token:
        return None
    users = read_users()
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    for u in users:
        if u.get("resetToken") == token:
            expires = u.get("resetTokenExpires")
            if expires and expires > now_ms:
                return u
    return None


def update_user_password(user_id, new_password_hash):
    users = read_users()
    user = None
    for u in users:
        if u.get("id") == user_id:
            user = u
            break

    if not user:
        raise UserStoreError("User not found.", status_code=404)

    user["passwordHash"] = new_password_hash
    user["resetToken"] = None
    user["resetTokenExpires"] = None
    user["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    write_users(users)
    return True


def update_user_profile(user_id, updates):
    users = read_users()
    user = None
    for u in users:
        if u.get("id") == user_id:
            user = u
            break

    if not user:
        raise UserStoreError("User not found.", status_code=404)

    name = updates.get("name")
    if name and isinstance(name, str) and name.strip():
        user["name"] = name.strip()

    company_name = updates.get("companyName")
    if company_name and isinstance(company_name, str):
        user["companyName"] = company_name.strip()

    phone = updates.get("phone")
    if phone and isinstance(phone, str):
        user["phone"] = phone.strip()

    if "jobTitle" in updates and isinstance(updates["jobTitle"], str):
        user["jobTitle"] = updates["jobTitle"].strip()

    if "companySize" in updates and isinstance(updates["companySize"], str):
        user["companySize"] = updates["companySize"].strip()

    if "industry" in updates and isinstance(updates["industry"], str):
        user["industry"] = updates["industry"].strip()

    user["profileCompleted"] = True
    user["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    write_users(users)

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user.get("phone", ""),
        "companyName": user.get("companyName", ""),
        "jobTitle": user.get("jobTitle", ""),
        "companySize": user.get("companySize", ""),
        "industry": user.get("industry", ""),
        "profileCompleted": bool(user.get("profileCompleted", False)),
        "createdAt": user.get("createdAt", ""),
        "updatedAt": user.get("updatedAt", "")
    }


_init_store()
