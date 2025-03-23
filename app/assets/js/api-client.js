/**
 * RFM Insights - API Client
 * 
 * This module handles all communication with the backend API
 */

// API Client
const apiClient = {
    baseUrl: window.appConfig.API_URL,
    version: window.appConfig.API_VERSION,
    timeout: window.appConfig.API_TIMEOUT,
    token: null,

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    },

    // Get authentication token
    getToken() {
        return this.token || localStorage.getItem('auth_token');
    },

    // Clear authentication token
    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    },

    // Prepare headers for API requests
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    },

    // Handle API response
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Erro na requisição');
        }
        return response.json();
    },

    // Make API request
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/api/${this.version}${endpoint}`;
        const headers = this.getHeaders();
        const timeout = this.timeout;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return this.handleResponse(response);
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('A requisição excedeu o tempo limite');
            }
            throw error;
        }
    },

    // Authentication Methods
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    async forgotPassword(email) {
        return this.request('/auth/forgot-password', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    },

    async resetPassword(token, password) {
        return this.request('/auth/reset-password', {
            method: 'POST',
            body: JSON.stringify({ token, password })
        });
    },

    // User Methods
    async getCurrentUser() {
        return this.request('/user/me');
    },

    async updateProfile(userData) {
        return this.request('/user/profile', {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    },

    async changePassword(currentPassword, newPassword) {
        return this.request('/user/change-password', {
            method: 'POST',
            body: JSON.stringify({ currentPassword, newPassword })
        });
    },

    // Logout
    logout() {
        this.clearToken();
        window.location.href = 'login.html';
    },

    // RFM Analysis endpoints
    async analyzeRFM(formData) {
        return this.request('/rfm/analyze', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
    },

    async getAnalysisHistory(limit = 5) {
        return this.request(`/rfm/analysis-history?limit=${limit}`);
    },

    async getSegmentDescriptions() {
        return this.request('/rfm/segment-descriptions');
    },

    // Marketplace endpoints
    async generateMessage(messageData) {
        return this.request('/marketplace/generate-message', {
            method: 'POST',
            body: JSON.stringify(messageData)
        });
    },

    async regenerateMessage(messageId) {
        return this.request('/marketplace/regenerate-message', {
            method: 'POST',
            body: JSON.stringify({ messageId })
        });
    },

    async getUserMessages(limit = 10, offset = 0) {
        return this.request(`/marketplace/messages?limit=${limit}&offset=${offset}`);
    },

    async generateInsight(insightData) {
        return this.request('/marketplace/generate-insight', {
            method: 'POST',
            body: JSON.stringify(insightData)
        });
    }
};

// Create and export API client instance
window.apiClient = apiClient;