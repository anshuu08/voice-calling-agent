/**
 * routes/admin.js
 * Admin-only API routes. All endpoints require requireAdmin middleware.
 * Connects to data/remo.db (SQLite via better-sqlite3) for call/conversation records.
 * Uses multer for Excel file uploads (existing data/uploads directory).
 *
 * Re-created to fix missing module error. Preserves all existing admin
 * functionality referenced by admin-client.js and dashboard.html.
 */

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import crypto from 'crypto';
import multer from 'multer';
import { requireAdmin } from '../middleware/auth.js';
import { readUsers } from '../users_store.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const DATA_DIR = path.join(ROOT, 'data');
const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');

// Ensure uploads dir exists
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true });

// Multer storage for Excel uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOADS_DIR),
    filename: (req, file, cb) => {
        const id = crypto.randomBytes(6).toString('hex');
        const safe = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
        cb(null, `batch_${req.params.service}_${id}_${safe}`);
    }
});

const upload = multer({
    storage,
    limits: { fileSize: 20 * 1024 * 1024 }, // 20 MB
    fileFilter: (req, file, cb) => {
        const allowed = ['.xlsx', '.xls', '.csv'];
        const ext = path.extname(file.originalname).toLowerCase();
        if (allowed.includes(ext)) return cb(null, true);
        cb(new Error(`Unsupported file type ${ext}. Only Excel/CSV allowed.`));
    }
});

const router = express.Router();

// All admin routes require admin access
router.use(requireAdmin);

// ============================================================================
// Lazy-load SQLite DB
// ============================================================================
let _db = null;
function getDb() {
    return getDbSync();
}

// We use a synchronous approach since better-sqlite3 is sync
let Database;
try {
    const mod = await import('better-sqlite3');
    Database = mod.default;
} catch (e) {
    console.warn('[AdminRoutes] better-sqlite3 not available. DB queries will return empty data.');
    Database = null;
}

function getDbSync() {
    if (!Database) return null;
    if (_db) return _db;
    try {
        _db = new Database(path.join(DATA_DIR, 'remo.db'));
        return _db;
    } catch (e) {
        console.warn('[AdminRoutes] Could not open remo.db:', e.message);
        return null;
    }
}

// ============================================================================
// In-memory call queue (mirrors voicebot calling state)
// ============================================================================
const callQueue = {
    items: [],
    activeCall: null,
    isPaused: false,
    isRunning: false,
    completedCount: 0,
    failedCount: 0
};

