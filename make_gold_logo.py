"""從公司向量標誌產生金色版（2026-11-02，Charles：「要不要放一個金色版本的？」）。

來源：D:/ai-memory/Projects/realpha_brand/assets/vector/（藍色 #388bfd 印記＋系統字型 Realpha）。
產物：site/brand/ 底下
  logo-gold-light.svg  淺底用：金色印記＋深色字（網站最上方）
  logo-gold-dark.svg   深底用：金色印記＋米白字（側欄）
  mark-gold.svg        只有印記（favicon、手機頂欄）
重跑即覆蓋，冪等。
"""
from pathlib import Path

SRC = Path("D:/ai-memory/Projects/realpha_brand/assets/vector")
OUT = Path(__file__).resolve().parent / "site" / "brand"
BLUE = 'fill="#388bfd"'
GRAD = (
    '<defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#f6d27a"/><stop offset="0.55" stop-color="#d9a12b"/>'
    '<stop offset="1" stop-color="#a8711a"/></linearGradient></defs>'
)


def golden(svg: str, text_fill: str | None) -> str:
    assert BLUE in svg, "來源檔沒有藍色印記，來源可能改版了"
    svg = svg.replace(BLUE, 'fill="url(#rg)"')
    j = svg.index(">", svg.index("<svg")) + 1  # 漸層定義塞在 <svg ...> 開頭標籤之後
    svg = svg[:j] + GRAD + svg[j:]
    if text_fill:
        for old in ('fill="#0d1117"', 'fill="#e6edf3"'):
            svg = svg.replace(old + ' letter-spacing', f'fill="{text_fill}" letter-spacing')
    return svg


light = (SRC / "logo_lockup_lighttheme.svg").read_text(encoding="utf-8")
(OUT / "logo-gold-light.svg").write_text(golden(light, "#1c1917"), encoding="utf-8")
(OUT / "logo-gold-dark.svg").write_text(golden(light, "#f5ecd9"), encoding="utf-8")
(OUT / "mark-gold.svg").write_text(golden((SRC / "logo_alpha_mark.svg").read_text(encoding="utf-8"), None), encoding="utf-8")

for f in ("logo-gold-light.svg", "logo-gold-dark.svg", "mark-gold.svg"):
    s = (OUT / f).read_text(encoding="utf-8")
    assert "#388bfd" not in s and 'id="rg"' in s and s.count('url(#rg)') >= 1, f
    print(f, len(s), "OK")
