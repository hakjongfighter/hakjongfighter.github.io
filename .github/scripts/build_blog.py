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

sys.path.insert(0, os.path.dirname(__file__))
import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BLOG = os.path.join(ROOT, "blog")
POSTS = os.path.join(BLOG, "posts")
SITE = "https://hakjongfighter.com"
IG = "https://www.instagram.com/hakjong_fighter/"
DM = "https://ig.me/m/hakjong_fighter"
# 공감·댓글 서버 주소 (Cloudflare Worker). 비워 두면 공감·댓글 칸이 보이지 않아요.
BLOG_API = os.environ.get("BLOG_API", "").strip()
# 상담 신청 페이지 (서버가 있을 때만 생김). 없으면 인스타그램으로 연결
CONSULT = "/consult/" if BLOG_API else IG

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
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]  # 양 끝이 같은 따옴표로 감싸진 경우만 벗김
        meta[k.strip()] = v
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
<!-- 운영자 기기(방문 현황 페이지를 연 브라우저)는 GA4·GTM에 기록을 보내지 않음 -->
<script>try{{if(localStorage.getItem('hf_internal')==='1'){{window.hfInternal=true;window['ga-disable-G-4G2NGCPVXG']=true;}}}}catch(e){{}}</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{if(w.hfInternal)return;w[l]=w[l]||[];w[l].push({{'gtm.start':
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
<!-- 자체 방문 집계 (GA4와 별개 · 쿠키와 IP 저장 없음) -->
<script defer src="/assets/hf-track.js"></script>
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
 <nav class="hnav"><a class="hide" href="/blog/"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.5" cy="6" r="1"/><circle cx="3.5" cy="12" r="1"/><circle cx="3.5" cy="18" r="1"/></svg>전체 글</a><a class="hide" href="/"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/></svg>학종파이터 홈</a><a class="sub" href="{IG}" target="_blank" rel="noopener" onclick="hfTrack('blog_follow',{{place:'header'}})"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.8" fill="currentColor"/></svg>instagram</a></nav>
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
    return f"""<div class="dm"><div class="st">1:1 전문 상담</div>학종 전문 선생님이 지금 학생부를 함께 보고, 과목 선택·수행평가부터 내신 공부 방법, 면접 대비까지 1:1로 상담해 드려요.<br><a href="{CONSULT}" onclick="hfTrack('blog_consult_click',{{place:'{place}'}})">전문 상담 신청 →</a></div>"""


def build_index(posts):
    featured = next((p for p in posts if p["featured"]), posts[0] if posts else None)
    rest = [p for p in posts if p is not featured]
    picks = [p for p in posts if p["pick"]][:5] or posts[:4]
    used = [c for c in CATEGORIES if any(p["category"] == c for p in posts)]
    used += sorted({p["category"] for p in posts} - set(used))
    out = [head("학종파이터 블로그 | 생기부를 하나의 이야기로 잇는 기록",
                "과목 선택부터 수행평가, 심화탐구까지. 고등학생과 학부모를 위한 학종파이터의 학생부 기록.",
                f"{SITE}/blog/", f"{SITE}/images/og.jpg")]
    out.append("""<div class="wrap">
 <section class="intro">
  <div class="k">HAKJONG FIGHTER JOURNAL</div>
  <h1 class="serif">3년의 생기부를<br><mark>하나의 이야기</mark>로 잇는 기록</h1>
  <p>과목 선택부터 수행평가, 심화탐구까지. 매주 한 편씩 차근차근 씁니다.</p>
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
   <div class="letter"><h4 class="serif">새 글 소식 받기</h4><p>새 글이 올라오면 인스타그램에서 가장 먼저 알려 드려요.</p><a class="b" href="{IG}" target="_blank" rel="noopener" onclick="hfTrack('blog_follow',{{place:'sidebar'}})">instagram</a></div>
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
    if BLOG_API:
        out.append(social_box(p))
    out.append(f""" <div class="end"><img src="/images/character.jpg" alt=""><div><h4 class="serif">내 생기부는 어떻게 이어 갈까?</h4><p>학종 전문 선생님이 지금 학생부를 함께 보고, 다음 학기에 무엇을 할지 1:1로 정리해 드려요.</p><div class="acts"><a class="d" href="{CONSULT}" onclick="hfTrack('blog_consult_click',{{place:'post_end'}})">전문 상담 신청</a><a href="{IG}" target="_blank" rel="noopener" onclick="hfTrack('blog_follow',{{place:'post_end'}})">instagram</a></div></div></div>
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


def social_box(p):
    return f"""<section id="social" data-api="{esc(BLOG_API)}" data-post="{p['slug']}" hidden>
 <div class="react"><p>이 글이 도움이 됐나요?<small>로그인 없이 한 번 누를 수 있어요.</small></p><button type="button" class="like" aria-pressed="false">❤️ 공감 <b>0</b></button></div>
 <div class="cmts">
  <h3>댓글<span class="ccount">0</span></h3>
  <div class="guide">💬 궁금한 점이나 생각을 남겨 주세요. 댓글은 <b>확인 후 공개</b>돼요.<br>🔒 이름, 학교, 연락처 같은 <b>개인정보는 적지 말아 주세요.</b></div>
  <form class="cform" autocomplete="off">
   <input class="nick" name="nick" maxlength="20" placeholder="닉네임" required aria-label="닉네임">
   <textarea name="body" maxlength="500" placeholder="댓글을 남겨 주세요" required aria-label="댓글 내용"></textarea>
   <input class="hp" name="website" tabindex="-1" aria-hidden="true">
   <div class="bot"><span class="len">0 / 500자</span><button type="submit">댓글 남기기</button></div>
   <p class="cmsg" role="status"></p>
  </form>
  <div class="clist"></div>
 </div>
</section>
<script src="/blog/assets/blog-social.js" defer></script>
"""


ADMIN = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>댓글 관리 | 학종파이터 블로그</title>
<link rel="stylesheet" href="/blog/assets/blog.css">
<style>
body{{padding:32px 0 80px}} .wrap{{max-width:820px}}
h1{{font-size:26px;margin:0 0 6px}} .sub{{color:var(--sub);font-size:14px;margin-bottom:20px}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}} .bar input{{flex:1;min-width:220px;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font:inherit}}
.bar button,.tabs button,.ad-act button{{border:1px solid var(--ink);background:#fff;border-radius:8px;padding:8px 14px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}}
.tabs{{display:flex;gap:6px;margin-bottom:14px}} .tabs button[aria-pressed=true]{{background:var(--ink);color:#fff}}
.ad-item{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:12px}}
.ad-meta{{font-size:13px;color:var(--faint)}} .ad-meta a{{color:var(--accent)}} .ad-txt{{margin:8px 0 12px;white-space:pre-wrap;word-break:break-word;font-size:15px}}
.ad-act{{display:flex;gap:6px;flex-wrap:wrap}} .ad-act .ok{{background:var(--ink);color:#fff}} .ad-act .no{{color:#A0522D;border-color:#A0522D}}
.ad-reply{{width:100%;margin-top:10px;border:1px solid var(--line);border-radius:8px;padding:8px 10px;font:inherit;font-size:14px;min-height:60px}}
.ad-status{{font-size:14px;color:var(--sub);margin:10px 0}}
</style></head><body><div class="wrap">
<div style="display:flex;gap:14px;font-size:14px;margin-bottom:14px"><b>댓글 관리</b><span>·</span><a href="/blog/admin/consult/" style="color:var(--accent);font-weight:700">상담 신청 관리</a></div><h1>댓글 관리</h1><p class="sub">승인한 댓글만 블로그에 보여요. 이 페이지 주소와 관리자 토큰은 다른 사람에게 알려 주지 마세요.</p>
<div class="bar"><input id="tok" type="password" placeholder="관리자 토큰"><button id="go">불러오기</button></div>
<div class="tabs"><button data-s="pending" aria-pressed="true">승인 대기</button><button data-s="approved" aria-pressed="false">공개 중</button><button data-s="rejected" aria-pressed="false">거절됨</button></div>
<p class="ad-status" id="st"></p><div id="list"></div>
</div>
<script>
(function(){{
var API={api!r}.replace(/[/]$/,''),S='pending',tok=document.getElementById('tok'),list=document.getElementById('list'),st=document.getElementById('st');
try{{tok.value=sessionStorage.getItem('hf_admin')||''}}catch(e){{}}
function esc(s){{return String(s==null?'':s).replace(/[&<>"']/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]}})}}
function call(path,opt){{opt=opt||{{}};opt.headers=Object.assign({{'Content-Type':'application/json','Authorization':'Bearer '+tok.value}},opt.headers||{{}});
 return fetch(API+path,opt).then(function(r){{if(r.status===401)throw new Error('토큰이 맞지 않아요.');return r.json()}})}}
function load(){{try{{sessionStorage.setItem('hf_admin',tok.value)}}catch(e){{}}
 st.textContent='불러오는 중…';
 call('/api/admin/comments?status='+S).then(function(d){{var cs=d.comments||[];st.textContent=cs.length+'개';
  list.innerHTML=cs.map(function(c){{var t=new Date(c.created_at*1000).toLocaleString('ko-KR');
   return '<div class="ad-item" data-id="'+c.id+'"><div class="ad-meta"><b>'+esc(c.nick)+'</b> · '+t+' · <a href="/blog/'+esc(c.post)+'/" target="_blank">'+esc(c.post)+'</a></div><div class="ad-txt">'+esc(c.body)+'</div>'+
   '<div class="ad-act">'+(S!=='approved'?'<button class="ok" data-a="approve">승인</button>':'')+(S!=='rejected'?'<button class="no" data-a="reject">거절</button>':'')+'<button data-a="delete">삭제</button></div>'+
   '<textarea class="ad-reply" placeholder="운영자 답글 (비우고 저장하면 답글 삭제)">'+esc(c.reply||'')+'</textarea><div class="ad-act" style="margin-top:6px"><button data-a="reply">답글 저장</button></div></div>'}}).join('')||'<p class="ad-status">비어 있어요.</p>'}}).catch(function(e){{st.textContent=e.message||'불러오지 못했어요.'}})}}
document.getElementById('go').onclick=load;
document.querySelectorAll('.tabs button').forEach(function(b){{b.onclick=function(){{S=b.dataset.s;document.querySelectorAll('.tabs button').forEach(function(x){{x.setAttribute('aria-pressed',x===b?'true':'false')}});load()}}}});
list.addEventListener('click',function(e){{var b=e.target.closest('button[data-a]');if(!b)return;var it=b.closest('.ad-item'),a=b.dataset.a;
 if(a==='delete'&&!confirm('이 댓글을 완전히 삭제할까요?'))return;
 var body={{action:a}};if(a==='reply')body.reply=it.querySelector('.ad-reply').value;
 call('/api/admin/comments/'+it.dataset.id,{{method:'POST',body:JSON.stringify(body)}}).then(function(){{if(a==='reply'){{st.textContent='답글을 저장했어요.'}}else load()}}).catch(function(e){{st.textContent=e.message}})}});
if(tok.value)load();
}})();
</script></body></html>
"""


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
    if BLOG_API:
        import consult_page as cp
        cdir = os.path.join(ROOT, "consult")
        os.makedirs(cdir, exist_ok=True)
        open(os.path.join(cdir, "index.html"), "w", encoding="utf-8").write(cp.consult_page(BLOG_API, SITE, date.today().year))
        os.makedirs(os.path.join(BLOG, "admin", "consult"), exist_ok=True)
        open(os.path.join(BLOG, "admin", "consult", "index.html"), "w", encoding="utf-8").write(cp.CONSULT_ADMIN.format(api=BLOG_API))
        os.makedirs(os.path.join(BLOG, "admin"), exist_ok=True)
        open(os.path.join(BLOG, "admin", "index.html"), "w", encoding="utf-8").write(ADMIN.format(api=BLOG_API))
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap(posts))
    print(f"블로그 글 {len(posts)}개를 만들었어요.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print("블로그 만들기 실패:", e, file=sys.stderr)
        sys.exit(1)
