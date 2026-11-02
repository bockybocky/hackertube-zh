# 派工說明：金屬材料學加「軟體教學」子分類（SolidWorks／DEFORM）

## 1. 目標
Charles 原話：「放soilwork 跟deform 軟體教學」（soilwork＝SolidWorks）。
在網站「金屬材料學」區塊（側欄置頂）加第六個子分類「軟體教學」，收 SolidWorks 與 DEFORM（金屬成形模擬軟體，SFTC 出品）的 YouTube 教學影片。

## 2. 背景（已存在的東西，照用不要重寫）
- 專案：C:/Users/Charles/projects/hackertube-zh（git 倉庫，公開在 GitHub）
- `build_data.py`：產生 `site/data/*.json`。裡面已有 `PINNED_AREA`、`PINNED`（五個子分類，影片 id 清單）、`apply_pinned()`。
  `PINNED` 裡的影片都來自原始資料包；新的教學影片**不在**資料包裡，要另外加進 videos 清單。
- 單支影片欄位（照這個形狀）：
  `vid, title, channel, summary(英文一句), why_hn(英文一句), content_type("tutorial"), level("intro"|"intermediate"|"advanced"), shelf_life("evergreen"), primary_topic, tags(list), categories(list), quote({"text":"","year":""}), hn({"recommenders":0,"rec_months":0,"strong_recs":0,"first_year":null,"last_year":null}), score(0.0)`
- 前端 `site/app.js`：`featured` 區的分類裡，零推薦的影片照樣顯示（不用改前端）。
- 相似影片計算吃 `source/embedding_ids.json` 與 `embeddings.npy`，長度必須等於影片數。**新影片沒有向量**：請把外加影片放在相似影片計算之後再併入，並給它們的 similar 一個空清單或同子分類的其他影片，不可讓長度檢查失敗。
- YouTube 搜尋用本機 `yt-dlp`（已裝，可用 `ytsearchN:關鍵字` 與 `--print "%(id)s|%(title)s|%(channel)s|%(duration)s"`）。

## 3. 要做的事
1. 用 yt-dlp 搜尋，挑 SolidWorks 教學約 12 支、DEFORM 教學約 10 支。
   - 挑選準則：真的是操作教學或完整示範；長度 ≥ 3 分鐘（DEFORM 官方頻道 SFTC DEFORM 的短示範片可例外收 2～3 支）；英文或中文皆可；偏機械設計／金屬成形相關（SolidWorks 優先：入門、鈑金、模擬 Simulation、工程圖）。
   - 每支用 `https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=<id>` 確認回 200（可嵌入），不是 200 的換掉。
2. 把挑好的清單寫成 `extra_videos.json`（專案根目錄，欄位如上，categories＝["metal-software"]，tags 要含 "solidworks" 或 "deform"）。
3. 改 `build_data.py`：讀 `extra_videos.json` 併入 videos；`PINNED` 加 `{"id":"metal-software","name":"軟體教學","vids":[...]}`（排在最後）；重複 id 要報錯。
4. 跑 `PYTHONUTF8=1 python build_data.py` 重建。
5. `site/index.html` 裡 `?v=20261102s` 兩處改成 `?v=20261102t`。

## 4. 邊界（不准做）
- 不准改 `site/app.js`、`site/style.css`、`serve.py`、任何排程、`~/.cloudflared/`。
- 不准 git commit／push（主對話驗收後自己提交）。
- 不准用 git stash／checkout／restore／reset。
- 不准刪 `source/` 底下任何檔。

## 5. 驗收（做完自己跑，貼輸出）
```
cd C:/Users/Charles/projects/hackertube-zh
PYTHONUTF8=1 python -c "import json;v=json.load(open('site/data/videos.json',encoding='utf-8'));t=json.load(open('site/data/taxonomy.json',encoding='utf-8'));s=[x for x in v if 'metal-software' in x['categories']];print(len(v),len(s),[c['name'] for c in t['areas'][0]['categories']]);print(sum('solidworks' in ' '.join(x['tags']).lower() for x in s),sum('deform' in ' '.join(x['tags']).lower() for x in s))"
```
預期：影片總數＝6454＋外加數；第一區最後一個子分類是「軟體教學」；SolidWorks ≥10、DEFORM ≥8。
另附一張表：每支的 id｜標題｜頻道｜長度｜oembed 狀態。產物報告寫進 `specs/metal_software_tutorials_report.md`。
