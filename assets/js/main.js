/* ==========================================================================
   الدكتور عبدالله اليابس للمحاماة — الحركة والتفاعل
   GSAP + ScrollTrigger + Lenis (محلية). تحسين تدريجي: المحتوى كله في HTML.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document, root = doc.documentElement, body = doc.body;
  root.classList.add('ready');
  var RM = root.classList.contains('rm');
  var HAS = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
  var ANIM = HAS && !RM;
  if (!HAS && !RM) root.classList.add('static');

  var page = (body.className.match(/\bp-([\w-]+)/) || [])[1] || '';
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var mq = function (q) { return window.matchMedia(q).matches; };
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var lenis = null;
  var bootT = Date.now();
  var D0 = root.classList.contains('is-arriving') ? 0.6 : 0.1;
  var d0 = function () { return Date.now() - bootT < 1500 ? D0 : 0; };

  /* ---------------------------------------------------------------- دائما */
  year();
  menu();
  header();
  transitions();
  composer();

  if (!ANIM) return;

  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.config({ ignoreMobileResize: true });
  lenis = smooth();
  anchors();
  splitHeadings();
  lines();
  if (page === 'home') heroIntro();
  reveals();
  frames();
  stones();
  colonnade();
  icons();

  var fontsReady = doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve();
  fontsReady.then(function () { ScrollTrigger.refresh(); handleHash(); });

  /* ================================================================ الأساسيات */
  function year() { $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); }); }

  function header() {
    var h = $('.hdr'), bar = $('.hdr__progress');
    if (!h) return;
    var queued = false;
    function update() {
      queued = false;
      var y = window.scrollY || root.scrollTop;
      h.classList.toggle('is-solid', y > 12);
      if (bar) {
        var max = root.scrollHeight - window.innerHeight;
        bar.style.transform = 'scaleX(' + (max > 0 ? clamp(y / max, 0, 1) : 0) + ')';
      }
    }
    window.addEventListener('scroll', function () { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  function menu() {
    var btn = $('.burger'), m = $('#menu');
    if (!btn || !m) return;
    function set(open) {
      root.classList.toggle('menu-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'إغلاق القائمة' : 'فتح القائمة');
      if (open) m.removeAttribute('inert'); else m.setAttribute('inert', '');
      if (lenis) { if (open) lenis.stop(); else lenis.start(); }
    }
    btn.addEventListener('click', function () { set(!root.classList.contains('menu-open')); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && root.classList.contains('menu-open')) { set(false); btn.focus(); } });
    $$('a', m).forEach(function (a) { a.addEventListener('click', function () { set(false); }); });
    window.addEventListener('resize', function () { if (window.innerWidth > 1080 && root.classList.contains('menu-open')) set(false); });
  }

  /* الانتقال بين الصفحات: لوح عاجي يصعد وعليه العمود (CSS) */
  function transitions() {
    if (RM) return;
    doc.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a') : null;
      if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if ((a.target && a.target !== '_self') || a.hasAttribute('download')) return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(mailto|tel):/i.test(href)) return;
      var url = new URL(a.href, location.href);
      if (url.origin !== location.origin) return;
      if (url.pathname === location.pathname && url.hash) return;
      e.preventDefault();
      try { sessionStorage.setItem('ya-nav', '1'); } catch (err) { /* بلا ستارة في الصفحة التالية */ }
      root.classList.add('is-leaving');
      setTimeout(function () { location.href = url.href; }, 600);
    });
    window.addEventListener('pageshow', function (e) { if (e.persisted) root.classList.remove('is-leaving', 'is-arriving'); });
  }

  /* نموذج واتساب: يبني الرسالة ويعرضها كما ستصل، ثم يفتح المحادثة */
  function composer() {
    var f = $('#wa-form');
    if (!f) return;
    var bubble = $('#wa-bubble', f), hidden = $('#wa-text', f), base = hidden.value;
    function build() {
      var name = $('#wa-name', f).value.trim(), msg = $('#wa-msg', f).value.trim();
      var type = $('#wa-type', f).value, time = $('input[name="time"]:checked', f);
      var text = 'السلام عليكم،';
      if (name) text += '\nمعكم ' + name + '.';
      text += type ? '\nأرغب في استشارة بخصوص: ' + type + '.' : '\nأرغب في حجز استشارة قانونية.';
      if (time) text += '\nالوقت المناسب للتواصل: ' + time.value + '.';
      if (msg) text += '\n' + msg;
      return (name || msg || type || time) ? text : base;
    }
    function update() { var t = build(); bubble.textContent = t; hidden.value = t; }
    f.addEventListener('input', update);
    f.addEventListener('change', update);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      update();
      window.open(f.getAttribute('action') + '?text=' + encodeURIComponent(hidden.value), '_blank', 'noopener');
    });
  }

  /* ================================================================ التمرير */
  function smooth() {
    if (typeof window.Lenis === 'undefined') return null;
    var l = new window.Lenis({ duration: 1.1, smoothWheel: true });
    l.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (t) { l.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
    window.__lenis = l;
    return l;
  }
  function goTo(target, immediate) {
    var off = ($('.hdr') ? $('.hdr').offsetHeight : 80) + 18;
    if (target === 0) { if (lenis) lenis.scrollTo(0, { immediate: !!immediate }); else window.scrollTo(0, 0); return; }
    if (lenis) lenis.scrollTo(target, { offset: -off, immediate: !!immediate, duration: 1.3 });
    else window.scrollTo(0, target.getBoundingClientRect().top + window.scrollY - off);
  }
  function anchors() {
    doc.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href*="#"]') : null;
      if (!a || e.defaultPrevented) return;
      var url = new URL(a.href, location.href);
      if (url.pathname !== location.pathname || !url.hash) return;
      var id = decodeURIComponent(url.hash.slice(1));
      var target = id === 'top' ? 0 : doc.getElementById(id);
      if (target === null) return;
      e.preventDefault();
      goTo(target);
      history.replaceState(null, '', id === 'top' ? location.pathname : url.hash);
    });
  }
  function handleHash() {
    if (!location.hash || location.hash === '#top') return;
    var t = doc.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (t) goTo(t, true);
  }

  /* ================================================================ النصوص */
  function wrapWords(el, cls, inner) {
    var walker = doc.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function (node) {
      var frag = doc.createDocumentFragment();
      node.nodeValue.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(doc.createTextNode(part)); return; }
        var w = doc.createElement('span');
        w.className = cls;
        if (inner) { var i = doc.createElement('span'); i.className = inner; i.textContent = part; w.appendChild(i); }
        else w.textContent = part;
        frag.appendChild(w);
      });
      node.parentNode.replaceChild(frag, node);
    });
    return $$(inner ? '.' + inner : '.' + cls, el);
  }
  function splitHeadings() {
    $$('[data-words]').forEach(function (el) {
      var words = wrapWords(el, 'w', 'wi');
      gsap.set(words, { yPercent: 115 });
      el.style.visibility = 'visible';
    });
  }
  /* جملة الشريك: تضيء كلماتها مع التمرير */
  function lines() {
    $$('[data-lines]').forEach(function (el) {
      var words = wrapWords(el, 'lw');
      gsap.fromTo(words, { opacity: 0.14 }, { opacity: 1, ease: 'none', stagger: 0.05,
        scrollTrigger: { trigger: el, start: 'top 80%', end: 'bottom 55%', scrub: 0.5 } });
    });
  }
  function reveals() {
    var outside = function (el) { return !el.closest('.hero'); };
    ScrollTrigger.batch($$('[data-rise]').filter(outside), {
      start: 'top 90%', once: true,
      onEnter: function (els) { gsap.to(els, { opacity: 1, y: 0, duration: 1, ease: 'power3.out', stagger: 0.09, delay: d0(), overwrite: true }); }
    });
    $$('[data-words]').filter(outside).forEach(function (el) {
      var words = $$('.wi', el);
      ScrollTrigger.create({ trigger: el, start: 'top 90%', once: true,
        onEnter: function () { gsap.to(words, { yPercent: 0, duration: 1.1, ease: 'power4.out', stagger: 0.05, delay: d0() }); } });
    });
    $$('[data-stagger]').forEach(function (g) {
      ScrollTrigger.create({ trigger: g, start: 'top 88%', once: true,
        onEnter: function () { gsap.to(g.children, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', stagger: 0.07, delay: d0() }); } });
    });
    $$('.ftr__logo').forEach(function (el) {
      ScrollTrigger.create({ trigger: el, start: 'top 90%', once: true, onEnter: function () { el.classList.add('is-in'); } });
    });
    $$('.phero__pillar').forEach(function (p) {
      gsap.fromTo(p, { yPercent: 30, opacity: 0 }, { yPercent: 0, opacity: 0.16, duration: 1.6, ease: 'power3.out', delay: d0() + 0.2 });
    });
  }

  /* ================================================================ الزخارف */
  /* إطار الصورة: القاعدة ثم التاج، ثم تنكشف الصورة من الأسفل */
  function frames() {
    $$('[data-frame]').forEach(function (f) {
      var caps = $$('.frame__cap i', f), base = $$('.frame__base i', f), img = $('.frame__img', f);
      var tl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out' } });
      tl.from(base.reverse(), { scaleX: 0, duration: 0.6, stagger: 0.1 })
        .from(img, { clipPath: 'inset(100% 0 0 0)', duration: 1.1, ease: 'power3.inOut' }, 0.25)
        .from(caps.reverse(), { scaleX: 0, y: -18, duration: 0.6, stagger: 0.1 }, 0.9);
      ScrollTrigger.create({ trigger: f, start: 'top 80%', once: true, onEnter: function () { tl.play(); } });
    });
  }
  /* الصفات المهنية: حجارة تستقر بالتتابع كأحجار الكتلة الكوفية */
  function stones() {
    $$('[data-stones]').forEach(function (g) {
      var s = $$('.stone', g);
      gsap.set(s, { opacity: 0, y: -40 });
      ScrollTrigger.create({ trigger: g, start: 'top 80%', once: true, onEnter: function () {
        gsap.to(s.slice().reverse(), { opacity: 1, y: 0, duration: 0.7, ease: 'back.out(1.4)', stagger: 0.16 });
      } });
    });
  }
  /* الخدمات: الأعمدة تقوم من قواعدها بالتتابع، ثم تستقر تيجانها */
  function colonnade() {
    $$('[data-colonnade]').forEach(function (g) {
      var cols = $$('.col', g);
      cols.forEach(function (c) {
        gsap.set($('.col__body', c), { scaleY: 0, transformOrigin: '50% 100%' });
        gsap.set($$('.col__cap i', c), { opacity: 0, y: -30 });
        gsap.set($$('.col__base i', c), { scaleX: 0 });
        gsap.set($$('.col__body > *', c), { opacity: 0 });
      });
      ScrollTrigger.create({ trigger: g, start: 'top 78%', once: true, onEnter: function () {
        cols.forEach(function (c, i) {
          var t = i * 0.12;
          var tl = gsap.timeline({ delay: t, defaults: { ease: 'power3.out' } });
          tl.to($$('.col__base i', c).reverse(), { scaleX: 1, duration: 0.45, stagger: 0.08 })
            .to($('.col__body', c), { scaleY: 1, duration: 0.8, ease: 'power3.inOut' }, 0.2)
            .to($$('.col__cap i', c).reverse(), { opacity: 1, y: 0, duration: 0.55, ease: 'back.out(1.6)', stagger: 0.08 }, 0.85)
            .to($$('.col__body > *', c), { opacity: 1, duration: 0.5, stagger: 0.06 }, 0.95)
            .to($$('.col__ico use', c), { strokeDashoffset: 0, autoRound: false, duration: 1.1, ease: 'power2.inOut' }, 1)
            .set([$('.col__body', c)].concat($$('.col__cap i, .col__base i', c)), { clearProps: 'transform' });
        });
      } });
    });
  }
  function icons() {
    $$('.srow__ico').forEach(function (ic) {
      ScrollTrigger.create({ trigger: ic, start: 'top 88%', once: true, onEnter: function () {
        gsap.to($$('use', ic), { strokeDashoffset: 0, autoRound: false, duration: 1.3, ease: 'power2.inOut' });
      } });
    });
  }

  /* ================================================================ الرئيسية */
  /* يبنى العمود: القاعدة، فالعمودان الذهبيان، فأحجار الكتلة الكوفية من الأسفل، فالتاج.
     ثم يكتب القلم الاسم من اليمين وتتساقط زخارفه، ثم تنزلق السطور تحته.
     ومع التمرير ينتقل العمود والاسم معا إلى الترويسة، كل إلى مكانه في الشعار الأفقي. */
  function heroIntro() {
    var fp = $('.fly--pillar'), fn = $('.fly--name');
    var sp = $('.hero__slot--pillar'), sn = $('.hero__slot--name');
    var bp = $('.hdr .brand__pillar'), bn = $('.hdr .brand__name'), hdr = $('.hdr');
    if (!fp || !fn || !sp || !sn || !bp || !bn) return;
    var svgP = $('svg', fp), svgN = $('svg', fn), under = $('.hero__under');
    var bars = $$('.yp-bar', svgP), cols = $$('.yp-col', svgP), stonesEls = $$('.yp-stone', svgP);
    var letters = $$('.yn-l', svgN), orns = $$('.yn-o', svgN), strokes = $$('.wm', svgN);
    var underParts = under ? $$('.yu', under) : [];
    var rises = $$('.hero [data-rise]');
    var seen = root.classList.contains('intro-seen') || window.scrollY > 40;
    var flies = [{ el: fp, slot: sp, target: bp, base: null }, { el: fn, slot: sn, target: bn, base: null }];

    function place() {
      flies.forEach(function (f) {
        var r = f.slot.getBoundingClientRect();
        f.base = { left: r.left, top: r.top + window.scrollY, w: r.width, h: r.height };
        f.el.style.width = r.width + 'px'; f.el.style.height = r.height + 'px';
        f.el.style.left = r.left + 'px'; f.el.style.top = f.base.top + 'px';
      });
    }
    place();
    root.classList.add('fly-on');
    ScrollTrigger.addEventListener('refreshInit', function () { gsap.set([fp, fn], { x: 0, y: 0, scale: 1 }); place(); });

    var dock = ScrollTrigger.create({
      trigger: '.hero', start: 'top top',
      end: function () { return '+=' + Math.max(260, window.innerHeight * 0.6); },
      onUpdate: dockTo, onRefresh: dockTo
    });
    function dockTo(self) {
      var st = self || dock;
      var p = st.progress, e = p < 0.5 ? 2 * p * p : 1 - Math.pow(2 - 2 * p, 2) / 2;
      var s = clamp(window.scrollY - st.start, 0, st.end - st.start);
      flies.forEach(function (f, k) {
        var b = f.target.getBoundingClientRect(), base = f.base;
        var ek = clamp(e * (k ? 1 : 1.08), 0, 1);             /* العمود يسبق الاسم قليلا */
        gsap.set(f.el, { x: base.left * (1 - ek) + b.left * ek - base.left, y: (base.top - s) * (1 - ek) + b.top * ek - base.top,
          scale: 1 - ek + ek * b.width / base.w });
      });
      if (under) gsap.set(under, { opacity: clamp(1 - p * 2.4, 0, 1) });
    }

    var tl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out' }, onComplete: finish });
    if (!seen) {
      var T0 = 2.05, SWEEP = 2.5;
      strokes.forEach(function (m) {
        var L = m.getTotalLength();
        m.style.strokeDasharray = L + ' ' + (L + 80);
        m.style.strokeDashoffset = L;
        m._L = L;
      });
      gsap.set(orns, { opacity: 0 });
      gsap.set(underParts, { opacity: 0, y: 14 });
      /* القاعدة: الشريطان السفليان يمتدان من الوسط، الأدنى أولا */
      tl.fromTo(bars[3], { scaleX: 0, transformOrigin: '50% 50%' }, { scaleX: 1, duration: 0.55, ease: 'power2.inOut' }, 0.15)
        .fromTo(bars[2], { scaleX: 0, transformOrigin: '50% 50%' }, { scaleX: 1, duration: 0.5, ease: 'power2.inOut' }, 0.32)
        /* العمودان الذهبيان يقومان من القاعدة */
        .fromTo(cols, { scaleY: 0, transformOrigin: '50% 100%' }, { scaleY: 1, duration: 0.8, ease: 'power3.inOut', stagger: 0.06 }, 0.5);
      /* أحجار الكتلة الكوفية تستقر من الأسفل إلى الأعلى */
      stonesEls.forEach(function (s, k) {
        tl.fromTo(s, { opacity: 0, y: -46 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 0.82 + k * 0.1);
      });
      /* التاج ينزل على العمودين */
      tl.fromTo(bars[1], { opacity: 0, y: -44 }, { opacity: 1, y: 0, duration: 0.55, ease: 'back.out(1.5)' }, 1.52)
        .fromTo(bars[0], { opacity: 0, y: -60 }, { opacity: 1, y: 0, duration: 0.6, ease: 'back.out(1.5)' }, 1.64);
      /* القلم: كل خط يبدأ حين تبلغ الكتابة موضعه من اليمين، ومدته بطوله */
      strokes.forEach(function (m) {
        var t = T0 + parseFloat(m.getAttribute('data-t')) * SWEEP;
        var d = clamp(m._L / 520, 0.14, 0.7);
        tl.to(m, { strokeDashoffset: 0, duration: d, ease: 'sine.inOut' }, t);
      });
      /* الزخارف والنقاط تسقط بعد مرور القلم بها */
      orns.forEach(function (o) {
        var t = T0 + parseFloat(o.getAttribute('data-t')) * SWEEP + 0.22;
        tl.fromTo(o, { opacity: 0, y: -14, scale: 0.4, transformOrigin: '50% 50%' },
          { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: 'back.out(2)' }, t);
      });
      tl.to(underParts, { opacity: 1, y: 0, duration: 0.8, stagger: 0.12 }, T0 + SWEEP - 0.1)
        .to(rises, { opacity: 1, y: 0, duration: 1, stagger: 0.1 }, T0 + SWEEP - 0.3)
        .to(hdr, { opacity: 1, duration: 0.8, ease: 'power1.out' }, T0 + SWEEP + 0.2);

      var evs = ['wheel', 'touchstart', 'keydown', 'pointerdown'];
      var skip = function () { tl.timeScale(5); evs.forEach(function (ev) { window.removeEventListener(ev, skip); }); };
      evs.forEach(function (ev) { window.addEventListener(ev, skip, { passive: true }); });
    } else {
      gsap.set(underParts, { opacity: 1 });
      tl.fromTo([svgP, svgN, under].filter(Boolean), { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.9, stagger: 0.08 }, 0.05)
        .to(rises, { opacity: 1, y: 0, duration: 0.9, stagger: 0.08 }, 0.25)
        .set(hdr, { opacity: 1 }, 0);
    }

    function finish() {
      letters.forEach(function (l) { l.removeAttribute('mask'); });
      gsap.set(bars.concat(cols, stonesEls, orns, underParts), { clearProps: 'transform' });
      dockTo();
      try { sessionStorage.setItem('ya-intro', '1'); } catch (e) { /* تعاد الافتتاحية */ }
    }

    var fontsReady = doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve();
    var wait = new Promise(function (r) { setTimeout(r, 700); });
    Promise.race([fontsReady, wait]).then(function () {
      place();
      gsap.delayedCall(root.classList.contains('is-arriving') ? 0.55 : 0, function () { tl.play(); });
    });
  }
})();
