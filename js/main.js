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

    /* Keyboard — repeated presses step on from where the strip is *heading*,
       not where it happens to be mid-flight, so ten presses move ten logos. */
    let keyTarget = null;
    viewport.addEventListener('pointerdown', () => { keyTarget = null; });
    viewport.addEventListener('wheel', () => { keyTarget = null; }, { passive: true });
    viewport.addEventListener('keydown', (e) => {
      if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(e.key)) return;
      e.preventDefault();
      const from = spring.running && keyTarget !== null ? keyTarget : nearestSnap(x);
      const i = snaps.indexOf(from);
      let next;
      if (e.key === 'Home') next = snaps[0];
      else if (e.key === 'End') next = snaps[snaps.length - 1];
      else next = snaps[Math.max(0, Math.min(snaps.length - 1, i + (e.key === 'ArrowRight' ? 1 : -1)))];
      keyTarget = next;
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
  const svcDialog = $('[data-svc-dialog]');
  if (svcDialog && svcDialog.showModal) initServices(svcDialog);

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
    const CARD_COLOR = getComputedStyle(document.documentElement).getPropertyValue('--golden-glow').trim() || '#CB8C7C';
    let origin = null, anim = null, contentAnim = null, closing = false;

    function fromCard() {
      const c = origin.getBoundingClientRect();
      const p = panel.getBoundingClientRect();
      const dx = (c.left + c.width / 2) - (p.left + p.width / 2);
      const dy = (c.top + c.height / 2) - (p.top + p.height / 2);
      return `translate(${dx}px, ${dy}px) scale(${c.width / p.width}, ${c.height / p.height})`;
    }

    function open(card) {
      const tpl = document.getElementById('svc-' + card.dataset.service);
      if (!tpl) return;
      if (anim) anim.cancel();
      if (contentAnim) contentAnim.forEach((a) => a.cancel());
      closing = false;
      origin = card;
      groupEl.textContent = tpl.dataset.group;
      titleEl.innerHTML = tpl.dataset.title;
      body.replaceChildren(tpl.content.cloneNode(true));
      cta.textContent = tpl.dataset.cta;
      cta.setAttribute('href', tpl.dataset.href);
      dialog.classList.remove('is-closing');
      dialog.showModal();
      panel.scrollTop = 0;

      if (reduceMotion.matches) {
        anim = panel.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 180, easing: 'ease-out' });
        return;
      }
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

    $$('.svc-card').forEach((card) => card.addEventListener('click', () => open(card)));
    $('[data-svc-close]', dialog).addEventListener('click', () => close());
    dialog.addEventListener('cancel', (e) => { e.preventDefault(); close(); });   // Esc
    dialog.addEventListener('click', (e) => { if (e.target === dialog) close(); }); // backdrop
    cta.addEventListener('click', (e) => {
      e.preventDefault();
      const href = cta.getAttribute('href');
      close(() => { location.hash = href; });
    });
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

  const header = $('[data-header]');
  if (header) { initHeader(header); initSearch(header); initMobileMenu(header); }
  $$('[data-strip]').forEach(initStrip);
  initReveal();
  const year = $('[data-year]'); if (year) year.textContent = new Date().getFullYear();
})();
