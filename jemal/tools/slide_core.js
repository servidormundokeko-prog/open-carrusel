// Slide renderer shared by the studio (html2canvas export) and the Remotion renderStill pipeline.
// Expects globals ICONS (Lucide inner SVG by name), PHOTOS (scene -> grayscale JPEG data URL) and
// PALETTES (palette key -> colours), all injected by tools/build.py.

const ICON_ALIAS = {
  "magnifying-glass": "search", "banner-with-star": "star", "blueprint": "pencil-ruler", "clipboard": "clipboard-check",
  "stack-of-storefronts": "store", "storefront": "store", "hard-hat": "hard-hat", "apartment-building": "building-2",
  "house": "house", "factory": "factory", "anchor-and-wave": "anchor", "map-pin": "map-pin", "location-pin": "map-pin",
  "map-grid": "map", "building-with-arrow": "building", "theater-curtain": "theater", "crane": "construction",
  "conveyor": "package", "cloud": "cloud", "laser": "scan-line", "robot-arm": "bot", "globe": "globe", "clock": "clock",
  "shield": "shield-check", "gear": "settings", "megaphone": "megaphone", "scale": "scale", "key": "key-round",
  "tag": "tag", "stairs": "trending-up", "chart": "chart-column", "people": "handshake", "document": "file-text",
};
// Scene -> icon for banner badges.
const SCENE_ICON = {
  houses: "house", storefront: "store", stairs: "trending-up", megaphone: "megaphone", pillars: "landmark", row: "store",
  clipboard: "clipboard-check", conveyor: "package", crane: "construction", map: "map", tower: "building-2",
  blueprint: "pencil-ruler", globe: "globe", chart: "chart-column", factory: "factory", shield: "shield-check", tag: "tag",
  keys: "key-round", scale: "scale", clock: "clock", laser: "scan-line", cloud: "cloud", robot: "bot", skyline: "building",
};
// Auto-icon: the first keyword that matches the text picks the icon; otherwise the palette's default.
const KEYWORDS = [
  [/\blease|contract|legal|document|paperwork|permit/i, "file-text"],
  [/zoning|map|route|neighbou?rhood|borough|area/i, "map"],
  [/waterfront|harbou?r|river/i, "anchor"],
  [/parcel|land|site|location|where/i, "map-pin"],
  [/robot|automat/i, "bot"],
  [/laser|precision|millimet|\bmm\b|measure/i, "scan-line"],
  [/cloud|software|data|digital|online/i, "cloud"],
  [/\bai\b|machine|algorithm|planning tool/i, "cpu"],
  [/factory|prefab|manufactur|panel|module/i, "factory"],
  [/built®|technology|tech\b/i, "cpu"],
  [/\bun\b|united nations|global|world|countr/i, "globe"],
  [/hous|home|apartment|residen|adequate/i, "house"],
  [/city|urban|tower|building|skyline|develop/i, "building-2"],
  [/store|shop|retail|storefront|chain/i, "store"],
  [/brand|name|identity|logo/i, "badge-check"],
  [/advertis|message|channel|marketing|promo/i, "megaphone"],
  [/cost|price|money|budget|rent|\$|fund|sales/i, "circle-dollar-sign"],
  [/fast|speed|quick|faster/i, "zap"],
  [/time|day|week|month|year|schedule|when/i, "clock"],
  [/waste|recycl|material/i, "recycle"],
  [/risk|safe|secur|protect/i, "shield-check"],
  [/quality|standard|consisten/i, "badge-check"],
  [/supplier|inventory|stock|deliver/i, "package"],
  [/train|learn|teach|lesson|school/i, "graduation-cap"],
  [/system|process|operation|repeat/i, "settings"],
  [/check|audit|test|question/i, "list-checks"],
  [/grow|scale|expand|more locations|next/i, "trending-up"],
  [/market|demand|customer|gap/i, "chart-line"],
  [/family|father|parent|value|together/i, "heart"],
  [/vision|future|goal|idea/i, "eye"],
  [/design|plan|blueprint/i, "pencil-ruler"],
  [/build|construct|crane|buildout/i, "hammer"],
];

