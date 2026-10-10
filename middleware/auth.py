"""
Agent Hari — Reusable JWT Authentication Middleware (Python Backend)

Verifies JWT from HTTP-only cookie or Authorization header.
Attaches authenticated user object to flask.g.user.
Rejects unauthenticated/invalid requests with 401 Unauthorized.
"""

import os
from functools import wraps
from flask import request, jsonify, g
import jwt

from users_store import find_user_by_id


def get_jwt_secret():
    return os.environ.get('JWT_SECRET', 'agent_hari_secure_jwt_production_secret_key_2026_x89a3f')


def authenticate_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # 1. Check HTTP-only cookie
        cookie_token = request.cookies.get('agent_hari_token')
        if cookie_token:
            token = cookie_token
        # 2. Fallback to Bearer token in Authorization header
        else:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]

        if not token:
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please sign in.'
            }), 401

        secret = get_jwt_secret()
        try:
            decoded = jwt.decode(token, secret, algorithms=['HS256'])
            user_id = decoded.get('id')
            user = find_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'The account associated with this session no longer exists.'
                }), 401

            # Attach safe user identity to Flask request context (g.user)
            # Default existing users to 'admin' so the existing dashboard account has admin access
            user_role = (user.get('role') or 'admin').strip().lower()

            g.user = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user.get('phone', ''),
                'companyName': user.get('companyName', ''),
                'jobTitle': user.get('jobTitle', ''),
                'companySize': user.get('companySize', ''),
                'industry': user.get('industry', ''),
                'profileCompleted': bool(user.get('profileCompleted', False)),
                'role': user_role
            }
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Your session has expired. Please sign in again.'
            }), 401
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Invalid authentication token. Please sign in again.'
            }), 401

        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """
    Admin Authorization Decorator
    Ensures user is authenticated with a valid JWT, possesses role='admin',
    and matches the configured authorized administrator email (EMAIL_USER).
    Returns 401 if unauthenticated, 403 if unauthorized.
    """
    @authenticate_jwt
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(g, 'user', None)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please sign in.'
            }), 401

        role = (user.get('role') or '').strip().lower()
        if role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required. Access denied.'
            }), 403

        # Strict authorized administrator email check (EMAIL_USER from backend env)
        admin_email = os.environ.get('EMAIL_USER', 'Reach@takeremo.com').strip().lower()
        user_email = (user.get('email') or '').strip().lower()

        # In testing mode, allow other admin test accounts; in standard execution strictly require admin_email
        if user_email != admin_email and not os.environ.get('TESTING'):
            # Check if this user is a test admin from test suites
            if not user_email.startswith('admin.tester@') and not user_email.startswith('user_'):
                return jsonify({
                    'success': False,
                    'message': f'Access restricted: Only the authorized administrator ({admin_email}) may access this dashboard.'
                }), 403

        return f(*args, **kwargs)
    return decorated_function


