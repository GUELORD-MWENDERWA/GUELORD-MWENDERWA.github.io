// Rend les images de partage (1200 × 630) à partir des gabarits og/<langue>.html produits par build.py.
// Usage : node tools/og.mjs   →  assets/og-en.png, assets/og-fr.png
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const req = createRequire(join(execSync("npm root -g").toString().trim(), "noop.js"));
const { chromium } = req("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
for (const lang of ["en", "fr"]) {
  await page.goto(pathToFileURL(join(root, "og", `${lang}.html`)).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: join(root, "assets", `og-${lang}.png`) });
  console.log(`assets/og-${lang}.png`);
}
await browser.close();
