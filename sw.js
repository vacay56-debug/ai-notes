/* 由 tools/build.py 產生，請勿手動編輯 */
const VERSION = '5a9df8d5b0';
const CACHE = 'ai-notes-' + VERSION;
const PRECACHE = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "10-ways-creative-without-ai.html",
  "10項AI核心技能.html",
  "2026-ai-skills-learning-guide.html",
  "351每日共學_20260815_AI時代解決問題.html",
  "AI工作流架構_2026H2完整版.html",
  "AI模型架構詳解.html",
  "AI精熟十級學習路線圖.html",
  "AI迴圈工作法_救護科應用.html",
  "AI迴圈工作法_救護科應用_1.html",
  "AI進入教室的政策選擇.html",
  "CPG_A0810_重大創傷指引_繁中詳解.html",
  "CPG_A0810_重大創傷指引_繁中詳解_v2.html",
  "Claude功能完整指南.html",
  "Gemini功能應用手冊.html",
  "HR績效分析自動化流程SOP.html",
  "HSEEP_圖卡內容查證報告.html",
  "NotebookLM提示詞應用指引.html",
  "SAFER救護安全手冊_線上閱讀版.html",
  "SAFER救護安全手冊_重點整理.html",
  "academic-seven-layers.html",
  "ai-agent-blueprint.html",
  "ai-agent-sop.html",
  "ai-automation-fundamentals.html",
  "ai-skills-2026.html",
  "ai-skills-top10.html",
  "banner.html",
  "claude-30min-learning-guide.html",
  "claude-4-modes.html",
  "claude-ai-7day-guide.html",
  "claude-code-7steps-guide.html",
  "claude-code-架構藍圖.html",
  "claude-code-架構藍圖_1.html",
  "claude-code-速成指南.html",
  "claude-design-速成指南.html",
  "claude-ecosystem-reference.html",
  "claude-fable5-提示詞完全指南.html",
  "claude-fable5-提示詞完全指南_1.html",
  "claude-mastery-climb.html",
  "claude-project-skills-cowork-指南.html",
  "claude-quickstart-guide.html",
  "claude-six-levels.html",
  "claude-skills-評估.html",
  "claude-voice-workflow.html",
  "claude-website-sop.html",
  "claude-website-sop_1.html",
  "cowork-sop.html",
  "excel-copilot-guide.html",
  "gemini-7day-guide.html",
  "github-upload-guide.html",
  "index_v2.1_判定式報告版.html",
  "iphone-long-screenshot.html",
  "iphone-scan-sop.html",
  "llm-engineering-framework.html",
  "n8n-whisper-guide.html",
  "nfa-claude-prompts.html",
  "notebooklm-claude-workflow-general.html",
  "notebooklm-workflow-nfa.html",
  "second-brain-ai-system.html",
  "sheets-canvas.html",
  "world-top10-laws.html",
  "三層AI工程架構教學.html",
  "九項自我提升策略.html",
  "五大AI系統選用引導手冊.html",
  "四大AI協作SOP對照表.html",
  "專案指示_Project_Instructions.html",
  "救護科-claude-應用實戰手冊.html",
  "管理常用12種高效工作方法.html",
  "行政工作流的底層邏輯.html",
  "赴澳洲研修交流_完整攻略.html",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/maskable-192.png",
  "icons/maskable-512.png",
  "icons/apple-touch-icon.png",
  "icons/favicon-32.png"
];

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
