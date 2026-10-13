import 'dotenv/config';

const LANGUAGE_CODE_MAP = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'te': 'te-IN'
};

/**
 * Calculates Root Mean Square (RMS) audio energy of 16-bit mono PCM bytes.
 */
export function calculateRms(pcmBuffer) {
    if (!pcmBuffer || pcmBuffer.length < 2) return 0;
    const numSamples = Math.floor(pcmBuffer.length / 2);
    let sumSq = 0;
    for (let i = 0; i < numSamples; i++) {
        const val = pcmBuffer.readInt16LE(i * 2);
        sumSq += val * val;
    }
    return Math.sqrt(sumSq / numSamples);
}

/**
 * Wraps raw PCM 16-bit mono bytes into a valid 44-byte RIFF WAV container.
 */
export function pcmToWav(pcmBuffer, sampleRate = 8000, channels = 1, bitsPerSample = 16) {
    const header = Buffer.alloc(44);
    const byteRate = sampleRate * channels * (bitsPerSample / 8);
    const blockAlign = channels * (bitsPerSample / 8);
    const dataSize = pcmBuffer.length;
    const chunkSize = 36 + dataSize;

    header.write('RIFF', 0);
    header.writeUInt32LE(chunkSize, 4);
    header.write('WAVE', 8);
    header.write('fmt ', 12);
    header.writeUInt32LE(16, 16);            // Subchunk1Size
    header.writeUInt16LE(1, 20);             // AudioFormat: Linear PCM
    header.writeUInt16LE(channels, 22);
    header.writeUInt32LE(sampleRate, 24);
    header.writeUInt32LE(byteRate, 28);
    header.writeUInt16LE(blockAlign, 32);
    header.writeUInt16LE(bitsPerSample, 34);
    header.write('data', 36);
    header.writeUInt32LE(dataSize, 40);

    return Buffer.concat([header, pcmBuffer]);
}

/**
 * Extracts raw PCM samples from a WAV buffer (skipping RIFF headers).
 */
export function wavToPcm(wavBuffer) {
    if (!wavBuffer || wavBuffer.length <= 44) return wavBuffer || Buffer.alloc(0);
    const dataIdx = wavBuffer.indexOf('data');
    if (dataIdx !== -1 && dataIdx + 8 <= wavBuffer.length) {
        const dataSize = wavBuffer.readUInt32LE(dataIdx + 4);
        return wavBuffer.subarray(dataIdx + 8, Math.min(wavBuffer.length, dataIdx + 8 + dataSize));
    }
    return wavBuffer.subarray(44);
}

/**
 * Resamples 16-bit mono Linear PCM using linear interpolation.
 * Default converts Sarvam TTS 22050Hz to Exotel telephony 8000Hz.
 */
export function resamplePcm16(inputBuffer, srcRate = 22050, dstRate = 8000) {
    if (!inputBuffer || inputBuffer.length < 2) return inputBuffer || Buffer.alloc(0);
    if (srcRate === dstRate) return inputBuffer;

    const numInputSamples = Math.floor(inputBuffer.length / 2);
    const numOutputSamples = Math.floor(numInputSamples * (dstRate / srcRate));
    if (numOutputSamples === 0) return Buffer.alloc(0);

    const outputBuffer = Buffer.alloc(numOutputSamples * 2);
    const ratio = (numInputSamples - 1) / Math.max(1, numOutputSamples - 1);

    for (let i = 0; i < numOutputSamples; i++) {
        const srcPos = i * ratio;
        const srcIndex = Math.floor(srcPos);
        const frac = srcPos - srcIndex;

        const s1 = inputBuffer.readInt16LE(srcIndex * 2);
        const s2 = (srcIndex + 1 < numInputSamples) ? inputBuffer.readInt16LE((srcIndex + 1) * 2) : s1;
        const interpolated = Math.round(s1 + frac * (s2 - s1));
        const clamped = Math.max(-32768, Math.min(32767, interpolated));

        outputBuffer.writeInt16LE(clamped, i * 2);
    }

    return outputBuffer;
}

export default class SarvamService {
    static getApiKey() {
        const key = process.env.SARVAM_API || process.env.SARVAM_API_KEY;
        if (!key) {
            throw new Error("SARVAM_API key is not configured in backend environment.");
        }
        return key.trim();
    }

    /**
     * Converts text into audio using Sarvam AI TTS (bulbul:v3).
     * Returns base64 string of WAV audio, or null on failure.
     */
    static async textToSpeech(text, language = 'en') {
        if (!text || !text.trim()) return null;

        const key = this.getApiKey();
        const langKey = String(language || 'en').toLowerCase();
        const langCode = LANGUAGE_CODE_MAP[langKey] || 'en-IN';
        const speaker = process.env.SARVAM_SPEAKER || 'aditya';

        const payload = {
            inputs: [text.trim()],
            target_language_code: langCode,
            speaker: speaker,
            model: "bulbul:v3"
        };

        try {
            const res = await fetch("https://api.sarvam.ai/text-to-speech", {
                method: "POST",
                headers: {
                    "api-subscription-key": key,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                if (data.audios && data.audios.length > 0) {
                    return data.audios[0]; // base64 string
                }
            } else {
                const errText = await res.text();
                console.error(`[SarvamService] TTS warning (HTTP ${res.status}):`, errText.slice(0, 150));
            }
            return null;
        } catch (e) {
            console.error(`[SarvamService] TTS request error:`, e.message);
            return null;
        }
    }

    /**
     * Transcribes audio buffer using Sarvam AI STT (saaras:v3).
     * Expects PCM or WAV audio buffer.
     * Returns { transcript: string, language: string }
     */
    static async speechToText(audioBuffer, filename = "caller_turn.wav", language = null) {
        if (!audioBuffer || audioBuffer.length === 0) {
            return { transcript: "", language: "en" };
        }

        const key = this.getApiKey();

        // Ensure audio has a WAV container
        let wavBytes = audioBuffer;
        if (audioBuffer.length > 4 && audioBuffer.toString('ascii', 0, 4) !== 'RIFF') {
            wavBytes = pcmToWav(audioBuffer, 8000, 1, 16);
        }

        const form = new FormData();
        const blob = new Blob([wavBytes], { type: 'audio/wav' });
        form.append('file', blob, filename);
        form.append('model', 'saaras:v3');

        if (language && LANGUAGE_CODE_MAP[language.toLowerCase()]) {
            form.append('language_code', LANGUAGE_CODE_MAP[language.toLowerCase()]);
        }

        try {
            const res = await fetch("https://api.sarvam.ai/speech-to-text", {
                method: "POST",
                headers: {
                    "api-subscription-key": key
                },
                body: form
            });

            if (res.ok) {
                const data = await res.json();
                const transcript = (data.transcript || "").trim();
                const detectedCode = String(data.language_code || "en").toLowerCase();
                let shortLang = "en";
                if (detectedCode.includes("hi")) shortLang = "hi";
                else if (detectedCode.includes("te")) shortLang = "te";

                return { transcript, language: shortLang };
            } else {
                const errText = await res.text();
                console.error(`[SarvamService] STT warning (HTTP ${res.status}):`, errText.slice(0, 150));
                return { transcript: "", language: "en" };
            }
        } catch (e) {
            console.error(`[SarvamService] STT request error:`, e.message);
            return { transcript: "", language: "en" };
        }
    }
}