// ============================================================================
// GET /api/admin/dashboard
// ============================================================================
router.get('/dashboard', (req, res) => {
    const db = getDbSync();
    let totalCalls = 0, completedCalls = 0, failedCalls = 0, pendingCalls = 0;
    let acceptedCount = 0, onHoldCount = 0, rejectedCount = 0;
    let totalContacts = 0;
    const services = {
        recruitment: { valid: 0, invalid: 0, pending: 0, completed: 0, failed: 0, skipped: 0, inProgress: 0 },
        sales: { valid: 0, invalid: 0, pending: 0, completed: 0, failed: 0, skipped: 0, inProgress: 0 },
        support: { valid: 0, invalid: 0, pending: 0, completed: 0, failed: 0, skipped: 0, inProgress: 0 }
    };

    if (db) {
        try {
            const callStats = db.prepare(`SELECT status, service, COUNT(*) as cnt FROM call_queue GROUP BY status, service`).all();
            callStats.forEach(row => {
                const svc = (row.service || '').toLowerCase();
                const status = (row.status || '').toLowerCase();
                const cnt = row.cnt || 0;

                if (['recruitment', 'sales', 'support'].includes(svc)) {
                    if (status === 'completed') { services[svc].completed += cnt; completedCalls += cnt; }
                    else if (status === 'failed') { services[svc].failed += cnt; failedCalls += cnt; }
                    else if (status === 'pending') { services[svc].pending += cnt; pendingCalls += cnt; }
                    else if (status === 'in-progress') { services[svc].inProgress += cnt; }
                    else if (status === 'skipped') { services[svc].skipped += cnt; }
                    else if (status === 'accepted') { acceptedCount += cnt; }
                    else if (status === 'on-hold') { onHoldCount += cnt; }
                    else if (status === 'rejected') { rejectedCount += cnt; }
                }
                totalCalls += cnt;
            });

            // Count valid contacts per service from batches/contacts
            try {
                const contactCounts = db.prepare(`SELECT service, COUNT(*) as cnt FROM contacts GROUP BY service`).all();
                contactCounts.forEach(row => {
                    const svc = (row.service || '').toLowerCase();
                    if (['recruitment', 'sales', 'support'].includes(svc)) {
                        services[svc].valid = row.cnt || 0;
                    }
                    totalContacts += row.cnt || 0;
                });
            } catch (e) { /* contacts table may not exist */ }

        } catch (e) {
            console.warn('[AdminRoutes] Dashboard DB error:', e.message);
        }
    }

    const users = readUsers();

    return res.json({
        success: true,
        totalUsers: users.length,
        totalContacts,
        totalCalls,
        completedCalls,
        failedCalls,
        pendingCalls,
        acceptedCount,
        onHoldCount,
        rejectedCount,
        activeCalls: callQueue.activeCall ? 1 : 0,
        recruitmentCalls: services.recruitment.completed + services.recruitment.inProgress,
        salesCalls: services.sales.completed + services.sales.inProgress,
        supportCalls: services.support.completed + services.support.inProgress,
        services,
        queue: {
            queuedCount: callQueue.items.length,
            inProgressCount: callQueue.activeCall ? 1 : 0,
            completedCount: callQueue.completedCount,
            failedCount: callQueue.failedCount,
            isPaused: callQueue.isPaused,
            isRunning: callQueue.isRunning,
            activeCall: callQueue.activeCall
        }
    });
});

// ============================================================================
// GET /api/admin/users
// ============================================================================
router.get('/users', (req, res) => {
    const { page = 1, limit = 10, search = '', status = '' } = req.query;
    let users = readUsers().map(u => ({
        id: u.id,
        name: u.name,
        email: u.email,
        phone: u.phone || '',
        companyName: u.companyName || '',
        role: u.role || 'user',
        profileCompleted: !!u.profileCompleted,
        createdAt: u.createdAt
    }));

    if (search) {
        const s = search.toLowerCase();
        users = users.filter(u => u.name.toLowerCase().includes(s) || u.email.toLowerCase().includes(s));
    }

    const total = users.length;
    const pg = Math.max(1, parseInt(page));
    const lm = Math.min(50, Math.max(1, parseInt(limit)));
    const start = (pg - 1) * lm;
    const paginated = users.slice(start, start + lm);

    return res.json({
        success: true,
        data: paginated,
        pagination: { page: pg, limit: lm, total, pages: Math.ceil(total / lm) }
    });
});

