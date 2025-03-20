/**
 * RFM Insights - API Client
 * 
 * This module handles all communication with the backend API
 */

const API_BASE_URL = '/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    /**
     * Set the authentication token
     * @param {string} token - JWT token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    /**
     * Clear the authentication token
     */
    clearToken() {
        this.token = null;
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

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
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
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
            if (this.token) {
                headers['Authorization'] = `Bearer ${this.token}`;
            }

            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
    async login(email, password) {
        return await this.post('/auth/token', {
            username: email,
            password: password
        });
    }

    async register(userData) {
        return await this.post('/auth/register', userData);
    }

    async getUserProfile() {
        return await this.get('/auth/me');
    }

    async updateUserProfile(userData) {
        return await this.put('/auth/me', userData);
    }

    async requestPasswordReset(email) {
        return await this.post('/auth/password-reset', { email });
    }

    async resetPassword(token, newPassword) {
        return await this.post('/auth/password-reset/confirm', {
            token,
            new_password: newPassword
        });
    }

    // RFM Analysis endpoints
    async analyzeRFM(formData) {
        return await this.uploadFile('/rfm/analyze-rfm', formData);
    }

    async getAnalysisHistory(limit = 5) {
        return await this.get(`/rfm/analysis-history?limit=${limit}`);
    }

    async getSegmentDescriptions() {
        return await this.get('/rfm/segment-descriptions');
    }

    // Marketplace endpoints
    async generateMessage(messageData) {
        return await this.post('/marketplace/generate-message', messageData);
    }

    async regenerateMessage(messageId) {
        return await this.post('/marketplace/regenerate-message', { messageId });
    }

    async getUserMessages(limit = 10, offset = 0) {
        return await this.get(`/marketplace/messages?limit=${limit}&offset=${offset}`);
    }

    async generateInsight(insightData) {
        return await this.post('/marketplace/generate-insight', insightData);
    }
}

// Create and export a singleton instance
const apiClient = new APIClient();