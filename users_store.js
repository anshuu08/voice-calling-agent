import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.resolve(__dirname, 'data');
const USERS_FILE = path.join(DATA_DIR, 'users.json');

export class UserStoreError extends Error {
    constructor(message, statusCode = 500) {
        super(message);
        this.statusCode = statusCode;
    }
}

function initStore() {
    if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    if (!fs.existsSync(USERS_FILE)) {
        fs.writeFileSync(USERS_FILE, JSON.stringify([], null, 2), 'utf-8');
    }
}

export function readUsers() {
    initStore();
    try {
        const data = fs.readFileSync(USERS_FILE, 'utf-8');
        return JSON.parse(data);
    } catch (e) {
        console.error(`[USER_STORE] Error reading users file: ${e}`);
        return [];
    }
}

export function writeUsers(users) {
    initStore();
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), 'utf-8');
}

export function findUserByEmail(email) {
    if (!email) return null;
    const normalized = email.trim().toLowerCase();
    const users = readUsers();
    return users.find(u => (u.email || '').trim().toLowerCase() === normalized) || null;
}

export function findUserById(userId) {
    if (!userId) return null;
    const users = readUsers();
    return users.find(u => u.id === userId) || null;
}

export function createUser(name, email, passwordHash) {
    const users = readUsers();
    const normalized = email.trim().toLowerCase();

    const existing = users.find(u => (u.email || '').trim().toLowerCase() === normalized);
    if (existing) {
        throw new UserStoreError("An account with this email already exists.", 409);
    }

    const now = new Date().toISOString();
    const userId = 'usr_' + crypto.randomBytes(12).toString('hex');

    const newUser = {
        id: userId,
        name: name.trim(),
        email: normalized,
        phone: "",
        companyName: "",
        jobTitle: "",
        companySize: "",
        industry: "",
        profileCompleted: false,
        role: "user",
        passwordHash: passwordHash,
        createdAt: now,
        updatedAt: now,
        resetToken: null,
        resetTokenExpires: null
    };

    users.push(newUser);
    writeUsers(users);

    return {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        phone: newUser.phone,
        companyName: newUser.companyName,
        jobTitle: newUser.jobTitle,
        companySize: newUser.companySize,
        industry: newUser.industry,
        profileCompleted: newUser.profileCompleted,
        createdAt: newUser.createdAt
    };
}

export function setResetToken(email, token, expiresAtMs) {
    if (!email) return false;
    const users = readUsers();
    const normalized = email.trim().toLowerCase();
    
    const userIndex = users.findIndex(u => (u.email || '').trim().toLowerCase() === normalized);
    if (userIndex === -1) return false;

    users[userIndex].resetToken = token;
    users[userIndex].resetTokenExpires = expiresAtMs;
    users[userIndex].updatedAt = new Date().toISOString();
    writeUsers(users);
    return true;
}

export function findUserByResetToken(token) {
    if (!token) return null;
    const users = readUsers();
    const nowMs = Date.now();
    return users.find(u => {
        if (u.resetToken === token && u.resetTokenExpires && u.resetTokenExpires > nowMs) {
            return true;
        }
        return false;
    }) || null;
}

export function updateUserPassword(userId, newPasswordHash) {
    const users = readUsers();
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        throw new UserStoreError("User not found.", 404);
    }

    users[userIndex].passwordHash = newPasswordHash;
    users[userIndex].resetToken = null;
    users[userIndex].resetTokenExpires = null;
    users[userIndex].updatedAt = new Date().toISOString();
    writeUsers(users);
    return true;
}

export function updateUserProfile(userId, updates) {
    const users = readUsers();
    const userIndex = users.findIndex(u => u.id === userId);

    if (userIndex === -1) {
        throw new UserStoreError("User not found.", 404);
    }

    const user = users[userIndex];

    if (typeof updates.name === 'string' && updates.name.trim()) {
        user.name = updates.name.trim();
    }
    if (typeof updates.companyName === 'string') {
        user.companyName = updates.companyName.trim();
    }
    if (typeof updates.phone === 'string') {
        user.phone = updates.phone.trim();
    }
    if (typeof updates.jobTitle === 'string') {
        user.jobTitle = updates.jobTitle.trim();
    }
    if (typeof updates.companySize === 'string') {
        user.companySize = updates.companySize.trim();
    }
    if (typeof updates.industry === 'string') {
        user.industry = updates.industry.trim();
    }

    user.profileCompleted = true;
    user.updatedAt = new Date().toISOString();
    writeUsers(users);

    return {
        id: user.id,
        name: user.name,
        email: user.email,
        phone: user.phone || "",
        companyName: user.companyName || "",
        jobTitle: user.jobTitle || "",
        companySize: user.companySize || "",
        industry: user.industry || "",
        profileCompleted: !!user.profileCompleted,
        createdAt: user.createdAt || "",
        updatedAt: user.updatedAt || ""
    };
}

initStore();
