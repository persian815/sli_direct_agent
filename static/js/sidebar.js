// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'aria-expanded') {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                const chatInput = document.querySelector('.chat-input-container');
                if (sidebar && chatInput) {
                    const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
                    chatInput.style.left = isExpanded ? '300px' : '0';
                }
            }
        });
    });

    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        observer.observe(sidebar, { attributes: true });
    }
}); 