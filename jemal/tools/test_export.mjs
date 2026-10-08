// Click the studio's export buttons in headless Chrome and save what they download.
// Usage: node tools/test_export.mjs <carouselIndex> [libsDir]
// CDN script requests are served from local node_modules (cdnjs is blocked here).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(path.resolve("/home/user/open-carrusel/package.json"));
const puppeteer = require("puppeteer");
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const ci = Number(process.argv[2] || 0);
const LIBS = process.argv[3];
const OUT = path.join(ROOT, "previews", "export-test");
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const args = ["--no-sandbox"];
if (process.env.HTTPS_PROXY) args.push(`--proxy-server=${process.env.HTTPS_PROXY}`);
const browser = await puppeteer.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args });
const page = await browser.newPage();
const logs = [];
page.on("console", (m) => logs.push(`${m.type()}: ${m.text()}`));
page.on("pageerror", (e) => logs.push(`pageerror: ${e.message}`));
await page.setRequestInterception(true);
page.on("request", (r) => {
  const u = r.url();
  const map = { "html2canvas.min.js": "html2canvas/dist/html2canvas.min.js", "jszip.min.js": "jszip/dist/jszip.min.js" };
  const hit = LIBS && Object.keys(map).find((k) => u.includes("cdnjs") && u.endsWith(k));
  if (process.env.OFFLINE && !u.startsWith("file:") && !u.startsWith("data:") && !u.startsWith("blob:")) return r.abort();
  if (hit) return r.respond({ status: 200, contentType: "application/javascript", body: fs.readFileSync(path.join(LIBS, "node_modules", map[hit])) });
  r.continue();
});
const cdp = await page.createCDPSession();
await cdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: OUT });
await page.setViewport({ width: 1300, height: 1200 });
await page.goto(pathToFileURL(path.join(ROOT, "jemal_carousel_studio.html")).href, { waitUntil: "networkidle0" });
await page.select("#carSel", String(ci));
await new Promise((r) => setTimeout(r, 1500));

async function run(btn, label) {
  const t0 = Date.now();
  await page.click(btn);
  await page.waitForFunction((b) => !document.querySelector(b).disabled, { timeout: 120000 }, btn).catch(() => {});
  await new Promise((r) => setTimeout(r, 1500));
  const st = await page.$eval("#st", (e) => e.textContent);
  console.log(`${label}: status="${st}" (${Date.now() - t0} ms)`);
}
const blocked = await page.evaluate(() => performance.getEntriesByType("resource").map((e) => e.name).filter((n) => !n.startsWith("data:")));
console.log("external requests:", blocked.length ? blocked : "none");
await run("#btnOne", "single PNG");
await run("#btnZip", "ZIP");
console.log("downloads:", fs.readdirSync(OUT));
console.log("export panel images:", await page.$$eval("#expList img", (a) => a.length));
console.log(logs.slice(0, 15).join("\n"));
await browser.close();
