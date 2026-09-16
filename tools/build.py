# -*- coding: utf-8 -*-
"""
建置腳本：產生索引頁、PWA manifest、service worker，並在各文件注入 App 導覽列。

用法（在專案根目錄）：
    python tools/build.py

新增或刪除 HTML 後重跑一次，index.html 與離線快取清單就會跟著更新。
"""
import os, re, sys, json, html, hashlib, datetime, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

APP_NAME = "AI 筆記庫"
ACCENT = "#b4530a"

# ---------------------------------------------------------------- 分類定義
CATS = [
 ("Claude 入門與操作", "從零上手到進階，Claude 的功能、模式與生態", [
   "claude-quickstart-guide.html","claude-30min-learning-guide.html","claude-ai-7day-guide.html",
   "Claude功能完整指南.html","claude-4-modes.html","claude-six-levels.html",
   "claude-ecosystem-reference.html","claude-mastery-climb.html",
   "claude-fable5-提示詞完全指南.html","claude-project-skills-cowork-指南.html",
   "claude-skills-評估.html","claude-voice-workflow.html"]),
 ("Claude Code 與開發流程", "用 Claude Code 建網站、做 Agent、跑 Cowork", [
   "claude-code-速成指南.html","claude-code-7steps-guide.html","claude-code-架構藍圖.html",
   "claude-website-sop.html","claude-design-速成指南.html","ai-agent-sop.html",
   "ai-agent-blueprint.html","cowork-sop.html","github-upload-guide.html"]),
 ("AI 工程架構與自動化", "提示／脈絡／框架三層工程、工作流與自動化系統", [
   "AI工作流架構_2026H2完整版.html","三層AI工程架構教學.html","llm-engineering-framework.html",
   "ai-automation-fundamentals.html","AI模型架構詳解.html","AI迴圈工作法_救護科應用.html",
   "n8n-whisper-guide.html","second-brain-ai-system.html"]),
 ("AI 技能盤點與學習路線", "該學什麼、怎麼排順序，以及不靠 AI 的那一面", [
   "2026-ai-skills-learning-guide.html","ai-skills-2026.html","10項AI核心技能.html",
   "ai-skills-top10.html","AI精熟十級學習路線圖.html","351每日共學_20260815_AI時代解決問題.html",
   "AI進入教室的政策選擇.html","10-ways-creative-without-ai.html"]),
 ("其他 AI 工具", "Gemini、NotebookLM、Excel Copilot、Sheets 與工具選用", [
   "五大AI系統選用引導手冊.html","四大AI協作SOP對照表.html","Gemini功能應用手冊.html",
   "gemini-7day-guide.html","NotebookLM提示詞應用指引.html",
   "notebooklm-claude-workflow-general.html","notebooklm-workflow-nfa.html",
   "excel-copilot-guide.html","sheets-canvas.html"]),
 ("救護科 EMS 業務", "救護安全、臨床指引、國際研修與科內 AI 應用", [
   "SAFER救護安全手冊_線上閱讀版.html","SAFER救護安全手冊_重點整理.html",
   "CPG_A0810_重大創傷指引_繁中詳解_v2.html","CPG_A0810_重大創傷指引_繁中詳解.html",
   "HSEEP_圖卡內容查證報告.html","赴澳洲研修交流_完整攻略.html",
   "index_v2.1_判定式報告版.html","nfa-claude-prompts.html",
   "救護科-claude-應用實戰手冊.html","專案指示_Project_Instructions.html"]),
 ("工作方法與行政效率", "行政流程、管理方法、自我提升與行動裝置技巧", [
   "行政工作流的底層邏輯.html","管理常用12種高效工作方法.html","九項自我提升策略.html",
   "academic-seven-layers.html","world-top10-laws.html","HR績效分析自動化流程SOP.html",
   "iphone-scan-sop.html","iphone-long-screenshot.html","banner.html"]),
]

ICONS = ["icons/icon-192.png", "icons/icon-512.png", "icons/maskable-192.png",
         "icons/maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png"]


def read(p, n=None):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read() if n is None else fh.read(n)


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)


