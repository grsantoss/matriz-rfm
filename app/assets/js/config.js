// Configuration object
const config = {
    // API Configuration
    apiUrl: 'https://api.rfminsights.com.br',
    apiVersion: 'v1',
    apiTimeout: 30000,

    // Feature Flags
    enableAnalytics: true,
    enableLogging: true,

    // Authentication
    authDomain: 'rfminsights.com.br',
    authEndpoint: '/auth',
    authRedirectUri: 'https://app.rfminsights.com.br/callback.html',

    // Application Settings
    appName: 'RFM Insights',
    appVersion: '1.0.0',
    appEnv: 'production'
};

// Load environment variables from .env file if available
async function loadEnvConfig() {
    try {
        const response = await fetch('/.env');
        if (response.ok) {
            const envText = await response.text();
            const envVars = {};
            
            // Parse .env file
            envText.split('\n').forEach(line => {
                const [key, value] = line.split('=').map(s => s.trim());
                if (key && value) {
                    envVars[key] = value;
                }
            });

            // Update config with environment variables
            Object.keys(config).forEach(key => {
                const envKey = key.toUpperCase();
                if (envVars[envKey] !== undefined) {
                    config[key] = envVars[envKey];
                }
            });
        }
    } catch (error) {
        console.warn('Could not load .env file, using default configuration');
    }
}

// Initialize configuration
loadEnvConfig();

// Export configuration
window.appConfig = config; 