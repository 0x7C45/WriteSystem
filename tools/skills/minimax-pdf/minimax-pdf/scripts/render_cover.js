#!/usr/bin/env node
/**
 * render_cover.js — Render cover.html → cover.pdf via Playwright.
 *
 * Usage:
 *   node render_cover.js --input cover.html --out cover.pdf [--wait <ms>]
 *   USE_SYSTEM_CHROME=1 node render_cover.js --input cover.html --out cover.pdf
 *
 * Environment:
 *   USE_SYSTEM_CHROME=1     — Use system Chrome instead of Playwright Chromium
 *   CHROME_PATH=/path/to/chrome — custom Chrome path
 */

const path = require("path");
const fs   = require("fs");
const { execSync } = require("child_process");

function usage() {
  console.error("Usage: node render_cover.js --input <file.html> --out <file.pdf> [--wait <ms>]");
  process.exit(1);
}

// --- Arg parsing
const args = process.argv.slice(2);
let inputFile = null;
let outFile = null;
let waitMs = 800;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--input") inputFile = args[++i];
  else if (args[i] === "--out")   outFile = args[++i];
  else if (args[i] === "--wait") waitMs = parseInt(args[++i], 10);
}

if (!inputFile || !outFile) usage();
if (!fs.existsSync(inputFile)) {
  console.error(JSON.stringify({ status: "error", error: `File not found: ${inputFile}` }));
  process.exit(1);
}

// --- Playwright loader ---
function loadPlaywright() {
  try {
    return require("playwright");
  } catch (_) {
    try {
      const root = execSync("npm root -g", { stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
      return require(path.join(root, "playwright"));
    } catch (_) {
      console.error(JSON.stringify({
        status: "error",
        error: "playwright not found",
        hint: "Run: npm install -g playwright && npx playwright install chromium"
      }));
      process.exit(2);
    }
  }
}

// --- Main ---
(async () => {
  const playwright = loadPlaywright();
  const { chromium } = playwright;

  const sysChrome = process.env.CHROME_PATH ||
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  const useSystemChrome = !!process.env.USE_SYSTEM_CHROME || !!process.env.CHROME_PATH;
  let browser;

  try {
    if (useSystemChrome) {
      // System Chrome explicitly requested
      browser = await chromium.launch({ executablePath: sysChrome });
    } else {
      // Try Playwright Chromium first
      browser = await chromium.launch();
    }
  } catch (e) {
    // Playwright Chromium not installed — fallback to system Chrome
    if (fs.existsSync(sysChrome)) {
      browser = await chromium.launch({ executablePath: sysChrome });
    } else {
      console.error(JSON.stringify({
        status: "error",
        error: "No browser available",
        hint: "Run: npx playwright install chromium, or set USE_SYSTEM_CHROME=1"
      }));
      process.exit(2);
    }
  }

  try {
    const page = await browser.newPage();
    const fileUrl = "file://" + path.resolve(inputFile);
    await page.goto(fileUrl);
    await page.waitForTimeout(waitMs);

    await page.pdf({
      path:            outFile,
      width:           "794px",
      height:          "1123px",
      printBackground: true,
    });

    await browser.close();

    // Basic sanity: output file must exist and > 5 KB
    const stat = fs.statSync(outFile);
    if (stat.size < 5000) {
      console.error(JSON.stringify({
        status: "error",
        error: "Output PDF is suspiciously small — cover may be blank",
        hint: "Check cover.html for render errors"
      }));
      process.exit(3);
    }

    console.log(JSON.stringify({
      status: "ok",
      out:    outFile,
      size_kb: Math.round(stat.size / 1024),
    }));

  } catch (e) {
    if (browser) await browser.close().catch(() => {});
    console.error(JSON.stringify({ status: "error", error: String(e) }));
    process.exit(3);
  }
})();
