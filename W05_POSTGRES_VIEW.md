# W5 — PostgreSQL 關聯查詢、Function 與 View API

## 本週完成目標

- 用 PostgreSQL 建立 `class`、`inheritance`、`object`、`co` 四張資料表。
- 用 `insertclass` function 在同一個資料庫交易中新增或連結子分類，並更新階層路徑。
- 建立 `vd_subclass` view，將父分類、繼承關係與子分類合併為 API 可直接使用的資料。
- 以唯讀 view 權限提供 `GET /api/subclass/pcid/{parent_id}`，並以資料庫 function 新增分類。

## 資料表關係

```text
class 1 ────< inheritance >──── 1 class
   │
   └────────< co >───────────── object
```

`inheritance` 是分類父子關係的關聯表；`co` 是分類與內容物件之間的關聯表。
主鍵與外鍵限制由 PostgreSQL 維護，避免重複關係或指向不存在的資料。

`insertclass` 先確認父分類 ID 與名稱相符，再建立／尋找子分類、寫入父子關係，
並更新 `idpath` 和 `namepath`。function 呼叫與 API 查詢都在同一個資料庫交易內；
API 在取得完整回應資料後才提交交易。

## 安裝資料庫結構

確認 PostgreSQL 正在執行，並用管理者帳號執行：

```powershell
psql -h localhost -U postgres -d postgres -f psql/academic.sql
```

預設資料庫名稱為 `fastapi_dev`。如需其他名稱：

```powershell
psql -h localhost -U postgres -d postgres -v DBName=fastapi_dev -f psql/academic.sql
```

SQL 會在資料庫不存在時建立資料庫，在目標資料庫內以 `CREATE TABLE IF NOT EXISTS`
建立資料表，並建立或更新 function 與 view。腳本假設 `dev_user` 已存在；若尚未建立，
請先執行 `psql/createdb.sql`，再重新執行授權步驟。API 帳號只能讀取 `vd_subclass`
view、查詢新增後的分類必要欄位，以及執行 `insertclass`，不需直接寫入四張資料表。

## 連線設定與啟動

`.env` 的 `DATABASE_URL` 必須指向執行上述 SQL 的資料庫，例如：

```env
DATABASE_URL=postgresql://dev_user:your-password@localhost:5432/fastapi_dev
```

啟動 FastAPI 後開啟 `http://127.0.0.1:7777/docs`。

## 操作 API

### 新增子分類

`POST /api/classes`

```json
{
  "parent_id": 0,
  "parent_name": "首頁",
  "name": "校務"
}
```

API 會呼叫 PostgreSQL `insertclass` function，並回傳新分類的 ID 與階層路徑。
不存在的父分類回傳 `404`；父分類 ID 與名稱不一致則回傳 `422`。

### 取得指定父分類的子分類

`GET /api/subclass/pcid/0`

回應範例：

```json
[
  {
    "pcid": 0,
    "parent_name": "首頁",
    "cid": 1,
    "child_name": "校務"
  }
]
```

查詢 SQL 使用 `%s` 參數化傳入父分類 ID；API 對資料庫 view 執行唯讀查詢。

## 驗收

- [ ] 重複執行 `psql/academic.sql` 不會重複建立表格或根分類。
- [ ] `insertclass` 可以新增父子分類，並設定正確的 `idpath`／`namepath`。
- [ ] 不存在的父分類與錯誤的父分類名稱會被拒絕。
- [ ] `GET /api/subclass/pcid/{parent_id}` 回傳 view 的欄位與資料。
- [ ] `dev_user` 可讀取 view、執行 function，但不直接擁有四張資料表的寫入權限。
- [ ] 執行 `python -m unittest discover -s tests -v` 通過。

## 自己的練習

1. 用 `/docs` 新增「校務」及其子分類，觀察 `cid`、`idpath` 和 `namepath`。
2. 在 `psql` 查詢 `SELECT * FROM vd_subclass WHERE pcid = 0;`，比對 API 回應。
3. 嘗試傳入不存在的 `parent_id` 和錯誤的 `parent_name`，觀察 HTTP 狀態碼。
