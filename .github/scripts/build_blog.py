"""blog/posts/*.md 글을 읽어 블로그 페이지를 만듭니다.

만드는 파일
  blog/index.html          글 목록 (메인)
  blog/<slug>/index.html   글 상세
  sitemap.xml              랜딩 + 블로그 글 주소

GitHub Actions 배포 때 자동 실행됩니다. 직접 미리 보려면:
  pip install markdown
  python .github/scripts/build_blog.py
"""
import html
import os
import re
import sys
from datetime import date

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BLOG = os.path.join(ROOT, "blog")
POSTS = os.path.join(BLOG, "posts")
SITE = "https://hakjongfighter.com"
IG = "https://www.instagram.com/hakjong_fighter/"
DM = "https://ig.me/m/hakjong_fighter"

# 카테고리 순서 (글의 category 값은 이 중 하나로 쓰세요)
LANDING_LASTMOD = "2026-11-20"  # 랜딩페이지(index.html)를 고치면 날짜를 바꿔 주세요
CATEGORIES = ["진로·과목 선택", "수행평가·세특", "심화탐구", "내신 공부법", "대학·전형 정보", "학부모 가이드", "4컷 만화"]


def esc(s):
    return html.escape(str(s), quote=True)


def parse_post(path):
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise ValueError(f"{path}: 맨 위에 --- 로 감싼 글 정보가 없어요")
    meta = {}
    for line in m.group(1).split("\n"):
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"').strip("'")
    for need in ("title", "date", "category"):
        if not meta.get(need):
            raise ValueError(f"{path}: '{need}' 항목이 비어 있어요")
    if meta.get("draft", "").lower() in ("true", "yes", "1"):
        return None
    fname = os.path.basename(path)[:-3]
    slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fname)
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError(f"{path}: 주소(slug)는 영어 소문자·숫자·하이픈만 써요 → '{slug}'")
    body = m.group(2)
    text_len = len(re.sub(r"<[^>]+>|[#*>\-\s`|]", "", body))
    post = {
        "slug": slug,
        "title": meta["title"],
        "date": date.fromisoformat(meta["date"]),
        "category": meta["category"],
        "summary": meta.get("summary", ""),
        "thumbnail": meta.get("thumbnail", ""),
        "caption": meta.get("caption", ""),
        "tags": [t.strip().lstrip("#") for t in meta.get("tags", "").split(",") if t.strip()],
        "featured": meta.get("featured", "").lower() in ("true", "yes", "1"),
        "pick": meta.get("pick", "").lower() in ("true", "yes", "1"),
        "minutes": max(1, round(text_len / 400)),
        "html": markdown.markdown(body, extensions=["extra", "toc", "sane_lists"],
                                  extension_configs={"toc": {"slugify": slugify_unicode}}),
    }
    post["toc"] = re.findall(r'<h2 id="[^"]+">(.*?)</h2>', post["html"])
    return post


def head(title, desc, url, image, extra=""):
    return f"""<!doctype html>
<html lang="ko">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-WP2WRX3L');</script>
<!-- Google Analytics (GA4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4G2NGCPVXG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-4G2NGCPVXG');
  window.hfTrack = function (name, params) {{ gtag('event', name, params || {{}}); }};
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:type" content="{'article' if extra else 'website'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:url" content="{esc(url)}">
<link rel="canonical" href="{esc(url)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBFAF7">
<link rel="icon" type="image/png" href="/images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/blog/assets/blog.css">
{extra}</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WP2WRX3L" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<header><div class="wrap">
 <a class="brand" href="/blog/"><img src="/images/character.jpg" alt="">학종파이터 <i>블로그</i></a>
 <nav class="hnav"><a class="hide" href="/blog/">전체 글</a><a class="hide" href="/">학종파이터 홈</a><a class="sub" href="{IG}" target="_blank" rel="noopener" onclick="hfTrack('blog_follow',{{place:'header'}})">인스타 팔로우</a></nav>
</div></header>
"""


FOOT = """<footer><div class="wrap"><span>© {y} 강남에듀플랜 · 학종파이터</span><span><a href="/">hakjongfighter.com</a></span></div></footer>
</body>
</html>
"""


def thumb(p, cls=""):
    if p["thumbnail"]:
        return f'<img src="{esc(p["thumbnail"])}" alt="" loading="lazy">'
    return '<div class="t">✏️</div>'


def fmt_date(d, full=False):
    return f"{d.year}년 {d.month}월 {d.day}일" if full else f"{d.month}월 {d.day}일"


