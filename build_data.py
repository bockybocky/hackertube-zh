# -*- coding: utf-8 -*-
"""把 source/ 轉成 site/data/。只用標準函式庫與 numpy。重跑會整份覆蓋。"""
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source"
OUT = ROOT / "site" / "data"

# id → 繁體中文。翻不準的保留英文（此表沒有這種情況時，缺漏會退回原文）。
AREA_ZH = {
    "software": "軟體工程與程式語言",
    "systems-security": "系統、網路與資安",
    "ai-data": "人工智慧、機器學習與資料",
    "math-theory": "數學與理論計算機科學",
    "hardware": "硬體與電子",
    "computing-history-culture": "電腦史與文化",
    "design-graphics-media": "設計、圖像與視覺媒體",
    "business-economics": "商業、新創與經濟",
    "politics-history-society": "政治、歷史與社會",
    "physics-space": "物理、太空與化學",
    "life-sciences-health": "生命科學、心智與健康",
    "earth-energy-environment": "地球、能源與環境",
    "engineering-making": "工程、交通與製作",
    "games": "遊戲與遊戲開發",
    "arts-entertainment": "藝術、喜劇、音樂與電影",
    "ideas-education": "思想、學習與語言",
}

CAT_ZH = {
    "programming-language-design": "程式語言設計",
    "functional-programming": "函數式程式設計",
    "systems-programming-languages": "C、C++、Rust、Go 與系統語言",
    "scripting-languages": "Python、Ruby 與腳本語言",
    "web-development": "網頁開發",
    "software-architecture-design": "軟體架構與設計",
    "software-performance": "軟體效能與最佳化",
    "compilers-interpreters": "編譯器、直譯器與程式分析",
    "testing-debugging-tools": "測試、除錯與開發工具",
    "software-practice-careers": "軟體實務、開源與職涯",
    "software-other": "軟體（其他）",
    "databases-storage": "資料庫與儲存",
    "distributed-systems": "分散式系統",
    "operating-systems": "作業系統與核心",
    "linux-open-source-os": "Linux 與開源生態",
    "networking-internet": "網路與網際網路基礎建設",
    "cloud-devops-sre": "雲端、DevOps 與可靠性",
    "security-hacking": "資安與駭客技術",
    "cryptography": "密碼學",
    "privacy-surveillance": "隱私、監控與網路犯罪",
    "systems-other": "系統與資安（其他）",
    "machine-learning": "機器學習與深度學習",
    "llms-generative-ai": "大型語言模型與生成式 AI",
    "ai-safety-impact": "AI 安全、AGI 與社會影響",
    "robotics": "機器人",
    "self-driving-cars": "自駕與自動駕駛車輛",
    "computer-vision-speech": "電腦視覺、語音與自然語言",
    "data-science-statistics": "資料科學與統計",
    "data-visualization": "資料視覺化與資訊設計",
    "ai-data-other": "AI 與資料（其他）",
    "algorithms-data-structures": "演算法與資料結構",
    "computational-theory": "可計算性與複雜度理論",
    "quantum-computing": "量子計算",
    "pure-mathematics": "純數學",
    "probability-game-theory": "機率與賽局理論",
    "recreational-math": "休閒與視覺數學",
    "logic-formal-methods": "邏輯與形式方法",
    "information-theory": "資訊理論與訊號處理",
    "math-theory-other": "數學與理論（其他）",
    "computer-architecture": "計算機架構與 CPU",
    "semiconductors-manufacturing": "半導體與晶片製造",
    "electronics-circuits": "電子與電路設計",
    "embedded-diy-electronics": "嵌入式系統與 DIY 電子",
    "repair-teardown": "維修、拆解與維修權",
    "consumer-devices": "消費性裝置與小工具",
    "audio-video-engineering": "音訊與視訊工程",
    "hardware-other": "硬體（其他）",
    "history-of-computing": "電腦史",
    "gui-hci-history": "圖形介面、人機互動與介面史",
    "hacker-culture-free-software": "駭客文化與自由軟體",
    "demoscene-retrocomputing": "Demo 場景與復古電腦",
    "internet-culture": "網路文化與迷因",
    "tech-figures-interviews": "科技先驅與訪談",
    "tech-company-stories": "科技公司故事與紀錄片",
    "computing-history-other": "電腦文化（其他）",
    "ux-ui-design": "UX 與 UI 設計",
    "product-industrial-design": "產品與工業設計",
    "graphic-design-typography": "平面設計與字體",
    "computer-graphics-rendering": "電腦圖學與算圖",
    "creative-coding-generative-art": "創意程式與生成藝術",
    "animation-vfx": "動畫與視覺特效",
    "film-video-production": "電影與影片製作",
    "vr-ar-spatial": "VR、AR 與空間運算",
    "design-graphics-other": "設計與圖像（其他）",
    "startups-entrepreneurship": "新創與創業",
    "product-growth-marketing": "產品、行銷與業務",
    "management-leadership": "管理、領導與組織",
    "tech-industry-business": "科技產業與商業模式",
    "investing-personal-finance": "投資與個人理財",
    "macroeconomics": "總體經濟與金融危機",
    "microeconomics-behavioral": "個體經濟與行為經濟",
    "labor-work-wealth": "勞動、工作與不平等",
    "business-economics-other": "商業與經濟（其他）",
    "us-politics": "美國政治與選舉",
    "geopolitics-foreign-policy": "地緣政治與外交",
    "law-policing-justice": "法律、執法與司法",
    "free-speech-censorship": "言論自由、審查與公民自由",
    "world-history": "世界史",
    "military-warfare": "軍事史與戰爭",
    "social-issues-culture": "社會議題與文化",
    "media-journalism": "媒體、新聞與宣傳",
    "politics-history-other": "政治與歷史（其他）",
    "fundamental-physics": "基礎物理",
    "quantum-physics": "量子物理",
    "cosmology-astrophysics": "宇宙學與天文物理",
    "space-exploration": "太空探索與航太",
    "chemistry": "化學",
    "materials-science": "材料科學",
    "everyday-physics-demos": "日常物理與科學示範",
    "physics-space-other": "物理與太空（其他）",
    "neuroscience-brain": "神經科學與大腦",
    "psychology-behavior": "心理學與人類行為",
    "mental-health-neurodiversity": "心理健康與神經多樣性",
    "consciousness-mind": "意識與認知",
    "evolution-genetics": "演化與遺傳學",
    "biology-biotech": "生物與生物科技",
    "medicine-disease": "醫學與傳染病",
    "nutrition-diet": "營養與飲食科學",
    "fitness-sleep-longevity": "體能、睡眠與長壽",
    "animals-nature": "動物與自然",
    "life-sciences-other": "生命科學（其他）",
    "climate-science": "氣候科學與氣候變遷",
    "climate-debate-policy": "氣候政策、解方與爭論",
    "nuclear-energy": "核能與核融合",
    "renewables-storage": "再生能源、電池與儲能",
    "power-grid-heating": "電網、供暖與建築",
    "geology-earth-science": "地質與地球科學",
    "environment-agriculture": "環境、農業與糧食系統",
    "earth-energy-other": "地球與能源（其他）",
    "aviation": "航空與航太工程",
    "automotive-ev": "汽車、電動車與機車",
    "transit-urbanism": "大眾運輸、城市與都市規劃",
    "civil-engineering-construction": "土木工程與營建",
    "mechanical-engineering": "機械與精密工程",
    "manufacturing-industry": "製造與工業製程",
    "making-woodworking-metalwork": "木工、金工與工坊技藝",
    "3d-printing-cnc": "3D 列印、CNC 與自造專案",
    "home-diy-repair": "居家、DIY 與實用技能",
    "cooking-food": "烹飪與食物",
    "ships-ocean": "船舶、潛艇與海事",
    "engineering-making-other": "工程與製作（其他）",
    "game-design": "遊戲設計",
    "game-programming-engines": "遊戲程式與引擎",
    "indie-game-development": "獨立遊戲開發",
    "game-history-retro": "遊戲史與復古遊戲",
    "gaming-culture": "遊戲文化與分析",
    "speedrunning-glitches": "速通、漏洞與遊戲破解",
    "chess-board-games": "西洋棋、桌遊與謎題",
    "games-other": "遊戲（其他）",
    "standup-sketch-comedy": "單口與短劇喜劇",
    "satire-parody": "諷刺與戲仿",
    "music-performance": "音樂演出與歌曲",
    "music-theory-production": "樂理、合成與製作",
    "film-tv-clips": "電影與電視片段",
    "film-criticism-analysis": "電影分析與評論",
    "documentaries-storytelling": "紀錄片與敘事",
    "literature-writing": "文學與寫作技藝",
    "visual-arts": "視覺藝術、攝影與建築",
    "sports-athletics": "運動競技",
    "magic-performance-oddities": "魔術、謎題與奇趣",
    "arts-entertainment-other": "藝術與娛樂（其他）",
    "education-learning": "教育與學習",
    "university-lectures": "大學講座與課程",
    "philosophy-ethics": "哲學與倫理",
    "religion-belief": "宗教、信仰與懷疑論",
    "language-linguistics": "語言與語言學",
    "productivity-self-improvement": "生產力與自我精進",
    "futurism-technology-society": "未來學與科技社會",
    "science-method-communication": "科學方法與科學傳播",
    "ideas-education-other": "思想與學習（其他）",
}

