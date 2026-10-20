// Captures pleine page du site (390 et 1440 px), après défilement pour charger les images
// différées, avec contrôle des débordements horizontaux, des erreurs JS et des requêtes en échec.
//
// Usage : node tools/apercu.mjs [page.html …] [--sombre] [--serveur http://127.0.0.1:8765]
//         sans page : index.html et fr/index.html (fichiers locaux) ; 404.html en plus avec --serveur,
//         car la page 404 utilise des chemins absolus (python3 -m http.server 8765 dans ce dossier).
// Sortie : docs/maquettes/captures/<largeur>/<nom>[-sombre].jpg (densité 1, pour ne pas alourdir Git)
// Nécessite Playwright installé globalement (npm install -g playwright).
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const req = createRequire(join(execSync("npm root -g").toString().trim(), "noop.js"));
const { chromium } = req("playwright");

const args = process.argv.slice(2);
const dark = args.includes("--sombre");
const serverIndex = args.indexOf("--serveur");
const server = serverIndex >= 0 ? args.splice(serverIndex, 2)[1].replace(/\/$/, "") : null;
const pages = args.filter((a) => !a.startsWith("--"));
const targets = pages.length ? pages : ["index.html", "fr/index.html", ...(server ? ["404.html"] : [])];
const urlOf = (target) => server ? `${server}/${target.replace(/(^|\/)index\.html$/, "$1")}` : pathToFileURL(join(root, target)).href;

const browser = await chromium.launch();
let failures = 0;
for (const target of targets) {
  const name = target.replace(/\/index\.html$/, "").replace(/\.html$/, "").replace(/\//g, "-").replace(/^index$/, "accueil");
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1, colorScheme: dark ? "dark" : "light" });
    const problems = [];
    page.on("pageerror", (e) => problems.push(`erreur JS : ${e.message}`));
    page.on("console", (m) => { if (m.type() === "error") problems.push(`console : ${m.text().slice(0, 160)}`); });
    page.on("requestfailed", (r) => problems.push(`requête échouée : ${r.url().slice(0, 120)}`));
    await page.goto(urlOf(target), { waitUntil: "load", timeout: 60000 });
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => { /* réseau lent : on capture quand même */ });
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < height; y += 500) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(80); }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(600);
    const result = await page.evaluate(() => {
      const w = window.innerWidth;
      const offenders = [];
      for (const el of document.body.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.right <= w + 1) continue;
        let p = el.parentElement;
        while (p && p !== document.body && !["auto", "scroll", "hidden", "clip"].includes(getComputedStyle(p).overflowX)) p = p.parentElement;
        if (p && p !== document.body) continue;
        offenders.push(`${el.tagName.toLowerCase()}.${String(el.className).split(" ")[0]} (+${Math.round(r.right - w)} px)`);
      }
      const broken = [...document.images].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.src);
      return { overflow: document.documentElement.scrollWidth - w, offenders: offenders.slice(0, 5), broken };
    });
    const dir = join(root, "docs/maquettes/captures", String(width));
    mkdirSync(dir, { recursive: true });
    const file = join(dir, `${name}${dark ? "-sombre" : ""}.jpg`);
    await page.screenshot({ path: file, fullPage: true, type: "jpeg", quality: 62 });
    const bad = result.overflow > 0 || result.offenders.length || result.broken.length || problems.length;
    if (bad) failures++;
    console.log(`${bad ? "✘" : "✓"} ${width} px  ${target}${dark ? " (sombre)" : ""}  débordement ${result.overflow} px`);
    for (const o of result.offenders) console.log(`   dépasse : ${o}`);
    for (const b of result.broken) console.log(`   image cassée : ${b}`);
    for (const p of problems) console.log(`   ${p}`);
    await page.close();
  }
}
await browser.close();
process.exit(failures ? 2 : 0);