def title_of(f):
    m = re.search(r"<title>(.*?)</title>", read(f, 8000), re.S)
    return html.unescape(m.group(1).strip()) if m and m.group(1).strip() else os.path.splitext(f)[0]


docs = sorted(x for x in os.listdir(".") if x.lower().endswith(".html") and x != "index.html")
listed = set(f for _, _, fs in CATS for f in fs)
dupes = set(f for f in docs if f.endswith("_1.html") and f.replace("_1.html", ".html") in docs)
for f in docs:
    if f not in listed and f not in dupes:
        CATS[-1][2].append(f)
for _, _, fs in CATS:
    for f in fs:
        if not os.path.exists(f):
            raise SystemExit("找不到檔案：" + f)

total = len(docs)
today = datetime.date.today().isoformat()

# ------------------------------------------------- 1. 各文件注入 App 導覽列
NAV_MARK = "<!-- pwa-nav -->"
NAV = """%s
<style>
  #pwa-nav { display:none; }
  @media all and (display-mode: standalone) { #pwa-nav { display:block; } }
  #pwa-nav.on { display:block; }
  #pwa-nav a {
    position:fixed; left:14px; z-index:99999;
    bottom:calc(14px + env(safe-area-inset-bottom));
    display:flex; align-items:center; gap:6px;
    padding:10px 16px; border-radius:24px;
    background:%s; color:#fff; text-decoration:none;
    font:500 14px/1 -apple-system,"Segoe UI","Noto Sans TC","PingFang TC",sans-serif;
    box-shadow:0 4px 14px rgba(0,0,0,.28); -webkit-tap-highlight-color:transparent;
  }
  #pwa-nav a:active { transform:scale(.96); }
</style>
<div id="pwa-nav"><a href="./index.html">&#8592; 索引</a></div>
<script>
  if (window.navigator.standalone) document.getElementById('pwa-nav').classList.add('on');
</script>
""" % (NAV_MARK, ACCENT)

