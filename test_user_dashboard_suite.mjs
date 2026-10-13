import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import jwt from 'jsonwebtoken';

const BASE_URL = 'http://localhost:8080';
const JWT_SECRET = 'agent_hari_secure_jwt_production_secret_key_2026_x89a3f';

async function runTests() {
    console.log('--- Starting User Dashboard Verification Test Suite ---');
    let passed = 0;
    let failed = 0;

    function assert(condition, message) {
        if (condition) {
            console.log(`[PASS] ${message}`);
            passed++;
        } else {
            console.error(`[FAIL] ${message}`);
            failed++;
        }
    }

    try {
        // 1. Health check
        const healthRes = await fetch(`${BASE_URL}/api/health`);
        const healthData = await healthRes.json();
        assert(healthRes.status === 200 && healthData.status === 'ok', 'Server health check returns 200 OK');

        // 2. Unauthenticated redirects
        const unauthAdmin = await fetch(`${BASE_URL}/dashboard`, { redirect: 'manual' });
        assert(unauthAdmin.status === 302 && unauthAdmin.headers.get('location') === '/signin', 'Unauthenticated /dashboard redirects to /signin');

        const unauthUser = await fetch(`${BASE_URL}/user-dashboard`, { redirect: 'manual' });
        assert(unauthUser.status === 302 && unauthUser.headers.get('location') === '/signin', 'Unauthenticated /user-dashboard redirects to /signin');

        // Clean up any test proposals from prior runs
        const proposalsFile = path.resolve('data/proposals.json');
        if (fs.existsSync(proposalsFile)) {
            try {
                let existingProps = JSON.parse(fs.readFileSync(proposalsFile, 'utf8'));
                existingProps = existingProps.filter(p => p.userId !== 'test_user_uuid_101' && p.userId !== 'test_other_user_202');
                fs.writeFileSync(proposalsFile, JSON.stringify(existingProps, null, 2), 'utf8');
            } catch(e) {}
        }

        // 3. Create test users (1 normal user, 1 admin user) in users.json
        const usersFile = path.resolve('data/users.json');
        let users = [];
        try { users = JSON.parse(fs.readFileSync(usersFile, 'utf8')); } catch(e) {}

        const testUserId = 'test_user_uuid_101';
        const testUserEmail = 'test.user@takeremo-example.com';
        const existingIdx = users.findIndex(u => u.id === testUserId);
        const testUserObj = {
            id: testUserId,
            name: 'Priya Sharma',
            email: testUserEmail,
            phone: '+91 9876543210',
            companyName: 'Sharma Logistics Ltd',
            profileCompleted: true,
            role: 'user'
        };
        if (existingIdx >= 0) users[existingIdx] = testUserObj;
        else users.push(testUserObj);

        // Also ensure admin user exists
        const adminUserId = 'test_admin_uuid_999';
        const adminEmail = 'Reach@takeremo.com';
        const adminIdx = users.findIndex(u => u.id === adminUserId);
        const adminUserObj = {
            id: adminUserId,
            name: 'Remo Admin',
            email: adminEmail,
            role: 'admin',
            profileCompleted: true
        };
        if (adminIdx >= 0) users[adminIdx] = adminUserObj;
        else users.push(adminUserObj);

        fs.writeFileSync(usersFile, JSON.stringify(users, null, 2), 'utf8');

        // 4. Create JWT tokens
        const userToken = jwt.sign({ id: testUserId, email: testUserEmail, role: 'user' }, JWT_SECRET, { expiresIn: '1h' });
        const adminToken = jwt.sign({ id: adminUserId, email: adminEmail, role: 'admin' }, JWT_SECRET, { expiresIn: '1h' });

        // 5. Normal user attempts to access Admin Dashboard -> Must be redirected to /user-dashboard
        const userAccessAdmin = await fetch(`${BASE_URL}/dashboard`, {
            headers: { 'Cookie': `agent_hari_token=${userToken}` },
            redirect: 'manual'
        });
        assert(userAccessAdmin.status === 302 && userAccessAdmin.headers.get('location') === '/user-dashboard',
            'Non-admin user accessing /dashboard is redirected to /user-dashboard');

        // 6. Normal user accesses User Dashboard -> 200 OK
        const userAccessUserDash = await fetch(`${BASE_URL}/user-dashboard`, {
            headers: { 'Cookie': `agent_hari_token=${userToken}` }
        });
        assert(userAccessUserDash.status === 200, 'Normal user can access /user-dashboard successfully');
        const userDashHtml = await userAccessUserDash.text();
        assert(userDashHtml.includes('Build Your Agent') && userDashHtml.includes('Agent Remo'),
            '/user-dashboard contains Build Your Agent section and Agent Remo branding');
        assert(userDashHtml.includes('GST Number'), '/user-dashboard contains GST Number field');

        // 7. Normal user attempts to call Admin API -> 403 Forbidden
        const userAdminApi = await fetch(`${BASE_URL}/api/admin/dashboard`, {
            headers: { 'Cookie': `agent_hari_token=${userToken}` }
        });
        assert(userAdminApi.status === 403, 'Normal user calling /api/admin/dashboard is blocked with 403 Forbidden');

        // 8. Admin user accesses Admin Dashboard -> 200 OK
        const adminAccessAdminDash = await fetch(`${BASE_URL}/dashboard`, {
            headers: { 'Cookie': `agent_hari_token=${adminToken}` },
            redirect: 'manual'
        });
        assert(adminAccessAdminDash.status === 200, 'Admin user can access /dashboard with 200 OK');

        // 9. Proposal validation test (missing required fields)
        const emptyProposalRes = await fetch(`${BASE_URL}/api/user/proposals`, {
            method: 'POST',
            headers: {
                'Cookie': `agent_hari_token=${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        assert(emptyProposalRes.status === 400, 'Proposal submission with missing fields returns 400 Bad Request');

        // 10. Valid proposal submission with all fields including GST number and Govt ID
        const validProposal = {
            fullName: 'Priya Sharma',
            phone: '+91 9876543210',
            email: testUserEmail,
            companyName: 'Sharma Logistics Ltd',
            companyWebsite: 'https://sharmalogistics.com',
            gstNumber: '29ABCDE1234F1Z5',
            govtId: 'AAAPL1234C',
            industry: 'Sales & Lead Gen',
            agentType: 'Sales Agent',
            agentDescription: 'We want an AI caller to follow up with shipment enquiries and quote pricing directly to incoming queries.',
            businessBenefit: 'Automates our 200 daily status check calls and frees up 3 support executives to handle premium clients.',
            callVolume: '1,000–5,000 calls per month',
            languages: JSON.stringify(['English', 'Hindi', 'Telugu']),
            documentsText: 'Need product rate sheets, FAQ sheet, and freight pricing matrix.'
        };

        const submitRes = await fetch(`${BASE_URL}/api/user/proposals`, {
            method: 'POST',
            headers: {
                'Cookie': `agent_hari_token=${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(validProposal)
        });
        const submitData = await submitRes.json();
        assert(submitRes.status === 201 && submitData.success === true,
            'Valid proposal submitted successfully with 201 Created');
        assert(submitData.proposalId && submitData.proposalId.startsWith('prop_'),
            'Proposal received unique proposalId');

        // 11. Verify stored proposal in data/proposals.json
        const proposals = JSON.parse(fs.readFileSync(proposalsFile, 'utf8'));
        const savedProp = proposals.find(p => p.id === submitData.proposalId);
        assert(savedProp !== undefined, 'Proposal successfully saved to data/proposals.json');
        assert(savedProp.gstNumber === '29ABCDE1234F1Z5', 'GST number stored correctly in proposal record');
        assert(savedProp.govtId === 'AAAPL1234C', 'Govt ID stored correctly in proposal record');
        assert(savedProp.userId === testUserId, 'Proposal is securely associated with authenticated user ID from JWT');

        // 12. GET /api/user/proposals -> returns user proposals
        const getPropsRes = await fetch(`${BASE_URL}/api/user/proposals`, {
            headers: { 'Cookie': `agent_hari_token=${userToken}` }
        });
        const getPropsData = await getPropsRes.json();
        assert(getPropsRes.status === 200 && Array.isArray(getPropsData.data) && getPropsData.data.length >= 1,
            'GET /api/user/proposals returns current user submissions');

        // 13. Data isolation check: another user should not see this proposal
        const otherUserId = 'test_other_user_202';
        users.push({
            id: otherUserId,
            name: 'Vikram Mehta',
            email: 'other@example.com',
            role: 'user',
            profileCompleted: true
        });
        fs.writeFileSync(usersFile, JSON.stringify(users, null, 2), 'utf8');

        const otherToken = jwt.sign({ id: otherUserId, email: 'other@example.com', role: 'user' }, JWT_SECRET, { expiresIn: '1h' });
        const otherPropsRes = await fetch(`${BASE_URL}/api/user/proposals`, {
            headers: { 'Cookie': `agent_hari_token=${otherToken}` }
        });
        const otherPropsData = await otherPropsRes.json();
        assert(otherPropsRes.status === 200 && Array.isArray(otherPropsData.data) && otherPropsData.data.length === 0, 'Data privacy: Other users cannot view proposals belonging to another user');

        // 14. Deduplication: user trying to submit another pending proposal within 24 hours gets 409 Conflict
        const dupRes = await fetch(`${BASE_URL}/api/user/proposals`, {
            method: 'POST',
            headers: {
                'Cookie': `agent_hari_token=${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(validProposal)
        });
        assert(dupRes.status === 409, 'Duplicate proposal submission within 24h is safely handled with 409 Conflict');

    } catch (err) {
        console.error('Test Suite encountered an error:', err);
        failed++;
    }

    console.log(`\n========================================`);
    console.log(`Tests finished: ${passed} PASSED, ${failed} FAILED`);
    console.log(`========================================\n`);

    if (failed > 0) process.exit(1);
    else process.exit(0);
}

runTests();
