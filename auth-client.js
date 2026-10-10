/**
 * Agent Hari — Client-Side Authentication Manager
 * Handles API calls, state management, form validations, and navigation updates.
 */

const AuthClient = {
  /**
   * Fetch current authenticated user from /api/auth/me
   */
  async getCurrentUser() {
    try {
      const res = await fetch('/api/auth/me', {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        credentials: 'include'
      });
      if (!res.ok) return null;
      const data = await res.json();
      return data.success ? data.user : null;
    } catch (err) {
      console.warn('[AUTH] Could not fetch current user:', err);
      return null;
    }
  },

  /**
   * Register new user
   */
  async signup(payload) {
    const res = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Signup failed.');
    }
    return data;
  },

  /**
   * Login user
   */
  async login(payload) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Login failed.');
    }
    return data;
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        credentials: 'include'
      });
    } catch (err) {
      console.warn('[AUTH] Logout request error:', err);
    }
    window.location.href = '/signin';
  },

  /**
   * Request password reset link
   */
  async forgotPassword(payload) {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Could not process request.');
    }
    return data;
  },

  /**
   * Reset password with token
   */
  async resetPassword(payload) {
    const res = await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Password reset failed.');
    }
    return data;
  },  /**
   * Submit onboarding details
   */
  async completeOnboarding(payload) {
    const res = await fetch('/api/auth/onboarding', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Could not complete onboarding.');
    }
    return data;
  },

  /**
   * Update profile from dashboard
   */
  async updateProfile(payload) {
    const res = await fetch('/api/auth/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Could not update profile.');
    }
    return data;
  },

  /**
   * Show alert on form
   */
  showAlert(containerId, message, type = 'error') {
    const container = document.getElementById(containerId);
    if (!container) return;

    let iconSvg = '';
    if (type === 'error') {
      iconSvg = '<svg class="auth-alert-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="16"/></svg>';
    } else if (type === 'success') {
      iconSvg = '<svg class="auth-alert-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
    } else {
      iconSvg = '<svg class="auth-alert-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
    }

    container.innerHTML = `
      <div class="auth-alert auth-alert-${type}">
        ${iconSvg}
        <span>${message}</span>
      </div>
    `;
    container.style.display = 'block';
  },

  clearAlert(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = '';
      container.style.display = 'none';
    }
  }
};

