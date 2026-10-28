/* SUNDIAL website — the dial, drawn by the same rules as the panels.
   render() is copied unchanged from the panel page (firmware/panel_page_server/data/index.html, rules-1).
   sampleDay() INVENTS data for the preview pages; it is replaced by the Sun import data later. */

const RULES = 'rules-1';
const INK = { paper:'#F4EFE4', ochre:'#E8B33A', red:'#B5452F', blue:'#2E5A78', black:'#1E1D1B' };
const DEG_PER_MIN = 180 / 903;
const HEAT_FULL = 40;
const VIS_BANDS = [[1, 5, 1], [6, 10, 2], [11, Infinity, 3]];
const G = { cx:.5, cy:.70, Ri:.30, Ro:.38, Rd:.44, axis:.014, heat:.016, dot_min:.0235, outline:.012 };
const SEC = 15 * 60;
const BOSA = { lat: 40.2986, lng: 8.4970, tz: 'Europe/Rome' };

/* THE EVENT — edit here. Set confirmed: true once the dates are fixed. */
const EVENT = { name: 'La Meridiana', start: '2027-06-18', end: '2027-06-24', confirmed: false };

function multiply(a, b) {
  const p = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
  const [x, y] = [p(a), p(b)];
  return '#' + x.map((v, i) => (v * y[i] / 255 | 0).toString(16).padStart(2, '0')).join('');
}

// day = { rise, noon, set, failed, temps:[{e,t}], sun:{k:1|0|-1}, vis:{k:n} }
function render(ctx, S, day, nowE) {
  const { rise, noon, set } = day;
  const cx = G.cx * S, cy = G.cy * S, Ri = G.Ri * S, Ro = G.Ro * S, Rd = G.Rd * S;
  const ang = t => (t - noon) / 60 * DEG_PER_MIN * Math.PI / 180;
  const pol = (r, a) => [cx + r * Math.sin(a), cy - r * Math.cos(a)];
  const band = (a0, a1) => {
    const p = new Path2D(), n = 48;
    for (let i = 0; i <= n; i++) { const [x, y] = pol(Ro, a0 + (a1 - a0) * i / n); i ? p.lineTo(x, y) : p.moveTo(x, y); }
    for (let i = 0; i <= n; i++) { const [x, y] = pol(Ri, a1 - (a1 - a0) * i / n); p.lineTo(x, y); }
    p.closePath(); return p;
  };
  const axis = () => { ctx.fillStyle = INK.black; ctx.fillRect(cx - Ro, cy, 2 * Ro, G.axis * S); };

  ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = INK.paper; ctx.fillRect(0, 0, S, S);
  ctx.lineJoin = 'miter';

  if (day.failed) {
    ctx.strokeStyle = INK.black; ctx.lineWidth = G.outline * S;
    ctx.stroke(band(ang(rise), ang(set))); axis(); return;
  }

  const end = nowE && nowE < set ? Math.max(rise, nowE) : set;
  const kFirst = Math.floor((rise - noon) / SEC), kLast = Math.ceil((set - noon) / SEC) - 1;
  const runs = [];
  for (let k = kFirst; k <= kLast; k++) {
    const t0 = Math.max(rise, noon + k * SEC), t1 = Math.min(set, noon + (k + 1) * SEC);
    const v = day.sun[k];
    const col = v === 1 ? INK.ochre : v === 0 ? INK.blue : null;
    const last = runs[runs.length - 1];
    if (last && last.col === col) last.t1 = t1; else runs.push({ t0, t1, col });
  }
  const segs = runs.filter(r => r.col).map(r => ({ path: band(ang(r.t0), ang(r.t1)), col: r.col }));
  for (const s of segs) { ctx.fillStyle = s.col; ctx.fill(s.path); }
  ctx.strokeStyle = INK.black; ctx.lineWidth = G.outline * S * .5;
  for (const r of runs) if (!r.col && r.t0 < set) ctx.stroke(band(ang(r.t0), ang(r.t1)));

  const temps = day.temps.filter(r => r.e >= rise && r.e <= set && isFinite(r.t));
  if (temps.length) {
    const base = temps[0].t, line = new Path2D();
    temps.forEach((r, i) => {
      const x = cx + Ri * Math.sin(ang(r.e)), y = cy - (r.t - base) / HEAT_FULL * Ri;
      i ? line.lineTo(x, y) : line.moveTo(x, y);
    });
    ctx.lineWidth = G.heat * S; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = INK.red; ctx.stroke(line);
    for (const s of segs) {
      ctx.save(); ctx.clip(s.path); ctx.strokeStyle = multiply(s.col, INK.red); ctx.stroke(line); ctx.restore();
    }
    ctx.lineCap = 'butt'; ctx.lineJoin = 'miter';
  }

  axis();

  ctx.fillStyle = INK.black;
  for (const [k, n] of Object.entries(day.vis)) {
    const a = k * 60 * DEG_PER_MIN * Math.PI / 180;
    if (!n || a < ang(rise) || a > ang(set)) continue;
    const step = VIS_BANDS.find(([lo, hi]) => n >= lo && n <= hi)[2];
    const [x, y] = pol(Rd, a);
    ctx.beginPath(); ctx.arc(x, y, G.dot_min * S * step / 2, 0, 2 * Math.PI); ctx.fill();
  }

  if (nowE && nowE >= rise && nowE < set) {
    const a = ang(nowE), [x1, y1] = pol(Ro + S * .012, a), [x2, y2] = pol(Rd - S * .02, a);
    ctx.strokeStyle = 'rgba(30,29,27,.45)'; ctx.lineWidth = Math.max(1, S / 300);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  }
}

