// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const showRegisterFormBtn = document.getElementById('showRegisterForm');
const showLoginFormBtn = document.getElementById('showLoginForm');
const forgotPasswordLink = document.getElementById('forgotPasswordLink');

// Form Validation
function validateForm(form) {
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// Show Notification
function showNotification(type, title, message) {
    const template = document.getElementById('notification-template');
    const notification = template.content.cloneNode(true).querySelector('.notification');
    
    notification.classList.add(type);
    
    const icon = notification.querySelector('.notification-icon i');
    switch (type) {
        case 'success':
            icon.classList.add('bi-check-circle-fill');
            break;
        case 'error':
            icon.classList.add('bi-x-circle-fill');
            break;
        case 'warning':
            icon.classList.add('bi-exclamation-triangle-fill');
            break;
    }
    
    notification.querySelector('.notification-title').textContent = title;
    notification.querySelector('.notification-message').textContent = message;
    
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Form Switch
showRegisterFormBtn.addEventListener('click', () => {
    loginForm.classList.add('d-none');
    registerForm.classList.remove('d-none');
});

showLoginFormBtn.addEventListener('click', () => {
    registerForm.classList.add('d-none');
    loginForm.classList.remove('d-none');
});

// Login Form Submit
loginForm.addEventListener('submit', async (event) => {
    if (!validateForm(loginForm)) return;
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await apiClient.login(email, password);
        if (response.success) {
            stateManager.setToken(response.token);
            stateManager.setUser(response.user);
            window.location.href = 'index.html';
        } else {
            showNotification('error', 'Erro de Login', response.message || 'Credenciais inválidas');
        }
    } catch (error) {
        showNotification('error', 'Erro', 'Ocorreu um erro ao tentar fazer login. Tente novamente.');
    }
});

// Register Form Submit
registerForm.addEventListener('submit', async (event) => {
    if (!validateForm(registerForm)) return;
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    
    if (password !== passwordConfirm) {
        showNotification('error', 'Erro de Validação', 'As senhas não coincidem');
        return;
    }
    
    try {
        const response = await apiClient.register({ name, email, password });
        if (response.success) {
            showNotification('success', 'Sucesso', 'Conta criada com sucesso! Faça login para continuar.');
            registerForm.classList.add('d-none');
            loginForm.classList.remove('d-none');
            loginForm.reset();
        } else {
            showNotification('error', 'Erro de Registro', response.message || 'Erro ao criar conta');
        }
    } catch (error) {
        showNotification('error', 'Erro', 'Ocorreu um erro ao tentar criar a conta. Tente novamente.');
    }
});

// Forgot Password
forgotPasswordLink.addEventListener('click', async (event) => {
    event.preventDefault();
    const email = prompt('Digite seu e-mail para recuperar a senha:');
    if (!email) return;
    
    try {
        const response = await apiClient.forgotPassword(email);
        if (response.success) {
            showNotification('success', 'Sucesso', 'Um e-mail com instruções foi enviado para sua conta.');
        } else {
            showNotification('error', 'Erro', response.message || 'Erro ao processar a solicitação');
        }
    } catch (error) {
        showNotification('error', 'Erro', 'Ocorreu um erro ao tentar recuperar a senha. Tente novamente.');
    }
});

// Check if user is already logged in
document.addEventListener('DOMContentLoaded', () => {
    const token = stateManager.getToken();
    if (token) {
        window.location.href = 'index.html';
    }
});