# Learning Log

> 每週心得獨立於程式碼提交。請補上自己的觀察，不要在公開 repo 放個資、密碼或真實教務資料。

## W5 — 關聯式資料設計

### 本週完成
- 在 Notes API 加入分類與標籤。
- `categories` 對 `notes` 使用一對多外鍵。
- `notes` 對 `tags` 使用 `note_tags` 關聯表表示多對多。
- 筆記 API 回傳關聯物件，並支援依分類或標籤篩選。

### 我自己的心得
- 我如何用自己的話解釋一對多與多對多：
- 為什麼多對多需要關聯表：
- 我對分類刪除時 `ON DELETE SET NULL` 的看法：
- 我遇到的問題與解決方式：
- 下一步想練習的資料庫功能：

## W5 Web — JavaScript DOM 與事件處理

### 本週完成
- 導覽選單、卡片與說明由前端 JSON 範例資料 render。
- 加入側欄開關與 Escape 關閉、導覽 hover/focus 預覽、卡片選取及 detail panel。
- 加入帳戶選單、深色模式和提示文字更新等 Event → Function → DOM 練習。
- FastAPI 只公開首頁所需的靜態檔案白名單。

### 我自己的心得
- 我選的一個互動流程（Event → Function → DOM → UI）：
- 我如何用鍵盤操作側邊欄或卡片：
- 我用瀏覽器開發者工具驗證了什麼：
- 我遇到的問題與解決方式：