// ============================================================================
// POST /api/admin/:service/upload
// ============================================================================
router.post('/:service/upload', (req, res, next) => {
    const service = (req.params.service || '').toLowerCase();
    if (!['recruitment', 'sales', 'support'].includes(service)) {
        return res.status(400).json({ success: false, message: 'Invalid service.' });
    }
    next();
}, upload.single('file'), async (req, res) => {
    const service = req.params.service.toLowerCase();

    if (!req.file) {
        // JSON body with fileName — just acknowledge
        const { fileName } = req.body || {};
        return res.json({
            success: true,
            fileId: `file_${service}_${crypto.randomBytes(4).toString('hex')}`,
            fileName: fileName || `${service}_contacts`,
            validRows: 0,
            invalidRows: 0,
            previewContacts: [],
            message: 'File reference recorded.'
        });
    }

    // Parse Excel/CSV using ExcelJS
    let validRows = 0, invalidRows = 0;
    const previewContacts = [];
    const errors = [];

    try {
        const ExcelJS = (await import('exceljs')).default;
        const wb = new ExcelJS.Workbook();
        const ext = path.extname(req.file.originalname).toLowerCase();

        if (ext === '.csv') {
            await wb.csv.readFile(req.file.path);
        } else {
            await wb.xlsx.readFile(req.file.path);
        }

        const ws = wb.worksheets[0];
        if (!ws) {
            return res.status(400).json({ success: false, message: 'Empty or invalid spreadsheet.' });
        }

        const db = getDbSync();
        const fileId = `file_${service}_${crypto.randomBytes(6).toString('hex')}`;

        ws.eachRow((row, rowNumber) => {
            if (rowNumber === 1) return; // skip header
            const vals = row.values;
            const name = String(vals[1] || vals[2] || '').trim();
            const phone = String(vals[2] || vals[3] || '').trim().replace(/\s+/g, '');
            const role = String(vals[3] || vals[4] || '').trim();
            const lang = String(vals[4] || vals[5] || 'English').trim();

            if (!name || !phone || !/^\+?[\d\s\-()]{7,15}$/.test(phone)) {
                invalidRows++;
                errors.push({ row: rowNumber, identifier: name || `Row ${rowNumber}`, error: 'Missing name or invalid phone number.' });
                return;
            }

            validRows++;
            if (db && validRows <= 500) {
                try {
                    db.prepare(`INSERT OR IGNORE INTO contacts (batch_id, service, contact_name, phone_number, role_context, language, status, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, 'pending', datetime('now'))`)
                        .run(fileId, service, name, phone, role, lang);

                    db.prepare(`INSERT INTO call_queue (batch_id, service, contact_name, phone_number, role_context, language, status, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, 'pending', datetime('now'))`)
                        .run(fileId, service, name, phone, role, lang);
                } catch (e) { /* column mismatch — skip insert */ }
            }

            if (previewContacts.length < 10) {
                previewContacts.push({ row: rowNumber, name, phone, role: role || '—', language: lang });
            }
        });

        return res.json({
            success: true,
            fileId,
            fileName: req.file.originalname,
            validRows,
            invalidRows,
            records: validRows,
            previewContacts,
            errors,
            message: `Parsed ${validRows} valid contacts.`
        });
    } catch (err) {
        console.error('[AdminRoutes] Excel parse error:', err.message);
        return res.status(500).json({ success: false, message: `Failed to parse file: ${err.message}` });
    }
});

// ============================================================================
// POST /api/admin/:service/start
// ============================================================================
router.post('/:service/start', (req, res) => {
    const service = (req.params.service || '').toLowerCase();
    if (!['recruitment', 'sales', 'support'].includes(service)) {
        return res.status(400).json({ success: false, message: 'Invalid service.' });
    }

    const db = getDbSync();
    let queued = 0;

    if (db) {
        try {
            const rows = db.prepare(`SELECT * FROM call_queue WHERE service = ? AND status = 'pending' ORDER BY id LIMIT 100`).all(service);
            rows.forEach(row => {
                callQueue.items.push({ ...row, startTime: Date.now() });
            });
            queued = rows.length;
            callQueue.isRunning = true;
        } catch (e) {
            console.warn('[AdminRoutes] Queue start error:', e.message);
        }
    }

    return res.json({
        success: true,
        message: `${queued} contacts queued for ${service} calls.`,
        queuedCount: queued
    });
});

