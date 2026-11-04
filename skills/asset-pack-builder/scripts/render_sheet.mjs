#!/usr/bin/env node
// Render real thumbnails of every model in a pack and compose contact sheets.
//
//   npm i playwright && npx playwright install chromium     (once)
//   node render_sheet.mjs art/<pack>/manifest.json [--cols 8] [--size 512] [--cell 300]
//
// Writes, next to manifest.json:
//   thumbs/<asset_id>.png, thumbs/<asset_id>__<variant>.png, thumbs/<asset_id>__parts.png
//   contact-sheet.png   every base model, in plan order (the hero image for a launch post)
//   variants-sheet.png  each asset with variants, base first, then its variants and parts
//
// Uses local files when present, otherwise the public Sloyd URLs. Headless Chromium renders
// with SwiftShader, so no GPU is needed. Rendering one model per page load is deliberate:
// one page with 40 live WebGL viewers screenshots blank in headless mode.

import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const manifestPath = path.resolve(args.find(a => a.endsWith('.json')) || 'manifest.json');
const cols = +opt('cols', 8), size = +opt('size', 512), cell = +opt('cell', 300);
const base = path.dirname(manifestPath);
const man = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const VIEWER = 'https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js';
const ok = j => j && ['success', 'completed'].includes(j.status);

const items = []; // {key, src}
for (const a of man.assets) {
  for (const [k, j] of Object.entries(a.jobs || {})) {
    if (!ok(j) || !(k === 'model' || k === 'split' || k.startsWith('variant:'))) continue;
    const key = k === 'model' ? a.id : k === 'split' ? `${a.id}__parts` : `${a.id}__${k.split(':')[1]}`;
    const local = j.file && fs.existsSync(path.join(base, j.file));
    items.push({ key, asset: a.id, stage: k, src: local ? '/' + j.file.split(path.sep).join('/') : j.url });
  }
}

const server = http.createServer((q, r) => {
  const p = path.join(base, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(base) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  const ext = path.extname(p);
  r.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.png': 'image/png', '.glb': 'model/gltf-binary' }[ext] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(r);
}).listen(0);
const origin = `http://127.0.0.1:${server.address().port}`;
const tmp = path.join(base, '_render.html');

const browser = await chromium.launch();
try {
  fs.mkdirSync(path.join(base, 'thumbs'), { recursive: true });
  fs.writeFileSync(tmp, `<!doctype html><html><head><script type="module" src="${VIEWER}"></script>
<style>html,body{margin:0;background:transparent}model-viewer{width:${size}px;height:${size}px;--poster-color:transparent}</style></head>
<body><model-viewer id=m environment-image="neutral" exposure="1.1" shadow-intensity="1" shadow-softness="0.8"
camera-orbit="35deg 68deg 105%" field-of-view="28deg" interaction-prompt="none"></model-viewer></body></html>`);
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.goto(`${origin}/_render.html`);
  await page.waitForFunction(() => customElements.get('model-viewer'), null, { timeout: 60000 });
  for (const it of items) {
    try {
      await page.evaluate(src => new Promise((res, rej) => {
        const m = document.getElementById('m');
        const t = setTimeout(() => rej(new Error('timeout')), 120000);
        m.addEventListener('load', () => { clearTimeout(t); res(); }, { once: true });
        m.addEventListener('error', e => { clearTimeout(t); rej(new Error('load error')); }, { once: true });
        m.src = src;
      }), it.src);
      await page.waitForTimeout(1200);
      await page.locator('#m').screenshot({ path: path.join(base, 'thumbs', `${it.key}.png`), omitBackground: true });
      it.thumb = `thumbs/${it.key}.png`;
      console.log('thumb', it.key);
    } catch (e) {
      console.error('skip', it.key, e.message);
    }
  }

  async function sheet(rowsOfKeys, out, ncols) {
    const keys = rowsOfKeys.flat();
    if (!keys.length) return;
    const pad = 12, w = ncols * cell + (ncols + 1) * pad;
    const cells = rowsOfKeys.map(row => row.map(k => `<div class=c><img src="/thumbs/${k}.png"></div>`).join('')
      + '<div class=c style="visibility:hidden"></div>'.repeat(Math.max(0, ncols - row.length))).join('');
    fs.writeFileSync(tmp, `<!doctype html><html><body style="margin:0;background:#0b1833">
<div style="display:grid;grid-template-columns:repeat(${ncols},${cell}px);gap:${pad}px;padding:${pad}px;width:${w}px;box-sizing:border-box">${cells}</div>
<style>.c{width:${cell}px;height:${cell}px;border-radius:18px;background:#12234a;overflow:hidden}.c img{width:100%;height:100%}</style></body></html>`);
    const p = await browser.newPage({ viewport: { width: w, height: 400 } });
    await p.goto(`${origin}/_render.html`);
    await p.waitForFunction(() => [...document.images].every(i => i.complete));
    await p.screenshot({ path: path.join(base, out), fullPage: true });
    await p.close();
    console.log('sheet', out);
  }

  const done = new Set(items.filter(i => i.thumb).map(i => i.key));
  const baseKeys = man.assets.map(a => a.id).filter(k => done.has(k));
  const rows = [];
  for (let i = 0; i < baseKeys.length; i += cols) rows.push(baseKeys.slice(i, i + cols));
  await sheet(rows, 'contact-sheet.png', cols);

  const groups = man.assets.map(a => items.filter(i => i.asset === a.id && i.thumb).map(i => i.key)).filter(g => g.length > 1);
  if (groups.length) await sheet(groups, 'variants-sheet.png', Math.max(...groups.map(g => g.length)));
} finally {
  if (fs.existsSync(tmp)) fs.unlinkSync(tmp);
  await browser.close();
  server.close();
}