K_SIM = 12
K_RELATED = 12
K_MENTIONS = 5


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def load_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def slim_video(raw: dict) -> dict:
    hn = raw.get("hn") or {}
    quote = raw.get("quote")
    if quote and quote.get("text"):
        quote_out = {"text": quote.get("text") or "", "year": quote.get("year")}
    else:
        quote_out = None
    cats = []
    for c in raw.get("categories") or []:
        cid = c.get("id") if isinstance(c, dict) else c
        if cid:
            cats.append(cid)
    return {
        "vid": raw["vid"],
        "title": raw.get("title") or "",
        "channel": raw.get("channel") or "",
        "summary": raw.get("summary") or "",
        "why_hn": raw.get("why_hn") or "",
        "content_type": raw.get("content_type") or "other",
        "level": raw.get("level") or "general",
        "shelf_life": raw.get("shelf_life") or "",
        "primary_topic": raw.get("primary_topic") or "",
        "tags": raw.get("tags") or [],
        "categories": cats,
        "quote": quote_out,
        "hn": {
            "recommenders": int(hn.get("recommenders") or 0),
            "rec_months": int(hn.get("rec_months") or 0),
            "strong_recs": int(hn.get("strong_recs") or 0),
            "first_year": hn.get("first_year"),
            "last_year": hn.get("last_year"),
        },
        "score": raw.get("score") or 0,
    }


