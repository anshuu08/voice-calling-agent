"""
Agent Hari — Authentication API Routes (Python Backend)

Endpoints:
- POST /api/auth/signup
- POST /api/auth/login
- POST /api/auth/logout
- GET  /api/auth/me
- POST /api/auth/onboarding
- PUT  /api/auth/profile
- POST /api/auth/forgot-password
- POST /api/auth/reset-password
"""

import os
import re
import secrets
import datetime
from flask import Blueprint, request, jsonify, make_response, g
import bcrypt
import jwt

from users_store import (
    find_user_by_email,
    find_user_by_id,
    create_user,
    set_reset_token,
    find_user_by_reset_token,
    update_user_password,
    update_user_profile,
    UserStoreError
)
from middleware.auth import authenticate_jwt, get_jwt_secret

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def generate_token(user: dict) -> str:
    secret = get_jwt_secret()
    payload = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def set_auth_cookie(response, token: str):
    is_prod = os.environ.get('NODE_ENV') == 'production' or os.environ.get('FLASK_ENV') == 'production'
    response.set_cookie(
        'agent_hari_token',
        token,
        max_age=7 * 24 * 3600,
        httponly=True,
        samesite='Strict' if is_prod else 'Lax',
        secure=is_prod,
        path='/'
    )
    return response


def clear_auth_cookie(response):
    response.set_cookie(
        'agent_hari_token',
        '',
        expires=0,
        max_age=0,
        path='/'
    )
    return response


# ============================================================================
# 1. SIGNUP API: POST /api/auth/signup
# ============================================================================
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            'success': False,
            'message': 'Please provide a valid full name (at least 2 characters).'
        }), 400

    if not email or not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
        return jsonify({
            'success': False,
            'message': 'Please provide a valid email address.'
        }), 400

    if not password or not isinstance(password, str) or len(password) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must contain at least 6 characters.'
        }), 400

    if password != confirm_password:
        return jsonify({
            'success': False,
            'message': 'Passwords do not match. Please re-enter your password.'
        }), 400

    existing = find_user_by_email(email.strip())
    if existing:
        return jsonify({
            'success': False,
            'message': 'An account with this email already exists.'
        }), 409

    pwd_hash = hash_password(password)
    try:
        new_user = create_user(name.strip(), email.strip(), pwd_hash)
    except UserStoreError as e:
        return jsonify({'success': False, 'message': e.message}), e.status_code

    token = generate_token(new_user)
    resp = make_response(jsonify({
        'success': True,
        'message': 'Account created successfully.',
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'phone': new_user.get('phone', ''),
            'companyName': new_user.get('companyName', ''),
            'profileCompleted': bool(new_user.get('profileCompleted', False))
        },
        'token': token
    }), 201)

    return set_auth_cookie(resp, token)


# ============================================================================
# 2. LOGIN API: POST /api/auth/login
# ============================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Please provide both email and password.'
        }), 400

    user = find_user_by_email(email.strip())
    if not user:
        return jsonify({
            'success': False,
            'message': 'Email or password is incorrect.'
        }), 401

    if not verify_password(password, user.get('passwordHash', '')):
        return jsonify({
            'success': False,
            'message': 'Email or password is incorrect.'
        }), 401

    token = generate_token(user)
    resp = make_response(jsonify({
        'success': True,
        'message': 'Signed in successfully.',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'companyName': user.get('companyName', ''),
            'jobTitle': user.get('jobTitle', ''),
            'companySize': user.get('companySize', ''),
            'industry': user.get('industry', ''),
            'profileCompleted': bool(user.get('profileCompleted', False))
        },
        'token': token
    }), 200)

    return set_auth_cookie(resp, token)


# ============================================================================
# 3. LOGOUT API: POST /api/auth/logout
# ============================================================================
@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = make_response(jsonify({
        'success': True,
        'message': 'Logged out successfully.'
    }), 200)
    return clear_auth_cookie(resp)


