// Login Form Handling
const loginForm = document.querySelector('form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
// Google login button is not present in the HTML
// const googleLoginBtn = document.querySelector('.btn-outline-dark');

// API Endpoints are now handled by the centralized API client

// Email/Password Login
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        const result = await apiClient.login(emailInput.value, passwordInput.value);
        
        // Store token and redirect
        apiClient.setToken(result.access_token);
        window.location.href = 'analise.html';
    } catch (error) {
        console.error('Erro no login:', error);
        alert('Erro ao tentar fazer login: ' + error.message);
    }
});

// Google OAuth2 Login functionality is commented out as the button doesn't exist in the HTML
/*
googleLoginBtn.addEventListener('click', () => {
    // Google OAuth2 configuration
    const clientId = ''; // Will be set from environment variables
    const redirectUri = `${window.location.origin}/auth/google/callback`;
    const scope = 'email profile';

    const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
    
    window.location.href = googleAuthUrl;
});
*/

// Password Reset
const forgotPasswordLink = document.querySelector('a[href="#"]');
forgotPasswordLink.addEventListener('click', async (e) => {
    e.preventDefault();
    
    const email = prompt('Digite seu e-mail para recuperar a senha:');
    if (!email) return;

    try {
        await apiClient.requestPasswordReset(email);
        alert('Um link de recuperação foi enviado para seu e-mail.');
    } catch (error) {
        console.error('Erro na recuperação de senha:', error);
        alert('Erro ao solicitar recuperação de senha: ' + error.message);
    }
});

// Dynamic Footer Year Update
// Footer is not present in the login.html page, so this function is commented out
/*
const updateFooterYear = () => {
    const footerYear = document.querySelector('.footer p');
    if (footerYear) {
        const currentYear = new Date().getFullYear();
        footerYear.innerHTML = `&copy; ${currentYear} RFM Insights. Todos os direitos reservados.`;
    }
};

// Update year on page load and set interval for future updates
updateFooterYear();
setInterval(updateFooterYear, 1000 * 60 * 60); // Check every hour
*/