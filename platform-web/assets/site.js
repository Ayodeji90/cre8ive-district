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

  // Fog cloud animation
  const fogCanvas = document.getElementById('fog');
  if (fogCanvas && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const fCtx = fogCanvas.getContext('2d');
    let fw, fh;
    const fogResize = () => { fw = fogCanvas.width = window.innerWidth; fh = fogCanvas.height = window.innerHeight; };
    fogResize();
    window.addEventListener('resize', fogResize, { passive: true });

    const palette = [[243,107,53],[180,170,155],[80,75,65],[220,210,195],[243,107,53]];
    const blobs = Array.from({ length: 18 }, () => {
      const depth = Math.random();
      const [r,g,b] = palette[Math.floor(Math.random() * palette.length)];
      return {
        x: Math.random() * fw * 1.4 - fw * 0.2,
        y: Math.random() * fh,
        r: 180 + depth * 350,
        vx: 0.1 + depth * 0.3,
        vy: (Math.random() - 0.5) * 0.06,
        wobble: Math.random() * Math.PI * 2,
        wAmp: 0.15 + Math.random() * 0.4,
        wFreq: 0.001 + Math.random() * 0.002,
        opacity: 0.025 + depth * 0.05,
        cr: r, cg: g, cb: b
      };
    });

    const drawFog = () => {
      fCtx.clearRect(0, 0, fw, fh);
      for (const b of blobs) {
        b.wobble += b.wFreq;
        b.x += b.vx;
        b.y += b.vy + Math.sin(b.wobble) * b.wAmp;
        if (b.x - b.r > fw + 100) { b.x = -b.r - 100; b.y = Math.random() * fh; }
        if (b.y < -b.r) b.y = fh + b.r;
        if (b.y > fh + b.r) b.y = -b.r;
        const g = fCtx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
        g.addColorStop(0, `rgba(${b.cr},${b.cg},${b.cb},${b.opacity})`);
        g.addColorStop(0.4, `rgba(${b.cr},${b.cg},${b.cb},${b.opacity * 0.45})`);
        g.addColorStop(1, `rgba(${b.cr},${b.cg},${b.cb},0)`);
        fCtx.fillStyle = g;
        fCtx.beginPath();
        fCtx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        fCtx.fill();
      }
      requestAnimationFrame(drawFog);
    };
    drawFog();
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
    if (status) status.textContent = 'A WhatsApp draft is being prepared. Review it and press Send to reach us. If it does not open, use the direct WhatsApp or email links on this page.';
    window.open(`https://wa.me/2349038753287?text=${encodeURIComponent(message)}`, '_blank', 'noopener,noreferrer');
  });
})();
