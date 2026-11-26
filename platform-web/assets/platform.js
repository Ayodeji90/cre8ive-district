(() => {
  const promptForm = document.querySelector('[data-idea-form]');
  if (promptForm) {
    const prompt = promptForm.querySelector('textarea');
    const error = promptForm.querySelector('.prompt-error');
    promptForm.querySelectorAll('[data-example]').forEach(button => {
      button.addEventListener('click', () => {
        prompt.value = button.dataset.example;
        prompt.focus();
      });
    });
    promptForm.addEventListener('submit', event => {
      event.preventDefault();
      const idea = prompt.value.trim();
      if (!idea) {
        error.classList.add('is-visible');
        prompt.focus();
        return;
      }
      error.classList.remove('is-visible');
      sessionStorage.setItem('cre8ive-business-idea', idea);
      window.location.href = '/start/';
    });
  }

  const chatForm = document.querySelector('[data-chat-form]');
  if (!chatForm) return;
  const messages = document.querySelector('[data-messages]');
  const input = chatForm.querySelector('textarea');
  const businessTitle = document.querySelector('[data-business-title]');
  const idea = sessionStorage.getItem('cre8ive-business-idea');
  let turn = 0;
  if (idea) {
    addMessage('user', idea);
    addMessage('assistant', 'Thanks for sharing that. I’ll help shape it into a clear brand brief. What name should customers know your business by? If you have not chosen one yet, say so and we can start with naming ideas.');
    sessionStorage.removeItem('cre8ive-business-idea');
  }
  chatForm.addEventListener('submit', event => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addMessage('user', text);
    input.value = '';
    turn += 1;
    if (turn === 1 && businessTitle) businessTitle.textContent = text.slice(0, 32);
    const replies = [
      'Good. What do you offer, and who are the people you most want to reach?',
      'Got it. How should the business feel to a customer — for example, warm and familiar, bold and modern, or calm and premium?',
      'That gives us a useful starting point. I’ve added your answers to the brief. In the connected platform, the next step will create brand directions for you to review here.'
    ];
    addMessage('assistant', replies[Math.min(turn - 1, replies.length - 1)]);
    if (turn >= 3) document.querySelector('[data-progress]')?.classList.add('is-ready');
  });

  function addMessage(role, text) {
    const message = document.createElement('div');
    message.className = `message ${role}`;
    if (role === 'assistant') {
      const label = document.createElement('small');
      label.textContent = 'Cre8ive District';
      message.append(label);
    }
    message.append(document.createTextNode(text));
    messages.append(message);
    messages.scrollTop = messages.scrollHeight;
  }

  document.querySelectorAll('[data-preview-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('[data-preview-tab]').forEach(other => other.setAttribute('aria-selected', String(other === tab)));
      document.querySelector('[data-preview-brand]').hidden = tab.dataset.previewTab !== 'brand';
      document.querySelector('[data-preview-website]').hidden = tab.dataset.previewTab !== 'website';
    });
  });
  document.querySelector('[data-preview-toggle]')?.addEventListener('click', event => {
    const open = document.body.classList.toggle('preview-open');
    event.currentTarget.textContent = open ? '← Back to chat' : 'Preview ↑';
    event.currentTarget.setAttribute('aria-expanded', String(open));
  });
})();