def top_similar(emb: np.ndarray, k: int) -> np.ndarray:
    """emb 已 L2 正規化。回傳 (n, k) 的列索引，不含自己，相似度由高到低。"""
    n = emb.shape[0]
    out = np.empty((n, k), dtype=np.int32)
    batch = 512
    for start in range(0, n, batch):
        end = min(start + batch, n)
        sims = emb[start:end] @ emb.T
        for i, gi in enumerate(range(start, end)):
            sims[i, gi] = -1e9
        idx = np.argpartition(sims, -k, axis=1)[:, -k:]
        part = np.take_along_axis(sims, idx, axis=1)
        order = np.argsort(-part, axis=1)
        out[start:end] = np.take_along_axis(idx, order, axis=1)
    return out


def build_taxonomy(raw: dict) -> dict:
    areas = []
    missing = []
    for area in raw["areas"]:
        aid = area["id"]
        cats = []
        for c in area["categories"]:
            cid = c["id"]
            name = CAT_ZH.get(cid)
            if not name:
                missing.append(cid)
                name = c["name"]
            cats.append({"id": cid, "name": name})
        aname = AREA_ZH.get(aid)
        if not aname:
            missing.append(aid)
            aname = area["name"]
        areas.append({"id": aid, "name": aname, "categories": cats})
    if missing:
        print("未翻譯、保留英文：", ", ".join(missing))
    return {"areas": areas}


# 置頂精選分類（2026-11-02 Charles：「加入金屬材料學放在最上面」）。
# 人工挑選：冶煉、鍛造、鑄造、沖壓、焊接、切削與精密工具機、超合金、金屬積層製造、合金檢測。
# 排除只是字面撞到 metal／steel／rust 的（Rust 程式語言、青銅時代史、金屬樂、玻璃）。
PINNED = [
    {
        "id": "metal-materials",
        "name": "金屬材料學",
        "vids": [
            "fzBRYsiyxjI", "RuCnZClWwpQ", "hpgK51w6uhk", "iZ50nZU3oG8", "GDzBE6vz5r0",
            "hUhisi2FBuw", "QtxVdC7pBQM", "BwoiFC-HwPE", "gNRnrn5DE58", "djB9oK6pkbA",
            "sFrVdoOhu1Q", "RnIvhlKT7SY", "iptAkpqjtMQ", "xMP_AfiNlX4", "PaypcVFPs48",
            "B8Y146v8HxE", "EWqThb9Z1jk", "o0fG_lnVhHw", "5uxsFglz2ig", "zqmOSMAtadc",
            "FzF1KySHmUA", "jeghGhVdt9s", "d6Pcp944sRI", "KdfHVcU8U7U", "v5GPWJPLcHg",
            "VVV4xeWBIxE", "MBVmnKuBocc",
        ],
    },
]


