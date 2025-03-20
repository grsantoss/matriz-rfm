/**
 * RFM Insights - State Manager
 * 
 * This module handles global state management for the frontend application
 */

class StateManager {
    constructor() {
        this.state = {
            user: null,
            isAuthenticated: false,
            notifications: [],
            currentPage: 'dashboard',
            dashboardStats: {
                rfmCount: 0,
                messageCount: 0,
                customerCount: 0,
                insightCount: 0
            },
            rfmAnalysis: null,
            messages: [],
            insights: [],
            loading: false,
            error: null
        };
        
        this.listeners = new Set();
        this.init();
    }
    
    /**
     * Initialize the state manager
     */
    init() {
        // Check if user is authenticated
        const token = localStorage.getItem('auth_token');
        if (token) {
            this.setState({ isAuthenticated: true });
            this.loadUserProfile();
        }
        
        // Set current page based on URL
        const currentPath = window.location.pathname;
        const pageName = this.getPageNameFromPath(currentPath);
        this.setState({ currentPage: pageName });
    }
    
    /**
     * Get page name from URL path
     * @param {string} path - URL path
     * @returns {string} Page name
     */
    getPageNameFromPath(path) {
        if (path === '/' || path === '/index.html') {
            return 'dashboard';
        }
        
        const pageName = path.split('/').pop().replace('.html', '');
        return pageName || 'dashboard';
    }
    
    /**
     * Load user profile from API
     */
    async loadUserProfile() {
        try {
            const apiClient = window.apiClient;
            if (!apiClient) return;
            
            const userData = await apiClient.getUserProfile();
            this.setState({ user: userData, isAuthenticated: true });
        } catch (error) {
            console.error('Error loading user profile:', error);
            this.setState({ user: null, isAuthenticated: false });
        }
    }
    
    /**
     * Get current state
     * @returns {Object} Current state
     */
    getState() {
        return { ...this.state };
    }
    