/* ---------- sunrise / noon / sunset, epoch seconds (same formula as the firmware) ---------- */
function sunTimes(dateStr, lat = BOSA.lat, lng = BOSA.lng) {
  const rad = Math.PI / 180, J1970 = 2440588, J2000 = 2451545;
  const fromJ = j => (j + 0.5 - J1970) * 86400;
  const noon = new Date(dateStr + 'T12:00:00Z').valueOf() / 1000;
  const d = noon / 86400 - 0.5 + J1970 - J2000;
  const lw = -lng * rad, phi = lat * rad;
  const n = Math.round(d - 0.0009 - lw / (2 * Math.PI));
  const ds = 0.0009 + lw / (2 * Math.PI) + n;
  const M = rad * (357.5291 + 0.98560028 * ds);
  const C = rad * (1.9148 * Math.sin(M) + 0.02 * Math.sin(2 * M) + 0.0003 * Math.sin(3 * M));
  const L = M + C + rad * 102.9372 + Math.PI;
  const dec = Math.asin(Math.sin(L) * Math.sin(rad * 23.4397));
  const Jnoon = J2000 + ds + 0.0053 * Math.sin(M) - 0.0069 * Math.sin(2 * L);
  const w = Math.acos((Math.sin(-0.833 * rad) - Math.sin(phi) * Math.sin(dec)) / (Math.cos(phi) * Math.cos(dec)));
  const Jset = J2000 + 0.0009 + (w + lw) / (2 * Math.PI) + n + 0.0053 * Math.sin(M) - 0.0069 * Math.sin(2 * L);
  return { rise: fromJ(2 * Jnoon - Jset), noon: fromJ(Jnoon), set: fromJ(Jset) };
}

/* ---------- formatting, in Bosa's time ---------- */
const pad = n => String(n).padStart(2, '0');
const hhmm = e => new Date(e * 1000).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: BOSA.tz });
const hm = s => Math.floor(s / 3600) + 'h ' + pad(Math.floor(s % 3600 / 60)) + 'm';
const longDate = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
const shortDate = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' });
const weekday = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { weekday: 'short', timeZone: 'UTC' });
function addDays(d, n) { const t = new Date(d + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + n); return t.toISOString().slice(0, 10); }

/* ---------- INVENTED data, for previews only ---------- */
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function hash(s) { let h = 2166136261; for (const c of s) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }

// Each invented panel has a street: how early it gets the sun, how late it loses it.
const STREETS = [[-4.5, 3.0], [-2.5, 4.5], [-5.0, 5.0], [-3.0, 1.5], [-1.5, 5.5], [-4.0, 4.0], [-5.5, 2.5], [-2.0, 3.0], [-3.5, 5.0]];

