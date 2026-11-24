"""상담 신청 페이지(/consult/)와 상담 신청 관리 페이지(/blog/admin/consult/)를 만들어요.
build_blog.py 가 BLOG_API 가 있을 때 불러서 써요.
상담 페이지는 블로그가 아니라 랜딩페이지(index.html)와 같은 디자인(남색·민트·노랑)을 써요."""
import html

def esc(s):
    return html.escape(str(s), quote=True)

IG = "https://www.instagram.com/hakjong_fighter/"
TEL = "02-459-4945"

# 상담 페이지 전체. {{API}} {{SITE}} {{YEAR}} 만 바꿔 넣어요 (중괄호 이스케이프 없이 쓰려고 replace 사용)
PAGE = r"""<!doctype html>
<html lang="ko">
<head>
<!-- 운영자 기기(방문 현황 페이지를 연 브라우저)는 GA4·GTM에 기록을 보내지 않음 -->
<script>try{if(localStorage.getItem('hf_internal')==='1'){window.hfInternal=true;window['ga-disable-G-4G2NGCPVXG']=true;}}catch(e){}</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){if(w.hfInternal)return;w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WP2WRX3L');</script>
<!-- Google Analytics (GA4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4G2NGCPVXG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-4G2NGCPVXG');
  window.hfTrack = function (name, params) { gtag('event', name, params || {}); };
</script>
<script defer src="/assets/hf-track.js"></script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>전문 상담 신청 | 학종파이터</title>
<meta name="description" content="과목 선택·수행평가부터 내신 공부 방법, 면접 대비까지. 학종 전문 선생님이 지금 학생부를 함께 보고 1:1로 상담해 드려요.">
<meta property="og:type" content="website">
<meta property="og:title" content="전문 상담 신청 | 학종파이터">
<meta property="og:description" content="과목 선택·수행평가부터 내신 공부 방법, 면접 대비까지. 학종 전문 선생님이 1:1로 상담해 드려요.">
<meta property="og:image" content="{{SITE}}/images/og.jpg">
<meta property="og:url" content="{{SITE}}/consult/">
<link rel="canonical" href="{{SITE}}/consult/">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F3FCFA">
<link rel="icon" type="image/png" href="/images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
:root{--navy:#1C2A5E;--navy2:#141F48;--yellow:#FFC72C;--mint:#B8F0E7;--mint2:#6CCFC8;--card:#F3FCFA;--muted:#33447F;--muted2:#22336A;--err:#C8372D}
*{box-sizing:border-box}
body{margin:0;background:var(--card);color:var(--navy);font-family:'Noto Sans KR',system-ui,-apple-system,sans-serif;line-height:1.5;word-break:keep-all}
img{display:block;max-width:100%}
a{color:var(--navy)}
h1,h2,h3{margin:0;font-weight:900;letter-spacing:-.8px}
p{margin:0}
.wrap{max-width:1120px;margin:0 auto;padding-left:20px;padding-right:20px}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--yellow);outline-offset:3px}
button,a,label,summary{-webkit-tap-highlight-color:transparent}

/* 헤더: 랜딩과 같은 모양 + 홈으로 */
.hdr{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);border-bottom:1px solid #E4ECF0;backdrop-filter:saturate(1.4) blur(6px)}
.hdr .wrap{display:flex;align-items:center;justify-content:space-between;gap:10px;padding-top:8px;padding-bottom:8px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;min-width:0}
.logo img{width:36px;height:36px;border-radius:999px;object-fit:cover;background:#fff;flex:none}
.logo span{display:flex;flex-direction:column;line-height:1.15;white-space:nowrap}
.logo b{font-size:18px;font-weight:900;letter-spacing:-.3px}
.logo small{font-size:11.5px;font-weight:500;color:var(--muted)}
.hdr-r{display:flex;align-items:center;gap:2px;flex:none}
.hdr-link{display:flex;align-items:center;gap:6px;min-height:44px;padding:0 12px;border-radius:999px;font-size:15px;font-weight:700;color:var(--navy);text-decoration:none}
.hdr-link:hover{background:#EEF5F7}

/* 첫 화면 */
.cs-hero{background:var(--mint);border-bottom:2px solid var(--navy)}
.cs-hero .wrap{display:flex;align-items:center;gap:28px;padding-top:44px;padding-bottom:40px}
.cs-hero .txt{flex:1;min-width:0;display:flex;flex-direction:column;gap:16px}
.pill{align-self:flex-start;display:inline-block;background:var(--navy);color:var(--yellow);font-weight:700;font-size:15px;padding:8px 16px;border-radius:999px}
.cs-hero h1{font-size:44px;line-height:1.3;text-wrap:balance}
.cs-hero .lead{font-size:18px;line-height:1.75;color:var(--muted2);max-width:560px}
.cs-hero .pic{flex:none;width:210px;height:auto}
.cs-hero{position:relative;overflow:hidden}
.form-hint{display:none;font-size:15px;font-weight:700;color:var(--muted2)}

/* 본문 배치: PC는 왼쪽 안내 + 오른쪽 신청서(따라옴), 휴대폰은 안내 → 신청서 → 자주 묻는 질문 */
.cs-grid{display:grid;grid-template-columns:minmax(0,1fr) 420px;grid-template-areas:"info form" "faq form";grid-template-rows:auto 1fr;column-gap:48px;row-gap:40px;padding-top:44px;padding-bottom:72px;align-items:start}
.cs-info{grid-area:info}
.cs-faq{grid-area:faq}
.cs-form{grid-area:form;position:sticky;top:76px}
.cs-h{font-size:24px;margin:0 0 16px}

.cs-cards{list-style:none;margin:0 0 40px;padding:0;display:grid;gap:14px}
.cs-card{display:flex;gap:16px;align-items:center;background:#fff;border:2px solid var(--navy);border-radius:18px;padding:16px 18px;box-shadow:4px 4px 0 var(--navy)}
.cs-card img{width:72px;height:72px;object-fit:contain;flex:none}
.cs-card b{display:block;font-size:18px;font-weight:900;margin-bottom:4px}
.cs-card span{display:block;font-size:15.5px;line-height:1.65;color:var(--muted2)}

.cs-steps{list-style:none;margin:0;padding:0;display:grid;gap:14px}
.cs-steps li{display:flex;gap:14px;align-items:flex-start;font-size:16.5px;font-weight:700;line-height:1.55}
.cs-steps i{font-style:normal;flex:none;width:32px;height:32px;border-radius:999px;background:var(--yellow);color:var(--navy);border:2px solid var(--navy);font-weight:900;display:flex;align-items:center;justify-content:center;font-size:15px}
.cs-steps small{display:block;color:var(--muted2);font-size:15px;font-weight:400;margin-top:2px}

.cs-faq details{border-top:2px solid var(--navy);padding:0}
.cs-faq details:last-of-type{border-bottom:2px solid var(--navy)}
.cs-faq summary{cursor:pointer;font-weight:700;font-size:16.5px;padding:16px 4px;list-style:none;display:flex;justify-content:space-between;gap:12px;min-height:56px;align-items:center}
.cs-faq summary::-webkit-details-marker{display:none}
.cs-faq summary::after{content:"+";font-size:22px;font-weight:500;line-height:1;flex:none}
.cs-faq details[open] summary::after{content:"−"}
.cs-faq p{margin:0 4px 16px;color:var(--muted2);font-size:15.5px;line-height:1.75}
.cs-faq a{font-weight:700}

/* 신청서 */
.cs-form{background:#fff;border:2px solid var(--navy);border-radius:20px;padding:24px 22px;box-shadow:6px 6px 0 var(--navy);scroll-margin-top:76px}
.cs-form h2{font-size:24px;margin:0 0 6px}
.cs-form .lead{font-size:15px;color:var(--muted2);margin:0 0 20px;line-height:1.6}
.fld{margin-bottom:18px;scroll-margin-top:96px}
.fld>label,.fld>.lb{display:block;font-size:15px;font-weight:700;margin-bottom:8px}
.fld>label em,.fld>.lb em{font-style:normal;color:var(--err);margin-left:2px}
.fld>label small,.fld>.lb small{font-weight:400;color:var(--muted);font-size:13.5px;margin-left:4px}
/* 16px 이상: 아이폰에서 칸을 눌러도 화면이 커지지 않아요 */
.fld input[type=text],.fld input[type=tel],.fld select,.fld textarea{width:100%;border:2px solid #C9D6E0;border-radius:12px;padding:12px 14px;font:inherit;font-size:16px;background:var(--card);color:var(--navy);min-height:50px}
.fld select{appearance:none;-webkit-appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%231C2A5E' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;padding-right:38px}
.fld textarea{height:104px;resize:vertical;line-height:1.6}
.fld input:focus,.fld select:focus,.fld textarea:focus{outline:none;border-color:var(--navy);background-color:#fff}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips label{position:relative}
.chips input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}
.chips span{display:inline-flex;align-items:center;min-height:44px;border:2px solid #C9D6E0;border-radius:999px;padding:0 16px;font-size:15.5px;font-weight:500;background:#fff;cursor:pointer}
.chips input:checked+span{background:var(--navy);color:#fff;border-color:var(--navy);font-weight:700}
.chips input:focus-visible+span{outline:3px solid var(--yellow);outline-offset:2px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.ferr{display:none;margin:8px 0 0;font-size:14.5px;font-weight:700;color:var(--err)}
.fld.bad .ferr{display:block}
.fld.bad input[type=text],.fld.bad input[type=tel],.fld.bad select{border-color:var(--err);background-color:#FFF6F5}
.fld.bad .chips span{border-color:var(--err)}

.agree{background:var(--card);border:2px solid #C9D6E0;border-radius:14px;padding:6px 14px;margin:4px 0 14px;font-size:15px}
.agree.bad{border-color:var(--err);background:#FFF6F5}
.agree .ck{display:flex;gap:10px;align-items:flex-start;cursor:pointer;line-height:1.55;padding:10px 0;min-height:44px}
.agree .ck+.ck,.agree details+.ck{border-top:1px solid #DCE6EC}
.agree input{margin:2px 0 0;flex:none;width:22px;height:22px;accent-color:var(--navy)}
.agree details{margin:-4px 0 8px 32px;color:var(--muted2);font-size:13.5px;line-height:1.7}
.agree summary{cursor:pointer;color:var(--navy);font-weight:700;text-decoration:underline;text-underline-offset:3px;padding:4px 0;display:inline-block}
.agree table{border-collapse:collapse;width:100%;margin-top:6px}
.agree td{border-top:1px solid #DCE6EC;padding:6px 0;vertical-align:top}
.agree td:first-child{width:72px;font-weight:700;color:var(--navy)}
.agree .ferr{margin:0 0 10px}
.agree.bad .ferr{display:block}
.cs-form .hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}
.cs-submit{width:100%;display:flex;align-items:center;justify-content:center;gap:10px;border:2px solid var(--navy);border-radius:16px;background:var(--yellow);color:var(--navy);font:inherit;font-weight:900;font-size:18px;min-height:60px;cursor:pointer;box-shadow:5px 5px 0 var(--navy);transition:transform .15s,box-shadow .15s}
.cs-submit:hover{transform:translate(2px,2px);box-shadow:3px 3px 0 var(--navy)}
.cs-submit:disabled{opacity:.6;cursor:default;transform:none}
.cs-msg{margin:14px 0 0;font-size:15px;font-weight:700;color:var(--err)}
.cs-msg:empty{display:none}
.cs-note{margin:14px 0 0;font-size:13.5px;color:var(--muted);text-align:center;line-height:1.6}
.cs-done{text-align:center;padding:16px 4px}
.cs-done img{width:120px;margin:0 auto 12px}
.cs-done h2{margin-bottom:10px}
.cs-done p{color:var(--muted2);font-size:15.5px;line-height:1.75}

/* 하단: 랜딩과 같은 사업자 정보 */
footer{background:var(--navy2);color:#fff}
footer .wrap{padding-top:32px;padding-bottom:36px}
footer .top{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:16px;padding-bottom:22px;border-bottom:1px solid #2C3A6E;margin-bottom:22px}
footer .top .logo b{color:var(--yellow)}
footer .top .logo small{color:#C9D1EC}
footer .top a.h{color:#fff;font-weight:700;text-decoration:none;font-size:15px}
footer address{font-style:normal;display:flex;flex-direction:column;gap:10px}
.biz-name{font-size:15px;font-weight:700}
footer dl{margin:0;display:flex;flex-wrap:wrap;gap:6px 28px;font-size:14px;line-height:1.6;color:#AEB8D9}
footer dl>div{display:flex;gap:8px}
footer dt{color:#7F8BB3;flex:none}
footer dd{margin:0}
footer dd a{color:#AEB8D9;text-decoration:none}
footer .links{margin-top:16px;font-size:14px}
footer .links a{color:#fff;font-weight:700}
footer .copy{margin-top:12px;font-size:13px;color:#7F8BB3}

@media (max-width:920px){
  .cs-grid{grid-template-columns:minmax(0,1fr);grid-template-areas:"info" "form" "faq";grid-template-rows:auto;padding-top:32px}
  .cs-form{position:static}
  .cs-hero .pic{width:150px}
  .cs-hero h1{font-size:34px}
}
@media (max-width:600px){
  .wrap{padding-left:18px;padding-right:18px}
  .cs-hero .wrap{display:block;padding-top:24px;padding-bottom:26px}
  .cs-hero .pic{position:absolute;right:10px;top:12px;width:78px}
  .cs-hero .pill{margin-bottom:2px}
  .cs-hero h1{font-size:29px;line-height:1.35}
  .cs-hero .lead{font-size:16.5px}
  .form-hint{display:block}
  .hdr-link .t{display:none}
  .cs-card{padding:14px;gap:12px}
  .cs-card img{width:60px;height:60px}
  .cs-form{padding:22px 16px;box-shadow:4px 4px 0 var(--navy)}
}
@media (max-width:400px){ .row2{grid-template-columns:1fr;gap:0} }
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
</style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WP2WRX3L" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<header class="hdr">
 <nav class="wrap" aria-label="사이트">
  <a class="logo" href="/"><img src="/images/logo.webp" alt="학종파이터 로고" width="36" height="36"><span><b>학종파이터</b><small>1:1 전문 상담</small></span></a>
  <div class="hdr-r">
   <a class="hdr-link" href="/" aria-label="학종파이터 홈"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/></svg><span class="t">홈</span></a>
   <a class="hdr-link" href="/blog/" aria-label="블로그"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg><span class="t">blog</span></a>
   <a class="hdr-link" href="https://www.instagram.com/hakjong_fighter/" target="_blank" rel="noopener" aria-label="인스타그램 @hakjong_fighter"><svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.8" fill="currentColor"/></svg><span class="t">instagram</span></a>
  </div>
 </nav>
</header>

<main>
<section class="cs-hero">
 <div class="wrap">
  <div class="txt">
   <span class="pill">1:1 전문 상담</span>
   <h1>지금 학생부를 함께 보고, 다음 1년의 방향을 잡아 드려요</h1>
   <p class="lead">학교도, 과목도, 지금까지의 기록도 학생마다 달라요. 학종 전문 선생님이 지금 위치에서 할 수 있는 것부터 1:1로 정리해 드려요.</p>
   <p class="form-hint">신청서는 상담 안내 바로 아래에 있어요.</p>
  </div>
  <img class="pic" src="/images/characters/salute.webp" alt="경례하는 연필 캐릭터 학종파이터" width="360" height="360" fetchpriority="high">
 </div>
</section>

<div class="wrap cs-grid">
 <div class="cs-info">
  <h2 class="cs-h">이런 상담을 해 드려요</h2>
  <ol class="cs-cards">
   <li class="cs-card"><img src="/images/characters/blueprint.webp" alt="설계도를 펼쳐 든 연필 캐릭터" width="360" height="360" loading="lazy"><div><b>과목 선택 · 수행평가</b><span>희망 계열에 맞는 과목을 고르고, 수행평가 하나하나가 세특으로 이어지도록 설계해요. 목표는 지금보다 1~2단계 높은 대학이에요.</span></div></li>
   <li class="cs-card"><img src="/images/characters/boxing.webp" alt="복싱 글러브를 끼고 힘을 내는 연필 캐릭터" width="360" height="360" loading="lazy"><div><b>내신 공부 방법</b><span>지금 성적에서 바로 시작할 수 있게, 과목별 공부 순서와 시험 전 루틴을 함께 잡아요.</span></div></li>
   <li class="cs-card"><img src="/images/characters/present-book.webp" alt="책을 펼쳐 들고 설명하는 연필 캐릭터" width="360" height="360" loading="lazy"><div><b>면접 대비</b><span>내 생기부에서 나올 질문을 미리 뽑고, 활동의 이유와 배운 점을 내 말로 답하는 연습을 해요.</span></div></li>
  </ol>
  <h2 class="cs-h">상담은 이렇게 진행돼요</h2>
  <ol class="cs-steps">
   <li><i>1</i><div>신청서 남기기<small>학년과 궁금한 점만 적어도 충분해요. 1분이면 끝나요.</small></div></li>
   <li><i>2</i><div>담당 선생님 연락<small>남겨 주신 연락 방법과 편한 시간에 맞춰 직접 연락드려요.</small></div></li>
   <li><i>3</i><div>1:1 전문 상담<small>지금 위치를 함께 점검하고, 학기별로 무엇을 할지 정리해 드려요.</small></div></li>
  </ol>
 </div>

 <div class="cs-form" id="csBox">
  <form id="csForm" novalidate autocomplete="on">
   <h2>전문 상담 신청</h2>
   <p class="lead">남겨 주시면 담당 선생님이 직접 연락드려요. 별표(<b style="color:var(--err)">*</b>) 칸만 채우면 돼요.</p>

   <div class="fld" data-f="who"><span class="lb" id="lbWho">신청하시는 분<em>*</em></span>
    <div class="chips" role="radiogroup" aria-labelledby="lbWho">
     <label><input type="radio" name="who" value="학생"><span>학생</span></label>
     <label><input type="radio" name="who" value="학부모"><span>학부모</span></label></div>
    <p class="ferr">신청하시는 분을 골라 주세요.</p></div>

   <div class="row2">
    <div class="fld" data-f="name"><label for="csName">이름 또는 호칭<em>*</em></label>
     <input type="text" id="csName" name="name" maxlength="20" placeholder="예: 김OO, OO 어머니" autocomplete="name">
     <p class="ferr">이름이나 호칭을 적어 주세요.</p></div>
    <div class="fld" data-f="grade"><label for="csGrade">학생 학년<em>*</em></label>
     <select id="csGrade" name="grade"><option value="">선택</option><option>중3</option><option>고1</option><option>고2</option><option>고3</option><option>N수</option><option>기타</option></select>
     <p class="ferr">학년을 골라 주세요.</p></div>
   </div>

   <div class="fld" data-f="track"><label for="csTrack">관심 계열<small>(선택)</small></label>
    <select id="csTrack" name="track"><option value="">선택 안 함</option><option>인문·사회</option><option>상경</option><option>자연·공학</option><option>의약</option><option>예체능</option><option>아직 모르겠어요</option></select></div>

   <div class="fld" data-f="topics"><span class="lb" id="lbTopics">상담받고 싶은 내용<small>(여러 개 골라도 돼요)</small></span>
    <div class="chips" role="group" aria-labelledby="lbTopics">
     <label><input type="checkbox" name="topics" value="과목 선택"><span>과목 선택</span></label>
     <label><input type="checkbox" name="topics" value="수행평가·세특"><span>수행평가·세특</span></label>
     <label><input type="checkbox" name="topics" value="내신 공부법"><span>내신 공부 방법</span></label>
     <label><input type="checkbox" name="topics" value="면접 대비"><span>면접 대비</span></label>
     <label><input type="checkbox" name="topics" value="대학·전형"><span>대학·전형</span></label>
     <label><input type="checkbox" name="topics" value="기타"><span>기타</span></label></div></div>

   <div class="fld" data-f="question"><label for="csQ">가장 궁금한 점<small>(선택)</small></label>
    <textarea id="csQ" name="question" maxlength="500" placeholder="지금 가장 고민되는 것을 한두 줄로 적어 주세요. 학교 이름이나 성적표는 적지 않아도 돼요."></textarea></div>

   <div class="fld" data-f="method"><span class="lb" id="lbMethod">연락받을 방법<em>*</em></span>
    <div class="chips" role="radiogroup" aria-labelledby="lbMethod">
     <label><input type="radio" name="method" value="전화"><span>전화</span></label>
     <label><input type="radio" name="method" value="문자"><span>문자</span></label>
     <label><input type="radio" name="method" value="카카오톡"><span>카카오톡</span></label></div>
    <p class="ferr">연락받을 방법을 골라 주세요.</p></div>

   <div class="row2">
    <div class="fld" data-f="contact"><label for="csContact"><span id="csContactLb">연락처</span><em>*</em></label>
     <input type="tel" id="csContact" name="contact" maxlength="40" placeholder="010-0000-0000" autocomplete="tel" inputmode="tel">
     <p class="ferr" id="csContactErr">연락처를 적어 주세요.</p></div>
    <div class="fld" data-f="time"><label for="csTime">연락 편한 시간</label>
     <select id="csTime" name="time"><option value="">상관없음</option><option>평일 낮</option><option>평일 저녁</option><option>주말</option></select></div>
   </div>

   <input class="hp" name="website" tabindex="-1" aria-hidden="true" autocomplete="off">

   <div class="agree fld" data-f="agree">
    <label class="ck"><input type="checkbox" name="agree_privacy"><span><b>[필수]</b> 개인정보 수집·이용에 동의해요.</span></label>
    <details><summary>무엇을 왜 받는지 보기</summary><table>
     <tr><td>받는 정보</td><td>신청자 구분, 이름(호칭), 학생 학년, 관심 계열, 상담 희망 내용, 궁금한 점, 연락 방법·연락처, 연락 희망 시간</td></tr>
     <tr><td>쓰는 곳</td><td>상담 신청 확인과 상담 연락에만 써요.</td></tr>
     <tr><td>보관 기간</td><td>신청일로부터 180일 뒤 자동 삭제 (요청하면 바로 삭제)</td></tr>
     <tr><td>보관 장소</td><td>암호화된 연결(HTTPS)로 보내고, Cloudflare, Inc.(미국)의 서버에 보관해요.</td></tr>
     <tr><td>동의 거부</td><td>동의하지 않아도 되지만, 이 경우 신청서로는 상담 신청이 어려워요. 전화 {{TEL}}로 문의해 주세요.</td></tr>
    </table><p style="margin:8px 0 0">자세한 내용은 <a href="/privacy/" target="_blank" rel="noopener">개인정보처리방침</a>에 있어요.</p></details>
    <label class="ck"><input type="checkbox" name="agree_age"><span><b>[필수]</b> 신청하는 사람이 만 14세 이상이에요.<br><small style="color:var(--muted)">만 14세 미만이면 보호자가 신청해 주세요.</small></span></label>
    <p class="ferr" id="csAgreeErr">필수 항목 두 개에 모두 체크해 주세요.</p>
   </div>

   <button type="submit" class="cs-submit">전문 상담 신청하기</button>
   <p class="cs-msg" id="csMsg" role="alert"></p>
   <p class="cs-note">신청해도 바로 결제되거나 등록되지 않아요.<br>전화가 편하시면 <a href="tel:024594945">{{TEL}}</a></p>
  </form>
 </div>

 <div class="cs-faq">
  <h2 class="cs-h">자주 묻는 질문</h2>
  <details><summary>부모님이 신청해도 되나요?</summary><p>네. 학생과 학부모 모두 신청할 수 있어요. 고민이 서로 다를 때가 많아서, 가능하면 상담에는 함께 참여하시길 권해요.</p></details>
  <details><summary>미리 준비할 게 있나요?</summary><p>없어도 괜찮아요. 최근 성적, 학교 교육과정 편성표, 가장 궁금한 것 한두 가지를 적은 메모가 있으면 이야기가 더 빨라져요. 면접 대비라면 생기부 출력본이 있으면 좋아요.</p></details>
  <details><summary>언제 상담받는 게 좋아요?</summary><p>과목 선택은 2학년 과목을 신청하기 전, 면접 대비는 원서 접수 전후가 좋아요. 고3이라면 남은 학기에 맞춰 지금 할 일부터 다시 정리해요.</p></details>
  <details><summary>신청 정보는 어떻게 관리되나요?</summary><p>상담 연락에만 쓰고, 신청일로부터 180일이 지나면 자동으로 삭제돼요. 그 전에 지우고 싶으면 {{TEL}}로 요청해 주세요. 자세한 내용은 <a href="/privacy/">개인정보처리방침</a>에 있어요.</p></details>
 </div>
</div>
</main>

<footer>
 <div class="wrap">
  <div class="top">
   <a class="logo" href="/" style="color:#fff"><img src="/images/logo.webp" alt="학종파이터 로고" width="36" height="36" loading="lazy"><span><b>학종파이터</b><small>고등학생을 위한 학생부종합전형 로드맵</small></span></a>
   <a class="h" href="https://www.instagram.com/hakjong_fighter/" target="_blank" rel="noopener">@hakjong_fighter</a>
  </div>
  <address>
   <strong class="biz-name">강남에듀플랜</strong>
   <dl>
    <div><dt>전화</dt><dd><a href="tel:024594945">{{TEL}}</a></dd></div>
    <div><dt>사업자등록번호</dt><dd>862-22-01618</dd></div>
    <div><dt>주소</dt><dd>서울 강남구 밤고개로1길 10 수서현대벤쳐빌 1324호</dd></div>
   </dl>
  </address>
  <p class="links"><a href="/privacy/">개인정보처리방침</a></p>
  <p class="copy">© {{YEAR}} 강남에듀플랜 · 학종파이터</p>
 </div>
</footer>

<script>
(function(){
 var API='{{API}}'.replace(/[/]$/,''), f=document.getElementById('csForm'), msg=document.getElementById('csMsg');
 var ct=document.getElementById('csContact'), lb=document.getElementById('csContactLb'), cerr=document.getElementById('csContactErr');
 function track(n,p){ try{ window.hfTrack&&hfTrack(n,p||{}) }catch(_){} }
 var started=false;
 f.addEventListener('focusin',function(){ if(!started){ started=true; track('consult_form_start'); } });
 function v(n){ var el=f.querySelector('[name="'+n+'"]:checked'); return el?el.value:'' }
 function fld(k){ return f.querySelector('.fld[data-f="'+k+'"]') }
 function setBad(k,on,text){ var el=fld(k); if(!el) return; el.classList.toggle('bad',!!on);
   var e=el.querySelector('.ferr'); if(e&&text) e.textContent=text;
   el.querySelectorAll('input,select').forEach(function(i){ if(i.type!=='hidden') i.setAttribute('aria-invalid',on?'true':'false') }); }
 function isKakao(){ return v('method')==='카카오톡' }
 function phoneOk(s){ return /^[0-9+\-\s()]{9,20}$/.test(s) && s.replace(/\D/g,'').length>=9 }
 function check(){
   var bad=[];
   if(!v('who')) bad.push(['who']);
   if(!f.name.value.trim()) bad.push(['name']);
   if(!f.grade.value) bad.push(['grade']);
   if(!v('method')) bad.push(['method']);
   var c=f.contact.value.trim();
   if(!c) bad.push(['contact', isKakao()?'카카오톡 아이디나 휴대폰 번호를 적어 주세요.':'연락처를 적어 주세요.']);
   else if(!isKakao() && !phoneOk(c)) bad.push(['contact','전화번호를 010-0000-0000처럼 적어 주세요.']);
   else if(isKakao() && c.length<3) bad.push(['contact','카카오톡 아이디를 다시 확인해 주세요.']);
   if(!f.agree_privacy.checked||!f.agree_age.checked) bad.push(['agree', !f.agree_privacy.checked&&!f.agree_age.checked?'필수 항목 두 개에 모두 체크해 주세요.':!f.agree_privacy.checked?'개인정보 수집·이용 동의에 체크해 주세요.':'만 14세 이상인지 확인하고 체크해 주세요.']);
   return bad;
 }
 var tried=false;
 function refresh(){ if(!tried) return; var bad=check(), keys=bad.map(function(b){return b[0]});
   ['who','name','grade','method','contact','agree'].forEach(function(k){ var b=bad.filter(function(x){return x[0]===k})[0]; setBad(k,keys.indexOf(k)>-1,b&&b[1]); }); }
 f.addEventListener('change',function(e){
   if(e.target.name==='method'){ var k=e.target.value==='카카오톡';
     ct.type=k?'text':'tel'; ct.inputMode=k?'text':'tel'; ct.placeholder=k?'카카오톡 아이디 또는 휴대폰 번호':'010-0000-0000'; lb.textContent=k?'카카오톡 아이디':'연락처'; }
   refresh(); });
 f.addEventListener('input',refresh);
 f.addEventListener('submit',function(e){
  e.preventDefault(); msg.textContent=''; tried=true; refresh();
  var bad=check();
  if(bad.length){
    var first=fld(bad[0][0]);
    track('consult_form_error',{field:bad[0][0],count:bad.length});
    if(first){ first.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});
      var inp=first.querySelector('input:not([type=hidden]),select'); if(inp) setTimeout(function(){ try{inp.focus({preventScroll:true})}catch(_){inp.focus()} },350); }
    msg.textContent='빠진 곳이 '+bad.length+'군데 있어요. 빨갛게 표시된 칸을 확인해 주세요.';
    return;
  }
  var d={who:v('who'),name:f.name.value,grade:f.grade.value,track:f.track.value,question:f.question.value,method:v('method'),contact:f.contact.value,time:f.time.value,website:f.website.value,
   topics:[].map.call(f.querySelectorAll('[name=topics]:checked'),function(x){return x.value}),agree_privacy:f.agree_privacy.checked,agree_age:f.agree_age.checked};
  var b=f.querySelector('.cs-submit'); b.disabled=true; b.textContent='보내는 중…';
  fetch(API+'/api/consult',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})
   .then(function(r){ return r.json().catch(function(){return {}}).then(function(j){ return {ok:r.ok,status:r.status,j:j} }) })
   .then(function(x){ if(!x.ok){ var er=new Error(x.j.error||''); er.status=x.status; throw er; }
     track('consult_submit',{who:d.who,grade:d.grade,dup:x.j.duplicate?1:0});
     var box=document.getElementById('csBox');
     box.innerHTML='<div class="cs-done" tabindex="-1"><img src="/images/characters/cheer.webp" alt="신청 접수를 축하하는 연필 캐릭터" width="360" height="360"><h2>'+(x.j.duplicate?'이미 신청이 접수돼 있어요':'신청이 접수됐어요')+'</h2><p>담당 선생님이 남겨 주신 연락처로 직접 연락드릴게요.<br>조금만 기다려 주세요.</p><p style="margin-top:14px;font-size:14px">급하시면 <a href="tel:024594945">{{TEL}}</a></p></div>';
     box.scrollIntoView({behavior:'smooth',block:'start'}); try{box.firstChild.focus({preventScroll:true})}catch(_){} })
   .catch(function(er){
     track('consult_submit_fail',{status:er.status||0});
     msg.textContent=(er.message&&/[가-힣]/.test(er.message))?er.message:'신청을 보내지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요. 급하시면 {{TEL}}로 연락 주세요.';
     b.disabled=false; b.textContent='전문 상담 신청하기'; });
 });
})();
</script>
</body>
</html>
"""

