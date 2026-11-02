"""黑客影片靜態站伺服器：127.0.0.1:8818 → tube.getrealpha.com（Cloudflare 門禁只放 Charles）。

為什麼不用 `pythonw -m http.server`：pythonw 沒有 stderr，內建伺服器每個請求都寫存取紀錄到
stderr，寫不出去就讓請求中途斷線（2026-11-02 實測 ResponseEnded）。這裡把紀錄關掉。
"""
import functools
import http.server
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


if __name__ == "__main__":
    handler = functools.partial(QuietHandler, directory=str(SITE))
    http.server.ThreadingHTTPServer(("127.0.0.1", 8818), handler).serve_forever()
