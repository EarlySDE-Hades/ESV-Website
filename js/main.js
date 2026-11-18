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
    let keyTarget = null;                                // where arrow/key steps are heading
    const carousel = viewport.closest('[data-carousel]');
    const prevBtn = carousel && $('[data-strip-prev]', carousel);
    const nextBtn = carousel && $('[data-strip-next]', carousel);
    function updateArrows() {
      if (!prevBtn) return;
      const t = spring.running && keyTarget !== null ? keyTarget : x;
      prevBtn.disabled = t >= maxX - 1;
      nextBtn.disabled = t <= minX + 1;
    }
    const render = (v) => { x = v; track.style.transform = `translate3d(${v}px,0,0)`; updateArrows(); };
    const spring = createSpring(render);

    function measure() {
      // data-visible="4": size items so exactly N fit (fewer on narrow screens)
      if (carousel && carousel.dataset.visible) {
        const want = +carousel.dataset.visible;
        const n = innerWidth <= 560 ? Math.min(want, 2) : innerWidth <= 960 ? Math.min(want, 3) : want;
        const pad = parseFloat(getComputedStyle(track).paddingLeft) || 0;
        // Equal *gaps*, not equal slots: wide wordmarks would otherwise crowd their neighbours.
        // Each item = its logo's width + one gap; the gap is chosen so the first n fill the strip.
        const items = $$('.company', track);
        const logoW = items.map((li) => { const img = $('img', li); return img ? +img.getAttribute('width') : 160; });
        const avail = viewport.clientWidth - pad * 2;
        const first = logoW.slice(0, n).reduce((a, b) => a + b, 0);
        const gap = Math.max(28, (avail - first) / n);
        const fit = first + gap * n > avail ? avail / (first + gap * n) : 1;   // very narrow: shrink logos a touch
        items.forEach((li, i) => {
          li.style.width = `${Math.floor(logoW[i] * fit + gap)}px`;
          const img = $('img', li); if (img) img.style.width = `${Math.floor(logoW[i] * fit)}px`;
        });
      }
      const overflow = track.scrollWidth - viewport.clientWidth;
      const fits = overflow <= 0;
      if (carousel) carousel.classList.toggle('is-static', fits);   // everything visible: centre it, hide arrows
      if (fits) {
        minX = maxX = Math.round(-overflow / 2);
        snaps = [minX];
      } else {
        maxX = 0;
        minX = -overflow;
        const pad = parseFloat(getComputedStyle(track).paddingLeft) || 0;
        const raw = $$('.company', track).map((el) => -(el.offsetLeft - pad));
        snaps = [...new Set(raw.map((v) => Math.round(clamp(v))).concat([minX, maxX]))].sort((a, b) => b - a);
      }
      spring.stop();
      render(clamp(fits ? minX : x));
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
    let pointerId = null, startX = 0, startY = 0, originX = 0, dragging = false, dragEnded = false, history = [];

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
      dragEnded = true;                                  // the click that ends a drag is not a tap
      setTimeout(() => { dragEnded = false; }, 0);
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

    /* Arrows + keyboard. Repeated steps go on from where the strip is *heading*,
       not where it happens to be mid-flight, so ten presses move ten logos. */
    viewport.addEventListener('pointerdown', () => { keyTarget = null; });
    viewport.addEventListener('wheel', () => { keyTarget = null; }, { passive: true });
    function go(where) {                                 // -1 / +1 = one logo; 'start' / 'end'
      const from = spring.running && keyTarget !== null ? keyTarget : nearestSnap(x);
      const i = snaps.indexOf(from);
      const next = where === 'start' ? snaps[0]
        : where === 'end' ? snaps[snaps.length - 1]
        : snaps[Math.max(0, Math.min(snaps.length - 1, i + where))];
      keyTarget = next;
      spring.to(next, { from: x, damping: 1, response: 0.4 });
      updateArrows();
    }
    viewport.addEventListener('keydown', (e) => {
      const map = { ArrowRight: 1, ArrowLeft: -1, Home: 'start', End: 'end' };
      if (!(e.key in map)) return;
      e.preventDefault();
      go(map[e.key]);
    });
    if (prevBtn) {
      prevBtn.addEventListener('click', () => go(-1));
      nextBtn.addEventListener('click', () => go(1));
    }

    viewport.addEventListener('click', (e) => {
      if (dragEnded) { e.preventDefault(); e.stopPropagation(); dragEnded = false; }
    }, true);

    /* Bring a logo fully into view: on keyboard focus, or when the company
       dialog switches to it (so closing returns into a visible logo). */
    function reveal(el, instant) {
      const item = el.closest('.company') || el;
      const pad = parseFloat(getComputedStyle(track).paddingLeft) || 0;
      const left = item.offsetLeft + x, right = left + item.offsetWidth, w = viewport.clientWidth;
      let target = null;
      if (left < pad) target = clamp(-(item.offsetLeft - pad));
      else if (right > w - pad) target = clamp(-(item.offsetLeft + item.offsetWidth - w + pad));
      if (target === null) return;
      keyTarget = null;
      if (instant || reduceMotion.matches) { spring.stop(); render(target); }
      else spring.to(target, { from: x, damping: 1, response: 0.4 });
    }
    viewport.addEventListener('focusin', (e) => { if (e.target !== viewport) reveal(e.target); });
    viewport.addEventListener('scroll', () => { viewport.scrollLeft = 0; });   // focus must not scroll the clipped box
    viewport.addEventListener('strip:reveal', (e) => reveal(e.detail.el, e.detail.instant));

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
    { title: 'About Earlyseed', section: 'About', href: 'about.html' },
    { title: 'Our mission', section: 'About', href: 'about.html' },
    { title: 'Our growth journey', section: 'About', href: 'about.html#ab-journey-title' },
    { title: 'Sectors we work across', section: 'About', href: 'about.html#ab-sectors-title' },
    { title: 'Leadership team', section: 'Team', href: 'team.html#leadership' },
    { title: 'CA Monica Gupta, Co-founder and CEO', section: 'Team', href: 'team.html#leadership' },
    { title: 'CA Manan Patel, Head of Investments & Tax', section: 'Team', href: 'team.html#leadership' },
    { title: 'CA Nimit Shah, Head of Partnerships', section: 'Team', href: 'team.html#leadership' },
    { title: 'Adv. Rahul Hingmire, Chief Legal Advisor', section: 'Team', href: 'team.html#leadership' },
    { title: 'Sudhir Mehta, Strategy and International Relations', section: 'Team', href: 'team.html#leadership' },
    { title: 'Strategic Growth Partners', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'Pankaj Harwansh, Growth Partner', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'S Robin, Growth Partner', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'Subramanian Srinivasan, Growth Partner', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'Suresh Menon, Growth Partner', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'Sandeep Agrawal, Growth Partner', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'Anup Nathani, Growth Partner', section: 'Team', href: 'team.html#growth-partners' },
    { title: 'Sakshay Upadhyay, Investment Associate', section: 'Team', href: 'team.html#team-members' },
    { title: 'Karan Shah, Deal Manager', section: 'Team', href: 'team.html#team-members' },
    { title: 'Mehak Gupta, Creative Head', section: 'Team', href: 'team.html#team-members' },
    { title: 'Ruhaan Gupta, Investment Associate', section: 'Team', href: 'team.html#team-members' },
    { title: 'Siddhant Baliga, Venture & Technology Strategy Consultant', section: 'Team', href: 'team.html#team-members' },
    { title: 'Dhwani Joshi, Bootcamp Coordinator', section: 'Team', href: 'team.html#team-members' },
    { title: 'Dale Galbano, Executive Assistant', section: 'Team', href: 'team.html#team-members' },
    { title: 'Sneha Lakra, Communication Designer', section: 'Team', href: 'team.html#team-members' },
    { title: 'Siddarth Menon, Investment Associate', section: 'Team', href: 'team.html#team-members' },
    { title: 'Manav Khare, Investor Relations', section: 'Team', href: 'team.html#team-members' },
    { title: 'Our Portfolio', section: 'Portfolio', href: '#portfolio' },
    { title: 'Campus Partnerships', section: 'Partners', href: '#team' },
    { title: 'Events', section: 'Events', href: 'events.html' },
    { title: 'Upcoming events', section: 'Events', href: 'events.html#upcoming' },
    { title: 'Past events', section: 'Events', href: 'events.html#past' },
    { title: 'From seed to success: event recap', section: 'Events', href: 'event-seed-to-success.html' },
    { title: 'Services for Founders: fundraising', section: 'Services', href: '#services' },
    { title: 'Services for Investors', section: 'Services', href: '#for-investors' },
    { title: 'Syndicate access', section: 'Services', href: '#for-investors' },
    { title: 'Curated deal flow', section: 'Services', href: '#for-investors' },
    { title: 'Community & education', section: 'Services', href: '#for-investors' },
    { title: 'Prologue by Earlyseed Ventures', section: 'Prologue', href: 'prologue.html' },
    { title: 'Prologue: pitch deck review and build, financial models', section: 'Prologue', href: 'prologue.html#pl-services' },
    { title: 'Fundraise Readiness Package', section: 'Prologue', href: 'prologue.html#pl-services' },
    { title: 'Founders’ Bootcamp', section: 'Prologue', href: 'prologue.html#pl-services' },
    { title: 'Pre-funding: data room, consultancy', section: 'Prologue', href: '#prologue' },
    { title: 'From the deal table', section: 'Perspectives', href: '#perspectives' },
    { title: 'Founder Stories', section: 'Perspectives', href: '#perspectives' },
    { title: 'Podcasts', section: 'Perspectives', href: '#perspectives' },
    { title: 'Pitch to us', section: 'Raise', href: 'https://ecosystem.earlyseedventures.com/apply' },
    { title: 'Invest with us', section: 'Invest', href: '#for-investors' },
  ];  // Companies and partners come from the JSON the dialogs already use (home page only)
  let fullIndex = null;
  function searchIndex() {
    if (fullIndex) return fullIndex;
    const read = (id, section, href) => {
      try { return JSON.parse($('#' + id).textContent).map((c) => ({ title: c.name, section, href })); } catch { return []; }
    };
    fullIndex = SEARCH_INDEX.concat(read('portfolio-data', 'Portfolio', '#portfolio'), read('partner-data', 'Partners', '#team'));
    return fullIndex;
  }



  function initSearch(header) {
    const panel = $('[data-search-panel]', header);
    const toggle = $('[data-search-toggle]', header);
    const input = $('[data-search-input]', header);
    const results = $('[data-search-results]', header);
    if (!panel || !toggle) return;

    let active = 0, matches = [];
    function renderResults() {
      const q = input.value.trim().toLowerCase();
      matches = q ? searchIndex().filter((r) => (r.title + ' ' + r.section).toLowerCase().includes(q)).slice(0, 8) : SEARCH_INDEX.slice(0, 6);
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
        if (link) {
          e.preventDefault(); pop.hide({ restoreFocus: false });
          const href = link.getAttribute('href');
          if (href.startsWith('#') && $(href)) location.hash = href;
          else location.href = href.startsWith('#') ? 'index.html' + href : href;
        }
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

  /* ------------------------------------------------------------------------
     Hero collage — one assembly, then occasional, visibility-gated depth
     ------------------------------------------------------------------------ */
  function initCollage(collage) {
    const hero = collage.closest('.hero');
    const pointerMedia = window.matchMedia('(hover: hover) and (pointer: fine)');
    const slow = Math.max(1, Math.min(10, Number(new URLSearchParams(location.search).get('slow')) || 1));
    const schedule = {
      dome: [0, 1, 0.70, 4, 12], sun: [140, 0.9, 0.85, 4, 12],
      building: [220, 1, 0.60, 7, 6], plant: [320, 1, 0.60, 7, 6],
      women: [420, 1, 0.55, 10, 0], scientist: [500, 1, 0.55, 10, 0],
      student: [580, 1, 0.55, 10, 0],
      'sparkle-1': [900, 0.8, 0.50, 0, 0], 'sparkle-2': [900, 0.8, 0.50, 0, 0],
    };
    const layers = $$('[data-layer]', collage).map((el) => ({
      el, piece: $('.collage__piece', el), id: el.dataset.layer, spec: schedule[el.dataset.layer],
    }));
    const images = $$('img', collage);
    const sparkles = layers.filter((layer) => layer.id.startsWith('sparkle'));
    const entranceTimers = new Set();
    const entranceSprings = [];
    let ready = false, started = false, settled = false, failed = false;
    let visible = false, quarterVisible = false, scroll = 0;
    let px = 0, py = 0, scrollRaf = 0, twinkleTimer = 0, deadline = 0;
    let twinkle = null, fade = null;
    let completed = 0;
    collage.dataset.state = 'waiting';

    const ambientAllowed = () => settled && visible && !failed && !document.hidden && !reduceMotion.matches;

    function renderDepth() {
      layers.forEach(({ el, spec }) => {
        const x = px / 100 * spec[3];
        const y = py / 100 * spec[3] + scroll * spec[4];
        if (x === 0 && y === 0) el.style.removeProperty('transform');
        else el.style.transform = `translate3d(${x}px,${y}px,0)`;
      });
    }
    // Coordinates use a 100-unit range so the shared spring's pixel rest tolerance
    // remains precise. Re-targeting preserves both its current value and velocity.
    const pointerX = createSpring((value) => { px = value; renderDepth(); });
    const pointerY = createSpring((value) => { py = value; renderDepth(); });

    function stopAmbient() {
      clearTimeout(twinkleTimer); twinkleTimer = 0;
      if (twinkle) { twinkle.cancel(); twinkle = null; }
      if (scrollRaf) cancelAnimationFrame(scrollRaf);
      scrollRaf = 0;
      scroll = 0;
      pointerX.set(0); pointerY.set(0);
    }

    function queueTwinkle() {
      if (!ambientAllowed() || twinkleTimer || twinkle) return;
      twinkleTimer = setTimeout(() => {
        twinkleTimer = 0;
        if (!ambientAllowed()) return;
        const { piece } = sparkles[Math.floor(Math.random() * sparkles.length)];
        twinkle = piece.animate([
          { transform: 'rotate(0deg) scale(1)' },
          { transform: 'rotate(45deg) scale(1.3)', offset: 0.5 },
          { transform: 'rotate(0deg) scale(1)' },
        ], { duration: 900, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
        // Return to the original ray pattern, with no compositor hint at rest.
        twinkle.onfinish = () => { twinkle = null; queueTwinkle(); };
      }, 5000 + Math.random() * 4000);
    }

    function updateScroll() {
      scrollRaf = 0;
      if (!ambientAllowed()) return;
      const rect = collage.getBoundingClientRect();
      scroll = Math.max(0, Math.min(1, -rect.top / Math.max(rect.height, 1)));
      renderDepth();
    }
    function requestScroll() {
      if (ambientAllowed() && !scrollRaf) scrollRaf = requestAnimationFrame(updateScroll);
    }
    function syncAmbient() {
      if (ambientAllowed()) { requestScroll(); queueTwinkle(); }
      else stopAmbient();
    }

    function cancelEntrance() {
      clearTimeout(deadline);
      entranceTimers.forEach(clearTimeout); entranceTimers.clear();
      entranceSprings.forEach((spring) => spring.stop());
      collage.classList.remove('is-pre', 'is-entering');
      layers.forEach(({ piece }) => {
        piece.style.removeProperty('transform');
        piece.style.removeProperty('opacity');
      });
    }

    function showFinal(withFade = false) {
      started = true; settled = true;
      cancelEntrance();
      collage.dataset.state = failed ? 'fallback' : 'settled';
      if (withFade && !reduceMotion.matches) {
        fade = collage.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 250, easing: 'ease-out' });
        fade.onfinish = () => { fade = null; };
      }
      syncAmbient();
    }

    function fallback() {
      if (failed) return;
      failed = true;
      if (fade) { fade.cancel(); fade = null; }
      showFinal();
      const flat = new Image(1600, 640);
      flat.className = 'collage__fallback';
      flat.alt = ''; flat.draggable = false; flat.decoding = 'async';
      flat.setAttribute('aria-hidden', 'true');
      flat.src = 'assets/hero/collage-flat.webp';
      collage.replaceChildren(flat);
    }

    function renderEntrance(layer, value) {
      const p = value / 100, remaining = 1 - p;
      let transform;
      switch (layer.id) {
        case 'dome': transform = `translateY(${28 * remaining}px) scale(${1 - 0.015 * remaining})`; break;
        case 'sun': transform = `translateY(${45 * remaining}%)`; break;
        case 'building': transform = `translateX(${28 * remaining}px)`; break;
        case 'plant': transform = `scaleY(${1 - 0.1 * remaining})`; break;
        case 'women': case 'scientist': case 'student': transform = `translateY(${20 * remaining}px)`; break;
        default: transform = `rotate(${-45 * remaining}deg) scale(${p})`;
      }
      layer.piece.style.transform = transform;
      // Opacity leads position: each piece is solid after the first ~30% of its travel and
      // lands opaque. Tying opacity 1:1 to travel left overlapping layers see-through
      // (back layers ghosting through front ones) and exposed inpainted seams for longer.
      layer.piece.style.opacity = Math.max(0, Math.min(1, p / 0.3));
    }

    function maybeStart() {
      if (started || failed || !ready || !quarterVisible || document.hidden) return;
      if (reduceMotion.matches) { showFinal(); return; }
      started = true;
      clearTimeout(deadline);
      collage.classList.add('is-entering');
      collage.dataset.state = 'entering';
      layers.forEach((layer) => {
        renderEntrance(layer, 0);
        const spring = createSpring((value) => renderEntrance(layer, value), () => {
          layer.piece.style.removeProperty('transform');
          layer.piece.style.removeProperty('opacity');
          // This piece must stay final while the remaining pieces finish.
          layer.piece.style.opacity = '1';
          layer.piece.style.transform = 'none';
          if (++completed === layers.length) showFinal();
        });
        entranceSprings.push(spring);
        const timer = setTimeout(() => {
          entranceTimers.delete(timer);
          spring.to(100, { from: 0, damping: layer.spec[1], response: layer.spec[2] * slow });
        }, layer.spec[0] * slow);
        entranceTimers.add(timer);
      });
      collage.classList.remove('is-pre');
    }

    images.forEach((img) => img.addEventListener('error', fallback, { once: true }));
    if (reduceMotion.matches) showFinal();
    else {
      collage.classList.add('is-pre');
      deadline = setTimeout(() => showFinal(true), 1500);
    }
    Promise.all(images.map((img) => img.decode())).then(() => {
      ready = true; maybeStart();
    }).catch(fallback);

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([entry]) => {
        visible = entry.isIntersecting;
        quarterVisible = entry.intersectionRatio >= 0.25;
        maybeStart(); syncAmbient();
      }, { threshold: [0, 0.25] }).observe(collage);
    } else { visible = true; quarterVisible = true; maybeStart(); }

    hero.addEventListener('pointermove', (event) => {
      if (!ambientAllowed() || !pointerMedia.matches) return;
      const rect = collage.getBoundingClientRect();
      const x = Math.max(-100, Math.min(100, (event.clientX - rect.left - rect.width / 2) / (rect.width / 2) * 100));
      const y = Math.max(-100, Math.min(100, (event.clientY - rect.top - rect.height / 2) / (rect.height / 2) * 100));
      pointerX.to(x, { damping: 1, response: 0.6 });
      pointerY.to(y, { damping: 1, response: 0.6 });
    }, { passive: true });
    hero.addEventListener('pointerleave', () => {
      if (!ambientAllowed()) return;
      pointerX.to(0, { damping: 1, response: 0.6 });
      pointerY.to(0, { damping: 1, response: 0.6 });
    }, { passive: true });
    pointerMedia.addEventListener('change', () => { pointerX.set(0); pointerY.set(0); });
    window.addEventListener('scroll', requestScroll, { passive: true });
    window.addEventListener('resize', requestScroll, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && started && !settled) showFinal();
      maybeStart(); syncAmbient();
    });
    reduceMotion.addEventListener('change', () => {
      if (reduceMotion.matches) {
        if (fade) { fade.cancel(); fade = null; }
        showFinal();
      } else syncAmbient();
    });
  }

  /* ------------------------------------------------------------------------ */
  const collage = $('[data-collage]');
  if (collage) initCollage(collage);
  const heroSection = $('.hero');
  if (heroSection) initHeroField(heroSection);
  $$('[data-svc-dialog]').forEach((d) => { if (d.showModal) initServices(d); });
  const growth = $('[data-growth]');
  if (growth) initGrowth(growth);
  const evHero = $('.ev-hero');
  if (evHero) initEventsHero(evHero);
  initTouchCards();
  const evFilter = $('[data-ev-filter]');
  if (evFilter) initEventFilter(evFilter);
  $$('[data-pl-tabs]').forEach(initPlTabs);
  $$('[data-co-dialog]').forEach((d) => { if (d.showModal) initCompanies(d); });

  /* ------------------------------------------------------------------------
     Services — each card opens a native modal <dialog> that grows out of the
     card (its size and colour) and returns into it on close. Closing mid-open
     reverses from the current frame, so it is always interruptible.
     ------------------------------------------------------------------------ */
  function initServices(dialog) {
    const panel = $('[data-svc-panel]', dialog);
    const body = $('[data-svc-body]', dialog);
    const groupEl = $('[data-svc-group]', dialog);
    const titleEl = $('[data-svc-title]', dialog);
    const cta = $('[data-svc-cta]', dialog);
    // One component for every card-to-dialog: Services, Prologue, team profiles (data-cards / data-prefix)
    const prefix = dialog.dataset.prefix || 'svc-';
    let CARD_COLOR = '#CB8C7C';
    const colourOf = (el) => { const c = getComputedStyle(el).backgroundColor; return !c || c === 'transparent' || c === 'rgba(0, 0, 0, 0)' ? '#FFFFFF' : c; };
    let origin = null, anim = null, contentAnim = null, closing = false;

    function fromCard() {
      const c = origin.getBoundingClientRect();
      const p = panel.getBoundingClientRect();
      const dx = (c.left + c.width / 2) - (p.left + p.width / 2);
      const dy = (c.top + c.height / 2) - (p.top + p.height / 2);
      return `translate(${dx}px, ${dy}px) scale(${c.width / p.width}, ${c.height / p.height})`;
    }

    /* Shared-element mode (team profiles): the headshot on the card flies into its place in
       the profile while the panel rises around it; closing sends it home again. The flying
       copy always starts from where the photo is on screen right now, so opening and closing
       can interrupt each other without a jump. */
    const EASE_OUT = 'cubic-bezier(0.22, 1, 0.36, 1)';
    const radiusOf = (el) => parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0;
    let hero = false, heroSrc = null, heroDst = null, fly = null, flyAnim = null;
    function endFly() {
      if (flyAnim) { flyAnim.onfinish = null; flyAnim.cancel(); flyAnim = null; }
      if (fly) { fly.remove(); fly = null; }
    }
    function flyPhoto(from, to, radFrom, radTo, timing) {
      endFly();
      fly = heroSrc.cloneNode();
      fly.removeAttribute('loading'); fly.removeAttribute('style');
      fly.className = 'fly-photo'; fly.alt = '';
      Object.assign(fly.style, { left: to.left + 'px', top: to.top + 'px', width: to.width + 'px', height: to.height + 'px' });
      dialog.append(fly);
      const sx = from.width / to.width, sy = from.height / to.height;
      flyAnim = fly.animate([
        { transform: `translate(${from.left - to.left}px, ${from.top - to.top}px) scale(${sx}, ${sy})`, borderRadius: `${radFrom / sx}px` },
        { transform: 'none', borderRadius: `${radTo}px` },
      ], { ...timing, fill: 'both' });
      return flyAnim;
    }
    function openHero() {
      const from = heroSrc.getBoundingClientRect(), to = heroDst.getBoundingClientRect();
      const r0 = radiusOf(heroSrc), r1 = radiusOf(heroDst);
      heroSrc.style.visibility = 'hidden'; heroDst.style.visibility = 'hidden';
      flyPhoto(from, to, r0, r1, { duration: 580, easing: EASE_OUT }).onfinish = () => { heroDst.style.visibility = ''; endFly(); };
      anim = panel.animate(
        [{ opacity: 0, transform: 'translateY(26px) scale(0.955)' }, { opacity: 1, transform: 'none' }],
        { duration: 480, easing: EASE_OUT });
      // Name, role, bio, link and affiliations follow the photo in, one after another
      const parts = [titleEl, groupEl, ...$$('.profile__text > *, .profile__aff', body)];
      contentAnim = parts.map((el, i) => el.animate(
        [{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'none' }],
        { duration: 460, delay: 150 + i * 55, easing: EASE_OUT, fill: 'backwards' }));
    }
    function closeHero(done) {
      const flying = !!fly;
      const from = (fly || heroDst).getBoundingClientRect();     // wherever the photo is right now
      const to = heroSrc.getBoundingClientRect();
      const opacity = getComputedStyle(panel).opacity;
      if (anim) anim.cancel();
      heroDst.style.visibility = 'hidden';
      // Text leaves first and fast; the photo takes the longer road home
      contentAnim = [titleEl, groupEl, ...$$('.profile__text > *, .profile__aff', body)].map((el) => el.animate(
        [{ opacity: getComputedStyle(el).opacity }, { opacity: 0 }], { duration: 140, easing: 'ease-in', fill: 'forwards' }));
      anim = panel.animate(
        [{ opacity, transform: 'none' }, { opacity: 0, transform: 'translateY(18px) scale(0.965)' }],
        { duration: 280, delay: 40, easing: 'cubic-bezier(0.4, 0, 1, 1)', fill: 'forwards' });
      const out = flyPhoto(from, to, flying ? radiusOf(heroSrc) : radiusOf(heroDst), radiusOf(heroSrc),
        { duration: flying ? 300 : 440, easing: 'cubic-bezier(0.32, 0.72, 0, 1)' });
      out.onfinish = () => {
        heroSrc.style.visibility = '';
        endFly();
        contentAnim.forEach((a) => a.cancel()); contentAnim = null;
        anim.cancel();
        done();
      };
    }

    function open(card) {
      const tpl = document.getElementById(prefix + card.dataset.service);
      if (!tpl) return;
      endFly();
      if (heroSrc) heroSrc.style.visibility = '';
      if (anim) anim.cancel();
      if (contentAnim) contentAnim.forEach((a) => a.cancel());
      closing = false;
      origin = card;
      CARD_COLOR = colourOf(card);
      groupEl.textContent = tpl.dataset.group;
      titleEl.innerHTML = tpl.dataset.title;
      body.replaceChildren(tpl.content.cloneNode(true));
      cta.hidden = !tpl.dataset.cta;
      cta.textContent = tpl.dataset.cta || '';
      cta.setAttribute('href', tpl.dataset.href || '#');
      dialog.classList.remove('is-closing');
      dialog.showModal();
      panel.scrollTop = 0;
      heroSrc = $('img.person__photo', card); heroDst = $('.profile__photo', body);
      hero = !!(heroSrc && heroDst);

      if (reduceMotion.matches) {
        anim = panel.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 180, easing: 'ease-out' });
        return;
      }
      if (hero) { openHero(); return; }
      anim = panel.animate([
        { transform: fromCard(), backgroundColor: CARD_COLOR, borderRadius: '12px' },
        { transform: 'none', backgroundColor: '#FAFAFA', borderRadius: '24px' },
      ], { duration: 520, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
      // Content arrives just behind the surface, so text is never seen stretched
      contentAnim = [...panel.children].map((el) => el.animate(
        [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }],
        { duration: 320, delay: 150, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'backwards' },
      ));
    }

    function close(then) {
      if (!dialog.open || closing) return;
      closing = true;
      dialog.classList.add('is-closing');
      const finish = () => {
        dialog.close();
        dialog.classList.remove('is-closing');
        closing = false; anim = null;
        if (origin) origin.focus({ preventScroll: true });
        if (then) then();
      };
      if (hero && origin && !reduceMotion.matches) { closeHero(finish); return; }
      if (contentAnim) contentAnim.forEach((a) => a.cancel());
      if (reduceMotion.matches || !origin) {
        anim = panel.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 160, easing: 'ease-in', fill: 'forwards' });
      } else if (anim && anim.playState === 'running') {
        anim.reverse();                                 // interrupted mid-open: retrace from here
      } else {
        [...panel.children].forEach((el) => el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 120, fill: 'forwards' }));
        anim = panel.animate([
          { transform: 'none', backgroundColor: '#FAFAFA', borderRadius: '24px' },
          { transform: fromCard(), backgroundColor: CARD_COLOR, borderRadius: '12px' },
        ], { duration: 360, easing: 'cubic-bezier(0.64, 0, 0.36, 1)', fill: 'forwards' });
      }
      anim.onfinish = () => { [...panel.children].forEach((el) => el.getAnimations().forEach((a) => a.cancel())); anim.cancel(); finish(); };
    }

    $$(dialog.dataset.cards || '.svc-card').forEach((card) => card.addEventListener('click', () => open(card)));
    $('[data-svc-close]', dialog).addEventListener('click', () => close());
    dialog.addEventListener('cancel', (e) => { e.preventDefault(); close(); });   // Esc
    dialog.addEventListener('click', (e) => { if (e.target === dialog) close(); }); // backdrop
    cta.addEventListener('click', (e) => {
      const href = cta.getAttribute('href');
      if (!href.startsWith('#')) return;                // a real page (e.g. the apply form): let the link go
      e.preventDefault();
      close(() => { location.hash = href; });
    });
  }

  /* ------------------------------------------------------------------------
     Events hero — the scene leans a little toward the pointer, nearer layers
     more than far ones (CSS reads --px / --py; see .ev-par). Mouse only.
     ------------------------------------------------------------------------ */
  /* Events filter: All / Offline / Online. A pill slides under the chosen option; events
     of the other kind are hidden, and a list with nothing left shows its empty line. */
  /* Prologue offerings: ARIA tabs (click, arrow keys, Home / End) */
  function initPlTabs(root) {
    const tabs = $$('[role="tab"]', root);
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) tab.focus();
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(t));
      t.addEventListener('keydown', (e) => {
        const n = tabs.length;
        const k = { ArrowRight: i + 1, ArrowLeft: i - 1 + n, Home: 0, End: n - 1 }[e.key];
        if (k === undefined) return;
        e.preventDefault();
        select(tabs[k % n], true);
      });
    });
  }

  function initEventFilter(bar) {
    const btns = $$('.ev-filter__btn', bar), pill = $('.ev-filter__pill', bar);
    const lists = $$('[data-ev-list]');
    const movePill = () => {
      const b = $('.ev-filter__btn.is-active', bar);
      pill.style.width = b.offsetWidth + 'px';
      pill.style.transform = `translateX(${b.offsetLeft}px)`;
    };
    function apply(mode) {
      btns.forEach((b) => { const on = b.dataset.mode === mode; b.classList.toggle('is-active', on); b.setAttribute('aria-pressed', String(on)); });
      movePill();
      lists.forEach((list) => {
        let shown = 0;
        $$(':scope > [data-mode]', list).forEach((li) => {
          const show = mode === 'all' || li.dataset.mode === mode;
          li.hidden = !show;
          if (!show) return;
          shown++;
          li.classList.add('is-in');                                   // never leave a filtered-in item waiting on scroll reveal
          if (!reduceMotion.matches) li.animate([{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }],
            { duration: 320, delay: (shown - 1) * 50, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'backwards' });
        });
        const empty = list.nextElementSibling;
        if (empty && empty.matches('[data-ev-empty]')) empty.hidden = shown > 0;
      });
    }
    btns.forEach((b) => b.addEventListener('click', () => apply(b.dataset.mode)));
    movePill();
    requestAnimationFrame(() => bar.classList.add('is-ready'));       // no slide on first paint
    window.addEventListener('resize', movePill);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(movePill);
  }

  /* Touch screens have no hover, so the Perspectives photos would stay frosted for good.
     There, a card clears while it sits in the middle band of the screen and frosts again
     as it scrolls away (.is-clear mirrors the hover styles). */
  function initTouchCards() {
    const cards = $$('.card:has(.card__photo)');
    if (!cards.length || !('IntersectionObserver' in window) || window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => e.target.classList.toggle('is-clear', e.isIntersecting));
    }, { rootMargin: '-30% 0px -30% 0px', threshold: 0 });
    cards.forEach((c) => io.observe(c));
  }

  function initEventsHero(hero) {
    const art = $('.ev-hero__art', hero);
    if (!art || reduceMotion.matches || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    hero.addEventListener('pointermove', (e) => {
      const r = hero.getBoundingClientRect();
      art.style.setProperty('--px', (((e.clientX - r.left) / r.width) * 2 - 1).toFixed(3));
      art.style.setProperty('--py', (((e.clientY - r.top) / r.height) * 2 - 1).toFixed(3));
    });
    hero.addEventListener('pointerleave', () => { art.style.setProperty('--px', 0); art.style.setProperty('--py', 0); });
  }

  /* ------------------------------------------------------------------------
     Growth — two seedling vines sprout below the hero and grow down the side
     margins as you scroll (never across the content; hidden when the margins
     are too narrow). Their growth depth is a critically
     damped spring chasing the reading line (75% down the viewport), so it
     trails the scroll organically and re-targets without seams. Leaves unfurl
     as the tip passes them; sparkles twinkle. Scrolling back folds it away.
     Reduced motion: fully grown and still.
     ------------------------------------------------------------------------ */
  function initGrowth(wrap) {
    const main = wrap.parentElement;
    const hero = $('.hero', main);
    const ref = $('main > section.container:not(.hero)') || $('.container', main);
    if (!hero || !ref) return;
    const NS = 'http://www.w3.org/2000/svg';
    const make = (tag, attrs = {}, parent) => {
      const n = document.createElementNS(NS, tag);
      for (const k in attrs) n.setAttribute(k, attrs[k]);
      if (parent) parent.append(n);
      return n;
    };
    const svg = make('svg', {}, wrap);
    let vines = [], top = 0, depth = 0, built = false;
    const MIN_MARGIN = 72;                               // below this there is no room: no vine

    // Deterministic wobble so the vines keep their shape across rebuilds
    let seed = 7;
    const rand = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

    // One spring on depth (px down the page); each vine maps depth to its own length
    const spring = createSpring((v) => { depth = v; paint(); });

    function buildVine(cx, amp, H, side, M, W, o) {
      const step = o.step;                               // long, lazy bends: a stem, not a ribbon
      const n = Math.max(2, Math.round(H / step));
      const dy = H / n;
      let x0 = cx, y0 = 0;
      let d = `M${x0} ${y0}`;
      for (let i = 1; i <= n; i++) {
        const x1 = cx + amp * ((i + o.phase) % 2 ? 1 : -1) * side * (0.7 + rand() * 0.3);
        const y1 = i * dy;
        d += ` C${x0} ${y0 + dy * 0.5} ${x1} ${y1 - dy * 0.5} ${x1} ${y1}`;
        x0 = x1; y0 = y1;
      }
      const stem = make('path', { d, class: 'growth__stem', stroke: 'url(#growth-stem)' }, svg);
      const total = stem.getTotalLength();
      stem.style.strokeDasharray = `${total} ${total}`;
      const samples = [];
      for (let i = 0; i <= 200; i++) {
        const l = (total * i) / 200;
        samples.push({ l, y: stem.getPointAtLength(l).y });
      }

      // What grows on the stem: leaves (alternating, some in pairs) and the odd sparkle. Everything is sized to the margin and kept out of the content.
      const fit = Math.min(1, (M - 24) / 150);
      const out = -side;                                     // direction away from the content column
      const inContent = (x) => x > M - 16 && x < W - M + 16;
      const nodes = [];
      const sprout = (g, base) => {
        const sway = make('g', { class: 'growth__sway' }, g);
        sway.style.setProperty('--sway', `${base + rand() * 3}s`);
        sway.style.animationDelay = `${-rand() * 6}s`;
        return make('g', { class: 'growth__grow' }, sway);
      };
      const leaf = (p, ang, dir, s, l) => {
        const reach = (d) => p.x + Math.cos(((ang + 58 * d) * Math.PI) / 180) * 44 * s;
        if (inContent(reach(dir)) && !inContent(reach(-dir))) dir = -dir;   // turn it outward
        const g = make('g', { class: 'growth__leaf', transform: `translate(${p.x} ${p.y}) rotate(${ang + 58 * dir})` }, svg);
        const grow = sprout(g, 5.5);
        const t = `scale(${s})`;
        make('path', { d: 'M0 0C9 -11 27 -13 40 0C27 13 9 11 0 0Z', transform: t }, grow);
        make('path', { d: 'M0 0C9 -11 27 -13 40 0Z', class: 'shade', transform: t }, grow);
        make('path', { d: 'M2 0Q20 -1.5 37 0M11 -.4l5 -5M19 -.7l6 -5.5M27 -.5l5 -4M13 -.4l5 4.6M22 -.6l5 4.6', class: 'rib', transform: t }, grow);
        nodes.push({ el: g, l, out: false });
      };
      let flip = side;
      for (let l = o.start + rand() * 50, k = o.k0; l < total - 30; l += o.gap * (0.8 + rand() * 0.4), k++) {
        const p = stem.getPointAtLength(l);
        const q = stem.getPointAtLength(Math.min(total, l + 2));
        const ang = (Math.atan2(q.y - p.y, q.x - p.x) * 180) / Math.PI;
        if (k % 5 === 3) {
          // A sparkle beside the stem, on the outer side
          const g = make('g', { class: 'growth__spark', transform: `translate(${p.x + 26 * out * fit} ${p.y - 10})` }, svg);
          const grow = sprout(g, 2.4);
          make('path', { d: 'M0 -9C1 -2 2 -1 9 0C2 1 1 2 0 9C-1 2 -2 1 -9 0C-2 -1 -1 -2 0 -9Z', transform: `scale(${(0.7 + rand() * 0.5) * fit})` }, grow);
          nodes.push({ el: g, l: l + 20, out: false });
        } else {
          const s = (0.8 + rand() * 0.5) * fit;
          leaf(p, ang, flip, s, l + 8);
          if (k % 5 === 0) leaf(p, ang, -flip, s * 0.68, l + 34);   // a smaller partner leaf
          flip = -flip;
        }
      }
      const tip = make('g', { class: 'growth__tip' }, svg);
      make('circle', { r: 9, class: 'halo' }, tip);
      make('circle', { r: 3 }, tip);
      return { stem, total, samples, nodes, tip, lag: o.lag };
    }

    function build() {
      seed = 7;
      top = hero.offsetTop + hero.offsetHeight - 24;
      const H = Math.max(0, main.offsetHeight - top - 40);
      const W = wrap.clientWidth;
      // Margin = space beside the content column
      const r = ref.getBoundingClientRect();
      const M = r.left + (parseFloat(getComputedStyle(ref).paddingLeft) || 0);
      wrap.style.top = top + 'px';
      wrap.style.height = H + 'px';
      svg.setAttribute('width', W); svg.setAttribute('height', H);
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      svg.replaceChildren();
      const grad = make('linearGradient', { id: 'growth-stem', gradientUnits: 'userSpaceOnUse', x1: 0, y1: 0, x2: 0, y2: Math.max(1, H) }, make('defs', {}, svg));
      [[0, '#D3C1A9'], [0.35, '#CFA391'], [0.7, '#D3C1A9'], [1, '#CFA391']].forEach(([o, c]) => make('stop', { offset: o, 'stop-color': c }, grad));
      vines = [];
      built = false;
      if (H < 200 || M < MIN_MARGIN) return;
      const amp = Math.min(M * 0.06, 9);                 // barely leaves the vertical
      const cx = M * 0.42;                                // sits toward the outer edge, clear of carousel arrows
      // The two sides are siblings, not mirror images: different bend length and phase,
      // leaf spacing, set-in from the edge, and the right one trails the left a little.
      vines.push(buildVine(cx, amp, H, 1, M, W, { step: 620, phase: 0, start: 50, gap: 150, k0: 0, lag: 0 }));
      seed = 31;
      vines.push(buildVine(W - M * 0.47, amp * 1.3, H, -1, M, W, { step: 530, phase: 1, start: 120, gap: 172, k0: 2, lag: 90 }));
      built = true;
    }

    const lengthAt = (v, y) => {
      if (y <= 0) return 0;
      const s = v.samples;
      if (y >= s[s.length - 1].y) return v.total;
      let lo = 0, hi = s.length - 1;
      while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (s[mid].y < y) lo = mid; else hi = mid; }
      const a = s[lo], b = s[hi];
      return a.l + (b.l - a.l) * ((y - a.y) / Math.max(1, b.y - a.y));
    };

    function paint() {
      if (!built) return;
      for (const v of vines) {
        const drawn = lengthAt(v, depth - v.lag);
        v.stem.style.strokeDashoffset = String(v.total - drawn);
        const p = v.stem.getPointAtLength(Math.max(0, drawn));
        v.tip.setAttribute('transform', `translate(${p.x} ${p.y})`);
        v.tip.style.opacity = drawn > 2 && drawn < v.total - 2 ? '1' : '0';
        for (const nd of v.nodes) {
          const out = drawn >= nd.l;
          if (out !== nd.out) { nd.out = out; nd.el.classList.toggle('is-out', out); }
        }
      }
    }

    const fullDepth = () => main.offsetHeight;
    const targetDepth = () => Math.max(0, window.scrollY + window.innerHeight * 0.75 - top);

    function update() {
      if (!built) return;
      if (reduceMotion.matches) { spring.set(fullDepth()); return; }
      spring.to(targetDepth(), { damping: 1, response: 0.9 });
    }

    let raf = 0;
    const rebuild = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        spring.stop();
        build();
        if (!built) return;
        if (reduceMotion.matches) depth = fullDepth();
        paint();
        update();
      });
    };
    window.addEventListener('scroll', update, { passive: true });
    reduceMotion.addEventListener('change', rebuild);
    new ResizeObserver(rebuild).observe(main);
    rebuild();
  }

  /* ------------------------------------------------------------------------
     Portfolio — each logo opens a company dialog that grows out of the logo
     and returns into it. "More from the portfolio" swaps companies in place
     with a short cross-fade, and keeps the strip in step underneath.
     ------------------------------------------------------------------------ */
  function initCompanies(dialog) {
    // One component, two uses: portfolio companies (default) and campus partners (data-kind="partner")
    const scope = $(dialog.dataset.scope || '#portfolio');
    const partner = dialog.dataset.kind === 'partner';
    const T = partner
      ? { kind: 'Campus partner', empty: 'A full partner profile is on its way.', page: 'View partner page', soon: 'Partner page coming soon' }
      : { kind: 'Portfolio company', empty: 'A full company profile is on its way.', page: 'View company page', soon: 'Company page coming soon' };
    let data;
    try { data = JSON.parse($(`#${dialog.dataset.source || 'portfolio-data'}`).textContent); } catch (err) { return; }
    if (!scope) return;
    const bySlug = new Map(data.map((c) => [c.slug, c]));
    const logos = new Map($$('[data-company]', scope).map((b) => [b.dataset.company, b]));
    const panel = $('[data-co-panel]', dialog);
    const content = $('[data-co-content]', dialog);
    const el = (k) => $(`[data-co-${k}]`, dialog);
    const logoImg = el('logo'), sectorEl = el('sector'), nameEl = el('name'), metaEl = el('meta');
    const summaryEl = el('summary'), postsEl = el('posts'), emptyEl = el('empty'), othersEl = el('others'), pageEl = el('page');
    const siteEl = el('site'), siteLabel = el('site-label');
    const strip = $('[data-strip]', scope);
    const PANEL = '#FAFAFA';
    let origin = null, current = null, anim = null, contentAnim = null, swapAnim = null, closing = false;
    const ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';

    // "More from the portfolio": one chip per company, built once from the strip's logos
    data.forEach((c) => {
      const src = logos.get(c.slug) && $('img', logos.get(c.slug));
      if (!src) return;
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'co-other'; b.dataset.slug = c.slug;
      const img = document.createElement('img');
      img.src = src.getAttribute('src'); img.alt = c.name; img.decoding = 'async';
      b.append(img); li.append(b); othersEl.append(li);
      b.addEventListener('click', () => swap(c.slug));
    });

    // Arrows page the chip row; they dim at either end
    const coPrev = $('[data-co-prev]', dialog), coNext = $('[data-co-next]', dialog);
    const syncChipArrows = () => {
      const max = othersEl.scrollWidth - othersEl.clientWidth - 6;
      coPrev.disabled = othersEl.scrollLeft <= 6;
      coNext.disabled = othersEl.scrollLeft >= max;
    };
    const page = (dir) => othersEl.scrollBy({ left: dir * othersEl.clientWidth, behavior: reduceMotion.matches ? 'auto' : 'smooth' });
    coPrev.addEventListener('click', () => page(-1));
    coNext.addEventListener('click', () => page(1));
    othersEl.addEventListener('scroll', syncChipArrows, { passive: true });
    new ResizeObserver(syncChipArrows).observe(othersEl);

    const esc = (t) => String(t).replace(/[&<>"]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
    function fill(c) {
      current = c;
      logoImg.src = $('img', logos.get(c.slug)).getAttribute('src');
      sectorEl.textContent = c.sector || T.kind;
      nameEl.textContent = c.name;
      metaEl.textContent = [c.location, c.founded && `Founded ${c.founded}`].filter(Boolean).join(' · ');
      metaEl.hidden = !metaEl.textContent;
      summaryEl.textContent = c.summary || T.empty;
      siteEl.hidden = !c.website;
      if (c.website) {
        siteEl.href = c.website;
        siteLabel.textContent = new URL(c.website).hostname.replace(/^www\./, '');
        siteEl.setAttribute('aria-label', `${c.name} website (opens in a new tab)`);
      }
      const posts = c.posts || [];
      postsEl.innerHTML = posts.map((p) => {
        const ext = /^https?:/.test(p.href);
        const when = p.date ? new Date(p.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
        const sub = [p.kind, when].filter(Boolean).join(' · ');
        return `<li><a class="co-post" href="${esc(p.href)}"${ext ? ' target="_blank" rel="noopener"' : ''}><span><strong>${esc(p.title)}</strong>${sub ? `<small>${esc(sub)}</small>` : ''}</span>${ARROW}</a></li>`;
      }).join('');
      emptyEl.hidden = posts.length > 0;
      if (c.page) {
        pageEl.href = c.page; pageEl.textContent = T.page;
        pageEl.removeAttribute('aria-disabled'); pageEl.classList.remove('is-disabled');
      } else {
        pageEl.href = '#'; pageEl.textContent = T.soon;
        pageEl.setAttribute('aria-disabled', 'true'); pageEl.classList.add('is-disabled');
      }
      $$('.co-other', othersEl).forEach((b) => {
        const on = b.dataset.slug === c.slug;
        b.setAttribute('aria-current', on ? 'true' : 'false');
        if (on) {                                         // keep the current chip in view without scrolling the page
          const l = b.offsetLeft - othersEl.offsetLeft, r = l + b.offsetWidth;
          if (l < othersEl.scrollLeft) othersEl.scrollLeft = Math.max(0, l - 4);
          else if (r > othersEl.scrollLeft + othersEl.clientWidth) othersEl.scrollLeft = r - othersEl.clientWidth + 4;
        }
      });
      syncChipArrows();
    }

    function fromOrigin() {
      const c = origin.getBoundingClientRect();
      const p = panel.getBoundingClientRect();
      const dx = (c.left + c.width / 2) - (p.left + p.width / 2);
      const dy = (c.top + c.height / 2) - (p.top + p.height / 2);
      return `translate(${dx}px, ${dy}px) scale(${c.width / p.width}, ${c.height / p.height})`;
    }

    function open(btn) {
      const c = bySlug.get(btn.dataset.company);
      if (!c) return;
      if (anim) anim.cancel();
      if (contentAnim) contentAnim.forEach((a) => a.cancel());
      closing = false;
      origin = btn;
      dialog.classList.remove('is-closing');
      dialog.showModal();
      fill(c);
      panel.scrollTop = 0;
      if (reduceMotion.matches) {
        anim = panel.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 180, easing: 'ease-out' });
        return;
      }
      anim = panel.animate([
        { transform: fromOrigin(), backgroundColor: '#FFFFFF', borderRadius: '16px' },
        { transform: 'none', backgroundColor: PANEL, borderRadius: '24px' },
      ], { duration: 520, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
      // Content arrives just behind the surface, so text is never seen stretched
      contentAnim = [...panel.children].map((child) => child.animate(
        [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }],
        { duration: 320, delay: 150, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'backwards' },
      ));
    }

    // Switch company inside the open dialog: content dips out, refills, rises back
    function swap(slug) {
      const c = bySlug.get(slug);
      if (!c || c === current || closing) return;
      origin = logos.get(slug);
      if (strip) strip.dispatchEvent(new CustomEvent('strip:reveal', { detail: { el: origin, instant: true } }));
      if (swapAnim) swapAnim.cancel();
      if (reduceMotion.matches) { fill(c); return; }
      swapAnim = content.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 110, easing: 'ease-in', fill: 'forwards' });
      swapAnim.onfinish = () => {
        fill(c);
        swapAnim.cancel();
        swapAnim = content.animate(
          [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }],
          { duration: 260, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' },
        );
      };
    }

    function close(then) {
      if (!dialog.open || closing) return;
      closing = true;
      dialog.classList.add('is-closing');
      if (swapAnim) { swapAnim.cancel(); swapAnim = null; }
      const finish = () => {
        dialog.close();
        dialog.classList.remove('is-closing');
        closing = false; anim = null;
        if (origin && !then) origin.focus({ preventScroll: true });
        if (then) then();
      };
      if (contentAnim) contentAnim.forEach((a) => a.cancel());
      if (reduceMotion.matches || !origin) {
        anim = panel.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 160, easing: 'ease-in', fill: 'forwards' });
      } else if (anim && anim.playState === 'running') {
        anim.reverse();                                   // interrupted mid-open: retrace from here
      } else {
        [...panel.children].forEach((child) => child.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 120, fill: 'forwards' }));
        anim = panel.animate([
          { transform: 'none', backgroundColor: PANEL, borderRadius: '24px' },
          { transform: fromOrigin(), backgroundColor: '#FFFFFF', borderRadius: '16px' },
        ], { duration: 360, easing: 'cubic-bezier(0.64, 0, 0.36, 1)', fill: 'forwards' });
      }
      anim.onfinish = () => {
        [...panel.children].forEach((child) => child.getAnimations().forEach((a) => a.cancel()));
        anim.cancel(); finish();
      };
    }

    logos.forEach((btn) => btn.addEventListener('click', () => open(btn)));
    el('close').addEventListener('click', () => close());
    dialog.addEventListener('cancel', (e) => { e.preventDefault(); close(); });    // Esc
    dialog.addEventListener('click', (e) => { if (e.target === dialog) close(); }); // backdrop
    pageEl.addEventListener('click', (e) => { if (pageEl.getAttribute('aria-disabled') === 'true') e.preventDefault(); });
    $$('[data-co-jump]', dialog).forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault();
      const href = a.getAttribute('href');
      close(() => { location.hash = href; });
    }));
  }

  /* ------------------------------------------------------------------------
     Hero field — the collage's sparkle motif extended into a quiet, living
     background: sparkles and seeds drift up, twinkle one at a time, lean away
     from the pointer, and a tap on empty space pops a small burst.
     One rAF loop, paused off-screen; a still frame under reduced motion.
     ------------------------------------------------------------------------ */
  function initHeroField(hero) {
    const wrap = $('.hero__media-wrap', hero);
    if (!wrap || !document.createElement('canvas').getContext) return;

    const canvas = document.createElement('canvas');
    canvas.className = 'hero-field';
    canvas.setAttribute('aria-hidden', 'true');
    hero.prepend(canvas);
    const ctx = canvas.getContext('2d');
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

    const GREY = '161,161,161';        // the collage sparkles' own stroke colour
    const GLOW = '203,140,124';        // golden glow
    const SEED = '213,174,143';        // bronze
    const RADIUS = 160;                // pointer influence, px

    let W = 0, H = 0, dpr = 1, particles = [], bursts = [];
    let raf = 0, last = 0, visible = true, fieldAlpha = 0;
    let pointer = null;                // { x, y } in canvas px, or null

    const rand = (a, b) => a + Math.random() * (b - a);

    function makeParticle(spawnAnywhere = true) {
      const sparkle = Math.random() < 0.72;
      return {
        sparkle,
        x: rand(0, W),
        y: spawnAnywhere ? rand(0, H) : H + rand(10, 40),
        size: sparkle ? rand(7, 20) : rand(1.1, 2.1),
        color: sparkle ? (Math.random() < 0.18 ? GLOW : GREY) : SEED,
        base: sparkle ? rand(0.32, 0.62) : rand(0.28, 0.5),
        vy: -rand(3, 8),                       // px/s, rising like seeds
        sway: rand(4, 9), swayRate: rand(0.08, 0.16), phase: rand(0, Math.PI * 2),
        rot: rand(0, Math.PI / 4),
        // springs for pointer response (critically damped)
        ox: 0, oy: 0, vox: 0, voy: 0, lit: 0, vlit: 0,
        // twinkle
        nextTwinkle: rand(1, 14), twinkle: 0,
      };
    }

    function resize() {
      const heroRect = hero.getBoundingClientRect();
      const h = wrap.offsetTop + wrap.offsetHeight + 40;   // collage band, fading before the headline
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.round(heroRect.width); H = Math.round(h);
      canvas.style.height = H + 'px';
      canvas.width = W * dpr; canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const target = Math.max(12, Math.min(42, Math.round((W * H) / 24000)));
      while (particles.length < target) particles.push(makeParticle());
      particles.length = target;
      particles.forEach((p) => { if (p.x > W) p.x = rand(0, W); if (p.y > H) p.y = rand(0, H); });
      if (!raf) draw(performance.now() / 1000, 0);
    }

    function sparklePath(size) {
      // Eight rays with an open centre — same construction as the collage SVG sparkles
      const inner = size * 0.32, outer = size;
      for (let i = 0; i < 8; i++) {
        const a = (i * Math.PI) / 4;
        const r2 = i % 2 ? outer * 0.55 : outer;        // diagonals shorter
        ctx.moveTo(Math.cos(a) * inner, Math.sin(a) * inner);
        ctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
      }
    }

    function step(p, t, dt) {
      p.y += p.vy * dt;
      if (p.y < -30) Object.assign(p, makeParticle(false));

      // Pointer: lean away + light up, eased with a critically damped spring
      let tx = 0, ty = 0, tl = 0;
      if (pointer) {
        const px = p.x + Math.sin(t * p.swayRate + p.phase) * p.sway;
        const dx = px - pointer.x, dy = p.y - pointer.y;
        const d = Math.hypot(dx, dy);
        if (d < RADIUS && d > 0.01) {
          const f = (1 - d / RADIUS) ** 2;
          tx = (dx / d) * f * 24; ty = (dy / d) * f * 24; tl = f;
        }
      }
      const k = 110, c = 21;                              // ω ≈ 10.5 → response ≈ 0.6 s, ζ = 1
      p.vox += (-k * (p.ox - tx) - c * p.vox) * dt; p.ox += p.vox * dt;
      p.voy += (-k * (p.oy - ty) - c * p.voy) * dt; p.oy += p.voy * dt;
      p.vlit += (-k * (p.lit - tl) - c * p.vlit) * dt; p.lit += p.vlit * dt;

      // Occasional individual twinkle (never in unison, never a steady pulse)
      if (p.sparkle) {
        p.nextTwinkle -= dt;
        if (p.nextTwinkle <= 0 && p.twinkle === 0) { p.twinkle = 0.0001; p.nextTwinkle = rand(6, 14); }
        if (p.twinkle > 0) { p.twinkle += dt / 0.9; if (p.twinkle >= 1) p.twinkle = 0; }
      }
    }

    function draw(t, dt) {
      ctx.clearRect(0, 0, W, H);
      ctx.lineCap = 'round';
      for (const p of particles) {
        if (dt) step(p, t, dt);
        const x = p.x + Math.sin(t * p.swayRate + p.phase) * p.sway + p.ox;
        const y = p.y + p.oy;
        // fade near the field's top and bottom edges
        const edge = Math.min(1, y / 60, (H - y) / 90);
        if (edge <= 0) continue;
        const tw = p.twinkle > 0 ? Math.sin(p.twinkle * Math.PI) : 0;
        const lit = Math.max(0, Math.min(1, p.lit));
        const alpha = Math.min(1, (p.base + lit * 0.4 + tw * 0.3)) * edge * fieldAlpha;
        ctx.save();
        ctx.translate(x, y);
        if (p.sparkle) {
          ctx.rotate(p.rot + tw * (Math.PI / 4) + lit * 0.35);
          const s = 1 + tw * 0.3 + lit * 0.35;
          ctx.beginPath(); sparklePath(p.size * 0.5 * s);
          ctx.strokeStyle = `rgba(${p.color},${alpha})`;
          ctx.lineWidth = p.size > 14 ? 1.6 : 1.2;
          ctx.stroke();
        } else {
          ctx.beginPath(); ctx.arc(0, 0, p.size * (1 + lit * 0.5), 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${p.color},${alpha})`;
          ctx.fill();
        }
        ctx.restore();
      }
      // Tap bursts: a seed popping — rays open outward and fade
      bursts = bursts.filter((b) => (b.age += dt) < 0.9);
      for (const b of bursts) {
        const e = 1 - (1 - b.age / 0.9) ** 3;            // ease-out cubic
        const a = (1 - b.age / 0.9) * 0.75;
        b.parts.forEach((q) => {
          ctx.save();
          ctx.translate(b.x + Math.cos(q.a) * q.d * e, b.y + Math.sin(q.a) * q.d * e);
          ctx.rotate(q.a + e * 0.6);
          ctx.beginPath(); sparklePath(q.s * (0.6 + e * 0.4));
          ctx.strokeStyle = `rgba(${q.c},${a})`; ctx.lineWidth = 1.2; ctx.stroke();
          ctx.restore();
        });
      }
    }

    function frame(now) {
      const t = now / 1000;
      const dt = Math.min(t - last, 1 / 30); last = t;
      fieldAlpha = Math.min(1, fieldAlpha + dt / 1.2);    // gentle fade-in on load
      draw(t, dt);
      raf = requestAnimationFrame(frame);
    }
    function start() {
      if (raf || reduceMotion.matches || !visible || document.hidden) return;
      last = performance.now() / 1000;
      raf = requestAnimationFrame(frame);
    }
    function stop() { if (raf) cancelAnimationFrame(raf); raf = 0; }
    function sync() {
      if (reduceMotion.matches) { stop(); fieldAlpha = 1; pointer = null; bursts = []; draw(0, 0); return; }
      visible && !document.hidden ? start() : stop();
    }

    // Pointer: fine pointers only (on touch there is no hover to respond to)
    hero.addEventListener('pointermove', (e) => {
      if (!finePointer.matches || reduceMotion.matches) return;
      const r = canvas.getBoundingClientRect();
      pointer = { x: e.clientX - r.left, y: e.clientY - r.top };
    }, { passive: true });
    hero.addEventListener('pointerleave', () => { pointer = null; });

    // Tap / click on empty hero space pops a small burst (never on links or buttons)
    hero.addEventListener('pointerdown', (e) => {
      if (reduceMotion.matches || e.button !== 0 || e.target.closest('a, button, input')) return;
      const r = canvas.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      if (y > H) return;
      const n = 6;
      bursts.push({
        x, y, age: 0,
        parts: Array.from({ length: n }, (_, i) => ({
          a: (i / n) * Math.PI * 2 + rand(-0.25, 0.25),
          d: rand(28, 54), s: rand(3, 6),
          c: Math.random() < 0.34 ? GLOW : GREY,
        })),
      });
      if (bursts.length > 6) bursts.shift();
    });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([en]) => { visible = en.isIntersecting; sync(); }).observe(canvas);
    }
    document.addEventListener('visibilitychange', sync);
    reduceMotion.addEventListener('change', sync);
    new ResizeObserver(resize).observe(wrap);
    resize();
    sync();
  }

  /* About submenu — hover and keyboard focus open it in CSS; the chevron toggles it
     for click and touch. Esc or a click outside closes it. */
  function initNavMenu(menu) {
    const toggle = $('[data-nav-menu-toggle]', menu);
    const list = $('.nav-thread', menu);
    // The thread starts under the chevron and ends level with the last item; each branch curves
    // off it to an item. Measured on every open, as the panel sits differently once scrolled.
    // Layout offsets ignore transforms, so the geometry is right even while the panel is still
    // animating in (measuring the on-screen boxes mid-animation left gaps in the thread).
    const panel = list && list.closest('.nav-menu__panel');
    const measure = () => {
      if (!list) return;
      const last = list.lastElementChild;
      const listLeft = panel.offsetLeft + panel.clientLeft + list.offsetLeft;
      const listTop = panel.offsetTop + panel.clientTop + list.offsetTop;
      const chevronX = toggle.offsetLeft + toggle.offsetWidth / 2;
      const chevronBottom = toggle.offsetTop + toggle.offsetHeight / 2 + 7;
      list.style.setProperty('--tx', `${Math.round(chevronX - listLeft)}px`);
      list.style.setProperty('--up', `${Math.round(listTop - chevronBottom)}px`);
      list.style.setProperty('--len', `${Math.round(listTop + last.offsetTop + last.offsetHeight / 2 - chevronBottom)}px`);
    };
    ['mouseenter', 'focusin'].forEach((type) => menu.addEventListener(type, measure));
    toggle.addEventListener('pointerdown', measure);
    new MutationObserver(measure).observe(menu.closest('[data-header]') || document.body, { attributes: true, attributeFilter: ['class'] });
    window.addEventListener('resize', measure);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
    measure();
    const set = (open) => {
      menu.classList.toggle('is-open', open);
      menu.classList.toggle('is-closed', !open);
      toggle.setAttribute('aria-expanded', String(open));
    };
    toggle.addEventListener('click', (e) => { e.stopPropagation(); set(!menu.classList.contains('is-open')); });
    menu.addEventListener('keydown', (e) => { if (e.key === 'Escape') { set(false); toggle.focus(); } });
    // Leaving hands control back to hover/focus
    menu.addEventListener('mouseleave', () => { if (!menu.contains(document.activeElement)) menu.classList.remove('is-open', 'is-closed'); toggle.setAttribute('aria-expanded', 'false'); });
    menu.addEventListener('mouseenter', () => { if (!menu.classList.contains('is-closed')) toggle.setAttribute('aria-expanded', 'true'); });
    menu.addEventListener('focusout', (e) => { if (!menu.contains(e.relatedTarget)) { menu.classList.remove('is-open', 'is-closed'); toggle.setAttribute('aria-expanded', 'false'); } });
    document.addEventListener('click', (e) => { if (!menu.contains(e.target) && menu.classList.contains('is-open')) { menu.classList.remove('is-open', 'is-closed'); toggle.setAttribute('aria-expanded', 'false'); } });
  }
  $$('[data-nav-menu]').forEach(initNavMenu);

  const header = $('[data-header]');
  if (header) { initHeader(header); initSearch(header); initMobileMenu(header); }
  $$('[data-strip]').forEach(initStrip);
  initReveal();
  const year = $('[data-year]'); if (year) year.textContent = new Date().getFullYear();
})();
