# 任務：用 HackerTube 公開資料，做一個繁體中文介面的靜態影片推薦站

## objective
`source/` 是 Karpathy 公開的 HackerTube 資料包（Hacker News 二十年反覆推薦的 6,454 支 YouTube 影片）。
先讀 `source/DATA.md` 全文，它寫了每個欄位的意思與注意事項。
做出一個純靜態網站（不需要後端、不需要登入），介面文字全部繁體中文，影片摘要保留英文原文。

## files
- 只准讀：`source/` 底下全部檔案、本 spec。
- 要寫：
  - `build_data.py`：把 `source/` 轉成網站用的資料，輸出到 `site/data/`。只用 Python 標準函式庫＋numpy。重跑要能覆蓋（冪等）。
  - `site/index.html`（可再拆 `site/app.js`、`site/style.css`）：前端，原生 JS，不用任何框架、不用打包工具、不連任何 CDN。
  - `site/data/*.json`：由 build_data.py 產生。
  - `README.md`：繁中，說明怎麼重建資料、怎麼本機預覽（例：`python -m http.server -d site 8765`）。
- 禁止改動 `source/` 裡任何檔案。

## interfaces
資料處理（build_data.py）：
1. 影片只留前端要用的欄位：vid、title、channel、summary、why_hn、content_type、level、shelf_life、primary_topic、tags、categories（只留 id）、quote、hn（recommenders、rec_months、strong_recs、first_year、last_year）、score。
2. 相似影片：用 `embeddings.npy`（已正規化，直接內積）每支取前 12 支最相似的 vid；`related.jsonl` 有的「同一群人也推薦」另存一欄，最多 12 支。
3. 分類中文化：16 個大區與 150 個分類的名稱，由你翻成繁體中文，寫成 `build_data.py` 裡的對照表（id → 中文名）。翻不準的保留英文。
4. 每支影片的 HN 留言：從 `mentions.jsonl` 取 stance 為 rec 或 strong_rec 的，每支最多 5 則（author、month、quote 或 text 前 300 字、hn_url），分檔存放（例如依 vid 開頭字元分片），點進影片頁才載入。
5. 資料檔總大小盡量壓在 15 MB 以內。

前端功能：
- 首頁：依 score 由高到低排的影片卡格狀列表，分頁或捲動載入。
- 影片卡：縮圖用 `https://i.ytimg.com/vi/<vid>/hq2.jpg`（影片中段畫面），標題、頻道、推薦人數。
- 預設隱藏 `shelf_life == "news"` 與 `hn.recommenders == 0` 的影片；設定裡可打開。
- 左側選單：首頁、分類（16 大區展開 150 類）、已按讚、稍後觀看、觀看紀錄、設定。
- 篩選：內容類型（content_type 中文化）、程度（level 中文化）。
- 搜尋框：在瀏覽器端比對 title、channel、tags、primary_topic、中文分類名。
- 影片頁：嵌入播放器 `https://www.youtube-nocookie.com/embed/<vid>`；顯示摘要、why_hn、金句、HN 推薦留言（附原留言連結）、相似影片、同一群人也推薦。
- 按讚／稍後觀看／觀看紀錄存在 localStorage，不需登入。
- 支援深色模式（跟隨系統）。
- 網址可分享：用 hash 路由，例如 `#/watch/<vid>`、`#/c/<分類id>`。
- 每頁頁尾固定一行出處（授權要求，一字不改）：
  `資料來源：HackerTube（https://hackertube.org）與 open-index/hacker-news 資料集，依 ODC-By 1.0 授權。影片標題與頻道名稱屬原作者，影片由 YouTube 提供。`

## constraints
- 介面文字一律繁體中文，禁簡體字。影片標題、頻道名、摘要、留言保留英文原文。
- 禁止跑 qmd。禁止讀本資料夾以外的路徑。禁止上網（不需要）。
- 不准放任何金鑰、不准呼叫 YouTube API。
- 衝突時：「頁尾出處一字不改」優先於版面美觀；「純靜態、無框架」優先於功能多寡——做不到的功能寫進 README 的「未完成」段，不要硬塞。

## verification
請自己跑完以下全部，結果貼在回報裡：
1. `python build_data.py` 成功結束，印出影片數、被預設隱藏數、資料檔總大小。
2. 用一行 python 讀影片資料檔，印出筆數＝6454。
3. 在 site/data 的影片資料裡找得到字串 `Vectors | Chapter 1, Essence of linear algebra`。
4. `site/` 底下 HTML 或 JS 找得到頁尾出處那一整句。
5. `grep -rn "cdn\|googleapis.com/youtube" site/` 沒有命中。
- **產物收據**：回報末尾附一行
  `[產物] 目錄=site/ 檔數=<N> 資料總大小=<MB> 影片數=<N> 驗收1-5=<各自 通過/失敗>`
