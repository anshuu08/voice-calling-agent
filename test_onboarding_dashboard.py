"""
Automated Verification Suite for User Onboarding & User Dashboard (Python)
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
    print("\n--- 1. Testing Route Redirection & Availability ---")

    # Test 1: /account redirects to /dashboard
    res = requests.get(f"{BASE_URL}/account", allow_redirects=False)
    assert_test(res.status_code == 302 and res.headers.get('Location') == '/dashboard', 'GET /account redirects directly to /dashboard (302)')

    # Test 2: /onboarding serves dedicated onboarding page
    res = requests.get(f"{BASE_URL}/onboarding")
    assert_test(res.status_code == 200 and ("Let's set up your TakeRemo workspace" in res.text or "Let's set up your Agent Hari workspace" in res.text), 'GET /onboarding serves workspace setup card')

    # Test 3: /dashboard serves TakeRemo dashboard page
    res = requests.get(f"{BASE_URL}/dashboard")
    assert_test(res.status_code == 200 and ('TakeRemo' in res.text or 'Remo' in res.text), 'GET /dashboard serves TakeRemo dashboard')

    print("\n--- 2. Testing Registration with Initial Incomplete Profile ---")

    test_email = f"founder_{int(time.time() * 1000)}@kondrutech.com"
    session = requests.Session()
    res = session.post(f"{BASE_URL}/api/auth/signup", json={
        'name': 'Anshu Sharma',
        'email': test_email,
        'password': 'Password@2026!',
        'confirmPassword': 'Password@2026!'
    })
    data = res.json()
    assert_test(res.status_code == 201 and data.get('success') is True, 'Sign up successful')
    assert_test(data.get('user', {}).get('profileCompleted') is False, 'New user starts with profileCompleted: False')

    print("\n--- 3. Testing GET /api/auth/me Profile Check ---")

    res = session.get(f"{BASE_URL}/api/auth/me")
    data = res.json()
    assert_test(res.status_code == 200 and data.get('user', {}).get('profileCompleted') is False, 'GET /api/auth/me detects incomplete profile')
    assert_test(data.get('user', {}).get('email') == test_email, 'Email matches authenticated account')

    print("\n--- 4. Testing Onboarding Validation ---")

    # Test: Missing company name
    res = session.post(f"{BASE_URL}/api/auth/onboarding", json={
        'name': 'Anshu Sharma',
        'companyName': '',
        'phone': '+91 98765 43210'
    })
    data = res.json()
    assert_test(res.status_code == 400 and 'company name' in data.get('message', ''), 'Rejects onboarding with missing company name')

    # Test: Invalid phone number
    res = session.post(f"{BASE_URL}/api/auth/onboarding", json={
        'name': 'Anshu Sharma',
        'companyName': 'Kondru Technologies',
        'phone': '123'
    })
    data = res.json()
    assert_test(res.status_code == 400 and 'phone number' in data.get('message', ''), 'Rejects onboarding with invalid phone number (< 7 digits)')

    print("\n--- 5. Testing Successful Onboarding Completion ---")

    res = session.post(f"{BASE_URL}/api/auth/onboarding", json={
        'name': 'Anshu Sharma',
        'companyName': 'Kondru Technologies',
        'phone': '+91 98765 43210',
        'jobTitle': 'Founder & CEO',
        'industry': 'Technology / SaaS'
    })
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'POST /api/auth/onboarding succeeds')
    assert_test(data.get('user', {}).get('profileCompleted') is True, 'profileCompleted updated to True')
    assert_test(data.get('user', {}).get('companyName') == 'Kondru Technologies', 'Company name saved properly')
    assert_test(data.get('user', {}).get('phone') == '+91 98765 43210', 'Phone number saved properly')

    print("\n--- 6. Testing Persistence & Subsequent Login ---")

    # Verify GET /api/auth/me now returns profileCompleted: True
    res = session.get(f"{BASE_URL}/api/auth/me")
    data = res.json()
    assert_test(data.get('user', {}).get('profileCompleted') is True, 'GET /api/auth/me confirms profile is complete')

    # Logout
    res = session.post(f"{BASE_URL}/api/auth/logout")

    # Subsequent Login
    login_session = requests.Session()
    res = login_session.post(f"{BASE_URL}/api/auth/login", json={
        'email': test_email,
        'password': 'Password@2026!'
    })
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'Login successful')
    assert_test(data.get('user', {}).get('profileCompleted') is True, 'Subsequent login immediately recognizes completed profile')
    assert_test(data.get('user', {}).get('companyName') == 'Kondru Technologies', 'Preserves user company name across logins')

    print("\n--- 7. Testing Profile Update via Dashboard PUT /api/auth/profile ---")

    res = login_session.put(f"{BASE_URL}/api/auth/profile", json={
        'name': 'Anshu K. Sharma',
        'companyName': 'Kondru Technologies Enterprise',
        'phone': '+91 98765 00000',
        'jobTitle': 'Managing Director'
    })
    data = res.json()
    assert_test(res.status_code == 200 and data.get('success') is True, 'PUT /api/auth/profile updates profile from dashboard')
    assert_test(data.get('user', {}).get('name') == 'Anshu K. Sharma', 'Updated name preserved')
    assert_test(data.get('user', {}).get('companyName') == 'Kondru Technologies Enterprise', 'Updated company name preserved')

    print("\n===============================================")
    print(f"ONBOARDING & DASHBOARD TESTS: {passed} PASSED, {failed} FAILED")
    print("===============================================")

    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    run_tests()