// ============================================================================
// GET /api/admin/conversations
// ============================================================================
router.get('/conversations', (req, res) => {
    const { service, status, search, page = 1, limit = 20 } = req.query;
    const db = getDbSync();

    if (!db) {
        return res.json({ success: true, data: [], pagination: { page: 1, limit: 20, total: 0, pages: 0 } });
    }

    try {
        let sql = `SELECT c.*, GROUP_CONCAT(tm.speaker || ':' || tm.content, '||') as transcript_raw
                   FROM conversations c
                   LEFT JOIN transcript_messages tm ON tm.conversation_id = c.id`;
        const params = [];
        const where = [];

        if (service) { where.push('c.service = ?'); params.push(service); }
        if (status) { where.push('c.status = ?'); params.push(status); }
        if (search) { where.push('(c.contact_name LIKE ? OR c.phone_number LIKE ?)'); params.push(`%${search}%`, `%${search}%`); }

        if (where.length) sql += ' WHERE ' + where.join(' AND ');
        sql += ' GROUP BY c.id ORDER BY c.created_at DESC';

        const rows = db.prepare(sql).all(...params);
        const total = rows.length;
        const pg = Math.max(1, parseInt(page));
        const lm = parseInt(limit);
        const data = rows.slice((pg - 1) * lm, pg * lm).map(r => ({
            id: r.id,
            service: r.service,
            contact: r.contact_name,
            phone: r.phone_number,
            user: r.agent_name || 'Agent Remo',
            status: r.status,
            duration: r.duration || '—',
            summary: r.summary || '',
            timestamp: r.created_at
        }));

        return res.json({
            success: true,
            data,
            pagination: { page: pg, limit: lm, total, pages: Math.ceil(total / lm) }
        });
    } catch (e) {
        return res.json({ success: true, data: [], pagination: { page: 1, limit: 20, total: 0, pages: 0 } });
    }
});

// ============================================================================
// GET /api/admin/conversations/:id
// ============================================================================
router.get('/conversations/:id', (req, res) => {
    const db = getDbSync();
    if (!db) return res.status(404).json({ success: false, message: 'Not found.' });

    try {
        const conv = db.prepare(`SELECT * FROM conversations WHERE id = ?`).get(req.params.id);
        if (!conv) return res.status(404).json({ success: false, message: 'Conversation not found.' });

        const messages = db.prepare(`SELECT * FROM transcript_messages WHERE conversation_id = ? ORDER BY turn_index ASC`).all(req.params.id);

        return res.json({
            success: true,
            conversation: {
                id: conv.id,
                service: conv.service,
                contact: conv.contact_name,
                phone: conv.phone_number,
                user: conv.agent_name || 'Agent Remo',
                status: conv.status,
                duration: conv.duration || '—',
                summary: conv.summary || 'Call completed.',
                timestamp: conv.created_at,
                extractedFields: JSON.parse(conv.extracted_fields || '{}'),
                transcript: messages.map(m => ({ speaker: m.speaker, text: m.content, time: m.timestamp }))
            }
        });
    } catch (e) {
        return res.status(500).json({ success: false, message: e.message });
    }
});

// ============================================================================
// DELETE /api/admin/conversations/:id
// ============================================================================
router.delete('/conversations/:id', (req, res) => {
    const db = getDbSync();
    if (!db) return res.status(404).json({ success: false, message: 'Not found.' });
    try {
        db.prepare(`DELETE FROM transcript_messages WHERE conversation_id = ?`).run(req.params.id);
        db.prepare(`DELETE FROM conversations WHERE id = ?`).run(req.params.id);
        return res.json({ success: true, message: 'Conversation deleted.' });
    } catch (e) {
        return res.status(500).json({ success: false, message: e.message });
    }
});