def apply_pinned(videos: list, tax: dict) -> dict:
    by_vid = {v["vid"]: v for v in videos}
    cats = []
    for pin in PINNED:
        missing = [vid for vid in pin["vids"] if vid not in by_vid]
        if missing:
            raise SystemExit(f"置頂分類 {pin['id']} 有影片不在資料裡：{missing}")
        for vid in pin["vids"]:
            cs = by_vid[vid].get("categories") or []
            if pin["id"] not in cs:
                by_vid[vid]["categories"] = [pin["id"]] + cs
        cats.append({"id": pin["id"], "name": pin["name"]})
    return {"areas": [{"id": "pinned", "name": "置頂", "pinned": True, "categories": cats}] + tax["areas"]}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    videos_raw = [slim_video(r) for r in load_jsonl(SRC / "videos.jsonl")]
    videos_raw.sort(key=lambda v: (-float(v["score"]), v["vid"]))
    known = {v["vid"] for v in videos_raw}

    ids = json.loads((SRC / "embedding_ids.json").read_text(encoding="utf-8"))
    if len(ids) != len(videos_raw):
        raise SystemExit(f"embedding 列數 {len(ids)} 與影片數 {len(videos_raw)} 不一致")
    emb = np.load(SRC / "embeddings.npy").astype(np.float32)
    if emb.shape[0] != len(ids):
        raise SystemExit(f"embeddings 形狀 {emb.shape} 與 id 數不符")
    print("計算相似影片…", flush=True)
    neigh = top_similar(emb, K_SIM)
    row_of = {vid: i for i, vid in enumerate(ids)}
    similar = []
    for v in videos_raw:
        i = row_of[v["vid"]]
        similar.append([ids[j] for j in neigh[i]])

    cowatch = {}
    for row in load_jsonl(SRC / "related.jsonl"):
        vid = row["vid"]
        if vid not in known:
            continue
        rel = []
        for item in row.get("related") or []:
            rv = item.get("vid") if isinstance(item, dict) else item
            if rv and rv != vid and rv in known:
                rel.append(rv)
            if len(rel) >= K_RELATED:
                break
        if rel:
            cowatch[vid] = rel

    buckets = defaultdict(lambda: {"strong_rec": [], "rec": []})
    for m in load_jsonl(SRC / "mentions.jsonl"):
        stance = m.get("stance")
        if stance not in ("rec", "strong_rec"):
            continue
        vid = m.get("vid")
        if vid not in known:
            continue
        quote = (m.get("quote") or "").strip()
        if not quote:
            quote = (m.get("text") or "").strip()[:300]
        if not quote:
            continue
        buckets[vid][stance].append(
            {
                "author": m.get("author") or "",
                "month": m.get("month") or "",
                "quote": quote,
                "hn_url": m.get("hn_url") or "",
            }
        )

    mentions = {}
    for vid, bag in buckets.items():
        picked = (bag["strong_rec"] + bag["rec"])[:K_MENTIONS]
        if picked:
            mentions[vid] = picked

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    tax = json.loads((SRC / "taxonomy.json").read_text(encoding="utf-8"))
    tax_out = apply_pinned(videos_raw, build_taxonomy(tax))
    dump(OUT / "videos.json", videos_raw)
    dump(OUT / "similar.json", similar)
    dump(OUT / "cowatch.json", cowatch)
    dump(OUT / "taxonomy.json", tax_out)

    shards = defaultdict(dict)
    for vid, rows in mentions.items():
        shards[vid[0].lower()][vid] = rows
    mdir = OUT / "m"
    mdir.mkdir()
    for key, obj in shards.items():
        dump(mdir / f"{key}.json", obj)

    hidden = sum(
        1
        for v in videos_raw
        if v["shelf_life"] == "news" or v["hn"]["recommenders"] == 0
    )
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    nfiles = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"影片數 {len(videos_raw)}")
    print(f"被預設隱藏數 {hidden}")
    print(f"資料檔總大小 {total / 1048576:.2f} MB（{nfiles} 個檔）")


if __name__ == "__main__":
    main()
