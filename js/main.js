/* ==========================================================================
   Earlyseed Ventures — Homescreen interactions
   Principles (Apple, "Designing Fluid Interfaces"):
   - respond on pointer-down; track 1:1 and respect the grab offset
   - every animation is interruptible and starts from the on-screen value
   - release velocity is handed to the spring (no seam between drag & motion)
   - flicks project momentum forward before choosing a snap target
   - boundaries rubber-band instead of hard-stopping
   ========================================================================== */
(() => {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ------------------------------------------------------------------------
     Physics helpers
     ------------------------------------------------------------------------ */

  // Apple's momentum projection (exponential decay, as used by UIScrollView)
  const project = (velocity /* px/s */, decelerationRate = 0.998) =>
    ((velocity / 1000) * decelerationRate) / (1 - decelerationRate);

  // Progressive resistance past a boundary
  const rubberband = (overshoot, dimension, constant = 0.55) =>
    (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));

  /**
   * Damped spring parameterised the way Apple designers think about it:
   *   damping  — 1.0 = critically damped (no overshoot), < 1 bounces
   *   response — seconds to (roughly) reach the target; not a fixed duration
   * Re-targeting mid-flight keeps the current position AND velocity.
   */
  function createSpring(onUpdate, onRest) {
    const s = { x: 0, v: 0, target: 0, k: 0, c: 0, raf: 0, last: 0 };

    function frame(now) {
      let dt = Math.min((now - s.last) / 1000, 1 / 30); // clamp tab-switch gaps
      s.last = now;
      const step = 1 / 240;
      while (dt > 0) {                                   // fixed sub-steps for stability
        const h = Math.min(step, dt);
        const force = -s.k * (s.x - s.target) - s.c * s.v;
        s.v += force * h;
        s.x += s.v * h;
        dt -= h;
      }
      if (Math.abs(s.v) < 4 && Math.abs(s.x - s.target) < 0.4) {
        s.x = s.target; s.v = 0; s.raf = 0;
        onUpdate(s.x); onRest && onRest();
        return;
      }
      onUpdate(s.x);
      s.raf = requestAnimationFrame(frame);
    }

    return {
      get value() { return s.x; },
      get velocity() { return s.v; },
      get running() { return s.raf !== 0; },
      set(x) { this.stop(); s.x = x; s.v = 0; onUpdate(x); },
      stop() { if (s.raf) cancelAnimationFrame(s.raf); s.raf = 0; },
      to(target, { from = s.x, velocity = s.v, damping = 1, response = 0.4 } = {}) {
        s.x = from; s.v = velocity; s.target = target;
        if (reduceMotion.matches) { this.set(target); onRest && onRest(); return; }
        const omega = (2 * Math.PI) / response;
        s.k = omega * omega;
        s.c = 2 * damping * omega;
        if (!s.raf) { s.last = performance.now(); s.raf = requestAnimationFrame(frame); }
      },
    };
  }

  /* ------------------------------------------------------------------------
     Portfolio strip — drag / flick / trackpad / keyboard
     ------------------------------------------------------------------------ */
  function initStrip(viewport) {
    const track = $('[data-strip-track]', viewport);
    if (!track) return;

    let minX = 0, maxX = 0, snaps = [0];
    let x = 0;                                           // presentation value (what's on screen)
    const render = (v) => { x = v; track.style.transform = `translate3d(${v}px,0,0)`; };
    const spring = createSpring(render);

    function measure() {
      const overflow = track.scrollWidth - viewport.clientWidth;
      maxX = 0;
      minX = Math.min(0, -overflow);
      const pad = parseFloat(getComputedStyle(track).paddingLeft) || 0;
      const raw = $$('.company', track).map((el) => -(el.offsetLeft - pad));
      snaps = [...new Set(raw.map((v) => Math.round(clamp(v))).concat([minX, maxX]))].sort((a, b) => b - a);
      render(clamp(x));
    }
    const clamp = (v) => Math.max(minX, Math.min(maxX, v));
    const nearestSnap = (v) => snaps.reduce((best, s) => (Math.abs(s - v) < Math.abs(best - v) ? s : best), snaps[0]);
    const withResistance = (raw) => {
      const dim = viewport.clientWidth;
      if (raw > maxX) return maxX + rubberband(raw - maxX, dim);
      if (raw < minX) return minX + rubberband(raw - minX, dim);
      return raw;
    };

    // Spring to a snap point. Bounce only when the gesture carried momentum.
    const MAX_VELOCITY = 4000;                           // px/s — faster than a real flick is noise
    function settle(velocity = 0) {
      velocity = Math.max(-MAX_VELOCITY, Math.min(MAX_VELOCITY, velocity));
      const projected = x + project(velocity);
      const target = nearestSnap(clamp(projected));
      const flicked = Math.abs(velocity) > 400;
      const hitsEdge = projected !== clamp(projected);   // thrown past the end: land softly, no wobble
      spring.to(target, {
        from: x,
        velocity,
        damping: flicked && !hitsEdge ? 0.86 : 1,
        response: flicked ? 0.45 : 0.4,
      });
    }

    /* Pointer dragging */
    let pointerId = null, startX = 0, startY = 0, originX = 0, dragging = false, history = [];

    viewport.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      spring.stop();                                     // grab it mid-flight — from where it is now
      pointerId = e.pointerId;
      startX = e.clientX; startY = e.clientY;
      originX = x;                                       // respects the grab offset
      dragging = false;
      history = [{ x: e.clientX, t: e.timeStamp }];
    });

    viewport.addEventListener('pointermove', (e) => {
      if (e.pointerId !== pointerId) return;
      const dx = e.clientX - startX, dy = e.clientY - startY;
      if (!dragging) {
        if (Math.abs(dx) < 6) return;                    // hysteresis before committing to a direction
        if (Math.abs(dy) > Math.abs(dx)) { pointerId = null; return; }
        dragging = true;
        viewport.setPointerCapture(e.pointerId);
        viewport.classList.add('is-dragging');
      }
      history.push({ x: e.clientX, t: e.timeStamp });
      if (history.length > 6) history.shift();
      render(withResistance(originX + dx));              // 1:1 tracking
    });

    function release(e) {
      if (e.pointerId !== pointerId) return;
      pointerId = null;
      if (!dragging) { if (!spring.running) settle(0); return; }
      dragging = false;
      viewport.classList.remove('is-dragging');
      // Velocity from the last ~100ms of movement
      const now = e.timeStamp;
      const recent = history.filter((p) => now - p.t < 100);
      let v = 0;
      if (recent.length > 1) {
        const a = recent[0], b = recent[recent.length - 1];
        v = ((b.x - a.x) / Math.max(b.t - a.t, 1)) * 1000;
      }
      settle(v);
    }
    viewport.addEventListener('pointerup', release);
    viewport.addEventListener('pointercancel', release);
    viewport.addEventListener('dragstart', (e) => e.preventDefault());

    /* Trackpad horizontal scrolling — direct, with soft edges, then snap */
    let wheelRaw = 0, wheelTimer = 0, wheelActive = false;
    viewport.addEventListener('wheel', (e) => {
      if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return; // leave vertical scrolling alone
      e.preventDefault();
      if (!wheelActive) { spring.stop(); wheelRaw = x; wheelActive = true; }
      wheelRaw -= e.deltaX;
      // Keep the raw value from running away so the band can return
      wheelRaw = Math.max(minX - viewport.clientWidth, Math.min(maxX + viewport.clientWidth, wheelRaw));
      render(withResistance(wheelRaw));
      clearTimeout(wheelTimer);
      wheelTimer = setTimeout(() => { wheelActive = false; settle(0); }, 120);
    }, { passive: false });

    /* Keyboard */
    viewport.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      const current = nearestSnap(spring.running ? spring.value : x);
      const i = snaps.indexOf(current);
      const next = snaps[Math.max(0, Math.min(snaps.length - 1, i + (e.key === 'ArrowRight' ? 1 : -1)))];
      spring.to(next, { from: x, damping: 1, response: 0.4 });
    });

    new ResizeObserver(measure).observe(viewport);
    document.fonts && document.fonts.ready.then(measure);
    measure();
  }

  /* ------------------------------------------------------------------------
     Header — material appears only when content scrolls beneath it
     ------------------------------------------------------------------------ */
  function initHeader(header) {
    const update = () => header.classList.toggle('is-scrolled', window.scrollY > 4);
    update();
    window.addEventListener('scroll', update, { passive: true });
  }

  /* ------------------------------------------------------------------------
     Popover helper — enters & exits along the same path; never locks input
     ------------------------------------------------------------------------ */
  function createPopover(panel, toggle, { onOpen, onClose } = {}) {
    let open = false, closeTimer = 0;

    function show() {
      clearTimeout(closeTimer);
      panel.hidden = false;
      panel.classList.remove('is-closing');
      // next frame so the transition runs from the closed state
      requestAnimationFrame(() => panel.classList.add('is-open'));
      toggle.setAttribute('aria-expanded', 'true');
      open = true;
      onOpen && onOpen();
    }
    function hide({ restoreFocus = true } = {}) {
      if (!open) return;
      open = false;
      panel.classList.add('is-closing');
      panel.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      closeTimer = setTimeout(() => { panel.hidden = true; panel.classList.remove('is-closing'); }, 240);
      onClose && onClose();
      if (restoreFocus && panel.contains(document.activeElement)) toggle.focus();
    }

    toggle.addEventListener('click', () => (open ? hide() : show()));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && open) hide(); });
    document.addEventListener('pointerdown', (e) => {
      if (open && !panel.contains(e.target) && !toggle.contains(e.target)) hide({ restoreFocus: false });
    });
    return { show, hide, get open() { return open; } };
  }

  /* ------------------------------------------------------------------------
     Search
     ------------------------------------------------------------------------ */
  const SEARCH_INDEX = [
    { title: 'About Earlyseed', section: 'About', href: '#about' },
    { title: 'Our Portfolio', section: 'Portfolio', href: '#portfolio' },
    { title: 'Campus Partnerships', section: 'Team', href: '#team' },
    { title: 'Services for Founders', section: 'Services', href: '#services' },
    { title: 'Services for Investors', section: 'Services', href: '#services' },
    { title: 'Pre-funding: modelling, decks, valuations', section: 'Services', href: '#services' },
    { title: 'Fundraising & investor access', section: 'Services', href: '#services' },
    { title: 'Syndicate access', section: 'Services', href: '#services' },
    { title: 'From the deal table', section: 'Perspectives', href: '#perspectives' },
    { title: 'Founder Stories', section: 'Perspectives', href: '#perspectives' },
    { title: 'Podcasts', section: 'Prologue', href: '#prologue' },
    { title: 'Pitch to us', section: 'Raise', href: '#raise' },
    { title: 'Invest with us', section: 'Invest', href: '#invest' },
  ];

  function initSearch(header) {
    const panel = $('[data-search-panel]', header);
    const toggle = $('[data-search-toggle]', header);
    const input = $('[data-search-input]', header);
    const results = $('[data-search-results]', header);
    if (!panel || !toggle) return;

    let active = 0, matches = [];
    function renderResults() {
      const q = input.value.trim().toLowerCase();
      matches = q ? SEARCH_INDEX.filter((r) => (r.title + ' ' + r.section).toLowerCase().includes(q)) : SEARCH_INDEX.slice(0, 6);
      active = 0;
      results.innerHTML = matches.length
        ? matches.map((r, i) => `<li><a href="${r.href}" aria-selected="${i === 0}">${r.title}<span>${r.section}</span></a></li>`).join('')
        : '<li class="search-panel__empty">No matches yet — try “services” or “portfolio”.</li>';
    }
    function highlight(i) {
      const links = $$('a', results);
      if (!links.length) return;
      active = (i + links.length) % links.length;
      links.forEach((a, j) => a.setAttribute('aria-selected', String(j === active)));
      links[active].scrollIntoView({ block: 'nearest' });
    }

    const pop = createPopover(panel, toggle, {
      onOpen: () => { header.classList.add('is-open'); renderResults(); setTimeout(() => input.focus(), 30); },
      onClose: () => { if (!$('[data-mobile-menu].is-open')) header.classList.remove('is-open'); },
    });

    input.addEventListener('input', renderResults);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); highlight(active + 1); }
      if (e.key === 'ArrowUp') { e.preventDefault(); highlight(active - 1); }
      if (e.key === 'Enter') {
        const link = $$('a', results)[active];
        if (link) { e.preventDefault(); pop.hide({ restoreFocus: false }); location.hash = link.getAttribute('href'); }
      }
    });
    results.addEventListener('click', (e) => { if (e.target.closest('a')) pop.hide({ restoreFocus: false }); });

    // "/" focuses search, like most docs sites
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && !pop.open && !/input|textarea/i.test(document.activeElement.tagName)) {
        e.preventDefault(); pop.show();
      }
    });
  }

  /* ------------------------------------------------------------------------
     Mobile menu
     ------------------------------------------------------------------------ */
  function initMobileMenu(header) {
    const panel = $('[data-mobile-menu]', header);
    const toggle = $('[data-menu-toggle]', header);
    if (!panel || !toggle) return;
    const pop = createPopover(panel, toggle, {
      onOpen: () => { header.classList.add('is-open'); toggle.setAttribute('aria-label', 'Close menu'); },
      onClose: () => { header.classList.remove('is-open'); toggle.setAttribute('aria-label', 'Open menu'); },
    });
    panel.addEventListener('click', (e) => { if (e.target.closest('a')) pop.hide({ restoreFocus: false }); });
    window.matchMedia('(min-width: 1121px)').addEventListener('change', (m) => m.matches && pop.hide({ restoreFocus: false }));
  }

  /* ------------------------------------------------------------------------
     Scroll reveal
     ------------------------------------------------------------------------ */
  function initReveal() {
    const items = $$('[data-reveal]');
    if (!('IntersectionObserver' in window)) { items.forEach((el) => el.classList.add('is-in')); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    items.forEach((el) => io.observe(el));
  }

  /* ------------------------------------------------------------------------ */
  const header = $('[data-header]');
  if (header) { initHeader(header); initSearch(header); initMobileMenu(header); }
  $$('[data-strip]').forEach(initStrip);
  initReveal();
  const year = $('[data-year]'); if (year) year.textContent = new Date().getFullYear();
})();
