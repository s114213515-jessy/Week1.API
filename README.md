# Web Programming Lab

這是一個使用 FastAPI 建立的後端 API 練習專案。

本專案結合 FastAPI 後端與 WKE 教務系統前端練習，支援本機及學號子路徑部署。

## 使用技術

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL
- Psycopg
- HTML/CSS
- JavaScript
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
├── public/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── json/
│       ├── teacher_ops.json
│       └── dashboard_cards.json
├── psql/
│   └── createdb.sql
├── run.bat
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

使用預設的本機測試設定（`0.0.0.0:7777`）：

```powershell
.\run.bat
```

也可以指定 host 與 port：

```powershell
.\run.bat 192.168.1.10 7777
```

或直接啟動：

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 7777 --reload
```

### 6. 開啟 Web App 與 API 文件

瀏覽器開啟：

```text
http://127.0.0.1:7777/s114213515/
http://127.0.0.1:7777/docs
```

首頁以 `/s114213515/` 作為 `<base>`，支援老師 IIS URL Rewrite 的學號子路徑部署。
FastAPI 也會將本機測試網址中的相同學號前綴映射回應用程式根路徑。

API 路由統一使用 `/api/` 前綴。公開靜態資源限制為 HTML、CSS、SVG，以及 `js/` 和
`json/` 目錄；其他檔案路徑會回傳 404。

教務側欄由 `public/json/teacher_ops.json` 載入，儀表板卡片由
`public/json/dashboard_cards.json` 載入。側欄項目可切換不同的模擬卡片內容。

### 7. 設定 PostgreSQL

先複製 `.env.example` 為 `.env`，再依本機 PostgreSQL 的帳號、密碼和連接埠修改
`DATABASE_URL`。接著用 `psql` 執行 `psql/createdb.sql`，建立開發資料庫、
`dev_user` 和 `notes` table。

確認 Python 可以連線：

```powershell
python -m app.core.db_test
```

## API 端點

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/health` | 檢查 API 是否正常 |
| GET | `/api/version` | 查看 API 版本 |
| POST | `/api/items` | 建立一個商品 |
| GET | `/api/note/{id}` | 依 ID 取得筆記 |

## API 測試

### GET /health

```text
http://127.0.0.1:7777/api/health
```

回應：

```json
{
  "status": "ok"
}
```

### GET /version

```text
http://127.0.0.1:7777/api/version
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
http://127.0.0.1:7777/api/note/1
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