# 黑客影片

用 HackerTube 公開資料做的繁體中文靜態影片站。片單來自 Hacker News 上反覆被推薦的 YouTube 影片。介面是繁體中文，影片摘要與留言保留英文原文。

純靜態：沒有後端、沒有登入、沒有打包工具。按讚、稍後觀看、觀看紀錄存在瀏覽器的 localStorage。

## 重建資料

在專案根目錄執行：

```
python build_data.py
```

需要 Python 3 與 numpy。腳本只讀 `source/`，把結果寫進 `site/data/`。再跑一次會先清掉舊的 `site/data/` 再整份覆蓋。

結束時會印出影片數、預設隱藏數（`shelf_life` 為 `news`，或推薦人數為 0）、以及 `site/data/` 的總大小。

## 本機預覽

```
python -m http.server -d site 8765
```

瀏覽器開 `http://127.0.0.1:8765/`。請用這個方式開，不要直接點開 `index.html`，否則瀏覽器會擋住 `fetch` 讀取 JSON。

可分享的網址用 hash，例如 `#/watch/fNk_zzaMoSs`、`#/c/pure-mathematics`。

## 未完成

沒有。規格裡的清單都有做：首頁依分數排序並可繼續載入、分類樹、篩選、站內搜尋、影片頁、相似影片、同一群人也推薦、按讚／稍後觀看／觀看紀錄、深色模式、預設隱藏新聞與零推薦、頁尾出處。