    /**
     * Update state
     * @param {Object} newState - New state to merge
     */
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notify();
    }
    
    /**
     * Subscribe to state changes
     * @param {Function} listener - Callback function
     * @returns {Function} Unsubscribe function
     */
    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }
    
    /**
     * Notify all listeners of state change
     */
    notify() {
        this.listeners.forEach(listener => listener(this.state));
    }
    
    /**
     * Set user data and authentication state
     * @param {Object} userData - User data
     * @param {string} token - JWT token
     */
    setUser(userData, token) {
        if (token) {
            localStorage.setItem('auth_token', token);
        }
        
        this.setState({
            user: userData,
            isAuthenticated: true
        });
    }
    
    /**
     * Clear user data and authentication state
     */
    clearUser() {
        localStorage.removeItem('auth_token');
        
        this.setState({
            user: null,
            isAuthenticated: false
        });
    }
    
    /**
     * Add a notification
     * @param {string} type - Notification type (success, error, info, warning)
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {number} duration - Duration in milliseconds
     */
    addNotification(type, title, message, duration = 5000) {
        const id = Date.now();
        const notification = { id, type, title, message };
        
        this.setState({
            notifications: [...this.state.notifications, notification]
        });
        
        // Auto-remove notification after duration
        setTimeout(() => {
            this.removeNotification(id);
        }, duration);
        
        return id;
    }
    
    /**
     * Remove a notification
     * @param {number} id - Notification ID
     */
    removeNotification(id) {
        this.setState({
            notifications: this.state.notifications.filter(n => n.id !== id)
        });
    }
    
    /**
     * Set loading state
     * @param {boolean} isLoading - Loading state
     */
    setLoading(isLoading) {
        this.setState({ loading: isLoading });
    }
    
    /**
     * Set error state
     * @param {string} error - Error message
     */
    setError(error) {
        this.setState({ error });
        
        if (error) {
            this.addNotification('error', 'Erro', error);
        }
    }
    
    /**
     * Update dashboard statistics
     * @param {Object} stats - Dashboard statistics
     */
    updateDashboardStats(stats) {
        this.setState({
            dashboardStats: { ...this.state.dashboardStats, ...stats }
        });
    }
    
    /**
     * Set current page
     * @param {string} pageName - Page name
     */
    setCurrentPage(pageName) {
        this.setState({ currentPage: pageName });
    }
    
    /**
     * Set RFM analysis data
     * @param {Object} analysisData - RFM analysis data
     */
    setRFMAnalysis(analysisData) {
        this.setState({ rfmAnalysis: analysisData });
    }
    
    /**
     * Set messages list
     * @param {Array} messages - Messages list
     */
    setMessages(messages) {
        this.setState({ messages });
    }
    
    /**
     * Add a message to the list
     * @param {Object} message - Message object
     */
    addMessage(message) {
        this.setState({
            messages: [message, ...this.state.messages]
        });
    }
    
    /**
     * Set insights list
     * @param {Array} insights - Insights list
     */
    setInsights(insights) {
        this.setState({ insights });
    }
    
    /**
     * Add an insight to the list
     * @param {Object} insight - Insight object
     */
    addInsight(insight) {
        this.setState({
            insights: [insight, ...this.state.insights]
        });
    }
    
    /**
     * Reset state to initial values
     */
    resetState() {
        this.setState({
            user: null,
            isAuthenticated: false,
            rfmAnalysis: null,
            messages: [],
            insights: [],
            loading: false,
            error: null
        });
    }
    
    /**
     * Authenticate user
     * @param {Object} credentials - Login credentials
     * @returns {Promise<Object>} Authentication response
     */
    async login(credentials) {
        try {
            this.setState({ loading: true, error: null });
            const response = await window.apiClient.login(credentials);
            this.setState({
                user: response.user,
                isAuthenticated: true,
                loading: false
            });
            return response;
        } catch (error) {
            this.setState({
                error: error.message,
                loading: false
            });
            throw error;
        }
    }
    
    /**
     * Logout user
     * @returns {Promise<boolean>} Logout success
     */
    async logout() {
        try {
            this.setState({ loading: true, error: null });
            await window.apiClient.logout();
            this.resetState();
            return true;
        } catch (error) {
            this.setState({
                error: error.message,
                loading: false
            });
            throw error;
        }
    }
    
    /**
     * Analyze RFM
     * @param {Object} data - RFM analysis data
     * @returns {Promise<Object>} RFM analysis result
     */
    async analyzeRFM(data) {
        try {
            this.setState({ loading: true, error: null });
            const response = await window.apiClient.getRfmAnalysis(data);
            this.setState({
                rfmAnalysis: response,
                loading: false
            });
            return response;
        } catch (error) {
            this.setState({
                error: error.message,
                loading: false
            });
            throw error;
        }
    }
    
    /**
     * Generate message
     * @param {Object} data - Message generation data
     * @returns {Promise<Object>} Generated message
     */
    async generateMessage(data) {
        try {
            this.setState({ loading: true, error: null });
            const response = await window.apiClient.generateMessage(data);
            this.setState({
                messages: [...this.state.messages, response],
                loading: false
            });
            return response;
        } catch (error) {
            this.setState({
                error: error.message,
                loading: false
            });
            throw error;
        }
    }
    
    /**
     * Generate insight
     * @param {Object} data - Insight generation data
     * @returns {Promise<Object>} Generated insight
     */
    async generateInsight(data) {
        try {
            this.setState({ loading: true, error: null });
            const response = await window.apiClient.generateInsight(data);
            this.setState({
                insights: [...this.state.insights, response],
                loading: false
            });
            return response;
        } catch (error) {
            this.setState({
                error: error.message,
                loading: false
            });
            throw error;
        }
    }
}

// Create and export a singleton instance
const stateManager = new StateManager();
window.stateManager = stateManager;