HEAD_MARK = "<!-- pwa-head -->"
HEAD = ('%s\n<link rel="manifest" href="manifest.webmanifest">\n'
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n') % HEAD_MARK

patched = 0
for f in docs:
    src = read(f)
    out = src
    if HEAD_MARK not in out and "</head>" in out:
        out = out.replace("</head>", HEAD + "</head>", 1)
    if NAV_MARK not in out:
        out = out.replace("</body>", NAV + "</body>", 1) if "</body>" in out else out + NAV
    if out != src:
        write(f, out)
        patched += 1

# ------------------------------------------------------------ 2. manifest
manifest = {
    "name": APP_NAME,
    "short_name": "AI 筆記",
    "description": "Claude、AI 工程、EMS 業務與行政工作法的文件集，共 %d 份，可離線閱讀。" % total,
    "lang": "zh-Hant",
    "dir": "ltr",
    "start_url": "./index.html",
    "scope": "./",
    "id": "./",
    "display": "standalone",
    "orientation": "any",
    "background_color": "#f7f7f5",
    "theme_color": ACCENT,
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
    "shortcuts": [
        {"name": "SAFER 救護安全手冊", "url": "SAFER救護安全手冊_線上閱讀版.html"},
        {"name": "Claude 功能完整指南", "url": "Claude功能完整指南.html"},
        {"name": "AI 工作流架構", "url": "AI工作流架構_2026H2完整版.html"},
    ],
}
write("manifest.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------- 3. index.html
cards = []
for name, desc, fs in CATS:
    items = []
    for f in fs:
        t = title_of(f)
        main, _, sub = t.partition("｜")
        li = '      <li class="item" data-k="%s">\n' % html.escape((t + " " + f).lower())
        li += '        <a href="%s">\n' % urllib.parse.quote(f)
        li += '          <span class="t">%s</span>\n' % html.escape(main.strip())
        if sub.strip():
            li += '          <span class="s">%s</span>\n' % html.escape(sub.strip())
        li += '        </a>\n      </li>'
        items.append(li)
    cards.append('    <section class="cat">\n'
                 '      <h2>%s <span class="n">%d</span></h2>\n'
                 '      <p class="d">%s</p>\n'
                 '      <ul>\n%s\n      </ul>\n    </section>'
                 % (html.escape(name), len(fs), html.escape(desc), "\n".join(items)))

CSS = """
  :root {
    --bg:#f7f7f5; --card:#fff; --fg:#1f1f1d; --muted:#6b6b66;
    --line:#e3e3df; --accent:#b4530a; --accent-soft:#f5ece3;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg:#17171a; --card:#1f1f23; --fg:#ececea; --muted:#9a9a95;
      --line:#2e2e33; --accent:#e08b4c; --accent-soft:#2a211a;
    }
  }
  * { box-sizing:border-box; }
  body {
    margin:0; background:var(--bg); color:var(--fg);
    font-family:-apple-system,"Segoe UI","Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;
    line-height:1.65; -webkit-font-smoothing:antialiased;
  }
  .wrap {
    max-width:1080px; margin:0 auto;
    padding:calc(40px + env(safe-area-inset-top)) 16px calc(64px + env(safe-area-inset-bottom));
  }
  h1 { font-size:clamp(26px,5vw,38px); margin:0 0 8px; letter-spacing:-.02em; }
  .lead { color:var(--muted); margin:0 0 20px; font-size:15px; }
  .lead b { color:var(--accent); font-weight:600; }
  #q {
    width:100%; padding:12px 16px; font-size:16px; border-radius:10px;
    border:1px solid var(--line); background:var(--card); color:var(--fg);
  }
  #q:focus { outline:2px solid var(--accent); outline-offset:1px; border-color:transparent; }
  .grid { display:grid; gap:20px; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); margin-top:28px; }
  .cat { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:20px 22px; }
  .cat h2 { font-size:17px; margin:0 0 4px; display:flex; align-items:center; gap:8px; }
  .n { font-size:12px; font-weight:500; color:var(--accent); background:var(--accent-soft);
       padding:2px 8px; border-radius:20px; }
  .d { font-size:13px; color:var(--muted); margin:0 0 14px; }
  ul { list-style:none; margin:0; padding:0; }
  .item a { display:block; padding:9px 10px; margin:0 -10px; border-radius:8px;
            text-decoration:none; color:inherit; }
  .item a:hover { background:var(--accent-soft); }
  .t { display:block; font-size:14.5px; font-weight:500; }
  .s { display:block; font-size:12.5px; color:var(--muted); margin-top:1px; }
  .cat.hide, .item.hide { display:none; }
  footer { margin-top:48px; font-size:13px; color:var(--muted); text-align:center; }

  /* 安裝提示 / 離線狀態 */
  .bar {
    display:none; align-items:center; gap:12px; flex-wrap:wrap;
    margin:0 0 18px; padding:12px 16px; border-radius:12px;
    background:var(--accent-soft); border:1px solid var(--line); font-size:14px;
  }
  .bar.on { display:flex; }
  .bar p { margin:0; flex:1 1 220px; }
  .bar button {
    font:inherit; font-weight:600; cursor:pointer; padding:8px 16px;
    border:0; border-radius:8px; background:var(--accent); color:#fff;
  }
  .bar .ghost { background:transparent; color:var(--muted); font-weight:500; padding:8px 10px; }
  #offline { background:transparent; }
  #offline.on { display:flex; }
"""

JS = """
  // --- 篩選 ---
  var q = document.getElementById('q');
  q.addEventListener('input', function () {
    var v = q.value.trim().toLowerCase();
    document.querySelectorAll('.cat').forEach(function (c) {
      var n = 0;
      c.querySelectorAll('.item').forEach(function (it) {
        var hit = !v || it.dataset.k.indexOf(v) > -1;
        it.classList.toggle('hide', !hit);
        if (hit) n++;
      });
      c.classList.toggle('hide', n === 0);
    });
  });

  // --- Service worker ---
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }

  // --- 安裝提示 ---
  var bar = document.getElementById('install');
  var msg = document.getElementById('install-msg');
  var go = document.getElementById('install-go');
  var no = document.getElementById('install-no');
  var deferred = null;

  var standalone = window.matchMedia('(display-mode: standalone)').matches ||
                   window.navigator.standalone === true;
  var dismissed = false;
  try { dismissed = localStorage.getItem('install-dismissed') === '1'; } catch (e) {}

  var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
              (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

  function show() { if (!standalone && !dismissed) bar.classList.add('on'); }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferred = e;
    msg.textContent = '把這份筆記庫裝成 App，開啟更快，離線也能看。';
    go.hidden = false;
    show();
  });

  if (isIOS) {
    msg.textContent = '想裝成 App：點下方「分享」→「加入主畫面」，即可離線閱讀。';
    go.hidden = true;
    show();
  }

  go.addEventListener('click', function () {
    if (!deferred) return;
    deferred.prompt();
    deferred.userChoice.finally(function () { deferred = null; bar.classList.remove('on'); });
  });

  no.addEventListener('click', function () {
    bar.classList.remove('on');
    try { localStorage.setItem('install-dismissed', '1'); } catch (e) {}
  });

  window.addEventListener('appinstalled', function () { bar.classList.remove('on'); });

  // --- 離線狀態 ---
  var off = document.getElementById('offline');
  function net() { off.classList.toggle('on', !navigator.onLine); }
  window.addEventListener('online', net);
  window.addEventListener('offline', net);
  net();
"""

doc = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(app)s｜索引</title>
<meta name="description" content="Claude、AI 工程、EMS 業務與行政工作法的文件集，共 %(total)d 份，可離線閱讀。">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="%(accent)s">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AI 筆記">
<meta name="mobile-web-app-capable" content="yes">
<style>%(css)s</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>%(app)s</h1>
    <p class="lead">Claude、AI 工程、EMS 業務與行政工作法的自用文件集，共 <b>%(total)d</b> 份。更新於 %(today)s。</p>
    <div class="bar" id="offline"><p>目前離線，顯示的是已下載的離線版本。</p></div>
    <div class="bar" id="install">
      <p id="install-msg"></p>
      <button id="install-go" hidden>安裝 App</button>
      <button id="install-no" class="ghost">不用了</button>
    </div>
    <input id="q" type="search" placeholder="輸入關鍵字篩選，例如 Claude、SOP、救護⋯⋯" autocomplete="off">
  </header>
  <main class="grid">
%(cards)s
  </main>
  <footer>以 Claude Code 整理 · GitHub Pages 靜態託管 · 可安裝離線使用</footer>
</div>
<script>%(js)s</script>
</body>
</html>
""" % {"app": APP_NAME, "css": CSS, "js": JS, "total": total, "today": today,
       "accent": ACCENT, "cards": "\n".join(cards)}

write("index.html", doc)

# ------------------------------------------------------ 4. service worker
precache = ["./", "index.html", "manifest.webmanifest"] + docs + ICONS
h = hashlib.md5()
for p in ["index.html", "manifest.webmanifest"] + sorted(docs) + ICONS:
    if os.path.exists(p):
        with open(p, "rb") as fh:
            h.update(hashlib.md5(fh.read()).digest())
version = h.hexdigest()[:10]

sw = """/* 由 tools/build.py 產生，請勿手動編輯 */
const VERSION = '%s';
const CACHE = 'ai-notes-' + VERSION;
const PRECACHE = %s;

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(PRECACHE.map((u) => c.add(u).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', (e) => {
  if (e.data === 'skip-waiting') self.skipWaiting();
});

// 快取優先，背景更新；離線且未快取時回退到索引頁
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then((hit) => {
      const net = fetch(req).then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => hit || (req.mode === 'navigate' ? caches.match('index.html') : Response.error()));
      return hit || net;
    })
  );
});
""" % (version, json.dumps(precache, ensure_ascii=False, indent=2))
write("sw.js", sw)

print("文件總數：%d（重複備份 %d 份未列入索引）" % (total, len(dupes)))
print("注入 App 導覽列：%d 個檔案" % patched)
print("離線快取項目：%d，版本 %s" % (len(precache), version))
