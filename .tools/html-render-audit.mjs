#!/usr/bin/env node
// HTML 渲染验收（通用引擎）：CDP 连本地 Chrome → 加载页面 → 逐元素几何审计（尺寸/溢出/超限）→ 可选 printToPDF 成品 + 逐元素截图 + 自定义探针表达式
// 零 npm 依赖（Node ≥22——原生 fetch 需 18+、全局 WebSocket 客户端 22 起默认可用，20.x 会 ReferenceError）。语言归属：浏览器/CDP 域 = Node。
// 用法：
//   node .tools/html-render-audit.mjs --url <file:///...|https://...> [--port 9222] [--selector .page]
//     [--pdf <out.pdf>] [--shots <dir>] [--shots-prefix page] [--scale 2]
//     [--max-h <px>] [--wait <ms>] [--eval "<js 表达式，返回值打印>"]
// 退出码：0 = 几何全过；1 = 有溢出或超 --max-h；2 = 参数/连接错误。
// Chrome 需先带调试端口启动（渲染验证类无需登录态，user-data-dir 用临时目录即可）：
//   chrome.exe --headless=new --remote-debugging-port=9222 --user-data-dir=<临时目录> about:blank
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const url = opt('url');
if (!url) { console.error('需要 --url <file:///...|https://...>'); process.exit(2); }
const port = opt('port', '9222');
const selector = opt('selector', '.page');
const pdfOut = opt('pdf');
const shotsDir = opt('shots');
const shotsPrefix = opt('shots-prefix', 'page');
const scale = Number(opt('scale', 2));
const maxH = Number(opt('max-h', 0));
const evalExpr = opt('eval');
const waitMs = Number(opt('wait', 2500));

const tabs = await (await fetch(`http://localhost:${port}/json/list`)).json();
const tab = tabs.find(t => t.type === 'page');
if (!tab) { console.error(`端口 ${port} 无可用页面 tab（Chrome 是否已带 --remote-debugging-port 启动？）`); process.exit(2); }
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let seq = 0; const pending = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1000, height: 1400, deviceScaleFactor: 2, mobile: false });
await send('Page.navigate', { url });
await sleep(waitMs);

// 逐元素几何：尺寸 + 内容溢出（scrollHeight > clientHeight 即裁切）
const r = await send('Runtime.evaluate', {
  expression: `JSON.stringify([...document.querySelectorAll(${JSON.stringify(selector)})].map((p, i) => { const b = p.getBoundingClientRect(); return { i, x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height), overflowPx: p.scrollHeight > p.clientHeight ? p.scrollHeight - p.clientHeight : 0, scrollY: window.scrollY }; }))`,
  returnByValue: true,
});
const raw = r.result?.result?.value;
if (raw === undefined) { console.error(`evaluate 无返回值（页面未加载成功或选择器 ${selector} 无命中）`); process.exit(2); }
const metas = JSON.parse(raw);
const bad = metas.filter(m => m.overflowPx > 0 || (maxH > 0 && m.h > maxH));
console.log('audit:', JSON.stringify(metas.map(m => ({ i: m.i, w: m.w, h: m.h, overflowPx: m.overflowPx }))));
console.log(`result: ${metas.length} 个元素（${selector}），溢出/超限 ${bad.length} 个${maxH > 0 ? `（max-h ${maxH}px）` : ''}`);

if (evalExpr) {
  const er = await send('Runtime.evaluate', { expression: evalExpr, returnByValue: true });
  console.log('probe:', er.result.result.value);
}

if (shotsDir) {
  mkdirSync(shotsDir, { recursive: true });
  for (const m of metas) {
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: m.y + m.scrollY, width: m.w, height: m.h, scale } });
    if (shot.error) throw new Error(JSON.stringify(shot.error));
    const p = `${shotsDir}/${shotsPrefix}-${m.i + 1}.png`;
    writeFileSync(p, Buffer.from(shot.result.data, 'base64'));
    console.log('shot:', p);
  }
}

if (pdfOut) {
  const pdf = await send('Page.printToPDF', { printBackground: true, preferCSSPageSize: true });
  writeFileSync(pdfOut, Buffer.from(pdf.result.data, 'base64'));
  console.log('pdf:', pdfOut, `(${pdf.result.data.length} bytes base64)`);
}

ws.close();
process.exit(bad.length ? 1 : 0);