function rgba(hex, a) { const h = hex.replace("#", ""); return `rgba(${parseInt(h.slice(0, 2), 16)},${parseInt(h.slice(2, 4), 16)},${parseInt(h.slice(4, 6), 16)},${a})`; }
function palOf(c) { return PALETTES[c.palette] || PALETTES.founder; }
function lucide(name) {
  const d = ICONS[ICON_ALIAS[name] || name];
  return d ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>` : "";
}
function autoIcon(text, c) { for (const [re, n] of KEYWORDS) if (re.test(text || "")) return n; return palOf(c).icon; }
const escH = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// Duotone: map each grey level from the palette's background (shadows) to its accent2 (highlights).
const DUO = {};
function duoKey(scene, c) { return scene + "|" + c.palette; }
function duotone(scene, c) {
  const k = duoKey(scene, c);
  if (DUO[k] || !PHOTOS[scene]) return Promise.resolve(DUO[k]);
  const p = palOf(c);
  return new Promise((res) => {
    const img = new Image();
    img.onload = () => {
      const cv = document.createElement("canvas"); cv.width = img.naturalWidth; cv.height = img.naturalHeight;
      const x = cv.getContext("2d"); x.drawImage(img, 0, 0);
      const d = x.getImageData(0, 0, cv.width, cv.height), a = d.data;
      const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
      // Three stops: background in the shadows, card-to-accent2 in the mids, accent2 in the highlights (gamma darkens it).
      const lo = rgb(p.bg), hi = rgb(p.accent2), mid = rgb(p.card).map((v, i) => v + (hi[i] - v) * 0.4);
      const lut = [0, 1, 2].map((ch) => Array.from({ length: 256 }, (_, v) => {
        const t = Math.pow(v / 255, 1.35);
        return Math.round(t < 0.5 ? lo[ch] + (mid[ch] - lo[ch]) * (t / 0.5) : mid[ch] + (hi[ch] - mid[ch]) * ((t - 0.5) / 0.5));
      }));
      for (let i = 0; i < a.length; i += 4) { const v = a[i]; a[i] = lut[0][v]; a[i + 1] = lut[1][v]; a[i + 2] = lut[2][v]; }
      x.putImageData(d, 0, 0);
      res((DUO[k] = cv.toDataURL("image/jpeg", 0.85)));
    };
    img.onerror = () => res(undefined);
    img.src = PHOTOS[scene];
  });
}
// Call before buildSlide(): duotones every photo the carousel uses.
function prepare(c) {
  const scenes = new Set(c.slides.map((s) => s.photoScene || s.scene || (s.illustrationTop ? "blueprint" : "")).filter(Boolean));
  return Promise.all([...scenes].map((sc) => duotone(sc, c)));
}

function slideVars(c, H) {
  const p = palOf(c);
  return `--H:${H}px;--bg:${p.bg};--card:${p.card};--ac:${p.accent};--ac2:${p.accent2};--mut:${p.muted};` +
    `--line:${rgba(p.accent, 0.38)};--grid:${rgba(p.accent, 0.06)};--glow:${rgba(p.accent2, 0.28)};--glow2:${rgba(p.accent, 0.14)};` +
    `--soft:${rgba(p.accent, 0.14)};--track:${rgba(p.accent, 0.22)};--chipbg:${rgba(p.bg, 0.72)}`;
}

const CHECK_SVG = () => lucide("check");
const ARROW_SVG = () => lucide("arrow-right").replace("<svg ", '<svg class="ar" ');

function buildSlide(c, s, opts) {
  opts = opts || {};
  const photos = opts.photos || {}, H = opts.H || 1350, total = c.slides.length;
  const key = `${c.id}-${s.n}`;
  const icon = (n, cls) => { const svg = lucide(n); return svg ? `<span class="ic ${cls || ""}">${svg}</span>` : ""; };
  const checks = (a) => `<ul class="cl">${a.map((t) => `<li>${CHECK_SVG()}<span>${escH(t)}</span></li>`).join("")}</ul>`;
  const pull = (t) => (t ? `<div class="pull">${escH(t)}</div>` : "");
  const src = (t) => (t ? `<div class="src">${escH(t)}</div>` : "");
  const flow = (f, cls) => `<div class="flow ${cls || ""} ${f.length > 3 ? "n4" : ""}">${f.map((x, i) => (i ? ARROW_SVG() : "") + `<div class="tile">${icon(x[1])}<div class="tl2">${escH(x[0])}</div></div>`).join("")}</div>`;
  const photoBox = (w, h) => {
    const u = photos[key];
    return `<div class="photo ${u ? "" : "empty"}" style="width:calc(${w} * var(--u));height:calc(${h} * var(--u));${u ? `background-image:url(${u});` : ""}">${u ? "" : '<span class="ph no-export">Portrait goes here</span>'}</div>`;
  };
  const cardHtml = (cd, i, numbered) => {
    const lead = cd.icon ? icon(cd.icon) : numbered ? `<div class="stepn">${i + 1}</div>` : icon(autoIcon(`${cd.title || ""} ${cd.body || ""}`, c));
    return `<div class="card ${cd.accent ? "accent" : ""}">${cd.accent ? "" : lead}<div class="tx">${cd.title ? `<div class="ct">${escH(cd.title)}</div>` : ""}${cd.body ? `<div class="cb ${cd.italic ? "it" : ""}">${escH(cd.body)}</div>` : ""}${cd.checklist ? checks(cd.checklist) : ""}${cd.pills ? `<div class="pills">${cd.pills.map((p) => `<span class="pill">${escH(p)}</span>`).join("")}</div>` : ""}${cd.pullLine ? `<div class="pull" style="margin-top:10px">${escH(cd.pullLine)}</div>` : ""}</div></div>`;
  };
  const head = () => `<div class="head"><div class="krow"><span class="hb">${lucide(autoIcon(s.kicker + " " + s.headline, c))}</span><div class="kicker">${escH(s.kicker)}</div></div><div class="h1">${escH(s.headline)}</div>${s.subtitle ? `<div class="sub">${escH(s.subtitle)}</div>` : ""}</div>`;
  const banner = () => {
    if (!s.scene) return "";
    const u = photos[key + "-b"] || DUO[duoKey(s.scene, c)];
    return `<div class="banner" style="${u ? `background-image:url(${u})` : ""}"><span class="bi">${lucide(SCENE_ICON[s.scene] || "image")}</span></div>`;
  };
  // Last word of the cover headline in the accent colour.
  const accentLast = (t) => { const e = escH(t), i = e.trimEnd().lastIndexOf(" "); return i < 0 ? `<em>${e}</em>` : `${e.slice(0, i)} <em>${e.slice(i + 1)}</em>`; };

  const t = s.template;
  let h = "", b = "", bgLayer = "";
  if (t === "cover") {
    const hasPh = !!s.photo, p = palOf(c);
    const u = photos[key + "-bg"] || DUO[duoKey(s.photoScene || s.scene, c)];
    bgLayer = (u ? `<div class="art" style="background-image:url(${u})"></div>` : "") +
      `<div class="veil" style="background:linear-gradient(180deg,${rgba(p.bg, 0.55)} 0%,${rgba(p.bg, 0.4)} 22%,${rgba(p.bg, 0.6)} 40%,${rgba(p.bg, 0.9)} 58%,${p.bg} 78%)"></div>`;
    h = `<div class="ctop"><span class="chip">${lucide(p.icon)}${escH(p.name)}</span></div>`;
    const left = `<div class="col"><div class="bar"></div><div class="kicker" style="margin-bottom:calc(18 * var(--u))">${escH(s.kicker)}</div><div class="h1 big ${hasPh ? "withph" : ""}">${accentLast(s.headline)}</div><div class="sub">${escH(s.subline)}</div>${s.pills ? `<div class="pills" style="margin-top:26px">${s.pills.map((x) => `<span class="pill">${escH(x)}</span>`).join("")}</div>` : ""}${src(s.sourceLine)}</div>`;
    b = `<div class="spacer"></div><div class="cover-row">${left}${hasPh ? photoBox(340, 470) : ""}</div>`;
  } else {
    h = head();
    if (t === "cards_stack") {
      const numbered = s.cards.every((x) => !x.icon && !x.title);
      let top = "";
      if (s.illustrationTop) { const u = photos[key] || DUO[duoKey(s.scene || "blueprint", c)]; top = u ? `<div class="illo" style="background-image:url(${u})"></div>` : ""; }
      b = top + s.cards.map((x, i) => cardHtml(x, i, numbered)).join("");
    } else if (t === "table_compare") {
      b = `<div class="tbl"><div class="tr th"><span>${escH(s.columns[0])}</span><span></span><span>${escH(s.columns[1])}</span></div>${s.rows.map((r) => `<div class="tr"><span>${escH(r[0])}</span>${lucide("arrow-right")}<span>${escH(r[1])}</span></div>`).join("")}</div>`;
    } else if (t === "stats_rows") {
      b = s.rows.map((r) => `<div class="card rowstat"><div class="lb">${escH(r[0])}</div><div class="tx">${escH(r[1])}</div></div>`).join("");
    } else if (t === "stats_cards") {
      b = s.stats.map((x) => `<div class="card scard"><div class="sn">${escH(x[0])}</div><div class="sl">${escH(x[1])}</div></div>`).join("");
    } else if (t === "stats_grid") {
      const items = s.stats
        ? s.stats.map((x) => `<div class="card"><div class="sn sm">${escH(x[0])}</div><div class="sl">${escH(x[1])}</div></div>`)
        : s.cards.map((x) => `<div class="card">${icon(autoIcon(x[0] + " " + x[1], c), "sm")}<div class="ct">${escH(x[0])}</div><div class="cb">${escH(x[1])}</div></div>`);
      b = `<div class="g2">${items.join("")}</div>`;
    } else if (t === "timeline_vertical") {
      h = `<div class="head" style="display:flex;gap:30px;align-items:flex-start"><div style="flex:1;min-width:0"><div class="krow"><span class="hb">${lucide("clock")}</span><div class="kicker">${escH(s.kicker)}</div></div><div class="h1">${escH(s.headline)}</div>${s.subtitle ? `<div class="sub">${escH(s.subtitle)}</div>` : ""}</div>${s.photo ? photoBox(330, 380) : ""}</div>`;
      b = `<div class="tl">${s.points.map((p) => `<div class="pt">${escH(p)}</div>`).join("")}</div>`;
    } else if (t === "flow_steps") {
      b = (s.body ? `<div class="cb">${escH(s.body)}</div>` : "") + flow(s.flow) + (s.cards || []).map((x, i) => cardHtml(x, i, false)).join("");
    } else if (t === "name_cards_grid") {
      b = `<div class="cb">${escH(s.body)}</div><div class="g2">${s.names.map((n) => `<div class="card mono"><div class="m">${escH(n[0])}</div><div class="nm">${escH(n[1])}</div>${n[2] ? `<div class="tg">${escH(n[2])}</div>` : ""}</div>`).join("")}</div>`;
    } else if (t === "stat_flow_checklist") {
      b = `<div class="card rowstat"><div class="lb">${escH(s.topCard[0])}</div><div class="tx">${escH(s.topCard[1])}</div></div>` + flow(s.flow, "compact") + `<div class="card" style="align-items:flex-start"><div class="tx"><div class="ct">${escH(s.checklistTitle)}</div>${checks(s.checklist)}</div></div>`;
    } else if (t === "numbered_cta") {
      b = s.rows.map((r, i) => `<div class="nrow"><div class="no">${i + 1}</div><div class="t">${escH(r)}</div></div>`).join("") + `<div class="cta">${escH(s.button)}</div><div class="follow">${escH(s.followLine)}</div>`;
    }
    if (t !== "numbered_cta") b += pull(s.pullLine);
    b += src(s.sourceLine);
    if (t !== "numbered_cta" && !(t === "timeline_vertical" && s.photo) && !s.illustrationTop) b = banner() + b;
  }
  const prog = Array.from({ length: total }, (_, i) => `<i class="${i < s.n ? "on" : ""}"></i>`).join("");
  const el = document.createElement("div");
  el.className = "slide";
  el.setAttribute("style", slideVars(c, H));
  el.innerHTML = `<div class="bg"></div>${bgLayer}${h}<div class="body">${b}</div><div class="foot"><div class="prog">${prog}</div><div class="fl"><span>@StephenJemalNY</span><span>${s.n}/${total}</span></div></div>`;
  return el;
}

// Shrinks the slide's type scale until nothing overflows.
function fit(el) {
  let k = 1; el.style.setProperty("--k", k);
  const b = el.querySelector(".body"); let g = 0;
  const over = () => b.scrollHeight > b.clientHeight + 2 || [...el.querySelectorAll(".h1,.tl2,.rowstat .lb")].some((h) => h.scrollWidth > h.clientWidth + 1);
  while (over() && k > 0.45 && g++ < 60) { k -= 0.02; el.style.setProperty("--k", k.toFixed(3)); }
}
