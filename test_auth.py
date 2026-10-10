"""
Automated Test Suite for Agent Hari Authentication System (Python)
Tests all requirements: Signup, Login, Cookie/Bearer Auth, Reset Password, Page Routing.
"""

import sys
import time
import requests

BASE_URL = 'http://127.0.0.1:8080'
passed = 0
failed = 0

def assert_test(condition, test_name):
    global passed, failed
    if condition:
        print(f"  [PASS] {test_name}")
        passed += 1
    else:
        print(f"  [FAIL] {test_name}", file=sys.stderr)
        failed += 1

def run_tests():
    print("\n--- 1. Testing Signup Validation & Registration ---")
    
    # Test 1: Weak password (< 6 chars)
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={
        'name': 'Test User',
        'email': 'test@agenthari.com',
        'password': '123',
        'confirmPassword': '123'
    })
    data = res.json()
    assert_test(res.status_code == 400 and 'at least 6 characters' in data.get('message', ''), 'Rejects weak password (< 6 chars)')

    # Test 2: Mismatched passwords
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={
        'name': 'Test User',
        'email': 'test@agenthari.com',
        'password': 'Password@123',
        'confirmPassword': 'DifferentPassword'
    })
    data = res.json()
    assert_test(res.status_code == 400 and 'do not match' in data.get('message', ''), 'Rejects mismatched passwords')

    # Test 3: Invalid email
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={
        'name': 'Test User',
        'email': 'invalid-email-string',
        'password': 'Password@123',
        'confirmPassword': 'Password@123'
    })
    data = res.json()
    assert_test(res.status_code == 400 and 'valid email' in data.get('message', ''), 'Rejects invalid email format')

    # Test 4: Valid Registration
    test_email = f"user_{int(time.time() * 1000)}@agenthari.com"
    session = requests.Session()
    res = session.post(f"{BASE_URL}/api/auth/signup", json={
        'name': 'Aarav Sharma',
        'email': test_email,
        'password': 'SecurePassword123!',
        'confirmPassword': 'SecurePassword123!'
    })
    data = res.json()
    cookie_present = 'agent_hari_token' in session.cookies.get_dict()
    assert_test(res.status_code == 201 and data.get('success') is True, 'Successful signup with valid details')
    assert_test(data.get('user', {}).get('email') == test_email, 'Returns safe user object with correct email')
    assert_test('password' not in data.get('user', {}) and 'passwordHash' not in data.get('user', {}), 'NEVER exposes password or passwordHash')
    assert_test(cookie_present, 'Sets agent_hari_token HTTP-only cookie')

    # Test 5: Duplicate Email Signup
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={
        'name': 'Duplicate User',
        'email': test_email,
        'password': 'SecurePassword123!',
        'confirmPassword': 'SecurePassword123!'
    })
    data = res.json()
    assert_test(res.status_code == 409 and 'already exists' in data.get('message', ''), 'Rejects duplicate email with 409 conflict')

    print("\n--- 2. Testing Login Authentication ---")

    # Test 6: Login with incorrect password
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        'email': test_email,
        'password': 'WrongPassword999'
    })
    data = res.json()
    assert_test(res.status_code == 401 and 'incorrect' in data.get('message', ''), 'Rejects incorrect password with 401')

    # Test 7: Login with non-existent user
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        'email': 'does_not_exist@agenthari.com',
        'password': 'SomePassword123'
    })
    data = res.json()
    assert_test(res.status_code == 401 and 'incorrect' in data.get('message', ''), 'Rejects non-existent email safely')

    # Test 8: Login with valid credentials
    login_session = requests.Session()
    res = login_session.post(f"{BASE_URL}/api/auth/login", json={
        'email': test_email,
        'password': 'SecurePassword123!'
    })
    data = res.json()
    jwt_token = data.get('token')
    assert_test(res.status_code == 200 and data.get('success') is True, 'Successful login with valid credentials')
    assert_test(data.get('user', {}).get('name') == 'Aarav Sharma', 'Returns authenticated user profile')
    assert_test('password' not in data.get('user', {}) and 'passwordHash' not in data.get('user', {}), 'NEVER reveals password hashes on login')
    assert_test(bool(jwt_token), 'Issues valid signed JWT')

    print("\n--- 3. Testing Protected /api/auth/me & Middleware ---")

    # Test 9: Authenticated /api/auth/me via Cookie
    res = login_session.get(f"{BASE_URL}/api/auth/me")
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'Accesses /api/auth/me with HTTP-only cookie')
    assert_test(data.get('user', {}).get('email') == test_email, 'Correct user identity attached by authenticate_jwt')

    # Test 10: Authenticated /api/auth/me via Bearer Token
    res = requests.get(f"{BASE_URL}/api/auth/me", headers={'Authorization': f"Bearer {jwt_token}"})
    data = res.json()
    assert_test(res.status_code == 200 and data.get('user', {}).get('name') == 'Aarav Sharma', 'Accesses /api/auth/me with Bearer token')

    # Test 11: Unauthenticated /api/auth/me rejected
    res = requests.get(f"{BASE_URL}/api/auth/me")
    data = res.json()
    assert_test(res.status_code == 401 and data.get('success') is False, 'Rejects unauthenticated request with 401 Unauthorized')

    # Test 12: Invalid JWT rejected
    res = requests.get(f"{BASE_URL}/api/auth/me", headers={'Authorization': 'Bearer forged.tampered.token'})
    data = res.json()
    assert_test(res.status_code == 401 and 'Invalid authentication token' in data.get('message', ''), 'Rejects forged/tampered JWT')

    print("\n--- 4. Testing Logout & Session Clearing ---")

    # Test 13: Logout endpoint
    res = login_session.post(f"{BASE_URL}/api/auth/logout")
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'POST /api/auth/logout succeeds')
    set_cookie_hdr = res.headers.get('Set-Cookie', '')
    assert_test('agent_hari_token' in set_cookie_hdr and ('Max-Age=0' in set_cookie_hdr or 'Expires=' in set_cookie_hdr), 'Clears auth cookie on logout')

    print("\n--- 5. Testing Forgot Password & Reset Password Workflow ---")

    # Test 14: Forgot password request
    res = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={'email': test_email})
    data = res.json()
    reset_token = data.get('debugResetToken')
    assert_test(res.status_code == 200 and data.get('success') is True, 'POST /api/auth/forgot-password generates reset request')
    assert_test(bool(reset_token), 'Generates secure cryptographic reset token')

    # Test 15: Reset password with token
    res = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
        'token': reset_token,
        'newPassword': 'BrandNewPassword2026!',
        'confirmPassword': 'BrandNewPassword2026!'
    })
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'POST /api/auth/reset-password updates password successfully')

    # Test 16: Login with newly reset password
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        'email': test_email,
        'password': 'BrandNewPassword2026!'
    })
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'Successfully logs in with new password')

    # Test 17: Used reset token cannot be reused
    res = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
        'token': reset_token,
        'newPassword': 'AnotherPassword123',
        'confirmPassword': 'AnotherPassword123'
    })
    data = res.json()
    assert_test(res.status_code == 400 and data.get('success') is False, 'Cannot reuse an already consumed reset token')

    print("\n--- 6. Testing Dedicated Page Routing (NO POPUPS) ---")

    # Test 18: /signin serves HTML
    res = requests.get(f"{BASE_URL}/signin")
    assert_test(res.status_code == 200 and 'Welcome back' in res.text and 'Continue with Google' in res.text, 'GET /signin serves dedicated sign-in page')

    # Test 19: /signup serves HTML
    res = requests.get(f"{BASE_URL}/signup")
    assert_test(res.status_code == 200 and ('Create your TakeRemo account' in res.text or 'Create your Agent Hari account' in res.text), 'GET /signup serves dedicated sign-up page')

    # Test 20: /login redirects to /signin
    res = requests.get(f"{BASE_URL}/login", allow_redirects=False)
    assert_test(res.status_code == 301 and res.headers.get('Location') == '/signin', 'GET /login redirects cleanly to /signin')

    # Test 21: /account redirects to /dashboard
    res = requests.get(f"{BASE_URL}/account", allow_redirects=False)
    assert_test(res.status_code == 302 and res.headers.get('Location') == '/dashboard', 'GET /account redirects directly to /dashboard')

    print("\n===============================================")
    print(f"TEST SUMMARY: {passed} PASSED, {failed} FAILED")
    print("===============================================")

    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    run_tests()
