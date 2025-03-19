/**
 * RFM Insights - Notifications Module
 * 
 * This module handles displaying notifications to the user
 */

class NotificationManager {
    constructor() {
        this.container = document.getElementById('notification-area');
        this.template = document.getElementById('notification-template');
        this.notifications = [];
        this.init();
    }
    
    /**
     * Initialize the notification manager
     */
    init() {
        // Create container if it doesn't exist
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notification-area';
            this.container.className = 'notification-area';
            document.body.appendChild(this.container);
        }
        
        // Subscribe to state changes
        if (window.stateManager) {
            window.stateManager.subscribe(state => {
                this.updateNotifications(state.notifications);
            });
        }
    }
    
    /**
     * Update notifications based on state
     * @param {Array} notifications - Notifications from state
     */
    updateNotifications(notifications) {
        // Add new notifications
        notifications.forEach(notification => {
            if (!this.notifications.find(n => n.id === notification.id)) {
                this.showNotification(notification);
            }
        });
        
        // Remove old notifications
        this.notifications.forEach(notification => {
            if (!notifications.find(n => n.id === notification.id)) {
                this.removeNotification(notification.id);
            }
        });
        
        this.notifications = [...notifications];
    }
    
    /**
     * Show a notification
     * @param {Object} notification - Notification object
     */
    showNotification(notification) {
        const { id, type, title, message } = notification;
        
        // Clone template
        const notificationElement = this.template.content.cloneNode(true);
        const notificationDiv = notificationElement.querySelector('.notification');
        
        // Set notification ID
        notificationDiv.dataset.id = id;
        
        // Set notification type
        notificationDiv.classList.add(`notification-${type}`);
        
        // Set icon based on type
        const iconElement = notificationDiv.querySelector('.notification-icon i');
        switch (type) {
            case 'success':
                iconElement.classList.add('bi-check-circle');
                break;
            case 'error':
                iconElement.classList.add('bi-exclamation-circle');
                break;
            case 'warning':
                iconElement.classList.add('bi-exclamation-triangle');
                break;
            case 'info':
            default:
                iconElement.classList.add('bi-info-circle');
                break;
        }
        
        // Set title and message
        notificationDiv.querySelector('.notification-title').textContent = title;
        notificationDiv.querySelector('.notification-message').textContent = message;
        
        // Add close button event
        const closeButton = notificationDiv.querySelector('.notification-close');
        closeButton.addEventListener('click', () => {
            if (window.stateManager) {
                window.stateManager.removeNotification(id);
            } else {
                this.removeNotification(id);
            }
        });
        
        // Add to container
        this.container.appendChild(notificationDiv);
        
        // Animate in
        setTimeout(() => {
            notificationDiv.classList.add('show');
        }, 10);
    }
    
    /**
     * Remove a notification
     * @param {number} id - Notification ID
     */
    removeNotification(id) {
        const notificationDiv = this.container.querySelector(`.notification[data-id="${id}"]`);
        if (notificationDiv) {
            // Animate out
            notificationDiv.classList.remove('show');
            
            // Remove after animation
            setTimeout(() => {
                notificationDiv.remove();
            }, 300);
        }
    }
    
    /**
     * Show a success notification
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {number} duration - Duration in milliseconds
     */
    success(title, message, duration = 5000) {
        if (window.stateManager) {
            window.stateManager.addNotification('success', title, message, duration);
        } else {
            const id = Date.now();
            this.showNotification({ id, type: 'success', title, message });
            
            // Auto-remove after duration
            setTimeout(() => {
                this.removeNotification(id);
            }, duration);
        }
    }
    
    /**
     * Show an error notification
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {number} duration - Duration in milliseconds
     */
    error(title, message, duration = 8000) {
        if (window.stateManager) {
            window.stateManager.addNotification('error', title, message, duration);
        } else {
            const id = Date.now();
            this.showNotification({ id, type: 'error', title, message });
            
            // Auto-remove after duration
            setTimeout(() => {
                this.removeNotification(id);
            }, duration);
        }
    }
    
    /**
     * Show a warning notification
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {number} duration - Duration in milliseconds
     */
    warning(title, message, duration = 6000) {
        if (window.stateManager) {
            window.stateManager.addNotification('warning', title, message, duration);
        } else {
            const id = Date.now();
            this.showNotification({ id, type: 'warning', title, message });
            
            // Auto-remove after duration
            setTimeout(() => {
                this.removeNotification(id);
            }, duration);
        }
    }
    
    /**
     * Show an info notification
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {number} duration - Duration in milliseconds
     */
    info(title, message, duration = 5000) {
        if (window.stateManager) {
            window.stateManager.addNotification('info', title, message, duration);
        } else {
            const id = Date.now();
            this.showNotification({ id, type: 'info', title, message });
            
            // Auto-remove after duration
            setTimeout(() => {
                this.removeNotification(id);
            }, duration);
        }
    }
}

// Create and export a singleton instance
const notificationManager = new NotificationManager();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = notificationManager;
});