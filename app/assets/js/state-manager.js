/**
 * RFM Insights - State Manager
 * 
 * This module handles global state management for the frontend application
 */

// State Manager
const stateManager = {
    // User state
    user: null,
    token: null,

    // Initialize state from localStorage
    init() {
        const storedUser = localStorage.getItem('user');
        const storedToken = localStorage.getItem('auth_token');

        if (storedUser) {
            this.user = JSON.parse(storedUser);
        }
        if (storedToken) {
            this.token = storedToken;
        }
    },

    // User methods
    setUser(user) {
        this.user = user;
        localStorage.setItem('user', JSON.stringify(user));
    },

    getUser() {
        return this.user;
    },

    clearUser() {
        this.user = null;
        localStorage.removeItem('user');
    },

    // Token methods
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    },

    getToken() {
        return this.token || localStorage.getItem('auth_token');
    },

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    },

    // Authentication state
    isAuthenticated() {
        return !!this.getToken();
    },

    // Clear all state
    clearAll() {
        this.clearUser();
        this.clearToken();
    },

    // Logout
    logout() {
        this.clearAll();
        window.location.href = 'login.html';
    },

    // Check if user has specific role
    hasRole(role) {
        return this.user?.roles?.includes(role) || false;
    },

    // Check if user has specific permission
    hasPermission(permission) {
        return this.user?.permissions?.includes(permission) || false;
    },

    // Update user profile
    updateProfile(profileData) {
        if (this.user) {
            this.user = { ...this.user, ...profileData };
            this.setUser(this.user);
        }
    },

    // Check if user needs to complete profile
    needsProfileCompletion() {
        return this.user && !this.user.profile_completed;
    }
};

// Initialize state manager
stateManager.init();

// Export state manager
window.stateManager = stateManager;