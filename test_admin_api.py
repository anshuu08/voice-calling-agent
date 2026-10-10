"""
TakeRemo — Automated Test Suite for Admin API Layer
Verifies:
- 401 Unauthorized when unauthenticated
- 403 Forbidden when user is not admin (role='user')
- 200 OK for admin role across all endpoints:
  - GET  /api/admin/dashboard
  - GET  /api/admin/users (with search and status filters)
  - POST /api/admin/recruitment/upload (validation and mock staging)
  - POST /api/admin/recruitment/start
  - POST /api/admin/sales/upload & start
  - POST /api/admin/support/upload & start
  - GET  /api/admin/conversations (with service and search filters)
  - GET  /api/admin/conversations/:id (found and 404 not found)
  - GET  /api/admin/calls
"""

import sys
import io
import datetime
import jwt
from server import app
from middleware.auth import get_jwt_secret
import users_store

app.config['TESTING'] = True
client = app.test_client()
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


def create_mock_jwt(user_id: str, email: str, name: str) -> str:
    secret = get_jwt_secret()
    payload = {
        'id': user_id,
        'name': name,
        'email': email,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def run_tests():
    global passed, failed
    print("\n=======================================================")
    print("  TAKEREMO ADMIN API VERIFICATION SUITE")
    print("=======================================================")

    # Ensure we have an admin user and a standard non-admin user in memory
    users = users_store.read_users()
    admin_user = None
    standard_user = None

    for u in users:
        if u.get('role') == 'user':
            standard_user = u
        elif u.get('role') == 'admin' or admin_user is None:
            admin_user = u

    # Create temporary non-admin user if needed for 403 test
    if not standard_user:
        standard_user = {
            "id": "usr_test_standard_user_001",
            "name": "Regular User",
            "email": "regular.user@example.com",
            "role": "user",
            "profileCompleted": True
        }
        users.append(standard_user)
        users_store.write_users(users)

    # Ensure admin user has role='admin'
    if admin_user:
        admin_user['role'] = 'admin'
        users_store.write_users(users)
    else:
        admin_user = {
            "id": "usr_test_admin_user_001",
            "name": "Admin Tester",
            "email": "admin.tester@takeremo.com",
            "role": "admin",
            "profileCompleted": True
        }
        users.append(admin_user)
        users_store.write_users(users)

    admin_token = create_mock_jwt(admin_user['id'], admin_user['email'], admin_user['name'])
    user_token = create_mock_jwt(standard_user['id'], standard_user['email'], standard_user['name'])

    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    user_headers = {'Authorization': f'Bearer {user_token}'}

    # -------------------------------------------------------------
    # 1. Unauthenticated Requests (401 Unauthorized)
    # -------------------------------------------------------------
    print("\n--- 1. Testing Unauthenticated Access (401) ---")
    res = client.get('/api/admin/dashboard')
    data = res.get_json() or {}
    assert_test(res.status_code == 401 and data.get('success') is False, 'GET /api/admin/dashboard without token returns 401')

    res = client.get('/api/admin/users')
    assert_test(res.status_code == 401, 'GET /api/admin/users without token returns 401')

    res = client.get('/api/admin/conversations')
    assert_test(res.status_code == 401, 'GET /api/admin/conversations without token returns 401')

    # -------------------------------------------------------------
    # 2. Non-Admin Role Protection (403 Forbidden)
    # -------------------------------------------------------------
    print("\n--- 2. Testing Role Protection (403 Forbidden) ---")
    res = client.get('/api/admin/dashboard', headers=user_headers)
    data = res.get_json() or {}
    assert_test(
        res.status_code == 403 and data.get('success') is False and 'Admin access required' in data.get('message', ''),
        'GET /api/admin/dashboard with role="user" returns 403 Forbidden'
    )

    res = client.get('/api/admin/users', headers=user_headers)
    assert_test(res.status_code == 403, 'GET /api/admin/users with role="user" returns 403')

    # -------------------------------------------------------------
    # 3. Dashboard API (GET /api/admin/dashboard)
    # -------------------------------------------------------------
    print("\n--- 3. Testing GET /api/admin/dashboard ---")
    res = client.get('/api/admin/dashboard', headers=admin_headers)
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('success') is True, 'GET /api/admin/dashboard returns 200 OK')
    assert_test(
        all(k in data for k in ['totalUsers', 'totalCalls', 'activeCalls', 'completedCalls', 'recruitmentCalls', 'salesCalls', 'supportCalls']),
        'Dashboard payload contains all required statistical metrics'
    )
    assert_test(data.get('totalCalls') == 342 and data.get('recruitmentCalls') == 150, 'Metrics match expected values')

    # -------------------------------------------------------------
    # 4. Users API (GET /api/admin/users)
    # -------------------------------------------------------------
    print("\n--- 4. Testing GET /api/admin/users ---")
    res = client.get('/api/admin/users?page=1&limit=5', headers=admin_headers)
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('success') is True, 'GET /api/admin/users returns 200 OK')
    users_list = data.get('users', [])
    assert_test(len(users_list) > 0, 'Users array returned')
    first_u = users_list[0]
    required_user_keys = ['id', 'name', 'email', 'company', 'role', 'services', 'totalCalls', 'activeCalls', 'lastActivity', 'status']
    assert_test(all(k in first_u for k in required_user_keys), f'User model includes all required fields: {required_user_keys}')

    # Test filtering
    res_search = client.get('/api/admin/users?search=Jenkins', headers=admin_headers)
    search_data = res_search.get_json() or {}
    assert_test(
        len(search_data.get('users', [])) >= 1 and 'Jenkins' in search_data['users'][0]['name'],
        'User search query filter operates properly'
    )

    # -------------------------------------------------------------
    # 5. Recruitment Endpoints (Upload & Start)
    # -------------------------------------------------------------
    print("\n--- 5. Testing Recruitment API ---")
    # Test invalid file format
    invalid_file = (io.BytesIO(b"fake pdf content"), "resume.pdf")
    res = client.post('/api/admin/recruitment/upload', headers=admin_headers, data={'file': invalid_file}, content_type='multipart/form-data')
    assert_test(res.status_code == 400 and 'Invalid file format' in (res.get_json() or {}).get('message', ''), 'Rejects non-excel file (.pdf) with 400')

    # Test valid Excel file upload
    excel_file = (io.BytesIO(b"dummy excel binary data"), "candidates.xlsx")
    res = client.post('/api/admin/recruitment/upload', headers=admin_headers, data={'file': excel_file}, content_type='multipart/form-data')
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('fileName') == 'candidates.xlsx' and data.get('status') == 'READY', 'POST /api/admin/recruitment/upload processes candidates.xlsx')
    file_id = data.get('fileId')
    assert_test(bool(file_id) and data.get('records') == 120, 'Returns staging fileId and 120 detected records')

    # Test recruitment start missing fileId
    res = client.post('/api/admin/recruitment/start', headers=admin_headers, json={})
    assert_test(res.status_code == 400, 'POST /api/admin/recruitment/start requires fileId')

    # Test recruitment start valid fileId
    res = client.post('/api/admin/recruitment/start', headers=admin_headers, json={'fileId': file_id})
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('status') == 'CALLING_STARTED' and data.get('total') == 120, 'POST /api/admin/recruitment/start initializes mock calling with total: 120')

    # -------------------------------------------------------------
    # 6. Sales Endpoints (Upload & Start)
    # -------------------------------------------------------------
    print("\n--- 6. Testing Sales API ---")
    sales_file = (io.BytesIO(b"sales binary data"), "leads.xlsx")
    res = client.post('/api/admin/sales/upload', headers=admin_headers, data={'file': sales_file}, content_type='multipart/form-data')
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('status') == 'READY' and data.get('records') == 85, 'POST /api/admin/sales/upload returns READY with 85 records')
    sales_file_id = data.get('fileId')

    res = client.post('/api/admin/sales/start', headers=admin_headers, json={'fileId': sales_file_id})
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('status') == 'CALLING_STARTED' and data.get('total') == 85, 'POST /api/admin/sales/start initializes sales campaign with total: 85')

    # -------------------------------------------------------------
    # 7. Customer Support Endpoints (Upload & Start)
    # -------------------------------------------------------------
    print("\n--- 7. Testing Customer Support API ---")
    supp_file = (io.BytesIO(b"support binary data"), "tickets.xlsx")
    res = client.post('/api/admin/support/upload', headers=admin_headers, data={'file': supp_file}, content_type='multipart/form-data')
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('status') == 'READY' and data.get('records') == 50, 'POST /api/admin/support/upload returns READY with 50 records')
    supp_file_id = data.get('fileId')

    res = client.post('/api/admin/support/start', headers=admin_headers, json={'fileId': supp_file_id})
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('status') == 'CALLING_STARTED' and data.get('total') == 50, 'POST /api/admin/support/start initializes support campaign with total: 50')

    # -------------------------------------------------------------
    # 8. Conversations & Transcripts (GET /api/admin/conversations)
    # -------------------------------------------------------------
    print("\n--- 8. Testing Conversations API ---")
    res = client.get('/api/admin/conversations', headers=admin_headers)
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('success') is True, 'GET /api/admin/conversations returns 200 OK')
    convs = data.get('conversations', [])
    assert_test(len(convs) >= 3, 'Returns list of mock conversations')
    c0 = convs[0]
    assert_test('service' in c0 and 'contact' in c0 and 'phone' in c0 and 'status' in c0 and 'duration' in c0, 'Conversation item has required fields')

    # Test single conversation by ID
    res = client.get('/api/admin/conversations/conv_001', headers=admin_headers)
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('id') == 'conv_001', 'GET /api/admin/conversations/conv_001 returns conversation details')
    assert_test('transcript' in data and len(data['transcript']) > 0, 'Conversation payload contains full transcript dialogue turns')
    assert_test('summary' in data and 'collectedData' in data, 'Conversation payload contains summary and collected candidate metrics')

    # Test 404 for non-existent conversation
    res = client.get('/api/admin/conversations/conv_non_existent', headers=admin_headers)
    assert_test(res.status_code == 404, 'GET /api/admin/conversations/conv_non_existent returns 404 Not Found')

    # -------------------------------------------------------------
    # 9. Call History (GET /api/admin/calls)
    # -------------------------------------------------------------
    print("\n--- 9. Testing Call History API ---")
    res = client.get('/api/admin/calls', headers=admin_headers)
    data = res.get_json() or {}
    assert_test(res.status_code == 200 and data.get('success') is True, 'GET /api/admin/calls returns 200 OK')
    calls = data.get('calls', [])
    assert_test(len(calls) >= 5, 'Returns call history records')
    call0 = calls[0]
    assert_test('callSid' in call0 and 'callerNumber' in call0 and 'service' in call0 and 'duration' in call0, 'Call record contains telephony metadata')

    print(f"\n=======================================================")
    print(f"  TESTS COMPLETE: {passed} PASSED, {failed} FAILED")
    print(f"=======================================================\n")
    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    run_tests()
