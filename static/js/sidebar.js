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

// 모바일 환경에서 링크 클릭 이벤트 처리
document.addEventListener('DOMContentLoaded', function() {
    // 메시지 내용 내의 모든 링크에 이벤트 리스너 추가
    function addLinkEventListeners() {
        const messageContents = document.querySelectorAll('.message-content');
        messageContents.forEach(function(content) {
            const links = content.querySelectorAll('a');
            links.forEach(function(link) {
                // 링크에 터치 이벤트 리스너 추가
                link.addEventListener('click', function(e) {
                    // 기본 이벤트 방지
                    e.preventDefault();
                    
                    // 링크 URL 가져오기
                    const url = this.getAttribute('href');
                    
                    // 새 창에서 링크 열기
                    window.open(url, '_blank');
                });
                
                // 링크에 터치 이벤트 리스너 추가
                link.addEventListener('touchend', function(e) {
                    // 기본 이벤트 방지
                    e.preventDefault();
                    
                    // 링크 URL 가져오기
                    const url = this.getAttribute('href');
                    
                    // 새 창에서 링크 열기
                    window.open(url, '_blank');
                });
            });
        });
    }
    
    // 초기 이벤트 리스너 추가
    addLinkEventListeners();
    
    // DOM 변경 감지 및 이벤트 리스너 추가
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                addLinkEventListeners();
            }
        });
    });
    
    // 채팅 메시지 컨테이너 관찰
    const chatContainer = document.querySelector('.chat-messages-container');
    if (chatContainer) {
        observer.observe(chatContainer, { childList: true, subtree: true });
    }
}); 