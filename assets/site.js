(() => {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');

  const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 12);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  toggle?.addEventListener('click', () => {
    const open = nav?.classList.toggle('is-open') ?? false;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('is-open');
    toggle?.setAttribute('aria-expanded', 'false');
    toggle?.setAttribute('aria-label', 'Open menu');
  }));

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches === false) {
    document.querySelectorAll('.brand').forEach(logo => {
      logo.addEventListener('pointermove', event => {
        if (event.pointerType !== 'mouse') return;
        const rect = logo.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - .5;
        const y = (event.clientY - rect.top) / rect.height - .5;
        logo.style.setProperty('--brand-ry', `${(x * 12).toFixed(2)}deg`);
        logo.style.setProperty('--brand-rx', `${(-y * 10).toFixed(2)}deg`);
      });
      logo.addEventListener('pointerleave', () => {
        logo.style.setProperty('--brand-ry', '0deg');
        logo.style.setProperty('--brand-rx', '0deg');
      });
    });
  }

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: .12 });
    revealItems.forEach(item => observer.observe(item));
  } else {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }

  const form = document.querySelector('[data-whatsapp-form]');
  form?.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const message = [
      'Hello Cre8ive District, I would like to discuss a project.',
      `Name: ${data.get('name')}`,
      `Email: ${data.get('email')}`,
      `Business: ${data.get('business') || 'Not provided'}`,
      `Service: ${data.get('service')}`,
      `Budget: ${data.get('budget') || 'Not sure yet'}`,
      `Timeline: ${data.get('timeline') || 'Flexible'}`,
      `Project details: ${data.get('details') || 'I would like to discuss this with your team.'}`
    ].join('\n');
    const status = form.querySelector('.form-status');
    if (status) status.textContent = 'Your enquiry is ready. WhatsApp will open so you can send it to our team.';
    window.open(`https://wa.me/2349038753287?text=${encodeURIComponent(message)}`, '_blank', 'noopener,noreferrer');
  });
})();
