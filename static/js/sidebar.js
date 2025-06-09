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
                
                // 모바일 웹뷰를 위한 추가 이벤트 리스너
                link.addEventListener('touchstart', function(e) {
                    // 터치 시작 시 시각적 피드백 제공
                    this.style.backgroundColor = 'rgba(76, 175, 80, 0.2)';
                });
                
                link.addEventListener('touchend', function(e) {
                    // 터치 종료 시 시각적 피드백 제거
                    this.style.backgroundColor = '';
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
    
    // 모바일 웹뷰를 위한 전역 이벤트 리스너 추가
    document.addEventListener('click', function(e) {
        // 클릭된 요소가 링크인지 확인
        if (e.target.tagName === 'A' || e.target.closest('a')) {
            const link = e.target.tagName === 'A' ? e.target : e.target.closest('a');
            
            // 링크 URL 가져오기
            const url = link.getAttribute('href');
            
            // 새 창에서 링크 열기
            window.open(url, '_blank');
            
            // 기본 이벤트 방지
            e.preventDefault();
        }
    });
    
    // 모바일 웹뷰를 위한 전역 터치 이벤트 리스너 추가
    document.addEventListener('touchend', function(e) {
        // 터치된 요소가 링크인지 확인
        if (e.target.tagName === 'A' || e.target.closest('a')) {
            const link = e.target.tagName === 'A' ? e.target : e.target.closest('a');
            
            // 링크 URL 가져오기
            const url = link.getAttribute('href');
            
            // 새 창에서 링크 열기
            window.open(url, '_blank');
            
            // 기본 이벤트 방지
            e.preventDefault();
        }
    });
}); 