// ============ AIAD Website — Interactions ============

// 1) Year in footer
document.getElementById('year').textContent = new Date().getFullYear();

// 2) Smooth-scroll for in-page anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const id = link.getAttribute('href');
    if (id.length <= 1) return;
    const target = document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    const offset = 70; // sticky nav height
    const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});

// 3) Reveal-on-scroll using IntersectionObserver
const revealTargets = document.querySelectorAll(
  '.hero__content, .hero__visual, .problem-card, .approach__item, .pillar, .humanizer__copy, .humanizer__visual, .bullet, .section__head, .cta__inner'
);
revealTargets.forEach(el => el.classList.add('reveal'));

if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealTargets.forEach(el => io.observe(el));
} else {
  revealTargets.forEach(el => el.classList.add('is-visible'));
}

// 4) Mobile menu toggle
const burger = document.querySelector('.nav__burger');
const navLinks = document.querySelector('.nav__links');
if (burger && navLinks) {
  burger.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('is-open');
    if (isOpen) {
      navLinks.style.display = 'flex';
      navLinks.style.flexDirection = 'column';
      navLinks.style.position = 'absolute';
      navLinks.style.top = '68px';
      navLinks.style.left = '0';
      navLinks.style.right = '0';
      navLinks.style.background = '#fff';
      navLinks.style.padding = '20px 24px';
      navLinks.style.borderBottom = '1px solid var(--border)';
      navLinks.style.gap = '16px';
      navLinks.style.boxShadow = '0 10px 30px rgba(0,0,0,0.08)';
    } else {
      navLinks.removeAttribute('style');
    }
  });
  // Close menu when a link is clicked
  navLinks.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      navLinks.classList.remove('is-open');
      navLinks.removeAttribute('style');
    });
  });
}

// 5) Contact form (client-side only — placeholder)
const form = document.getElementById('contactForm');
const feedback = document.getElementById('formFeedback');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    feedback.className = '';
    const data = new FormData(form);
    const name = (data.get('name') || '').toString().trim();
    const email = (data.get('email') || '').toString().trim();
    const company = (data.get('company') || '').toString().trim();

    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!name || !company || !emailOk) {
      feedback.textContent = 'Please fill all fields with a valid work email.';
      feedback.classList.add('err');
      return;
    }
    // Placeholder: replace with real endpoint
    feedback.textContent = `Thanks ${name}! We'll be in touch shortly.`;
    feedback.classList.add('ok');
    form.reset();
  });
}

// 6) Subtle parallax on hero orbs
const orbs = document.querySelectorAll('.orb');
if (orbs.length && window.matchMedia('(hover: hover)').matches) {
  window.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 12;
    const y = (e.clientY / window.innerHeight - 0.5) * 12;
    orbs.forEach((orb, i) => {
      const f = i === 0 ? 1 : -1;
      orb.style.transform = `translate(${x * f}px, ${y * f}px)`;
    });
  });
}

// 7) Nav shadow on scroll
const nav = document.querySelector('.nav');
if (nav) {
  const onScroll = () => {
    if (window.scrollY > 8) nav.style.boxShadow = '0 6px 20px rgba(15,23,42,0.06)';
    else nav.style.boxShadow = 'none';
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}
