# Week2.API

這是一個使用 FastAPI 建立的後端 API 練習專案。

本專案是 FastAPI + PostgreSQL 後端課程的第二週成果。

## 使用技術

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL
- Psycopg
- Git
- GitHub

## 專案結構

```text
api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── notes.py
│   └── core/
│       ├── database.py
│       └── db_test.py
├── psql/
│   └── createdb.sql
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── venv/
```

## 安裝與執行

### 1. 下載專案

```powershell
git clone https://github.com/s114213515-jessy/Week1.API.git
cd Week1.API
```

### 2. 建立虛擬環境

```powershell
py -m venv venv
```

### 3. 啟動虛擬環境

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

成功後，PowerShell 前面應該會出現：

```text
(venv)
```

### 4. 安裝套件

```powershell
python -m pip install -r requirements.txt
```

### 5. 啟動 FastAPI

```powershell
uvicorn app.main:app --reload
```

### 6. 設定 PostgreSQL

先複製 `.env.example` 為 `.env`，再依本機 PostgreSQL 的帳號、密碼和連接埠修改
`DATABASE_URL`。接著用 `psql` 執行 `psql/createdb.sql`，建立開發資料庫、
`dev_user` 和 `notes` table。

確認 Python 可以連線：

```powershell
python -m app.core.db_test
```

### 7. 開啟 API 文件

在瀏覽器開啟：

```text
http://127.0.0.1:8000/docs
```

## API 端點

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/health` | 檢查 API 是否正常 |
| GET | `/version` | 查看 API 版本 |
| POST | `/items` | 建立一個商品 |
| GET | `/note/{id}` | 依 ID 取得筆記 |

## API 測試

### GET /health

```text
http://127.0.0.1:8000/health
```

回應：

```json
{
  "status": "ok"
}
```

### GET /version

```text
http://127.0.0.1:8000/version
```

回應：

```json
{
  "version": "0.1.0"
}
```

### POST /items

請求內容：

```json
{
  "name": "keyboard",
  "price": 1200.5
}
```

回應：

```json
{
  "name": "keyboard",
  "price": 1200.5
}
```

### GET /note/{id}

例如：

```text
http://127.0.0.1:8000/note/1
```

找不到筆記時會回傳 HTTP 404。

## 環境變數

目前 PostgreSQL 設定範例放在：

```text
.env.example
```

真正的 `.env` 不應該上傳到 GitHub，因為裡面可能包含密碼。

## GitHub

GitHub Repository：

https://github.com/s114213515-jessy/Week1.API