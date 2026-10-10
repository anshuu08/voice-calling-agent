"""
Agent Hari — Production Python Server with JWT Authentication (Flask)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from flask import Flask, send_from_directory, Response, request, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
from routes.admin import admin_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PORT = int(os.environ.get('PORT', 8080))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

# Configure CORS
CORS(app, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    return response

# Mount Authentication & Admin APIs
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# Dedicated Full-Page Routes (NO POPUPS / NO MODALS)
@app.route('/signin')
def signin():
    return send_from_directory(BASE_DIR, 'signin.html')

@app.route('/login')
def login():
    # Login redirects to dedicated signin page (301)
    return Response('', status=301, headers={'Location': '/signin'})

@app.route('/signup')
def signup():
    return send_from_directory(BASE_DIR, 'signup.html')

@app.route('/forgot-password')
def forgot_password():
    return send_from_directory(BASE_DIR, 'forgot-password.html')

@app.route('/reset-password')
def reset_password():
    return send_from_directory(BASE_DIR, 'reset-password.html')

@app.route('/onboarding')
def onboarding():
    return send_from_directory(BASE_DIR, 'onboarding.html')

@app.route('/dashboard')
def dashboard():
    # Protected Admin Route: If no auth token in cookies/headers and not in testing, redirect to /signin
    token = request.cookies.get('agent_hari_token')
    if not token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]

    if not token and not os.environ.get('TESTING'):
        return Response('', status=302, headers={'Location': '/signin'})

    return send_from_directory(BASE_DIR, 'dashboard.html')

@app.route('/account')
def account():
    # Old /account route redirects directly to /dashboard (302)
    return Response('', status=302, headers={'Location': '/dashboard'})

@app.route('/api/exotel/callback', methods=['POST', 'GET'])
@app.route('/api/exotel/webhook', methods=['POST', 'GET'])
def exotel_public_webhook():
    from routes.admin import exotel_webhook
    return exotel_webhook()


@app.route('/phone-preview')
@app.route('/phone-designs-preview')
def phone_preview():
    return send_from_directory(BASE_DIR, 'phone-designs-preview.html')

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

# Centralized error handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    print(f"Unhandled server error: {e}")
    return jsonify({
        'success': False,
        'message': str(e) or 'An unexpected error occurred.'
    }), 500

if __name__ == '__main__':
    print("===============================================")
    print(f"  Agent Hari Python Server running on http://localhost:{PORT}")
    print(f"  Exotel AgentStream WebSocket Active on /voicebot")
    print("===============================================")

    import uvicorn
    from starlette.applications import Starlette
    from starlette.middleware.wsgi import WSGIMiddleware
    from starlette.routing import WebSocketRoute, Mount
    from services.voicebot_stream_service import handle_voicebot_websocket

    asgi_app = Starlette(
        routes=[
            WebSocketRoute('/voicebot', handle_voicebot_websocket),
            Mount('/', WSGIMiddleware(app))
        ]
    )

    uvicorn.run(asgi_app, host='0.0.0.0', port=PORT, log_level='info')
