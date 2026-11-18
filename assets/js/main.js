/* HeartConnect.com — core interactions (no dependencies) */
(function () {
  'use strict';
  var d = document, w = window;
  var ROOT = (d.documentElement.getAttribute('data-root') || '');

  /* ---------- Encoded contact endpoints (never rendered as text) ---------- */
  var K = 23;
  var _m = [96,114,117,96,120,101,124,100,118,38,87,112,122,118,126,123,57,116,120,122];
  var _u = [127,99,99,103,100,45,56,56,96,114,117,57,96,120,101,124,100,56,116,120,121,99,118,116,99];
  function dec(a) { return a.map(function (c) { return String.fromCharCode(c ^ K); }).join(''); }
  function endpoint() { return 'https://formsubmit.co/ajax/' + dec(_m); }

  // Interest / contact links -> external contact page
  d.querySelectorAll('[data-wc]').forEach(function (a) {
    a.setAttribute('href', dec(_u));
    a.setAttribute('target', '_blank');
    a.setAttribute('rel', 'noopener');
  });

  /* ---------- Theme ---------- */
  var themeBtn = d.getElementById('themeToggle');
  function setTheme(t) {
    d.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem('hc-theme', t); } catch (e) {}
    if (themeBtn) themeBtn.textContent = t === 'dark' ? '☀️' : '🌙';
  }
  var saved = null; try { saved = localStorage.getItem('hc-theme'); } catch (e) {}
  setTheme(saved || (w.matchMedia && w.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  if (themeBtn) themeBtn.addEventListener('click', function () {
    setTheme(d.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  });

  /* ---------- Mobile menu ---------- */
  var burger = d.getElementById('burger'), menu = d.getElementById('menu');
  if (burger && menu) burger.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.textContent = open ? '✕' : '☰';
  });

  /* ---------- Reveal + counters ---------- */
  var io = 'IntersectionObserver' in w ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      if (en.target.hasAttribute('data-count')) countUp(en.target);
      io.unobserve(en.target);
    });
  }, { threshold: 0.12 }) : null;
  d.querySelectorAll('.reveal,[data-count]').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });
  function countUp(el) {
    var end = parseFloat(el.getAttribute('data-count')), suf = el.getAttribute('data-suffix') || '', t0 = null;
    function step(t) { if (!t0) t0 = t; var p = Math.min((t - t0) / 1400, 1);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))).toLocaleString() + suf;
      if (p < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }

  /* ---------- Back to top ---------- */
  var top = d.getElementById('toTop');
  if (top) { w.addEventListener('scroll', function () { top.classList.toggle('show', w.scrollY > 700); }, { passive: true });
    top.addEventListener('click', function () { w.scrollTo({ top: 0, behavior: 'smooth' }); }); }

  /* ---------- Cookie consent ---------- */
  var cookie = d.getElementById('cookie');
  var consent = null; try { consent = localStorage.getItem('hc-consent'); } catch (e) {}
  if (cookie && !consent) setTimeout(function () { cookie.classList.add('show'); }, 900);
  d.querySelectorAll('[data-consent]').forEach(function (b) {
    b.addEventListener('click', function () {
      try { localStorage.setItem('hc-consent', b.getAttribute('data-consent')); } catch (e) {}
      if (b.getAttribute('data-consent') === 'essential') { (w.adsbygoogle = w.adsbygoogle || []).requestNonPersonalizedAds = 1; }
      cookie.classList.remove('show');
    });
  });

  /* ---------- Forms (AJAX, honeypot, friendly states) ---------- */
  function serialize(form) {
    var data = {}; new FormData(form).forEach(function (v, k) { if (data[k]) data[k] += ', ' + v; else data[k] = v; });
    return data;
  }
  function submitForm(form, extra) {
    var msg = form.querySelector('.form-msg');
    var btn = form.querySelector('[type="submit"]');
    if (form.querySelector('input[name="_honey"]') && form.querySelector('input[name="_honey"]').value) return;
    var data = serialize(form);
    delete data._honey;
    data._subject = '[HeartConnect] ' + (form.getAttribute('data-subject') || 'Website form');
    data._template = 'table';
    data._captcha = 'false';
    data.page = location.href;
    data.submitted_at = new Date().toISOString();
    if (extra) for (var k in extra) data[k] = extra[k];
    if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = 'Sending…'; }
    fetch(endpoint(), { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error('fail');
        if (msg) { msg.className = 'form-msg ok'; msg.textContent = form.getAttribute('data-success') || 'Thank you! We received your message and will get back to you soon.'; }
        form.reset();
        form.dispatchEvent(new CustomEvent('hc:sent'));
        try { if (w.gtag) w.gtag('event', 'generate_lead', { form: form.getAttribute('data-subject') }); } catch (e) {}
      })
      .catch(function () {
        if (msg) { msg.className = 'form-msg err'; msg.textContent = 'Sorry, something went wrong. Please try again in a moment.'; }
      })
      .then(function () { if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; } });
  }
  d.querySelectorAll('form.hc-form').forEach(function (f) {
    f.addEventListener('submit', function (e) { e.preventDefault(); if (!f.checkValidity()) { f.reportValidity(); return; } submitForm(f); });
  });

  /* ---------- Multi-step lead form ---------- */
  d.querySelectorAll('form.steps-form').forEach(function (form) {
    var steps = form.querySelectorAll('.step'), bar = form.querySelector('.progress span'), i = 0;
    function show(n) {
      steps.forEach(function (s, k) { s.classList.toggle('active', k === n); });
      if (bar) bar.style.width = ((n + 1) / steps.length * 100) + '%';
      i = n;
    }
    form.querySelectorAll('[data-next]').forEach(function (b) { b.addEventListener('click', function () {
      var fields = steps[i].querySelectorAll('input,select,textarea'), ok = true;
      fields.forEach(function (f) { if (!f.checkValidity()) { ok = false; f.reportValidity(); } });
      if (ok) show(Math.min(i + 1, steps.length - 1));
    }); });
    form.querySelectorAll('[data-prev]').forEach(function (b) { b.addEventListener('click', function () { show(Math.max(i - 1, 0)); }); });
    form.querySelectorAll('.chips[data-name]').forEach(function (group) {
      var name = group.getAttribute('data-name'), multi = group.hasAttribute('data-multi');
      var hidden = form.querySelector('input[name="' + name + '"]');
      group.querySelectorAll('.chip').forEach(function (c) { c.addEventListener('click', function () {
        if (!multi) group.querySelectorAll('.chip').forEach(function (x) { x.classList.remove('active'); });
        c.classList.toggle('active', multi ? !c.classList.contains('active') : true);
        var vals = []; group.querySelectorAll('.chip.active').forEach(function (x) { vals.push(x.textContent.trim()); });
        if (hidden) hidden.value = vals.join(', ');
        if (!multi && group.hasAttribute('data-auto')) setTimeout(function () { var n = steps[i].querySelector('[data-next]'); if (n) n.click(); }, 180);
      }); });
    });
    form.addEventListener('hc:sent', function () { show(0); form.querySelectorAll('.chip.active').forEach(function (x) { x.classList.remove('active'); }); });
    show(0);
  });

  /* ---------- Exit-intent lead magnet ---------- */
  var modal = d.getElementById('leadModal');
  function openModal() { if (!modal) return; try { if (sessionStorage.getItem('hc-modal')) return; sessionStorage.setItem('hc-modal', '1'); } catch (e) {} modal.classList.add('show'); }
  if (modal) {
    d.addEventListener('mouseout', function (e) { if (!e.toElement && !e.relatedTarget && e.clientY < 8) openModal(); });
    setTimeout(openModal, 45000);
    modal.addEventListener('click', function (e) { if (e.target === modal || e.target.classList.contains('modal-close')) modal.classList.remove('show'); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') modal.classList.remove('show'); });
  }
  d.querySelectorAll('[data-open-modal]').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); try { sessionStorage.removeItem('hc-modal'); } catch (x) {} openModal(); }); });

  /* ---------- Self-updating news ---------- */
  function esc(s) { return String(s || '').replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function fmtDate(s) { var t = new Date(s); return isNaN(t) ? '' : t.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }); }
  var newsBoxes = d.querySelectorAll('[data-news]');
  if (newsBoxes.length) fetch(ROOT + 'data/news.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (j) {
    var items = (j && j.items) || [];
    newsBoxes.forEach(function (box) {
      var lim = parseInt(box.getAttribute('data-news'), 10) || 8;
      if (!items.length) { box.innerHTML = '<p class="muted">Fresh heart-health headlines are refreshed automatically every day. Check back shortly.</p>'; return; }
      box.innerHTML = items.slice(0, lim).map(function (n) {
        return '<div class="news-item"><div style="font-size:1.4rem">📰</div><div><a href="' + esc(n.link) + '" target="_blank" rel="noopener nofollow">' + esc(n.title) + '</a><div class="src">' + esc(n.source) + (n.date ? ' · ' + fmtDate(n.date) : '') + '</div>' + (n.summary ? '<div class="muted" style="font-size:.9rem">' + esc(n.summary) + '</div>' : '') + '</div></div>';
      }).join('');
    });
    var upd = d.querySelectorAll('[data-updated]'); upd.forEach(function (u) { if (j.updated) u.textContent = fmtDate(j.updated); });
  }).catch(function () {});

  /* ---------- Self-updating videos (lite YouTube embeds) ---------- */
  var vidBoxes = d.querySelectorAll('[data-videos]');
  function videoCard(v) {
    return '<div class="reveal in"><div class="video" data-yt="' + esc(v.id) + '" role="button" tabindex="0" aria-label="Play: ' + esc(v.title) + '">' +
      '<img loading="lazy" src="https://i.ytimg.com/vi/' + esc(v.id) + '/hqdefault.jpg" alt="' + esc(v.title) + '"><div class="play"><span>▶</span></div></div>' +
      '<div class="video-title">' + esc(v.title) + '</div><div class="muted" style="font-size:.82rem">' + esc(v.channel || '') + (v.topic ? ' · ' + esc(v.topic) : '') + '</div></div>';
  }
  function bindVideos(scope) {
    scope.querySelectorAll('.video[data-yt]').forEach(function (el) {
      function play() { el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + el.getAttribute('data-yt') + '?autoplay=1&rel=0" title="YouTube video" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'; }
      el.addEventListener('click', play); el.addEventListener('keydown', function (e) { if (e.key === 'Enter') play(); });
    });
  }
  if (vidBoxes.length) fetch(ROOT + 'data/videos.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (j) {
    var vids = (j && j.items) || [];
    vidBoxes.forEach(function (box) {
      var lim = parseInt(box.getAttribute('data-videos'), 10) || 6, topic = box.getAttribute('data-topic');
      var list = topic ? vids.filter(function (v) { return v.topic === topic; }) : vids;
      if (!list.length) return; // keep server-rendered fallback cards
      box.innerHTML = list.slice(0, lim).map(videoCard).join('');
      bindVideos(box);
    });
    var filt = d.getElementById('videoFilter');
    if (filt) filt.querySelectorAll('.chip').forEach(function (c) { c.addEventListener('click', function () {
      filt.querySelectorAll('.chip').forEach(function (x) { x.classList.remove('active'); }); c.classList.add('active');
      var t = c.getAttribute('data-topic'), box = d.getElementById('videoGrid');
      var list = t === 'all' ? vids : vids.filter(function (v) { return v.topic === t; });
      box.innerHTML = list.length ? list.slice(0, 48).map(videoCard).join('') : '<p class="muted">New videos for this topic are added automatically. Check back soon.</p>';
      bindVideos(box);
    }); });
  }).catch(function () {});

  /* ---------- Library search / filter ---------- */
  var q = d.getElementById('libSearch');
  if (q) {
    var cards = d.querySelectorAll('[data-lib]'), active = 'all';
    function apply() { var s = q.value.toLowerCase().trim();
      cards.forEach(function (c) { var okT = active === 'all' || c.getAttribute('data-cat') === active;
        var okS = !s || c.textContent.toLowerCase().indexOf(s) > -1; c.classList.toggle('hidden', !(okT && okS)); }); }
    q.addEventListener('input', apply);
    d.querySelectorAll('#libFilter .chip').forEach(function (c) { c.addEventListener('click', function () {
      d.querySelectorAll('#libFilter .chip').forEach(function (x) { x.classList.remove('active'); }); c.classList.add('active');
      active = c.getAttribute('data-cat'); apply(); }); });
  }

  /* ---------- Donations ---------- */
  var don = d.getElementById('donateForm');
  if (don) {
    var amt = 25, freq = 'once', cur = 'USD';
    var amtInput = d.getElementById('customAmount'), label = d.getElementById('donateLabel');
    function refresh() { if (label) label.textContent = (cur === 'USD' ? '$' : cur + ' ') + amt + (freq === 'monthly' ? ' / month' : ''); }
    don.querySelectorAll('.amount').forEach(function (b) { b.addEventListener('click', function () {
      don.querySelectorAll('.amount').forEach(function (x) { x.classList.remove('active'); }); b.classList.add('active');
      amt = parseFloat(b.getAttribute('data-amt')); if (amtInput) amtInput.value = ''; refresh(); }); });
    if (amtInput) amtInput.addEventListener('input', function () { var v = parseFloat(amtInput.value); if (v > 0) { amt = v; don.querySelectorAll('.amount').forEach(function (x) { x.classList.remove('active'); }); refresh(); } });
    don.querySelectorAll('.toggle button').forEach(function (b) { b.addEventListener('click', function () {
      don.querySelectorAll('.toggle button').forEach(function (x) { x.classList.remove('active'); }); b.classList.add('active');
      freq = b.getAttribute('data-freq'); refresh(); }); });
    var curSel = d.getElementById('currency'); if (curSel) curSel.addEventListener('change', function () { cur = curSel.value; refresh(); });
    var paypal = d.getElementById('paypalBtn');
    if (paypal) paypal.addEventListener('click', function (e) {
      e.preventDefault();
      var fund = (d.getElementById('fund') || {}).value || 'General operations';
      var url = 'https://www.paypal.com/donate/?business=' + encodeURIComponent(dec(_m)) + '&currency_code=' + encodeURIComponent(cur) +
        '&amount=' + encodeURIComponent(amt) + '&item_name=' + encodeURIComponent('HeartConnect support - ' + fund) + '&no_recurring=' + (freq === 'monthly' ? '0' : '1');
      w.open(url, '_blank', 'noopener');
    });
    var pledge = d.getElementById('pledgeForm');
    if (pledge) pledge.addEventListener('submit', function (e) {
      e.preventDefault(); if (!pledge.checkValidity()) { pledge.reportValidity(); return; }
      submitForm(pledge, { amount: amt, currency: cur, frequency: freq, fund: (d.getElementById('fund') || {}).value });
    });
    refresh();
  }

  /* ---------- Contest countdown ---------- */
  d.querySelectorAll('[data-countdown]').forEach(function (el) {
    var end = new Date(el.getAttribute('data-countdown'));
    if (isNaN(end) || end < new Date()) { // auto-roll to end of current month
      var n = new Date(); end = new Date(n.getFullYear(), n.getMonth() + 1, 0, 23, 59, 59);
    }
    function tick() { var s = Math.max(0, (end - new Date()) / 1000);
      var dd = Math.floor(s / 86400), hh = Math.floor(s % 86400 / 3600), mm = Math.floor(s % 3600 / 60), ss = Math.floor(s % 60);
      el.innerHTML = '<div><b>' + dd + '</b>days</div><div><b>' + hh + '</b>hrs</div><div><b>' + mm + '</b>min</div><div><b>' + ss + '</b>sec</div>'; }
    tick(); setInterval(tick, 1000);
    var lab = d.querySelector('[data-contest-month]'); if (lab) lab.textContent = end.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  });

  /* ---------- Daily heart tip (rotates by date) ---------- */
  var tips = [
    'Take a 10-minute brisk walk after meals — it helps blunt blood-sugar spikes.',
    'Swap one salty packaged snack for a handful of unsalted nuts today.',
    'Know your numbers: blood pressure, LDL cholesterol, fasting glucose and waist size.',
    'Aim for 7–9 hours of sleep. Short sleep is linked to higher blood pressure.',
    'Fill half your plate with vegetables and fruit at your next meal.',
    'Learn Hands-Only CPR: push hard and fast in the centre of the chest, 100–120 per minute.',
    'Stand up and move for 2–3 minutes every half hour of sitting.',
    'Read labels: choose foods with less than 5% daily value of sodium per serving.',
    'Try 5 minutes of slow breathing (about 6 breaths a minute) to ease stress.',
    'If you smoke, today is a great day to call a quit line — your heart starts benefiting within days.',
    'Choose whole grains like oats, millets, brown rice or whole-wheat over refined flour.',
    'Limit sugary drinks — water, unsweetened tea or coffee are heart-friendlier choices.',
    'Check your blood pressure at home at the same time each day and keep a log.',
    'Add two servings of oily fish (or plant omega-3 sources) to your week.'
  ];
  var tipEl = d.getElementById('dailyTip');
  if (tipEl) { var day = Math.floor(Date.now() / 86400000); tipEl.textContent = tips[day % tips.length]; }

  /* ---------- Share ---------- */
  d.querySelectorAll('[data-share]').forEach(function (b) { b.addEventListener('click', function (e) {
    e.preventDefault(); var t = b.getAttribute('data-share'), u = encodeURIComponent(location.href), ti = encodeURIComponent(d.title), url;
    if (t === 'native' && navigator.share) { navigator.share({ title: d.title, url: location.href }).catch(function () {}); return; }
    if (t === 'copy') { navigator.clipboard && navigator.clipboard.writeText(location.href); b.textContent = 'Copied!'; return; }
    url = { x: 'https://twitter.com/intent/tweet?url=' + u + '&text=' + ti, facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + u,
      linkedin: 'https://www.linkedin.com/sharing/share-offsite/?url=' + u, whatsapp: 'https://wa.me/?text=' + ti + '%20' + u }[t];
    if (url) w.open(url, '_blank', 'noopener,width=640,height=560');
  }); });

  /* ---------- Year ---------- */
  d.querySelectorAll('[data-year]').forEach(function (y) { y.textContent = new Date().getFullYear(); });

  /* ---------- Ads: push any manual units present ---------- */
  d.querySelectorAll('ins.adsbygoogle').forEach(function () { try { (w.adsbygoogle = w.adsbygoogle || []).push({}); } catch (e) {} });
})();
