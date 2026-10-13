export default class ExotelService {
    static getConfig() {
        const sid = (process.env.EXOTEL_ACCOUNT_SID || '').trim();
        const key = (process.env.EXOTEL_API_KEY || '').trim();
        const token = (process.env.EXOTEL_API_TOKEN_PASSWORD || process.env.EXOTEL_API_TOKEN || '').trim();
        const sub = (process.env.EXOTEL_SUBDOMAIN || 'api.exotel.com').trim();
        const vn = (process.env.EXOTEL_VIRTUAL_NUMBER || '').trim();

        if (!sid || !key || !token) {
            throw new Error('Exotel credentials (EXOTEL_ACCOUNT_SID, EXOTEL_API_KEY, EXOTEL_API_TOKEN) are missing in environment.');
        }

        return {
            accountSid: sid,
            apiKey: key,
            apiToken: token,
            subdomain: sub,
            virtualNumber: vn
        };
    }

    static async initiateOutboundCall(toPhone, customField, callbackUrl = null) {
        const cfg = this.getConfig();
        const url = `https://${cfg.subdomain}/v1/Accounts/${cfg.accountSid}/Calls/connect.json`;

        // Normalize phone number for Exotel (Indian numbers formatted as 0XXXXXXXXXX)
        let formattedPhone = String(toPhone || '').trim().replace(/[\s-]/g, '');
        if (formattedPhone.startsWith('+91')) {
            formattedPhone = '0' + formattedPhone.slice(3);
        } else if (formattedPhone.startsWith('91') && formattedPhone.length === 12) {
            formattedPhone = '0' + formattedPhone.slice(2);
        } else if (formattedPhone.length === 10 && /^[6-9]/.test(formattedPhone)) {
            formattedPhone = '0' + formattedPhone;
        }

        const callerId = cfg.virtualNumber.replace(/[\s-]/g, '');
        const appId = (process.env.EXOTEL_APP_ID || '').trim();
        const appUrl = (process.env.EXOTEL_APP_URL || '').trim();

        const params = new URLSearchParams();
        params.append('From', formattedPhone);
        params.append('CallerId', callerId);
        params.append('CustomField', customField);
        params.append('TimeLimit', '600');

        if (appUrl) {
            params.append('Url', appUrl);
        } else if (appId) {
            params.append('Url', `http://my.exotel.com/${cfg.accountSid}/exoml/start_voice/${appId}`);
        } else {
            params.append('To', callerId);
        }

        const cb = callbackUrl || (process.env.EXOTEL_CALLBACK_URL || '').trim();
        if (cb) {
            params.append('StatusCallback', cb);
        }

        const authHeader = 'Basic ' + Buffer.from(`${cfg.apiKey}:${cfg.apiToken}`).toString('base64');

        try {
            console.log(`[ExotelService] Sending call request to Exotel for ${formattedPhone} (CallerId: ${callerId})...`);
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    Authorization: authHeader,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: params.toString()
            });

            const data = await res.json().catch(() => ({}));
            if (res.ok && data.Call) {
                console.log(`[ExotelService] Call successfully dispatched! Sid: ${data.Call.Sid}, Status: ${data.Call.Status}`);
                return {
                    success: true,
                    callSid: data.Call.Sid,
                    status: data.Call.Status || 'in-progress',
                    provider: 'exotel',
                    raw: data.Call
                };
            } else {
                const errMsg = data.RestException ? data.RestException.Message : `HTTP ${res.status}`;
                console.error(`[ExotelService] Exotel API rejected call to ${formattedPhone}:`, errMsg);
                return {
                    success: false,
                    error: errMsg,
                    status: 'failed'
                };
            }
        } catch (err) {
            console.error(`[ExotelService] Network error calling Exotel API:`, err);
            return {
                success: false,
                error: err.message,
                status: 'failed'
            };
        }
    }

    static async getCallStatus(callSid) {
        const cfg = this.getConfig();
        const url = `https://${cfg.subdomain}/v1/Accounts/${cfg.accountSid}/Calls/${callSid}.json`;
        const authHeader = 'Basic ' + Buffer.from(`${cfg.apiKey}:${cfg.apiToken}`).toString('base64');

        try {
            const res = await fetch(url, {
                headers: { Authorization: authHeader }
            });
            if (res.ok) {
                const data = await res.json();
                return { success: true, call: data.Call || {} };
            }
            return { success: false, error: `HTTP ${res.status}` };
        } catch (err) {
            return { success: false, error: err.message };
        }
    }
}