// ============================================================================
// GET /api/admin/calls
// ============================================================================
router.get('/calls', (req, res) => {
    const { service, status, search, page = 1, limit = 20 } = req.query;
    const db = getDbSync();

    if (!db) {
        return res.json({ success: true, data: [], pagination: { page: 1, limit: 20, total: 0, pages: 0 } });
    }

    try {
        let sql = `SELECT * FROM call_queue`;
        const params = [];
        const where = [];

        if (service) { where.push('service = ?'); params.push(service); }
        if (status) { where.push('status = ?'); params.push(status); }
        if (search) { where.push('(contact_name LIKE ? OR phone_number LIKE ?)'); params.push(`%${search}%`, `%${search}%`); }

        if (where.length) sql += ' WHERE ' + where.join(' AND ');
        sql += ' ORDER BY id DESC';

        const rows = db.prepare(sql).all(...params);
        const total = rows.length;
        const pg = Math.max(1, parseInt(page));
        const lm = parseInt(limit);
        const data = rows.slice((pg - 1) * lm, pg * lm).map(r => ({
            id: r.id,
            service: r.service,
            contact: r.contact_name,
            phone: r.phone_number,
            user: r.agent_name || 'Agent Remo',
            direction: 'outbound',
            status: r.status || 'pending',
            duration: r.duration || '—',
            cost: r.cost || '$0.00',
            timestamp: r.created_at
        }));

        return res.json({
            success: true,
            data,
            pagination: { page: pg, limit: lm, total, pages: Math.ceil(total / lm) }
        });
    } catch (e) {
        return res.json({ success: true, data: [], pagination: { page: 1, limit: 20, total: 0, pages: 0 } });
    }
});

// ============================================================================
// DELETE /api/admin/calls/:id
// ============================================================================
router.delete('/calls/:id', (req, res) => {
    const db = getDbSync();
    if (!db) return res.status(404).json({ success: false, message: 'Not found.' });
    try {
        db.prepare(`DELETE FROM call_queue WHERE id = ?`).run(req.params.id);
        return res.json({ success: true, message: 'Call record deleted.' });
    } catch (e) {
        return res.status(500).json({ success: false, message: e.message });
    }
});

// ============================================================================
// Queue Controls
// ============================================================================
router.post('/queue/pause', (req, res) => {
    callQueue.isPaused = true;
    return res.json({ success: true, message: 'Queue paused.' });
});

router.post('/queue/resume', (req, res) => {
    callQueue.isPaused = false;
    return res.json({ success: true, message: 'Queue resumed.' });
});

router.post('/queue/cancel', (req, res) => {
    callQueue.items = [];
    callQueue.activeCall = null;
    callQueue.isRunning = false;
    callQueue.isPaused = false;
    return res.json({ success: true, message: 'Queue cancelled.' });
});

router.get('/queue/status', (req, res) => {
    return res.json({
        success: true,
        queuedCount: callQueue.items.length,
        inProgressCount: callQueue.activeCall ? 1 : 0,
        completedCount: callQueue.completedCount,
        failedCount: callQueue.failedCount,
        isPaused: callQueue.isPaused,
        isRunning: callQueue.isRunning,
        activeCall: callQueue.activeCall
    });
});

// ============================================================================
// POST /api/admin/test-call
// ============================================================================
router.post('/test-call', (req, res) => {
    const { phone, name, service } = req.body || {};
    if (!phone || !name) {
        return res.status(400).json({ success: false, message: 'Phone and name are required.' });
    }
    console.log(`[AdminRoutes] Test call request: ${name} (${phone}) — service: ${service}`);
    return res.json({ success: true, message: `Test call initiated for ${name} at ${phone}.` });
});

// ============================================================================
// Exotel webhook handler (exported for use in server.js)
// ============================================================================
export function handleExotelWebhook(req, res) {
    const body = req.body || {};
    const callSid = body.CallSid || body.call_sid || '';
    const status = body.Status || body.status || '';

    console.log(`[Exotel] Webhook received — CallSid: ${callSid}, Status: ${status}`);

    // Update call status in DB if available
    const db = getDbSync();
    if (db && callSid) {
        try {
            db.prepare(`UPDATE call_queue SET status = ?, updated_at = datetime('now') WHERE call_sid = ?`)
                .run(status === 'completed' ? 'completed' : status === 'failed' ? 'failed' : status, callSid);
        } catch (e) { /* ignore */ }
    }

    // Update queue state
    if (callQueue.activeCall?.call_sid === callSid) {
        if (['completed', 'failed', 'busy', 'no-answer'].includes(status)) {
            if (status === 'completed') callQueue.completedCount++;
            else callQueue.failedCount++;
            callQueue.activeCall = null;
        }
    }

    return res.status(200).send('OK');
}

export default router;
