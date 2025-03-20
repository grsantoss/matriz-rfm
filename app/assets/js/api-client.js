/**
 * RFM Insights - API Client
 * 
 * This module handles all communication with the backend API
 */

// API Client
class ApiClient {
    constructor() {
        this.baseUrl = window.appConfig.apiUrl;
        this.version = window.appConfig.apiVersion;
        this.timeout = window.appConfig.apiTimeout;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/${this.version}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add authentication token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    /**
     * Set the authentication token
     * @param {string} token - JWT token
     */
    setToken(token) {
        localStorage.setItem('auth_token', token);
    }

    /**
     * Clear the authentication token
     */
    clearToken() {
        localStorage.removeItem('auth_token');
    }

    /**
     * Get the authentication headers
     * @returns {Object} Headers object
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * Handle API response
     * @param {Response} response - Fetch API response
     * @returns {Promise} Promise with response data
     */
    async handleResponse(response) {
        const data = await response.json();

        if (!response.ok) {
            // Handle authentication errors
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/login.html';
            }

            // Throw error with message from API
            throw new Error(data.detail || 'Erro na requisição');
        }

        return data;
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Promise with response data
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}${endpoint}`, {
                method: 'GET',
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error(`Error in GET ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @returns {Promise} Promise with response data
     */
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}${endpoint}`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error(`Error in POST ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @returns {Promise} Promise with response data
     */
    async put(endpoint, data) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}${endpoint}`, {
                method: 'PUT',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error(`Error in PUT ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Promise with response data
     */
    async delete(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}${endpoint}`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error(`Error in DELETE ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Upload a file
     * @param {string} endpoint - API endpoint
     * @param {FormData} formData - Form data with file
     * @returns {Promise} Promise with response data
     */
    async uploadFile(endpoint, formData) {
        try {
            const headers = {};
            const token = localStorage.getItem('auth_token');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${this.baseUrl}/${this.version}${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: formData
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error(`Error in file upload ${endpoint}:`, error);
            throw error;
        }
    }

    // Authentication endpoints
    async login(credentials) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async getUserProfile() {
        return this.request('/auth/me');
    }

    async updateUserProfile(userData) {
        return this.put('/auth/me', userData);
    }

    async requestPasswordReset(email) {
        return this.request('/auth/password-reset', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    async resetPassword(token, newPassword) {
        return this.request('/auth/password-reset/confirm', {
            method: 'POST',
            body: JSON.stringify({
                token,
                new_password: newPassword
            })
        });
    }

    // RFM Analysis endpoints
    async analyzeRFM(formData) {
        return this.request('/rfm/analyze', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
    }

    async getAnalysisHistory(limit = 5) {
        return this.get(`/rfm/analysis-history?limit=${limit}`);
    }

    async getSegmentDescriptions() {
        return this.get('/rfm/segment-descriptions');
    }

    // Marketplace endpoints
    async generateMessage(messageData) {
        return this.post('/marketplace/generate-message', messageData);
    }

    async regenerateMessage(messageId) {
        return this.post('/marketplace/regenerate-message', { messageId });
    }

    async getUserMessages(limit = 10, offset = 0) {
        return this.get(`/marketplace/messages?limit=${limit}&offset=${offset}`);
    }

    async generateInsight(insightData) {
        return this.post('/marketplace/generate-insight', insightData);
    }
}

// Create and export API client instance
const apiClient = new ApiClient();
window.apiClient = apiClient;