def consult_page(api, site, year):
    return (PAGE.replace("{{API}}", api.replace("'", ""))
                .replace("{{SITE}}", site)
                .replace("{{YEAR}}", str(year))
                .replace("{{TEL}}", TEL))


CONSULT_ADMIN = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>상담 신청 관리 | 학종파이터</title>
<link rel="stylesheet" href="/blog/assets/blog.css">
<style>
body{{padding:32px 0 80px}} .wrap{{max-width:900px}}
.top{{display:flex;gap:14px;font-size:14px;margin-bottom:14px}} .top a{{color:var(--accent);font-weight:700}}
h1{{font-size:26px;margin:0 0 6px}} .sub{{color:var(--sub);font-size:14px;margin-bottom:20px}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}} .bar input{{flex:1;min-width:220px;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font:inherit}}
.bar button,.tabs button,.ad-act button{{border:1px solid var(--ink);background:#fff;border-radius:8px;padding:8px 14px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}}
.tabs{{display:flex;gap:6px;margin-bottom:14px}} .tabs button[aria-pressed=true]{{background:var(--ink);color:#fff}}
.ad-item{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:12px}}
.ad-meta{{font-size:13px;color:var(--faint)}} .ad-name{{font-size:17px;font-weight:700;margin:4px 0}}
.ad-grid{{display:grid;grid-template-columns:110px 1fr;gap:4px 10px;font-size:14.5px;margin:8px 0 12px}} .ad-grid b{{color:var(--sub);font-weight:500}}
.ad-q{{white-space:pre-wrap;word-break:break-word}}
.ad-act{{display:flex;gap:6px;flex-wrap:wrap}} .ad-act .ok{{background:var(--ink);color:#fff}} .ad-act .no{{color:#A0522D;border-color:#A0522D}}
.ad-memo{{width:100%;margin-top:10px;border:1px solid var(--line);border-radius:8px;padding:8px 10px;font:inherit;font-size:14px;min-height:54px}}
.ad-status{{font-size:14px;color:var(--sub);margin:10px 0}}
</style></head><body><div class="wrap">
<div class="top"><a href="/blog/admin/">댓글 관리</a><span>·</span><b>상담 신청 관리</b></div>
<h1>상담 신청 관리</h1><p class="sub">신청 정보는 180일이 지나면 자동으로 삭제돼요. 상담이 끝난 신청은 바로 삭제해도 돼요. 이 페이지와 토큰은 다른 사람에게 알려 주지 마세요.</p>
<div class="bar"><input id="tok" type="password" placeholder="관리자 토큰"><button id="go">불러오기</button></div>
<div class="tabs"><button data-s="new" aria-pressed="true">새 신청</button><button data-s="contacted" aria-pressed="false">연락함</button><button data-s="done" aria-pressed="false">완료</button></div>
<p class="ad-status" id="st"></p><div id="list"></div>
</div>
<script>
(function(){{
var API={api!r}.replace(/[/]$/,''),S='new',tok=document.getElementById('tok'),list=document.getElementById('list'),st=document.getElementById('st');
try{{tok.value=sessionStorage.getItem('hf_admin')||''}}catch(e){{}}
function esc(s){{return String(s==null?'':s).replace(/[&<>"']/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]}})}}
function call(path,opt){{opt=opt||{{}};opt.headers=Object.assign({{'Content-Type':'application/json','Authorization':'Bearer '+tok.value}},opt.headers||{{}});
 return fetch(API+path,opt).then(function(r){{if(r.status===401)throw new Error('토큰이 맞지 않아요.');return r.json()}})}}
function row(k,v){{return v?'<b>'+k+'</b><span class="ad-q">'+esc(v)+'</span>':''}}
function load(){{try{{sessionStorage.setItem('hf_admin',tok.value)}}catch(e){{}}
 st.textContent='불러오는 중…';
 call('/api/admin/consults?status='+S).then(function(d){{var cs=d.consults||[];st.textContent=cs.length+'건';
  list.innerHTML=cs.map(function(c){{var t=new Date(c.created_at*1000).toLocaleString('ko-KR');
   return '<div class="ad-item" data-id="'+c.id+'"><div class="ad-meta">'+t+' 신청 · '+esc(c.who)+'</div><div class="ad-name">'+esc(c.name)+' · '+esc(c.grade)+'</div><div class="ad-grid">'+
    row('연락',c.method+' · '+c.contact)+row('편한 시간',c.time_pref)+row('관심 계열',c.track)+row('상담 내용',c.topics)+row('궁금한 점',c.question)+'</div>'+
    '<div class="ad-act">'+(S!=='contacted'?'<button class="ok" data-a="contacted">연락함으로</button>':'')+(S!=='done'?'<button data-a="done">완료로</button>':'')+(S!=='new'?'<button data-a="new">새 신청으로</button>':'')+'<button class="no" data-a="delete">삭제</button></div>'+
    '<textarea class="ad-memo" placeholder="메모 (예: 11/21 통화, 다음 주 상담 예약)">'+esc(c.memo||'')+'</textarea><div class="ad-act" style="margin-top:6px"><button data-a="memo">메모 저장</button></div></div>'}}).join('')||'<p class="ad-status">비어 있어요.</p>'}}).catch(function(e){{st.textContent=e.message||'불러오지 못했어요.'}})}}
document.getElementById('go').onclick=load;
document.querySelectorAll('.tabs button').forEach(function(b){{b.onclick=function(){{S=b.dataset.s;document.querySelectorAll('.tabs button').forEach(function(x){{x.setAttribute('aria-pressed',x===b?'true':'false')}});load()}}}});
list.addEventListener('click',function(e){{var b=e.target.closest('button[data-a]');if(!b)return;var it=b.closest('.ad-item'),a=b.dataset.a;
 if(a==='delete'&&!confirm('이 신청을 완전히 삭제할까요? 되돌릴 수 없어요.'))return;
 var body={{action:a}};if(a==='memo')body.memo=it.querySelector('.ad-memo').value;
 call('/api/admin/consults/'+it.dataset.id,{{method:'POST',body:JSON.stringify(body)}}).then(function(){{if(a==='memo'){{st.textContent='메모를 저장했어요.'}}else load()}}).catch(function(e){{st.textContent=e.message}})}});
if(tok.value)load();
}})();
</script></body></html>
"""