function sampleDay(d, panel, { visitors = 'event' } = {}) {
  const st = sunTimes(d), r = rng(hash(d + '|' + panel));
  const dayR = rng(hash(d));                         // the town's weather is shared by all nine
  const month = +d.slice(5, 7), winter = month <= 2 || month >= 11;
  const empty = { temps: [], sun: {}, sunRaw: [], vis: {} };
  if (r() < 0.03) return Object.assign(st, empty, { failed: true });

  let [a0, a1] = STREETS[(panel - 1) % 9].map(h => h * 3600);
  if (winter) { a0 *= 0.75; a1 *= 0.75; }            // low winter sun: walls and roofs block more of the day
  const cloudy = winter ? 0.25 + dayR() * 0.5 : dayR() * 0.22;
  const sun = {}, sunRaw = [];
  const kFirst = Math.floor((st.rise - st.noon) / SEC), kLast = Math.ceil((st.set - st.noon) / SEC) - 1;
  let cloud = false;
  for (let k = kFirst; k <= kLast; k++) {
    const mid = (k + .5) * SEC;
    const cloudR = rng(hash(d + 'c' + k))();          // a passing cloud covers the town, not one wall
    cloud = cloud ? cloudR < 0.6 : cloudR < cloudy * 0.45;
    const v = mid >= a0 && mid <= a1 && !cloud ? 1 : 0;
    sun[k] = v; sunRaw.push({ k, v });
  }
  const temps = []; let heat = 0;
  const base = (winter ? 9 : 22) + r() * 3;
  for (let e = st.rise + 120; e <= st.set; e += 300) {
    const k = Math.floor((e - st.noon) / SEC);
    heat = Math.max(0, heat + (sun[k] === 1 ? (winter ? 0.55 : 0.75) : -0.45));
    temps.push({ e, t: base + Math.min(heat, winter ? 18 : 30) + (r() - .5) * .4 });
  }
  const vis = {}, max = visitors === 'event' ? 15 : 3;
  for (let h = Math.ceil((st.rise - st.noon) / 3600); h * 3600 <= st.set - st.noon; h++) {
    const busy = Math.exp(-((h - 1.5) ** 2) / 18);   // busier in the afternoon
    const n = Math.floor(r() ** 1.6 * max * busy);
    if (n) vis[h] = n;
  }
  return Object.assign(st, { temps, sun, sunRaw, vis, failed: false });
}

function figures(day) {
  if (day.failed) return null;
  const ts = day.temps.map(x => x.t);
  const sunny = day.sunRaw.filter(x => x.v === 1).map(x => x.k);
  const secT = k => Math.max(day.rise, day.noon + k * SEC);
  return {
    first: sunny.length ? hhmm(secT(Math.min(...sunny))) : 'none',
    last: sunny.length ? hhmm(Math.min(day.set, day.noon + (Math.max(...sunny) + 1) * SEC)) : '–',
    hours: sunny.length * 0.25,
    tmin: Math.min(...ts), tmax: Math.max(...ts),
    visits: Object.values(day.vis).reduce((a, b) => a + b, 0),
  };
}

/* ---------- drawing into a canvas at its displayed size ---------- */
function draw(cv, day) {
  const dpr = devicePixelRatio || 1, S = Math.max(1, Math.round(cv.clientWidth * dpr));
  if (cv.width !== S) { cv.width = S; cv.height = S; }
  render(cv.getContext('2d'), S, day, 0);
}
function redrawAll() { document.querySelectorAll('canvas[data-day]').forEach(cv => cv.__day && draw(cv, cv.__day)); }
let __rt; addEventListener('resize', () => { clearTimeout(__rt); __rt = setTimeout(redrawAll, 120); });

/* ---------- a sheet: nine panels across, seven days down ---------- */
function buildSheet(el, startDate, opts, onPick) {
  el.innerHTML = '';
  const days = [];
  for (let i = 0; i < 7; i++) for (let p = 1; p <= 9; p++) {
    const d = addDays(startDate, i), day = sampleDay(d, p, opts);
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('aria-pressed', 'false');
    b.setAttribute('aria-label', `Panel ${p}, ${longDate(d)}`);
    const cv = document.createElement('canvas'); cv.dataset.day = d; cv.__day = day;
    b.appendChild(cv); el.appendChild(b);
    b.onclick = () => {
      el.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', 'false'));
      b.setAttribute('aria-pressed', 'true'); onPick({ d, p, day });
    };
    days.push({ d, p, day, b });
  }
  requestAnimationFrame(() => el.querySelectorAll('canvas').forEach(cv => draw(cv, cv.__day)));
  return days;
}

/* ---------- where Bosa is in the event year: before, during, after ---------- */
function bosaToday() { return new Date().toLocaleDateString('en-CA', { timeZone: BOSA.tz }); }   // YYYY-MM-DD
function eventState(today = bosaToday()) {
  const len = Math.round((Date.parse(EVENT.end) - Date.parse(EVENT.start)) / 864e5) + 1;
  if (today < EVENT.start) return { phase: 'before',
    line: EVENT.confirmed ? `${EVENT.name}: ${longDate(EVENT.start)} to ${longDate(EVENT.end)}` : `${EVENT.name}, Bosa: summer ${EVENT.start.slice(0, 4)}, dates to be confirmed`,
    links: [['What is planned', 'bosa.html']] };
  if (today <= EVENT.end) {
    const n = Math.round((Date.parse(today) - Date.parse(EVENT.start)) / 864e5) + 1;
    return { phase: 'during', line: `On now in Bosa: day ${n} of ${len} · sunset at ${hhmm(sunTimes(today).set)}`,
      links: [['Open the map', 'map.html']] };
  }
  return { phase: 'after', line: `${EVENT.name} ${EVENT.start.slice(0, 4)} is over. The sundials stay, and keep recording`,
    links: [['See the week', 'bosa.html'], ['Sun', 'sun.html']] };
}
