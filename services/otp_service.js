import crypto from 'crypto';

// In-memory one-time-code store. Single server process, so a Map is enough;
// pending codes are simply lost on restart and the user requests a new one.
const OTP_TTL_MS = 10 * 60 * 1000;      // code valid for 10 minutes
const RESEND_COOLDOWN_MS = 45 * 1000;   // wait between sends
const MAX_ATTEMPTS = 5;                 // wrong guesses before the code is burned
const MAX_SENDS_PER_HOUR = 5;

const store = new Map();

function keyOf(purpose, email) {
    return `${purpose}:${String(email).trim().toLowerCase()}`;
}

function hashOtp(otp, salt) {
    return crypto.createHash('sha256').update(`${salt}:${otp}`).digest('hex');
}

// Remove expired entries now and then so the Map can't grow forever.
setInterval(() => {
    const now = Date.now();
    for (const [k, v] of store) {
        if (v.expiresAt < now && now - v.windowStart > 3600 * 1000) store.delete(k);
    }
}, 10 * 60 * 1000).unref();

export const OtpService = {
    /**
     * Create (or replace) a code. Returns { ok, otp } or { ok:false, message, retryAfterSec }.
     * `payload` is kept server-side with the code (e.g. the pending signup details).
     */
    issue(purpose, email, payload = null) {
        const key = keyOf(purpose, email);
        const now = Date.now();
        const prev = store.get(key);

        let sends = 1;
        let windowStart = now;
        if (prev) {
            const wait = prev.lastSentAt + RESEND_COOLDOWN_MS - now;
            if (wait > 0) {
                return { ok: false, message: `Please wait ${Math.ceil(wait / 1000)}s before requesting another code.`, retryAfterSec: Math.ceil(wait / 1000) };
            }
            if (now - prev.windowStart < 3600 * 1000) {
                if (prev.sends >= MAX_SENDS_PER_HOUR) {
                    return { ok: false, message: 'Too many codes requested. Please try again in an hour.', retryAfterSec: 3600 };
                }
                sends = prev.sends + 1;
                windowStart = prev.windowStart;
            }
        }

        const otp = String(crypto.randomInt(0, 1000000)).padStart(6, '0');
        const salt = crypto.randomBytes(8).toString('hex');
        store.set(key, {
            salt,
            hash: hashOtp(otp, salt),
            expiresAt: now + OTP_TTL_MS,
            attempts: 0,
            lastSentAt: now,
            sends,
            windowStart,
            payload: payload ?? (prev ? prev.payload : null)
        });
        return { ok: true, otp, expiresInMin: OTP_TTL_MS / 60000 };
    },

    /** Keep the pending payload but issue a fresh code (used by "Resend code"). */
    reissue(purpose, email) {
        const prev = store.get(keyOf(purpose, email));
        if (!prev) return { ok: false, message: 'Your session expired. Please start again.', expired: true };
        return OtpService.issue(purpose, email, prev.payload);
    },

    /** Check a submitted code. Returns { ok, payload } or { ok:false, message }. */
    verify(purpose, email, otp) {
        const key = keyOf(purpose, email);
        const entry = store.get(key);
        const submitted = String(otp || '').trim();

        if (!entry || entry.expiresAt < Date.now()) {
            store.delete(key);
            return { ok: false, message: 'This code has expired. Please request a new one.', expired: true };
        }
        if (!/^\d{6}$/.test(submitted)) {
            return { ok: false, message: 'Please enter the 6-digit code.' };
        }
        if (entry.attempts >= MAX_ATTEMPTS) {
            store.delete(key);
            return { ok: false, message: 'Too many incorrect attempts. Please request a new code.', expired: true };
        }

        const a = Buffer.from(hashOtp(submitted, entry.salt), 'hex');
        const b = Buffer.from(entry.hash, 'hex');
        if (!crypto.timingSafeEqual(a, b)) {
            entry.attempts += 1;
            const left = MAX_ATTEMPTS - entry.attempts;
            return { ok: false, message: left > 0 ? `Incorrect code. ${left} attempt${left === 1 ? '' : 's'} left.` : 'Too many incorrect attempts. Please request a new code.', expired: left <= 0 };
        }

        store.delete(key); // single use
        return { ok: true, payload: entry.payload };
    },

    discard(purpose, email) {
        store.delete(keyOf(purpose, email));
    }
};

export default OtpService;
