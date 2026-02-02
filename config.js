/**
 * SMARTSPORTS - Global Configuration
 * קובץ תצורה מרכזי פשוט ונקי
 */

(function() {
    'use strict';

    // API Base URL
    const hostname = window.location.hostname;
    const isDev = hostname === 'localhost' || hostname === '127.0.0.1';
    const API_BASE_URL = isDev ? 'http://127.0.0.1:8000' : window.location.origin;

    // Auth helpers
    function getAuthToken() {
        return localStorage.getItem('access_token');
    }

    function clearAuthToken() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }

    function isAuthenticated() {
        const token = getAuthToken();
        if (!token) return false;
        try {
            const parts = token.split('.');
            if (parts.length !== 3) return false;
            const payload = JSON.parse(atob(parts[1]));
            const now = Math.floor(Date.now() / 1000);
            if (payload.exp && payload.exp < now) {
                clearAuthToken();
                return false;
            }
            return true;
        } catch (e) {
            return false;
        }
    }

    function getCurrentUser() {
        try {
            const userStr = localStorage.getItem('user');
            return userStr ? JSON.parse(userStr) : null;
        } catch (e) {
            return null;
        }
    }

    // API Request
    async function apiPost(url, data) {
        const token = getAuthToken();
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            clearAuthToken();
            window.location.href = '/login.html';
        }

        return await response.json();
    }

    // Logger
    const logger = {
        info: (...args) => console.log('ℹ️', ...args),
        error: (...args) => console.error('❌', ...args),
        success: (...args) => console.log('✅', ...args)
    };

    // Export globally
    window.SMARTSPORTS = {
        API_BASE_URL,
        getAuthToken,
        clearAuthToken,
        isAuthenticated,
        getCurrentUser,
        apiPost,
        logger
    };

    console.log('✅ SMARTSPORTS Config loaded -', API_BASE_URL);
})();
