document.addEventListener('DOMContentLoaded', () => {
  const chatArea = document.getElementById('chat-area');
  const categoryArea = document.getElementById('category-area');
  const inputArea = document.getElementById('input-area');
  const messageForm = document.getElementById('message-form');
  const messageInput = document.getElementById('message-input');
  const loadingSpinner = document.getElementById('loading-spinner');
  let timeoutId;

  // data-attribute에서 초기 옵션 로드
  const initialOptions = JSON.parse(categoryArea.dataset.initialOptions);

  // 메시지 폼 제출 이벤트 처리
  if (messageForm && messageInput) {
    messageForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = messageInput.value.trim();
      if (message) {
        sendMessage(message);
        messageInput.value = '';
      }
    });
  }

  function addUserMessage(msg) {
    const div = document.createElement('div');
    div.className = 'chat-message user';
    div.textContent = msg;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function addBotMessage(msg) {
    const div = document.createElement('div');
    div.className = 'chat-message bot';
    
    // Add dog emoji at the beginning
    const emoji = document.createElement('span');
    emoji.className = 'dog-emoji';
    emoji.textContent = '🐶 ';
    div.appendChild(emoji);
    
    // Create container for message text
    const textContainer = document.createElement('div');
    textContainer.className = 'message-text';
    
    msg.split('\n').forEach(line => {
      const p = document.createElement('p');
      p.innerText = line;
      textContainer.appendChild(p);
    });
    
    div.appendChild(textContainer);
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function startIdleTimer() {
    clearTimeout(timeoutId);
    // 자동 메시지 비활성화
    // timeoutId = setTimeout(() => {
    //   addBotMessage('궁금한 점이 있으시면 언제든 말씀해주세요! 😊');
    // }, 5000);
  }

  function showOptions(options) {
    // 상단 카테고리 버튼 업데이트
    categoryArea.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = 'button-grid';
    options.forEach(opt => {
      const btn = document.createElement('button');
      btn.textContent = opt;
      btn.onclick = () => sendMessage(opt);
      grid.appendChild(btn);
    });
    categoryArea.appendChild(grid);
    
    // 입력란 초기화
    if (messageInput) {
      messageInput.value = '';
      messageInput.focus();
    }
  }

  // 로딩 스피너 표시/숨김
  function showLoading() {
    if (loadingSpinner) {
      loadingSpinner.style.display = 'block';
      chatArea.scrollTop = chatArea.scrollHeight;
    }
  }

  function hideLoading() {
    if (loadingSpinner) {
      loadingSpinner.style.display = 'none';
    }
  }

  function sendMessage(message) {
    clearTimeout(timeoutId);
    addUserMessage(message);
    showLoading();
    
    // 입력 폼 비활성화
    if (messageInput) {
      messageInput.disabled = true;
    }
    
    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
      hideLoading();
      // 입력 폼 다시 활성화
      if (messageInput) {
        messageInput.disabled = false;
        messageInput.focus();
      }
      addBotMessage(data.bot);
      showOptions(data.options);
      startIdleTimer();
    })
    .catch(error => {
      console.error('Error:', error);
      hideLoading();
      // 입력 폼 다시 활성화
      if (messageInput) {
        messageInput.disabled = false;
        messageInput.focus();
      }
      addBotMessage('죄송합니다, 응답을 받는 중 오류가 발생했습니다.');
    });
  }

  // 초기 UI 세팅
  showOptions(initialOptions);
}); 