document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle Functionality
    const headerToggle = document.getElementById('header-toggle');
    const navbar = document.getElementById('navbar-vertical');
    const bodyPd = document.body;
    const header = document.getElementById('header');

    if (headerToggle) {
        headerToggle.addEventListener('click', () => {
            navbar.classList.toggle('show');
            bodyPd.classList.toggle('body-pd');
            header.classList.toggle('body-pd');
        });
    }
    
    // Password Toggle Functionality
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInputs = document.querySelectorAll('.password-input');
    
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            const isPasswordVisible = togglePasswordBtn.classList.contains('showing-password');
            
            // Toggle password visibility for all password fields
            passwordInputs.forEach(input => {
                input.type = isPasswordVisible ? 'password' : 'text';
            });
            
            // Update button text and icon
            if (isPasswordVisible) {
                togglePasswordBtn.innerHTML = '<i class="fas fa-eye me-1"></i> Mostrar Senha';
                togglePasswordBtn.classList.remove('showing-password');
            } else {
                togglePasswordBtn.innerHTML = '<i class="fas fa-eye-slash me-1"></i> Esconder Senha';
                togglePasswordBtn.classList.add('showing-password');
            }
        });
    }
    
    // Profile Photo Management
    const profilePic = document.querySelector('.profile-pic');
    const profileInitials = document.querySelector('.profile-pic span');
    const uploadBtn = document.querySelector('.btn-primary.btn-sm');
    const removeBtn = document.querySelector('.btn-outline-danger.btn-sm');
    let currentPhoto = null;
    let hasCustomPhoto = false;

    // Add upload guidelines
    const avatarContainer = document.querySelector('.avatar-upload').parentElement;
    const guidelinesDiv = document.createElement('div');
    guidelinesDiv.className = 'avatar-guidelines small text-muted mt-1';
    guidelinesDiv.textContent = 'Máximo: 5MB • Formatos: .jpeg, .png';
    avatarContainer.insertBefore(guidelinesDiv, avatarContainer.querySelector('.d-grid'));

    // Generate initials avatar
    function generateInitialsAvatar(name) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 80;
        canvas.height = 80;

        // Background
        context.fillStyle = '#4a90e2';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // Text
        const initials = name.split(' ')
            .map(word => word.charAt(0))
            .join('')
            .toUpperCase();

        context.font = 'bold 32px Arial';
        context.fillStyle = '#ffffff';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(initials, canvas.width/2, canvas.height/2);

        return canvas.toDataURL();
    }

    // Handle photo upload
    uploadBtn.addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.jpeg,.jpg,.png';

        input.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showError(uploadBtn, 'O tamanho da imagem deve ser menor que 5 MB');
                    return;
                }

                // Validate file type
                const validTypes = ['image/jpeg', 'image/png'];
                if (!validTypes.includes(file.type)) {
                    showError(uploadBtn, 'Por favor, selecione uma imagem no formato .jpeg ou .png');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    // Remove any previous error messages
                    const errorElements = document.querySelectorAll('.error-message');
                    errorElements.forEach(el => el.remove());

                    // Create an image element to display the uploaded photo
                    profileInitials.style.display = 'none';
                    
                    // Check if we already have an image element
                    let imgElement = profilePic.querySelector('img');
                    if (!imgElement) {
                        imgElement = document.createElement('img');
                        imgElement.className = 'w-100 h-100 rounded-circle';
                        imgElement.style.objectFit = 'cover';
                        profilePic.appendChild(imgElement);
                    }
                    
                    imgElement.src = e.target.result;
                    currentPhoto = e.target.result;
                    hasCustomPhoto = true;
                }

                reader.onerror = function() {
                    showError(uploadBtn, 'Erro ao ler o arquivo. Por favor, tente novamente.');
                }

                reader.readAsDataURL(file);
            }
        }

        input.click();
    });

    // Handle photo removal
    removeBtn.addEventListener('click', function() {
        // Remove the image if it exists
        const imgElement = profilePic.querySelector('img');
        if (imgElement) {
            profilePic.removeChild(imgElement);
        }
        
        // Show the initials again
        profileInitials.style.display = '';
        
        // Update the initials based on the current name
        const firstName = document.getElementById('firstName').value;
        const initials = firstName.charAt(0).toUpperCase();
        profileInitials.textContent = initials;
        
        currentPhoto = null;
        hasCustomPhoto = false;
    });

    // Form Submission
    const profileForm = document.querySelector('#profileForm');
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Here you would typically send the data to your backend
        alert('Alterações de perfil salvas com sucesso!');
    });

    // Password Management
    const passwordForm = document.querySelector('#passwordForm');
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    const currentPassword = document.getElementById('currentPassword');

    passwordForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Reset previous error states
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(el => el.remove());

        // Validate current password (in real app, this would be checked against backend)
        if (!currentPassword.value) {
            showError(currentPassword, 'A senha atual é necessária');
            return;
        }

        // Validate password requirements
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        if (!passwordRegex.test(newPassword.value)) {
            showError(newPassword, 'A senha deve ter pelo menos 8 caracteres e incluir letras maiúsculas, minúsculas e números');
            return;
        }

        // Validate password match
        if (newPassword.value !== confirmPassword.value) {
            showError(confirmPassword, 'As senhas não correspondem');
            return;
        }

        // Here you would typically send the password update to your backend
        alert('Senha atualizada com sucesso!');
        passwordForm.reset();
    });

    // Cancel buttons
    document.querySelectorAll('.btn-outline-secondary').forEach(btn => {
        btn.addEventListener('click', function() {
            const form = this.closest('form');
            form.reset();
            
            // Reset profile picture if we're in the profile form
            if (form.id === 'profileForm' && hasCustomPhoto && currentPhoto) {
                let imgElement = profilePic.querySelector('img');
                if (!imgElement) {
                    imgElement = document.createElement('img');
                    imgElement.className = 'w-100 h-100 rounded-circle';
                    imgElement.style.objectFit = 'cover';
                    profilePic.appendChild(imgElement);
                    profileInitials.style.display = 'none';
                }
                imgElement.src = currentPhoto;
            }
        });
    });

    function showError(element, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-danger mt-1';
        errorDiv.textContent = message;
        element.parentNode.appendChild(errorDiv);
        element.classList.add('is-invalid');
    }

    // Make sure the profile form updates the initials when the name changes
    const firstNameInput = document.getElementById('firstName');
    if (firstNameInput) {
        firstNameInput.addEventListener('change', function() {
            if (!hasCustomPhoto) {
                const firstName = this.value;
                const initials = firstName.charAt(0).toUpperCase();
                profileInitials.textContent = initials;
            }
        });
    }
});