# ============================================================================
# 4. CURRENT AUTHENTICATED USER: GET /api/auth/me
# ============================================================================
@auth_bp.route('/me', methods=['GET'])
@authenticate_jwt
def get_me():
    return jsonify({
        'success': True,
        'user': g.user
    }), 200


# ============================================================================
# 5. ONBOARDING & PROFILE UPDATE: POST /api/auth/onboarding
# ============================================================================
@auth_bp.route('/onboarding', methods=['POST'])
@authenticate_jwt
def onboarding():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    company_name = data.get('companyName')
    phone = data.get('phone')

    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            'success': False,
            'message': 'Please enter your full name (at least 2 characters).'
        }), 400

    if not company_name or not isinstance(company_name, str) or len(company_name.strip()) < 2:
        return jsonify({
            'success': False,
            'message': 'Please enter your company name (at least 2 characters).'
        }), 400

    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone) if phone else ''
    if not phone or not isinstance(phone, str) or len(phone_clean) < 7:
        return jsonify({
            'success': False,
            'message': 'Please enter a valid phone number (at least 7 digits).'
        }), 400

    updated = update_user_profile(g.user['id'], {
        'name': name.strip(),
        'companyName': company_name.strip(),
        'phone': phone.strip(),
        'jobTitle': data.get('jobTitle', ''),
        'companySize': data.get('companySize', ''),
        'industry': data.get('industry', '')
    })

    return jsonify({
        'success': True,
        'message': 'Workspace profile saved successfully.',
        'user': updated
    }), 200


# ============================================================================
# 6. PROFILE UPDATE: PUT /api/auth/profile
# ============================================================================
@auth_bp.route('/profile', methods=['PUT'])
@authenticate_jwt
def update_profile():
    data = request.get_json(silent=True) or {}
    updated = update_user_profile(g.user['id'], {
        'name': data.get('name'),
        'companyName': data.get('companyName'),
        'phone': data.get('phone'),
        'jobTitle': data.get('jobTitle', ''),
        'companySize': data.get('companySize', ''),
        'industry': data.get('industry', '')
    })
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully.',
        'user': updated
    }), 200


# ============================================================================
# 7. FORGOT PASSWORD: POST /api/auth/forgot-password
# ============================================================================
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email')

    if not email or not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
        return jsonify({
            'success': False,
            'message': 'Please provide a valid email address.'
        }), 400

    user = find_user_by_email(email.strip())
    reset_token = None

    if user:
        reset_token = secrets.token_hex(32)
        expires_at_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000) + 3600000
        set_reset_token(user['email'], reset_token, expires_at_ms)
        print(f"[AUTH] Password reset requested for: {user['email']}")
        print(f"[AUTH] Reset Token: {reset_token}")

    is_dev = os.environ.get('NODE_ENV') != 'production' and os.environ.get('FLASK_ENV') != 'production'
    response_data = {
        'success': True,
        'message': 'If an account exists with this email, instructions to reset your password have been generated.'
    }
    if is_dev and reset_token:
        response_data['debugResetToken'] = reset_token

    return jsonify(response_data), 200


# ============================================================================
# 8. RESET PASSWORD: POST /api/auth/reset-password
# ============================================================================
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')

    if not token:
        return jsonify({
            'success': False,
            'message': 'Reset token is required.'
        }), 400

    if not new_password or len(new_password) < 6:
        return jsonify({
            'success': False,
            'message': 'New password must contain at least 6 characters.'
        }), 400

    if new_password != confirm_password:
        return jsonify({
            'success': False,
            'message': 'Passwords do not match.'
        }), 400

    user = find_user_by_reset_token(token)
    if not user:
        return jsonify({
            'success': False,
            'message': 'Invalid or expired password reset link. Please request a new one.'
        }), 400

    pwd_hash = hash_password(new_password)
    update_user_password(user['id'], pwd_hash)

    return jsonify({
        'success': True,
        'message': 'Your password has been reset successfully. You can now sign in.'
    }), 200
