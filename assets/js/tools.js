/* HeartConnect.com — interactive heart-health tools (educational only) */
(function () {
  'use strict';
  var d = document;
  function $(id) { return d.getElementById(id); }
  function num(id) { var v = parseFloat(($(id) || {}).value); return isNaN(v) ? null : v; }
  function out(id, html) { var el = $(id); if (el) el.innerHTML = html; }
  function badge(cls, t) { return '<span class="badge ' + cls + '">' + t + '</span>'; }
  function bind(formId, fn) { var f = $(formId); if (f) f.addEventListener('submit', function (e) { e.preventDefault(); fn(); }); }

  /* 1. Blood pressure category (ACC/AHA adult categories) */
  function bpCategory(s, di) {
    if (s > 180 || di > 120) return ['b-red', 'Severe — hypertensive crisis range', 'Re-check after 5 minutes of rest. If still this high, or with chest pain, shortness of breath, weakness, vision or speech changes, call emergency services now.'];
    if (s >= 140 || di >= 90) return ['b-red', 'Stage 2 high blood pressure', 'Talk with a clinician soon about a treatment plan; lifestyle change plus medication is commonly advised.'];
    if (s >= 130 || di >= 80) return ['b-orange', 'Stage 1 high blood pressure', 'Lifestyle changes help; a clinician may consider medication depending on your overall risk.'];
    if (s >= 120) return ['b-yellow', 'Elevated', 'Healthy habits now can prevent progression: less salt, more activity, limit alcohol.'];
    return ['b-green', 'Normal', 'Great — keep up heart-healthy habits and re-check regularly.'];
  }
  bind('bpForm', function () {
    var s = num('bpSys'), di = num('bpDia');
    if (!s || !di) return out('bpOut', 'Enter both numbers.');
    var c = bpCategory(s, di);
    out('bpOut', '<b>' + s + '/' + di + ' mmHg</b> ' + badge(c[0], c[1]) + '<p style="margin-top:8px">' + c[2] + '</p>');
  });

  /* 2. BMI with Asian cut-offs option */
  bind('bmiForm', function () {
    var h = num('bmiH'), wt = num('bmiW'), asian = ($('bmiAsian') || {}).checked;
    if (!h || !wt) return out('bmiOut', 'Enter height and weight.');
    var bmi = wt / Math.pow(h / 100, 2), c;
    var ow = asian ? 23 : 25, ob = asian ? 27.5 : 30;
    if (bmi < 18.5) c = ['b-yellow', 'Underweight'];
    else if (bmi < ow) c = ['b-green', 'Healthy range'];
    else if (bmi < ob) c = ['b-orange', 'Overweight'];
    else c = ['b-red', 'Obesity range'];
    out('bmiOut', '<b>BMI ' + bmi.toFixed(1) + '</b> ' + badge(c[0], c[1]) + '<p style="margin-top:8px">Cut-offs used: overweight ≥ ' + ow + ', obesity ≥ ' + ob + (asian ? ' (WHO expert consultation action points for Asian populations)' : ' (WHO standard)') + '. BMI does not measure body fat directly — pair it with waist size.</p>');
  });

  /* 3. Target heart rate zones */
  bind('hrForm', function () {
    var age = num('hrAge'), rest = num('hrRest');
    if (!age) return out('hrOut', 'Enter your age.');
    var max = Math.round(208 - 0.7 * age), z = function (p) { return Math.round(max * p); }, txt;
    if (rest) { var rr = max - rest, k = function (p) { return Math.round(rest + rr * p); };
      txt = 'Using heart-rate reserve (Karvonen): moderate <b>' + k(.5) + '–' + k(.7) + '</b> bpm, vigorous <b>' + k(.7) + '–' + k(.85) + '</b> bpm.'; }
    else txt = 'Moderate (50–70%): <b>' + z(.5) + '–' + z(.7) + '</b> bpm · Vigorous (70–85%): <b>' + z(.7) + '–' + z(.85) + '</b> bpm.';
    out('hrOut', '<b>Estimated max: ' + max + ' bpm</b> <span class="muted">(Tanaka formula 208 − 0.7 × age)</span><p style="margin-top:8px">' + txt + '</p><p class="form-note">Beta-blockers and some other medicines change heart-rate response — ask your clinician for personal targets.</p>');
  });

  /* 4. Cholesterol ratio */
  bind('cholForm', function () {
    var tc = num('cholTotal'), hdl = num('cholHdl'), unit = ($('cholUnit') || {}).value;
    if (!tc || !hdl) return out('cholOut', 'Enter total cholesterol and HDL.');
    var r = tc / hdl, c = r < 3.5 ? ['b-green', 'Ideal'] : r < 5 ? ['b-yellow', 'Acceptable'] : ['b-red', 'High — discuss with a clinician'];
    var nonHdl = tc - hdl;
    out('cholOut', '<b>Ratio ' + r.toFixed(2) + '</b> ' + badge(c[0], c[1]) + '<p style="margin-top:8px">Non-HDL cholesterol: <b>' + nonHdl.toFixed(unit === 'mmol' ? 1 : 0) + ' ' + (unit === 'mmol' ? 'mmol/L' : 'mg/dL') + '</b>. Lower total/HDL ratios generally mean lower cardiovascular risk.</p>');
  });

  /* 5. Waist-to-height ratio */
  bind('whtrForm', function () {
    var w = num('whtrWaist'), h = num('whtrHeight');
    if (!w || !h) return out('whtrOut', 'Enter waist and height in the same unit.');
    var r = w / h, c = r < 0.5 ? ['b-green', 'Healthy'] : r < 0.6 ? ['b-orange', 'Increased risk'] : ['b-red', 'High risk'];
    out('whtrOut', '<b>' + r.toFixed(2) + '</b> ' + badge(c[0], c[1]) + '<p style="margin-top:8px">A simple rule: keep your waist to less than half your height.</p>');
  });

  /* 6. Heart Habits Score (inspired by the 8 well-known cardiovascular health factors) */
  bind('scoreForm', function () {
    var f = $('scoreForm'), total = 0, n = 0, weak = [];
    f.querySelectorAll('select[data-factor]').forEach(function (s) { var v = parseInt(s.value, 10); total += v; n++; if (v < 50) weak.push(s.getAttribute('data-factor')); });
    var score = Math.round(total / n), c = score >= 80 ? ['b-green', 'Strong'] : score >= 50 ? ['b-yellow', 'Moderate'] : ['b-red', 'Needs attention'];
    out('scoreOut', '<b>' + score + ' / 100</b> ' + badge(c[0], c[1]) + (weak.length ? '<p style="margin-top:8px">Focus first on: <b>' + weak.join(', ') + '</b>.</p>' : '<p style="margin-top:8px">Excellent across the board — keep going!</p>') +
      '<p><a class="btn btn-primary btn-sm" href="find-care.html">Get a free personalised heart-care plan →</a></p>');
  });

  /* 7. Blood pressure log (stored only in this browser) */
  var KEY = 'hc-bp-log';
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
  function render() {
    var log = load(), tb = $('logBody'); if (!tb) return;
    tb.innerHTML = log.slice().reverse().map(function (r) { var c = bpCategory(r.s, r.d);
      return '<tr><td>' + new Date(r.t).toLocaleString() + '</td><td>' + r.s + '/' + r.d + '</td><td>' + (r.p || '–') + '</td><td>' + badge(c[0], c[1]) + '</td></tr>'; }).join('') || '<tr><td colspan="4" class="muted">No readings yet.</td></tr>';
    if (log.length) { var as = 0, ad = 0; log.forEach(function (r) { as += r.s; ad += r.d; });
      out('logAvg', 'Average of ' + log.length + ' readings: <b>' + Math.round(as / log.length) + '/' + Math.round(ad / log.length) + ' mmHg</b>'); }
    else out('logAvg', '');
    draw(log);
  }
  function draw(log) {
    var cv = $('logChart'); if (!cv || !cv.getContext) return;
    var ctx = cv.getContext('2d'), W = cv.width = cv.clientWidth * 2, H = cv.height = 440; ctx.clearRect(0, 0, W, H);
    var pts = log.slice(-30); if (pts.length < 2) { ctx.fillStyle = '#94a3b8'; ctx.font = '26px Inter,sans-serif'; ctx.fillText('Add 2+ readings to see your trend', 30, H / 2); return; }
    var min = 50, max = 200, x = function (i) { return 60 + i * (W - 90) / (pts.length - 1); }, y = function (v) { return H - 40 - (v - min) / (max - min) * (H - 70); };
    ctx.strokeStyle = 'rgba(148,163,184,.35)'; ctx.lineWidth = 1; ctx.fillStyle = '#94a3b8'; ctx.font = '20px Inter,sans-serif';
    [60, 80, 120, 140, 180].forEach(function (g) { ctx.beginPath(); ctx.moveTo(50, y(g)); ctx.lineTo(W - 20, y(g)); ctx.stroke(); ctx.fillText(g, 8, y(g) + 6); });
    [['s', '#e11d48'], ['d', '#0284c7']].forEach(function (k) { ctx.strokeStyle = k[1]; ctx.lineWidth = 4; ctx.beginPath();
      pts.forEach(function (p, i) { i ? ctx.lineTo(x(i), y(p[k[0]])) : ctx.moveTo(x(i), y(p[k[0]])); }); ctx.stroke();
      ctx.fillStyle = k[1]; pts.forEach(function (p, i) { ctx.beginPath(); ctx.arc(x(i), y(p[k[0]]), 6, 0, 7); ctx.fill(); }); });
  }
  bind('logForm', function () {
    var s = num('logSys'), di = num('logDia'), p = num('logPulse');
    if (!s || !di) return; var log = load(); log.push({ t: Date.now(), s: s, d: di, p: p }); save(log); $('logForm').reset(); render();
  });
  var clr = $('logClear'); if (clr) clr.addEventListener('click', function () { if (confirmClear()) { save([]); render(); } });
  function confirmClear() { var b = $('logClear'); if (b.dataset.armed) { delete b.dataset.armed; b.textContent = 'Clear log'; return true; } b.dataset.armed = '1'; b.textContent = 'Tap again to confirm'; setTimeout(function () { delete b.dataset.armed; b.textContent = 'Clear log'; }, 3000); return false; }
  var exp = $('logExport'); if (exp) exp.addEventListener('click', function () {
    var rows = [['date', 'systolic', 'diastolic', 'pulse']].concat(load().map(function (r) { return [new Date(r.t).toISOString(), r.s, r.d, r.p || '']; }));
    var a = d.createElement('a'); a.href = URL.createObjectURL(new Blob([rows.map(function (r) { return r.join(','); }).join('\n')], { type: 'text/csv' }));
    a.download = 'heartconnect-bp-log.csv'; a.click();
  });
  window.addEventListener('resize', function () { draw(load()); });
  render();
})();
