// Render 1080x1350 PNG previews of selected carousels from the studio, plus one
// contact sheet per carousel. Usage: node tools/render_previews.mjs 1 10 35
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(path.resolve("/home/user/open-carrusel/package.json"));
const puppeteer = require("puppeteer");

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = path.join(ROOT, "previews");
fs.mkdirSync(OUT, { recursive: true });
const ids = process.argv.slice(2).map(Number);

const args = ["--no-sandbox"];
if (process.env.HTTPS_PROXY) args.push(`--proxy-server=${process.env.HTTPS_PROXY}`);
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
  args,
});
const page = await browser.newPage();
await page.setViewport({ width: 1300, height: 1500 });
await page.goto(pathToFileURL(path.join(ROOT, "jemal_carousel_studio.html")).href, { waitUntil: "load" });
await page.evaluate(() => document.fonts.ready);

for (const id of ids) {
  const files = [];
  const n = await page.evaluate((id) => DATA.find((c) => c.id === id).slides.length, id);
  for (let i = 0; i < n; i++) {
    await page.evaluate((id, i) => {
      const c = DATA.find((x) => x.id === id);
      const host = document.getElementById("shot") || Object.assign(document.createElement("div"), { id: "shot" });
      host.style.cssText = "position:fixed;left:0;top:0;z-index:99";
      host.innerHTML = "";
      document.body.appendChild(host);
      const el = buildSlide(c, c.slides[i]);
      host.appendChild(el);
      fit(el);
    }, id, i);
    await page.evaluate(() => document.fonts.ready);
    const el = await page.$("#shot .slide");
    const f = path.join(OUT, `c${String(id).padStart(2, "0")}-s${i + 1}.png`);
    await el.screenshot({ path: f });
    files.push(f);
  }
  // Contact sheet: all slides side by side at 40%.
  const sheet = await browser.newPage();
  await sheet.setViewport({ width: 5 * 432 + 6 * 16, height: 540 + 32 });
  const imgs = files.map((f) => `<img src="data:image/png;base64,${fs.readFileSync(f).toString("base64")}">`).join("");
  await sheet.setContent(`<body style="margin:0;background:#070d18;display:flex;gap:16px;padding:16px">${imgs.replace(/<img /g, '<img style="width:432px;height:540px;border-radius:6px" ')}</body>`);
  await sheet.screenshot({ path: path.join(OUT, `c${String(id).padStart(2, "0")}-sheet.png`) });
  await sheet.close();
  console.log(`carousel ${id}: ${files.length} slides`);
}
await browser.close();
