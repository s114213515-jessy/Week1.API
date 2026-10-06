# W5 — PostgreSQL 關聯式資料設計

## 本週目標

- 認識一對多與多對多關係。
- 使用外鍵維護資料完整性。
- 以關聯表表示多對多，並由 API 回傳關聯資料。
- 為既有資料庫撰寫可重複執行的 schema migration。

## 資料模型

```text
categories
  id (PK)
  name (UNIQUE)
      │ 1
      └────────< notes
                   id (PK)
                   title
                   content
                   category_id (FK, nullable)
                       │
                       │ 1
                       └────────< note_tags >──────── tags
                                    (PK: note_id,       id (PK)
                                     tag_id)            name (UNIQUE)
```

### 一對多：分類與筆記

一個分類可對應多篇筆記；每篇筆記可選擇一個分類。外鍵放在「多」的一側，也就是
`notes.category_id`。欄位可為 `NULL`，因此舊筆記不需先搬移資料就能套用 migration。

### 多對多：筆記與標籤

一篇筆記可以有多個標籤，一個標籤可以被多篇筆記使用。資料庫不能在單一欄位直接保存
任意數量的標籤關係，因此用 `note_tags` 關聯表。複合主鍵 `(note_id, tag_id)` 同時
避免同一標籤被重複掛到同一篇筆記。

## 執行 migration

先確認目前資料庫已完成 W4 `psql/createdb.sql`，且 `.env` 的 `DATABASE_URL` 指向
`fastapi_dev`。用 PostgreSQL 管理者執行：

```powershell
psql -h localhost -U postgres -d fastapi_dev -f psql/w05_relations.sql
```

此 migration 可重複執行。它不會刪除現有筆記；已有筆記的 `category_id` 為 `NULL`，
標籤集合為空。

## API 練習順序

1. `POST /api/categories` 建立分類，例如 `{"name":"課程"}`。
2. `POST /api/tags` 建立標籤，例如 `{"name":"PostgreSQL"}`。
3. 再建立一個標籤，例如 `{"name":"W5"}`。
4. `POST /api/notes` 建立含有分類和兩個標籤的筆記：

```json
{
  "title": "整理關聯式設計",
  "content": "分類是一對多，標籤是多對多。",
  "category_id": 1,
  "tag_ids": [1, 2]
}
```

5. `GET /api/notes` 確認每筆筆記含 `category` 物件與 `tags` 陣列。
6. `GET /api/notes?category_id=1` 和 `GET /api/notes?tag_id=2` 練習關聯篩選。
7. 用 `PUT /api/notes/{id}` 更新標籤，確認它採用完整取代語意。

## 驗收標準

- [ ] 同一分類可關聯多篇筆記。
- [ ] 一篇筆記可有多個標籤，同一標籤也可被多篇筆記使用。
- [ ] 查詢筆記會回傳分類與標籤，而不是只回傳外鍵數字。
- [ ] 不存在的 category/tag ID 回傳 404；名稱重複回傳 409。
- [ ] `tag_ids` 重複或小於 1 時，Pydantic 驗證回傳 422。
- [ ] 執行 `python -m unittest discover -s tests -v` 通過。
- [ ] GitHub migration 不包含真實密碼或使用者資料。

## 延伸思考

1. 若分類有父子階層，資料表要如何表示？
2. 如果筆記只能有一個標籤，是否還需要 `note_tags`？
3. 分類刪除時可選擇 `SET NULL`、`CASCADE` 或 `RESTRICT`；本專案選哪一種，對使用者資料有何影響？