// ============================================================================
// DOM Initialization & Event Handlers
// ============================================================================
document.addEventListener('DOMContentLoaded', async () => {

  // 1. Check & Setup Navigation on Public Website
  const mainNavActions = document.getElementById('main-nav-actions');
  if (mainNavActions) {
    const user = await AuthClient.getCurrentUser();
    if (user) {
      const destination = user.profileCompleted ? '/dashboard' : '/onboarding';
      mainNavActions.innerHTML = `
        <a href="${destination}" class="btn btn-outline btn-sm" id="nav-dashboard-btn">
          <span>Dashboard</span>
        </a>
        <button class="btn btn-secondary btn-sm" id="nav-logout-btn">
          <span>Logout</span>
        </button>
      `;

      const logoutBtn = document.getElementById('nav-logout-btn');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
          e.preventDefault();
          AuthClient.logout();
        });
      }
    } else {
      // Unauthenticated state: Ensure links go to dedicated routes
      mainNavActions.innerHTML = `
        <a href="/signin" class="btn btn-outline btn-sm" id="nav-signin-btn">
          <span>Login</span>
        </a>
        <a href="/signup" class="btn btn-primary btn-sm btn-glow" id="nav-signup-btn">
          <span>Create Account</span>
        </a>
      `;
    }
  }

  // 2. Google OAuth UI Button Handler (Placeholder Only)
  const googleBtn = document.getElementById('btn-google-auth');
  if (googleBtn) {
    googleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      AuthClient.showAlert('auth-alert-container', 'Google authentication will be available soon.', 'info');
    });
  }

  // 3. Password Toggle Handlers
  document.querySelectorAll('.btn-toggle-pwd').forEach(btn => {
    btn.addEventListener('click', () => {
      const inputId = btn.getAttribute('data-target');
      const input = document.getElementById(inputId);
      if (!input) return;

      if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
      } else {
        input.type = 'password';
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
      }
    });
  });

  // 4. Signup Form Handler
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      AuthClient.clearAlert('auth-alert-container');

      const name = document.getElementById('signup-name').value.trim();
      const email = document.getElementById('signup-email').value.trim();
      const password = document.getElementById('signup-password').value;
      const confirmPassword = document.getElementById('signup-confirm-password').value;
      const submitBtn = signupForm.querySelector('button[type="submit"]');

      // Client-side validations
      if (!name || name.length < 2) {
        AuthClient.showAlert('auth-alert-container', 'Please enter your full name (at least 2 characters).');
        return;
      }
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        AuthClient.showAlert('auth-alert-container', 'Please enter a valid email address.');
        return;
      }
      if (!password || password.length < 6) {
        AuthClient.showAlert('auth-alert-container', 'Password must contain at least 6 characters.');
        return;
      }
      if (password !== confirmPassword) {
        AuthClient.showAlert('auth-alert-container', 'Passwords do not match. Please verify your password.');
        return;
      }

      // Submit
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="auth-spinner"></span> <span>Creating Account...</span>`;

      try {
        const result = await AuthClient.signup({ name, email, password, confirmPassword });
        AuthClient.showAlert('auth-alert-container', 'Account created successfully! Preparing workspace...', 'success');
        setTimeout(() => {
          if (result.user && result.user.profileCompleted) {
            window.location.href = '/dashboard';
          } else {
            window.location.href = '/onboarding';
          }
        }, 600);
      } catch (err) {
        AuthClient.showAlert('auth-alert-container', err.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // 5. Signin Form Handler
  const signinForm = document.getElementById('signin-form');
  if (signinForm) {
    signinForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      AuthClient.clearAlert('auth-alert-container');

      const email = document.getElementById('signin-email').value.trim();
      const password = document.getElementById('signin-password').value;
      const submitBtn = signinForm.querySelector('button[type="submit"]');

      if (!email || !password) {
        AuthClient.showAlert('auth-alert-container', 'Please fill in both email and password.');
        return;
      }

      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="auth-spinner"></span> <span>Logging in...</span>`;

      try {
        const result = await AuthClient.login({ email, password });
        AuthClient.showAlert('auth-alert-container', 'Logged in successfully! Redirecting...', 'success');
        setTimeout(() => {
          if (result.user && result.user.profileCompleted) {
            window.location.href = '/dashboard';
          } else {
            window.location.href = '/onboarding';
          }
        }, 600);
      } catch (err) {
        AuthClient.showAlert('auth-alert-container', err.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // 6. Forgot Password Form Handler
  const forgotForm = document.getElementById('forgot-password-form');
  if (forgotForm) {
    forgotForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      AuthClient.clearAlert('auth-alert-container');

      const email = document.getElementById('forgot-email').value.trim();
      const submitBtn = forgotForm.querySelector('button[type="submit"]');

      if (!email) {
        AuthClient.showAlert('auth-alert-container', 'Please enter your registered email address.');
        return;
      }

      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="auth-spinner"></span> <span>Sending...</span>`;

      try {
        const res = await AuthClient.forgotPassword({ email });
        let msg = res.message;
        if (res.debugResetToken) {
          msg += ` <br><br><strong>Dev Mode Token:</strong> <a href="/reset-password?token=${res.debugResetToken}" style="color:#2563EB;word-break:break-all;">Click here to reset password directly</a>`;
        }
        AuthClient.showAlert('auth-alert-container', msg, 'success');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      } catch (err) {
        AuthClient.showAlert('auth-alert-container', err.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // 7. Reset Password Form Handler
  const resetForm = document.getElementById('reset-password-form');
  if (resetForm) {
    // Auto-populate token from query param if present
    const urlParams = new URLSearchParams(window.location.search);
    const tokenParam = urlParams.get('token');
    const tokenInput = document.getElementById('reset-token');
    if (tokenParam && tokenInput) {
      tokenInput.value = tokenParam;
    }

    resetForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      AuthClient.clearAlert('auth-alert-container');

      const token = document.getElementById('reset-token').value.trim();
      const newPassword = document.getElementById('reset-new-password').value;
      const confirmPassword = document.getElementById('reset-confirm-password').value;
      const submitBtn = resetForm.querySelector('button[type="submit"]');

      if (!token) {
        AuthClient.showAlert('auth-alert-container', 'Password reset token is required.');
        return;
      }
      if (!newPassword || newPassword.length < 6) {
        AuthClient.showAlert('auth-alert-container', 'New password must contain at least 6 characters.');
        return;
      }
      if (newPassword !== confirmPassword) {
        AuthClient.showAlert('auth-alert-container', 'Passwords do not match.');
        return;
      }

      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="auth-spinner"></span> <span>Resetting Password...</span>`;

      try {
        await AuthClient.resetPassword({ token, newPassword, confirmPassword });
        AuthClient.showAlert('auth-alert-container', 'Password updated successfully! Redirecting to login...', 'success');
        setTimeout(() => {
          window.location.href = '/signin';
        }, 1500);
      } catch (err) {
        AuthClient.showAlert('auth-alert-container', err.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // 8. Protected Account Page Handler (/account)
  const accountContainer = document.getElementById('account-protected-page');
  if (accountContainer) {
    const user = await AuthClient.getCurrentUser();
    if (!user) {
      // Unauthenticated: Redirect to /signin immediately
      window.location.href = '/signin';
      return;
    }

    // Populate user details
    const userNameEl = document.getElementById('acc-user-name');
    const userEmailEl = document.getElementById('acc-user-email');
    const userInitialEl = document.getElementById('acc-user-avatar');

    if (userNameEl) userNameEl.textContent = user.name;
    if (userEmailEl) userEmailEl.textContent = user.email;
    if (userInitialEl) {
      const parts = user.name.trim().split(' ');
      const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0][0].toUpperCase();
      userInitialEl.textContent = initials;
    }

    // Logout button handler
    const accountLogoutBtn = document.getElementById('btn-account-logout');
    if (accountLogoutBtn) {
      accountLogoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        AuthClient.logout();
      });
    }
  }

});
