// Languages, themes, calm sound, smart search and reveal. No network, no cookies; choices kept in localStorage.
(function () {
  var d = document, root = d.documentElement, $ = function (s) { return d.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(d.querySelectorAll(s)); };
  var I = JSON.parse($('#i18n').textContent);
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var lang = 'en';

  function ui(k) { return (I.ui[lang] || {})[k] || I.ui.en[k] || k; }

  // ---- language
  function setLang(l) {
    if (!I.ui[l]) l = 'en';
    lang = l; root.lang = l; root.dir = l === 'ar' ? 'rtl' : 'ltr';
    $$('[data-u]').forEach(function (el) { el.textContent = ui(el.dataset.u); });
    $$('[data-ua]').forEach(function (el) {
      var p = el.dataset.ua.split(':'); el.setAttribute(p[0], ui(p[1]));
    });
    $$('[data-k]').forEach(function (el) {
      if (el.dataset.en === undefined) el.dataset.en = el.textContent;
      var t = (I.t[l] || {})[el.dataset.k];
      el.textContent = t || el.dataset.en;
    });
    $('#lang-btn span').textContent = I.names[l];
    $$('#lang-list [role=option]').forEach(function (o) { o.setAttribute('aria-selected', String(o.dataset.l === l)); });
    store.set('ppd-lang', l);
    index = null;
  }
  var btn = $('#lang-btn'), list = $('#lang-list'), opts = $$('#lang-list [role=option]'), act = 0;
  function open(v) {
    list.hidden = !v; btn.setAttribute('aria-expanded', String(v));
    if (v) { act = Math.max(0, opts.findIndex(function (o) { return o.dataset.l === lang; })); mark(); list.focus(); }
  }
  function mark() {
    opts.forEach(function (o, i) { o.classList.toggle('act', i === act); });
    list.setAttribute('aria-activedescendant', opts[act].id);
  }
  btn.addEventListener('click', function () { open(list.hidden); });
  opts.forEach(function (o) { o.addEventListener('click', function () { setLang(o.dataset.l); open(false); btn.focus(); }); });
  list.addEventListener('keydown', function (e) {
    var cols = 2, n = opts.length, k = e.key;
    if (k === 'ArrowDown') act = Math.min(n - 1, act + cols);
    else if (k === 'ArrowUp') act = Math.max(0, act - cols);
    else if (k === 'ArrowRight') act = Math.min(n - 1, act + 1);
    else if (k === 'ArrowLeft') act = Math.max(0, act - 1);
    else if (k === 'Enter' || k === ' ') { setLang(opts[act].dataset.l); open(false); btn.focus(); }
    else if (k === 'Escape' || k === 'Tab') { open(false); if (k === 'Escape') btn.focus(); return; }
    else return;
    e.preventDefault(); mark();
  });
  d.addEventListener('click', function (e) { if (!list.hidden && !e.target.closest('.langs')) open(false); });

  // ---- theme
  var th = $('#theme');
  function setTheme(t) {
    if (t && t !== 'auto') root.dataset.theme = t; else delete root.dataset.theme;
    th.value = t || 'auto'; store.set('ppd-theme', t || 'auto');
  }
  th.addEventListener('change', function () { setTheme(th.value); });

  // ---- calm sound: a soft binaural pair (left/right a few Hz apart), 15% volume, off until pressed
  var snd = $('#sound'), ctx = null, gain = null;
  if (snd) snd.addEventListener('click', function () {
    var on = snd.getAttribute('aria-pressed') !== 'true';
    snd.setAttribute('aria-pressed', String(on));
    if (on && !ctx) {
      var A = window.AudioContext || window.webkitAudioContext; if (!A) return;
      ctx = new A(); gain = ctx.createGain(); gain.gain.value = 0; gain.connect(ctx.destination);
      [[174, -1], [180, 1]].forEach(function (p) {
        var o = ctx.createOscillator(), pan = ctx.createStereoPanner ? ctx.createStereoPanner() : null;
        o.frequency.value = p[0];
        if (pan) { pan.pan.value = p[1]; o.connect(pan).connect(gain); } else o.connect(gain);
        o.start();
      });
    }
    if (!ctx) return;
    if (on) ctx.resume();
    gain.gain.setTargetAtTime(on ? 0.15 : 0, ctx.currentTime, 0.4);
  });

  // ---- smart search: typo-tolerant, synonym-aware, always lands on the closest item
  var SYN = { ai: 'artificial intelligence agent agents llm machine learning claude gpt', ml: 'machine learning ai model',
    js: 'javascript node web', ts: 'typescript', py: 'python', ui: 'design frontend interface', ux: 'design user experience',
    db: 'database sql data', data: 'analytics sql dashboard database', web: 'html css javascript site frontend',
    security: 'secure scorecard vulnerability audit', finance: 'fp&a budget accounting cash', game: 'games play browser',
    devops: 'ci cd github actions deploy', test: 'tests testing evals qa', app: 'application mobile web' };
  var index = null;
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function words(s) { return norm(s).split(/[^\p{L}\p{N}+#&.]+/u).filter(Boolean); }
  function grams(w) { var g = {}, s = ' ' + w + ' '; for (var i = 0; i < s.length - 2; i++) g[s.substr(i, 3)] = 1; return g; }
  function sim(a, b) {
    if (a === b) return 1;
    if (a.length > 1 && b.indexOf(a) === 0) return 0.9;
    if (b.length > 3 && a.indexOf(b) === 0 && b.length >= a.length * 0.75) return 0.85;
    if (a.length > 2 && b.indexOf(a) > -1) return 0.8;
    var ga = grams(a), gb = grams(b), n = 0, ta = 0, tb = 0, k;
    for (k in ga) { ta++; if (gb[k]) n++; } for (k in gb) tb++;
    return 2 * n / (ta + tb);
  }
  function build() {
    index = $$('[data-s]').map(function (el) {
      var title = el.querySelector('h3,b');
      return { el: el, label: title ? title.textContent : el.textContent.slice(0, 40),
               sub: el.dataset.kind ? ui(el.dataset.kind) : '', w: words(el.textContent + ' ' + el.dataset.s),
               t: words(title ? title.textContent : el.textContent) };
    });
  }
  function score(q) {
    if (!index) build();
    var qs = words(q), ex = [];
    qs.forEach(function (w) { if (SYN[w]) ex = ex.concat(words(SYN[w])); });
    return index.map(function (it) {
      var s = 0;
      qs.forEach(function (w) {
        var b = 0, h = 0;
        it.w.forEach(function (x) { b = Math.max(b, sim(w, x)); });
        it.t.forEach(function (x) { h = Math.max(h, sim(w, x)); });
        s += b + (h >= 0.5 ? 0.2 * h : 0);  // a hit in the title beats a hit in the body
      });
      ex.forEach(function (w) { if (it.w.indexOf(w) > -1) s += 0.35; });
      return { it: it, s: s / Math.max(1, qs.length) };
    }).sort(function (a, b) { return b.s - a.s; }).slice(0, 5);
  }
  var q = $('#q'), qr = $('#qr'), res = [], sel = 0;
  function go(r) {
    if (!r) return;
    qr.hidden = true; q.setAttribute('aria-expanded', 'false');
    r.it.el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    r.it.el.classList.remove('hit'); void r.it.el.offsetWidth; r.it.el.classList.add('hit');
  }
  function show() {
    var v = q.value.trim();
    if (!v) { qr.hidden = true; q.setAttribute('aria-expanded', 'false'); return; }
    res = score(v); sel = 0; qr.innerHTML = '';
    if (res.length && res[0].s < 0.6) {
      var h = d.createElement('li'); h.className = 'hint'; h.setAttribute('role', 'presentation');
      h.textContent = ui('nomatch') + ' · ' + ui('closest'); qr.appendChild(h);
    }
    res.forEach(function (r, i) {
      var li = d.createElement('li'), sm = d.createElement('small');
      li.id = 'qr' + i; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', String(i === 0));
      li.textContent = r.it.label; sm.textContent = r.it.sub; li.appendChild(sm);
      li.addEventListener('mousedown', function (e) { e.preventDefault(); go(r); });
      qr.appendChild(li);
    });
    qr.hidden = !res.length; q.setAttribute('aria-expanded', String(!!res.length));
    q.setAttribute('aria-activedescendant', 'qr0');
  }
  q.addEventListener('input', show);
  q.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      if (!res.length) return; e.preventDefault();
      sel = (sel + (e.key === 'ArrowDown' ? 1 : res.length - 1)) % res.length;
      $$('#qr [role=option]').forEach(function (li, i) { li.setAttribute('aria-selected', String(i === sel)); });
      q.setAttribute('aria-activedescendant', 'qr' + sel);
    } else if (e.key === 'Enter') { e.preventDefault(); if (!res.length) show(); go(res[sel]); }
    else if (e.key === 'Escape') { qr.hidden = true; q.setAttribute('aria-expanded', 'false'); }
  });
  q.addEventListener('blur', function () { setTimeout(function () { qr.hidden = true; q.setAttribute('aria-expanded', 'false'); }, 150); });

  // ---- reveal once on scroll
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    root.classList.add('js');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    $$('.fx').forEach(function (el) { io.observe(el); });
  }

  var pref = store.get('ppd-lang') || (navigator.language || 'en').slice(0, 2);
  setTheme(store.get('ppd-theme'));
  if (pref !== 'en') setLang(pref); else { $$('#lang-list [role=option]').forEach(function (o) { o.setAttribute('aria-selected', String(o.dataset.l === 'en')); }); }
})();