def dm_box(place):
    return f"""<div class="dm"><div class="st">1:1 상담</div>인스타그램 DM으로 <b>[설계도]</b>라고 보내면 세특 작성법과 내신 공부법을 무료로 상담해 드려요.<br><a href="{DM}" target="_blank" rel="noopener" onclick="hfTrack('blog_dm',{{place:'{place}'}})">@hakjong_fighter →</a></div>"""


def build_index(posts):
    featured = next((p for p in posts if p["featured"]), posts[0] if posts else None)
    rest = [p for p in posts if p is not featured]
    picks = [p for p in posts if p["pick"]][:5] or posts[:4]
    used = [c for c in CATEGORIES if any(p["category"] == c for p in posts)]
    used += sorted({p["category"] for p in posts} - set(used))
    out = [head("학종파이터 블로그 | 생기부를 하나의 이야기로 잇는 기록",
                "세특, 과목 선택, 심화탐구까지. 고등학생과 학부모를 위한 학종파이터의 학생부 기록.",
                f"{SITE}/blog/", f"{SITE}/images/og.jpg")]
    out.append("""<div class="wrap">
 <section class="intro">
  <div class="k">HAKJONG FIGHTER JOURNAL</div>
  <h1 class="serif">3년의 생기부를<br><mark>하나의 이야기</mark>로 잇는 기록</h1>
  <p>세특, 과목 선택, 심화탐구까지. 매주 한 편씩 차근차근 씁니다.</p>
 </section>
""")
    out.append(' <div class="cats" role="group" aria-label="카테고리"><button type="button" data-cat="" aria-pressed="true">전체</button>' +
               "".join(f'<button type="button" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in used) + "</div>\n")
    out.append(' <div class="body">\n  <div>\n')
    if featured:
        p = featured
        out.append(f"""   <a class="pin" href="/blog/{p['slug']}/" data-cat="{esc(p['category'])}">
    {thumb(p)}
    <div>
     <div class="lab">{esc(p['category'])} · 추천 글</div>
     <h2 class="serif">{esc(p['title'])}</h2>
     <p>{esc(p['summary'])}</p>
     <div class="meta">{fmt_date(p['date'], True)} · {p['minutes']}분 읽기</div>
    </div>
   </a>
""")
    for p in rest:
        out.append(f"""   <a class="item" href="/blog/{p['slug']}/" data-cat="{esc(p['category'])}"><div><div class="lab">{esc(p['category'])}</div><h3 class="serif">{esc(p['title'])}</h3><p>{esc(p['summary'])}</p><div class="meta">{fmt_date(p['date'])} · {p['minutes']}분</div></div>{thumb(p)}</a>
""")
    out.append('   <p class="empty" hidden>이 카테고리에는 아직 글이 없어요.</p>\n  </div>\n')
    out.append(f"""  <aside>
   <div class="who"><img src="/images/character.jpg" alt=""><b>학종파이터</b><p>고등학생과 학부모를 위한 학생부종합전형 기록. 3년의 활동이 한 방향으로 이어지도록 돕습니다.</p></div>
   <div><div class="st">추천 글</div><ol class="pop">{''.join(f'<li><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a></li>' for p in picks)}</ol></div>
   <div class="letter"><h4 class="serif">새 글 소식 받기</h4><p>새 글이 올라오면 인스타그램에서 가장 먼저 알려 드려요.</p><a class="b" href="{IG}" target="_blank" rel="noopener" onclick="hfTrack('blog_follow',{{place:'sidebar'}})">@hakjong_fighter 팔로우</a></div>
   {dm_box('index')}
  </aside>
 </div>
</div>
<script>
(function(){{
  var btns=document.querySelectorAll('.cats button'),cards=document.querySelectorAll('.pin,.item'),empty=document.querySelector('.empty');
  function set(cat){{
    var n=0;
    btns.forEach(function(b){{b.setAttribute('aria-pressed',b.dataset.cat===cat?'true':'false');}});
    cards.forEach(function(c){{var show=!cat||c.dataset.cat===cat;c.hidden=!show;if(show)n++;}});
    empty.hidden=n>0;
  }}
  btns.forEach(function(b){{b.addEventListener('click',function(){{set(b.dataset.cat);}});}});
}})();
</script>
""")
    out.append(FOOT.format(y=date.today().year))
    return "".join(out)


def build_post(p, posts):
    i = posts.index(p)
    newer = posts[i - 1] if i > 0 else None
    older = posts[i + 1] if i + 1 < len(posts) else None
    others = [q for q in posts if q is not p]
    related = ([q for q in others if q["category"] == p["category"]] + [q for q in others if q["category"] != p["category"]])[:3]
    url = f"{SITE}/blog/{p['slug']}/"
    img = SITE + p["thumbnail"] if p["thumbnail"].startswith("/") else (p["thumbnail"] or f"{SITE}/images/og.jpg")
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BlogPosting",'
          f'"headline":{json_str(p["title"])},"datePublished":"{p["date"].isoformat()}",'
          f'"image":{json_str(img)},"author":{{"@type":"Organization","name":"학종파이터"}},'
          f'"mainEntityOfPage":{json_str(url)}}}</script>\n')
    out = [head(f"{p['title']} | 학종파이터 블로그", p["summary"] or p["title"], url, img, ld)]
    out.append(f"""<div class="wrap">
<article class="art">
 <div class="crumb"><a href="/blog/">블로그</a> › <b>{esc(p['category'])}</b></div>
 <h1 class="serif">{esc(p['title'])}</h1>
 {f'<p class="sumline">{esc(p["summary"])}</p>' if p['summary'] else ''}
 <div class="by"><img src="/images/character.jpg" alt=""><div><b>학종파이터</b>{fmt_date(p['date'], True)} · {p['minutes']}분 읽기</div><div class="sh"><span role="button" tabindex="0" title="링크 복사" onclick="navigator.clipboard&&navigator.clipboard.writeText(location.href);this.textContent='✓'">🔗</span></div></div>
""")
    if p["thumbnail"]:
        out.append(f' <img class="hero-img" src="{esc(p["thumbnail"])}" alt="">\n')
        if p["caption"]:
            out.append(f' <div class="cap">{esc(p["caption"])}</div>\n')
    if len(p["toc"]) >= 2:
        out.append(' <div class="toc"><b>이 글의 순서</b><ol>' + "".join(f"<li>{t}</li>" for t in p["toc"]) + "</ol></div>\n")
    out.append(f' <div class="prose">\n{p["html"]}\n </div>\n')
    if p["tags"]:
        out.append(' <div class="tags2">' + "".join(f"<span>#{esc(t)}</span>" for t in p["tags"]) + "</div>\n")
    out.append(f""" <div class="end"><img src="/images/character.jpg" alt=""><div><h4 class="serif">내 생기부는 어떻게 이어 갈까?</h4><p>인스타그램 DM으로 [설계도]라고 보내면 세특 작성법과 내신 공부법을 무료로 상담해 드려요.</p><div class="acts"><a class="d" href="{DM}" target="_blank" rel="noopener" onclick="hfTrack('blog_dm',{{place:'post_end'}})">DM으로 [설계도] 보내기</a><a href="{IG}" target="_blank" rel="noopener" onclick="hfTrack('blog_follow',{{place:'post_end'}})">인스타 팔로우</a></div></div></div>
""")
    if newer or older:
        out.append(' <div class="pn">')
        out.append(f'<a href="/blog/{older["slug"]}/"><small>← 이전 글</small><b>{esc(older["title"])}</b></a>' if older else "<span></span>")
        out.append(f'<a href="/blog/{newer["slug"]}/"><small>다음 글 →</small><b>{esc(newer["title"])}</b></a>' if newer else "<span></span>")
        out.append("</div>\n")
    out.append("</article>\n")
    if related:
        out.append('<section class="rel"><div class="st">함께 읽으면 좋은 글</div><div class="relg">' + "".join(
            f'<a href="/blog/{q["slug"]}/">{thumb(q)}<div class="lab">{esc(q["category"])}</div><h3>{esc(q["title"])}</h3></a>' for q in related) + "</div></section>\n")
    out.append("</div>\n")
    out.append(FOOT.format(y=date.today().year))
    return "".join(out)


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def build_sitemap(posts):
    today = date.today().isoformat()
    urls = [(f"{SITE}/", LANDING_LASTMOD), (f"{SITE}/blog/", posts[0]["date"].isoformat() if posts else today)]
    urls += [(f"{SITE}/blog/{p['slug']}/", p["date"].isoformat()) for p in posts]
    body = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def main():
    posts = []
    for f in sorted(os.listdir(POSTS)):
        if f.endswith(".md") and not f.startswith("_"):
            p = parse_post(os.path.join(POSTS, f))
            if p:
                posts.append(p)
    slugs = [p["slug"] for p in posts]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        raise ValueError(f"주소(slug)가 겹치는 글이 있어요: {', '.join(dup)}")
    posts.sort(key=lambda p: p["date"], reverse=True)
    for p in posts:
        d = os.path.join(BLOG, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(build_post(p, posts))
    open(os.path.join(BLOG, "index.html"), "w", encoding="utf-8").write(build_index(posts))
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap(posts))
    print(f"블로그 글 {len(posts)}개를 만들었어요.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print("블로그 만들기 실패:", e, file=sys.stderr)
        sys.exit(1)
