# Week1.API

這是一個使用 FastAPI 建立的後端 API 練習專案。

本專案是 FastAPI + PostgreSQL 後端課程的第一週成果。

## 使用技術

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic
- Git
- GitHub

## 專案結構

```text
api/
├── app/
│   ├── __init__.py
│   └── main.py
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

### 6. 開啟 API 文件

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

## 環境變數

目前 PostgreSQL 設定範例放在：

```text
.env.example
```

真正的 `.env` 不應該上傳到 GitHub，因為裡面可能包含密碼。

## GitHub

GitHub Repository：

https://github.com/s114213515-jessy/Week1.API