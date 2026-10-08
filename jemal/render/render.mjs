// Final PNGs with Remotion renderStill: one folder per carousel ("01 - Title"), slides 01.png-05.png, plus a ZIP.
// Usage: node render.mjs [ids...]   (no ids = all 52)
// PORTRAIT=/path/photo.jpg fills the three portrait frames. Output goes to jemal/out/ (gitignored).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { bundle } from "@remotion/bundler";
import { openBrowser, renderStill, selectComposition } from "@remotion/renderer";
import JSZip from "jszip";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const JEMAL = path.dirname(HERE);
execFileSync("python3", [path.join(JEMAL, "tools", "build.py")], { stdio: "inherit" });
const design = JSON.parse(fs.readFileSync(path.join(JEMAL, "jemal_carousel_design.json"), "utf8"));
const ids = process.argv.slice(2).map(Number);
const cars = design.carousels.filter((c) => !ids.length || ids.includes(c.id));
const portrait = process.env.PORTRAIT ? `data:image/jpeg;base64,${fs.readFileSync(process.env.PORTRAIT).toString("base64")}` : null;
const ROOTDIR = "StephenJemalNY carousels 1080x1350";
const OUT = path.join(JEMAL, "out", ROOTDIR);
const pad = (n) => String(n).padStart(2, "0");
const folderName = (c) => `${pad(c.id)} - ${String(c.title).replace(/[\\/:*?"<>|]+/g, "").replace(/\s+/g, " ").trim()}`;

const serveUrl = await bundle({ entryPoint: path.join(HERE, "src", "index.js") });
const chromium = process.env.CHROME_PATH || "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
const browser = await openBrowser("chrome", { browserExecutable: chromium, chromiumOptions: { disableWebSecurity: false } });
const zip = new JSZip();
const missing = [];
for (const c of cars) {
  const dir = path.join(OUT, folderName(c));
  fs.mkdirSync(dir, { recursive: true });
  for (const s of c.slides) {
    const inputProps = { id: c.id, n: s.n, portrait: s.photo ? portrait : null };
    if (s.photo && !portrait) missing.push(`${c.id}/${s.n}`);
    const composition = await selectComposition({ serveUrl, id: "Slide", inputProps, puppeteerInstance: browser, browserExecutable: chromium });
    const output = path.join(dir, `${pad(s.n)}.png`);
    await renderStill({ composition, serveUrl, output, inputProps, imageFormat: "png", puppeteerInstance: browser, browserExecutable: chromium });
    zip.file(`${ROOTDIR}/${folderName(c)}/${pad(s.n)}.png`, fs.readFileSync(output));
  }
  console.log(`carousel ${c.id}: ${c.slides.length} slides`);
}
await browser.close({ silent: true });
const zipPath = path.join(JEMAL, "out", "StephenJemalNY-carousels-1080x1350.zip");
fs.writeFileSync(zipPath, await zip.generateAsync({ type: "nodebuffer", compression: "STORE" }));
console.log(`Wrote ${zipPath}` + (missing.length ? `. Empty portrait frames: ${missing.join(", ")} (set PORTRAIT=...)` : ""));
