/**
 * services/email_service.js
 * Reusable email utility — reads existing SMTP env vars.
 * Does NOT hardcode credentials. Does NOT replace any existing config.
 */

import nodemailer from 'nodemailer';

/**
 * Build a transporter from existing SMTP env vars.
 * Variables: EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD
 */
function createTransporter() {
    const host = process.env.EMAIL_HOST;
    const port = parseInt(process.env.EMAIL_PORT || '465', 10);
    const user = process.env.EMAIL_USER;
    const pass = process.env.EMAIL_PASSWORD;

    if (!host || !user || !pass) {
        throw new Error('SMTP not configured: EMAIL_HOST, EMAIL_USER, and EMAIL_PASSWORD are required.');
    }

    return nodemailer.createTransport({
        host,
        port,
        secure: port === 465, // true for 465, false for other ports
        auth: { user, pass },
        tls: { rejectUnauthorized: false }
    });
}

/**
 * Send an email.
 * @param {object} options
 * @param {string|string[]} options.to   - Recipient(s)
 * @param {string}          options.subject
 * @param {string}          options.html  - HTML body
 * @param {string}          [options.text] - Plain text fallback
 * @param {string}          [options.replyTo] - Reply-To header
 * @returns {Promise<{success: boolean, messageId?: string, error?: string}>}
 */
export async function sendEmail({ to, subject, html, text, replyTo }) {
    try {
        const transporter = createTransporter();
        const from = process.env.EMAIL_USER;

        const info = await transporter.sendMail({
            from: `TakeRemo <${from}>`,
            to,
            subject,
            html,
            text: text || stripHtmlTags(html),
            ...(replyTo ? { replyTo } : {})
        });

        return { success: true, messageId: info.messageId };
    } catch (err) {
        // Log error without revealing credentials
        console.error('[EmailService] Send failed:', err.code || err.message);
        return { success: false, error: err.message };
    }
}

function stripHtmlTags(html) {
    return (html || '').replace(/<[^>]*>/g, '').replace(/\s{2,}/g, ' ').trim();
}

/**
 * Escape HTML special chars to prevent injection.
 */
export function escapeHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
}
