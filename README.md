# AI 筆記庫

Claude、AI 工程、EMS 業務與行政工作法的自用 HTML 文件集，共 69 份。

**線上瀏覽 / 安裝 App：** https://vacay56-debug.github.io/ai-notes/

這是一個 PWA，可以裝成 App 使用：

- **iPhone / iPad（Safari）**：開啟網址 → 點下方「分享」→「加入主畫面」
- **Android（Chrome）**：開啟網址 → 頁面上方會出現「安裝 App」按鈕，或用選單「安裝應用程式」
- **Windows / Mac（Chrome、Edge）**：網址列右側的安裝圖示

裝完會有獨立圖示、無網址列，全部 69 份文件已預先下載，**離線也能看**。

## 分類

| 分類 | 內容 |
|---|---|
| Claude 入門與操作 | 功能指南、四種工作模式、六層架構、生態系對照、提示詞指南 |
| Claude Code 與開發流程 | 建站 SOP、Agent 建置、架構藍圖、Cowork、GitHub 上傳 |
| AI 工程架構與自動化 | 三層工程（提示／脈絡／框架）、工作流架構、n8n × Whisper、第二大腦 |
| AI 技能盤點與學習路線 | 2026 技能清單、十級學習路線、每日共學、政策討論 |
| 其他 AI 工具 | Gemini、NotebookLM、Excel Copilot、Sheets canvas、工具選用 |
| 救護科 EMS 業務 | SAFER 救護安全手冊、CPG A0810 重大創傷指引、HSEEP 查證、赴澳研修 |
| 工作方法與行政效率 | 行政工作流邏輯、12 種高效工作法、九項自我提升、iPhone 掃描 SOP |

## 使用方式

每份文件都是獨立的單檔 HTML，可直接用瀏覽器開啟，或從 [`index.html`](index.html) 的索引頁點選；索引頁上方有關鍵字篩選框。以 App 模式開啟時，每份文件左下角會出現「← 索引」快速返回鈕。

## 維護

新增或刪除 HTML 之後，在專案根目錄執行：

```
python tools/build.py
```

會重新產生索引頁、`manifest.webmanifest` 與 `sw.js` 的離線快取清單，並替新文件補上 App 導覽列。分類歸屬寫在 `tools/build.py` 最上方的 `CATS`；未列入分類的新檔會自動歸到最後一類。圖示如需重做，執行 `python tools/gen_icons.py`（需要 Pillow）。

## 說明

- 文件多為個人整理的學習與業務筆記，內容以整理當下的資訊為準，未必持續更新。
- 四份檔名帶 `_1` 的是早期重複備份，內容與同名主檔相同，索引頁未重複列出。
