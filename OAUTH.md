# W6 — Google OIDC、會員資料與 App JWT

## 本週目標

- 用 Google OpenID Connect (OIDC) 確認使用者身分。
- 以 Google `sub` 作穩定識別，在 PostgreSQL `members` table 建立或更新會員資料。
- 由 FastAPI 簽發本系統的 JWT，並以 HttpOnly cookie 或 Bearer token 傳送。
- 驗證 JWT 後再查資料庫，保護 Notes 與學術 subclass API。

## Authentication 與 Authorization

- **Authentication** 回答「你是誰？」本週由 Google OIDC 驗證 Google 身分，再由 App JWT 識別本系統會員。
- **Authorization** 回答「你可以做什麼？」本週先用 `members.is_active` 示範停用帳號；後續可加角色與資源擁有權。
- OAuth 2.0 常用來授權存取資源；OIDC 建立在 OAuth 2.0 上，提供登入所需的身分層。

## Google Cloud 與環境設定

1. 在 Google Cloud 建立 OAuth 用戶端，應用程式類型選 Web application。
2. 加入正確的授權 JavaScript origin，以及以下精確 callback URI：
   `http://127.0.0.1:7777/api/auth/google/callback`
3. 將 `.env.example` 複製為 `.env`，填入 Google client ID、client secret，以及兩個不同的隨機 secret。
4. 本機 HTTP 測試設定 `AUTH_COOKIE_SECURE=false`；HTTPS 部署設定 `true`。
5. `GOOGLE_REDIRECT_URI` 必須與 Google Console 登記值逐字相同。重新啟動 FastAPI 後再測試。
6. 若部署在 `/s115999999/` 這類子路徑，redirect URI 和 `AUTH_SUCCESS_REDIRECT_URL`
   都要包含該前綴；請依 IIS 反向代理實際對外網址設定。

例如正式網址為 `https://demo.wke.csie.ncnu.edu.tw/s115999999/` 時，callback URI 應為
`https://demo.wke.csie.ncnu.edu.tw/s115999999/api/auth/google/callback`，成功後可設定
`AUTH_SUCCESS_REDIRECT_URL=https://demo.wke.csie.ncnu.edu.tw/s115999999/`。

不要把 `.env`、OAuth client secret 或 JWT/session secret 提交到 GitHub。產生至少 32 bytes 隨機 secret 的範例：

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

JWT secret 與 session secret 請分別產生，不可共用。

## 安裝資料表

在專案根目錄以 PostgreSQL 管理者執行：

```powershell
psql -h localhost -U postgres -d fastapi_dev -f psql/w06_auth.sql
```

腳本只建立 `members` table 和必要授權，不會刪除或重建既有資料。API 帳號可讀寫會員資料並使用 identity sequence。

## 登入流程

```text
Browser → GET /api/auth/google/login
        → Google OIDC (openid email profile)
        → GET /api/auth/google/callback
        → 驗證 OAuth state / Google ID token / verified email
        → upsert members by google_sub
        → FastAPI 簽發短效 App JWT，設為 HttpOnly cookie
        → redirect 回首頁
        → GET /api/auth/me
        → 驗證 JWT 並確認會員仍存在且啟用
```

Google `sub` 是 Google 帳號穩定識別值；email 可能變更，因此不以 email 當唯一登入鍵。每次登入更新 email/name/picture，但不會自動重新啟用被管理員停用的會員。

## API

| Method | Path | 說明 |
| --- | --- | --- |
| GET | `/api/auth/google/login` | 導向 Google 登入 |
| GET | `/api/auth/google/callback` | 驗證回呼、upsert member、簽發 cookie |
| GET | `/api/auth/me` | 回傳登入者 name/email/picture；未登入回傳 401 |
| POST | `/api/auth/logout` | 清除瀏覽器中的 JWT cookie |
| Notes | `/api/notes...` | 要求有效 JWT 且會員仍啟用 |
| Classes | `/api/classes`、`/api/subclass/...` | 要求有效 JWT 且會員仍啟用 |

瀏覽器同源請求會自動傳送 HttpOnly cookie；API client 也可傳 `Authorization: Bearer <token>`。JWT 使用固定 HS256、issuer、subject、issued-at 與 expiry 驗證。即使 token 簽章正確，每次受保護請求仍會查詢會員資料庫，因此停用會員可立即失去 API 存取權。

登出會清除瀏覽器 cookie；已複製的 Bearer token 仍可用到期，除非會員被停用。預設有效時間為 8 小時，可用 `ACCESS_TOKEN_EXPIRE_SECONDS` 設定 60 至 86400 秒。

## Token 儲存位置比較

| 方式 | 優點 | 風險／注意事項 |
| --- | --- | --- |
| `localStorage` | 關閉瀏覽器後仍保留 | JavaScript 可讀；XSS 可竊取並重用 token |
| `sessionStorage` | 分頁關閉後通常清除 | JavaScript 仍可讀；XSS 期間仍可竊取 |
| HttpOnly cookie | JavaScript 無法讀取 token | 瀏覽器自動附帶；需 HTTPS、SameSite 與 CSRF 防護設計 |
| Memory | 關閉/重整後消失，較少持久暴露 | 頁面重整需重新取得；同頁 XSS 仍可能呼叫 API |

本實作採 HttpOnly、SameSite=Lax cookie；正式站必須啟用 Secure 並使用 HTTPS。OAuth state 驗證用來保護 callback 流程；不要在前端 JavaScript 儲存 JWT 或 Google client secret。

## 驗收與除錯

- [ ] 沒有登入時，`GET /api/auth/me` 回 401。
- [ ] Google 首次登入新增 member；再次登入更新同一筆，不產生重複會員。
- [ ] 未驗證 email 或缺少 `sub` 的 Google 回應不得登入。
- [ ] Notes 與 subclass API 未帶 JWT 回 401；有效 JWT 才可存取。
- [ ] 停用 `members.is_active` 後，既有 JWT 也回 401。
- [ ] 登出後瀏覽器 cookie 被清除。
- [ ] 本機 HTTP 使用 `AUTH_COOKIE_SECURE=false`；HTTPS 部署使用 `true`。
- [ ] `GOOGLE_REDIRECT_URI` 與 Google Cloud Console 設定完全一致。
- [ ] `python -m unittest discover -s tests -v` 通過。

直接打開 callback URL 不是有效的登入測試；必須先從 `/api/auth/google/login` 啟動完整流程，讓 OAuth state cookie 正常建立。
