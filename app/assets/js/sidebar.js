/**
 * RFM Insights - Sidebar Navigation Script
 * Controla o comportamento da barra lateral em todas as páginas
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const headerToggle = document.getElementById('header-toggle');
    const navbar = document.getElementById('navbar-vertical');
    const bodyPd = document.getElementById('body-pd');
    const header = document.getElementById('header');
    const mobileFooter = document.querySelector('.mobile-footer');
    const closeSidebarBtn = document.querySelector('.sidebar-close-btn');
    
    // Verifica se os elementos existem para evitar erros
    if (headerToggle && navbar && bodyPd) {
        // Função para alternar a visibilidade da barra lateral
        function toggleSidebar(event) {
            if (event) {
                event.preventDefault(); // Previne comportamento padrão do botão
                event.stopPropagation(); // Impede propagação do evento
            }
            
            // Toggle classes para mostrar/esconder a barra lateral
            navbar.classList.toggle('show');
            bodyPd.classList.toggle('body-pd');
            header.classList.toggle('body-pd');
            
            // Ajusta o rodapé móvel quando a barra lateral está aberta
            if (mobileFooter) {
                mobileFooter.classList.toggle('body-pd');
            }
        }
        
        // Adiciona evento de clique ao botão de toggle com debounce para evitar múltiplos cliques
        let isToggling = false;
        headerToggle.addEventListener('click', function(e) {
            if (!isToggling) {
                isToggling = true;
                toggleSidebar(e);
                
                // Previne múltiplos cliques em sequência
                setTimeout(() => {
                    isToggling = false;
                }, 300); // Tempo de debounce corresponde à transição CSS
            }
        });
        
        // Adiciona evento para fechar a sidebar ao clicar no botão de fechar
        if (closeSidebarBtn) {
            closeSidebarBtn.addEventListener('click', function() {
                navbar.classList.remove('show');
                bodyPd.classList.remove('body-pd');
                header.classList.remove('body-pd');
                if (mobileFooter) {
                    mobileFooter.classList.remove('body-pd');
                }
            });
        }
        
        // Detecta cliques fora da barra lateral em dispositivos móveis para fechá-la
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && 
                navbar.classList.contains('show') && 
                !navbar.contains(e.target) && 
                e.target !== headerToggle && 
                !headerToggle.contains(e.target)) {
                
                // Fecha a barra lateral
                navbar.classList.remove('show');
                bodyPd.classList.remove('body-pd');
                header.classList.remove('body-pd');
                
                // Ajusta o rodapé móvel quando a barra lateral é fechada
                if (mobileFooter) {
                    mobileFooter.classList.remove('body-pd');
                }
            }
        });
        
        // Fecha a barra lateral quando um link é clicado em dispositivos móveis
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768 && navbar.classList.contains('show')) {
                    setTimeout(() => {
                        navbar.classList.remove('show');
                        bodyPd.classList.remove('body-pd');
                        header.classList.remove('body-pd');
                        if (mobileFooter) {
                            mobileFooter.classList.remove('body-pd');
                        }
                    }, 150);
                }
            });
        });
    }
    
    // Ajusta a interface quando a janela é redimensionada
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && navbar) {
            navbar.classList.remove('show');
            if (bodyPd) bodyPd.classList.remove('body-pd');
            if (header) header.classList.remove('body-pd');
            if (mobileFooter) {
                mobileFooter.classList.remove('body-pd');
            }
        }
    });
    
    // Marca o link ativo com base na URL atual
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation.includes(linkPath) && linkPath !== '#') {
            link.classList.add('active');
        } else if (link !== navLinks[0]) {
            link.classList.remove('active');
        }
    });
    
    // Adiciona comportamento para o toggle de senha, se existir
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInputs = document.querySelectorAll('.password-input');
    
    if (togglePasswordBtn && passwordInputs.length > 0) {
        togglePasswordBtn.addEventListener('click', function() {
            const type = passwordInputs[0].type === 'password' ? 'text' : 'password';
            const iconClass = type === 'password' ? 'fa-eye' : 'fa-eye-slash';
            const buttonText = type === 'password' ? ' Mostrar Senha' : ' Ocultar Senha';
            
            passwordInputs.forEach(input => {
                input.type = type;
            });
            
            togglePasswordBtn.innerHTML = `<i class="fas ${iconClass} me-1"></i>${buttonText}`;
        });
    }
});
