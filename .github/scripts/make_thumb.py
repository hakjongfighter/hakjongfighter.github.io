"""블로그 썸네일(1600x1000) 만들기. 캐릭터는 images/characters/ 에서 골라요.

사용법 (Playwright + Chrome 필요):
  python .github/scripts/make_thumb.py <영어주소> <캐릭터이름> "<카테고리>" "<제목 줄1|줄2|줄3>" "<형광펜 단어>"
예:
  python .github/scripts/make_thumb.py seteuk-basics present-book "수행평가·세특" "세특이 뭐길래?|뜻부터 채우는|방법까지" "뜻부터"
결과: images/blog/<영어주소>.jpg
"""
import os, sys, html
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")

def main(slug, char, cat, title, hl=""):
    lines = [html.escape(x) for x in title.split("|")]
    if hl:
        lines = [l.replace(html.escape(hl), f"<em>{html.escape(hl)}</em>") for l in lines]
    fs = 92 if max(len(l) for l in title.split("|")) <= 9 else 80
    char_path = os.path.join(ROOT, "images", "characters", f"{char}.png")
    if not os.path.exists(char_path):
        sys.exit(f"캐릭터 이미지가 없어요: {char_path}")
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}}
body{{width:1600px;height:1000px;background:linear-gradient(135deg,#C9F4EC 0%,#7FD6CF 100%);font-family:'Noto Sans KR','Noto Sans CJK KR',sans-serif;color:#1C2A5E;position:relative;overflow:hidden}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(28,42,94,.10) 2px,transparent 2px);background-size:36px 36px}}
.blob{{position:absolute;right:230px;top:50%;width:560px;height:560px;margin-top:-280px;border-radius:999px;background:rgba(255,255,255,.55)}}
.safe{{position:absolute;left:225px;right:225px;top:0;bottom:0;display:flex;align-items:center;gap:20px}}
.t{{flex:1;display:flex;flex-direction:column;gap:30px;position:relative}}
.pill{{align-self:flex-start;background:#1C2A5E;color:#FFC72C;font-weight:700;font-size:34px;padding:12px 28px;border-radius:999px}}
h1{{font-size:{fs}px;line-height:1.22;font-weight:900;letter-spacing:-3px}}
h1 em{{font-style:normal;background:linear-gradient(transparent 60%,#FFC72C 60%)}}
.brand{{font-size:30px;font-weight:700;color:#33447F}}
.c{{flex:none;width:520px;height:720px;display:flex;align-items:center;justify-content:center;position:relative}}
.c img{{max-width:100%;max-height:100%;filter:drop-shadow(10px 14px 0 rgba(28,42,94,.18))}}
</style></head><body><div class="dots"></div><div class="blob"></div><div class="safe"><div class="t"><span class="pill">{html.escape(cat)}</span><h1>{'<br>'.join(lines)}</h1><div class="brand">학종파이터 블로그</div></div><div class="c"><img src="file://{char_path}"></div></div></body></html>"""
    tmp = os.path.join(ROOT, ".thumb_tmp.html")
    open(tmp, "w", encoding="utf-8").write(page)
    out = os.path.join(ROOT, "images", "blog", f"{slug}.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1600, "height": 1000})
        pg.goto("file://" + tmp); pg.wait_for_timeout(500)
        pg.screenshot(path=out, type="jpeg", quality=86)
        b.close()
    os.remove(tmp)
    print("만들었어요:", out)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    main(*sys.argv[1:6])
