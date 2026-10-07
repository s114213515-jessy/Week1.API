# W5 Web — JavaScript DOM 操作與事件處理

本週在 `public/` 的 WKE 教務儀表板加入互動。核心模型是：

```text
Event → Function → DOM Change → UI Result
```

範例資料來自 `public/json/`。本週重點是互動流程，不深入講解 `fetch()`；下週再討論
HTTP 與 API 請求。

## 本週新增的互動

| 操作 | Event | Function | DOM 變更 |
|---|---|---|---|
| 開啟側邊欄 | `#menuToggle` click | `openSidebar()` | sidebar 加上 `is-open`、顯示 backdrop、更新 `aria-expanded` |
| 關閉側邊欄 | 關閉按鈕、backdrop 或 Escape | `closeSidebar()` | 移除 `is-open`、隱藏 backdrop、更新按鈕狀態 |
| 切換功能頁 | 導覽按鈕 click | `showPage(item)` | 更新標題、說明、active class 與卡片 |
| 預覽功能說明 | 導覽項目 mouseenter/focus | `showNavigationPreview(item)` | 更新 `#navigationPreview` 文字 |
| 選取摘要卡 | 卡片 click、Enter 或 Space | `setSelectedCard(card)` | 唯一選取卡片切換 `is-selected` 和 `aria-pressed` |
| 展開卡片說明 | 卡片按鈕 click | `toggleDetail(button, detail)` | 切換 `hidden`、`aria-expanded` 與按鈕文字 |
| 顯示帳戶選單 | 帳戶按鈕 click | `toggleAccountPanel()` | 切換選單 `hidden` 與 `aria-expanded` |
| 切換深色模式 | 主題按鈕 click | `toggleTheme()` | 切換 body class 與 `aria-pressed` |
| 更新提示 | 更新按鈕 click | `changeMessage()` | 更新 `#message.textContent` |

## 如何測試

1. 依專案 README 啟動 FastAPI。
2. 開啟 `http://127.0.0.1:7777/`，確認儀表板、導覽項目及三張摘要卡出現。
3. 按選單按鈕，確認側欄與遮罩出現；按 Escape、關閉按鈕或遮罩，確認側欄關閉。
4. 用滑鼠移到側欄項目上，確認預覽說明更新；點選項目，確認主標題與卡片改變。
5. 點一張摘要卡，再點另一張，確認同一時間只有一張卡片被選取。
6. 使用 Tab 聚焦卡片，再按 Enter 或 Space，確認也能選取卡片。
7. 展開/收合卡片說明，檢查按鈕的 `aria-expanded` 是否同步。
8. 切換教師帳戶選單、深色模式及「更新提示」按鈕。
9. 開發者工具 Network 中確認 `app.js`、`json/teacher_ops.json` 和
   `json/dashboard_cards.json` 都是 HTTP 200。
10. 確認 JSON 載入失敗時頁面會顯示錯誤狀態，Console 會記錄原因。

## AI Coding Code Review

每次請 AI 修改互動後，請回答：

1. Event 是什麼？
2. Listener 綁在哪個 DOM element？
3. 觸發哪個 function？
4. Function 修改哪些 DOM、class 或 attribute？
5. 這個修改會不會影響既有互動？

可使用以下 prompt：

```text
需求：
Event：[使用者做什麼]
Function：[沿用或新增的 function]
DOM Change：[要改的 element/class/text/attribute]
Expected UI：[預期看到的畫面]

限制：
1. 只修改必要檔案與程式碼。
2. 不要重寫整份 app.js。
3. 保留既有 Sidebar、卡片與帳戶選單行為。
4. 修改後列出 Event → Function → DOM → UI Result。
```

## W5 AI Coding 工作流程

```text
Describe → Ask AI → Inspect → Run → Verify → Refine → Commit
```

- **Describe**：先寫出 Event、Function、DOM 和預期畫面。
- **Ask AI**：要求最小範圍修改與明確解釋。
- **Inspect**：確認只改了預期檔案，檢查 listener、function 和 DOM 目標。
- **Run**：啟動 FastAPI，使用瀏覽器操作。
- **Verify**：確認 event 發生、function 執行、DOM 改變且既有行為仍正常。
- **Refine**：有問題時提供實際重現步驟與瀏覽器錯誤。
- **Commit**：以描述功能的 commit message 提交。

## 本週範圍

前端內容是公開展示用範例，不含真實學生資料，也沒有真正的登入功能。資料載入失敗時，
畫面明確顯示錯誤；本週不將資料寫入資料庫，也不處理 W6 的 API/CORS 設定。
