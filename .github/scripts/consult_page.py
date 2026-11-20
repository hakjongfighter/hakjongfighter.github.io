"""상담 신청 페이지(/consult/)와 상담 신청 관리 페이지(/blog/admin/consult/)를 만들어요.
build_blog.py 가 BLOG_API 가 있을 때 불러서 써요."""
import html, os

def esc(s):
    return html.escape(str(s), quote=True)

CONSULT_CSS = """
.cs-hero{padding:56px 0 28px;max-width:760px}
.cs-hero .k{font-size:13px;letter-spacing:2px;color:var(--faint);font-weight:700}
.cs-hero h1{font-size:42px;line-height:1.35;margin:12px 0 14px;letter-spacing:-1px}
.cs-hero h1 mark{background:linear-gradient(transparent 62%,var(--hl) 62%);color:inherit}
.cs-hero p{color:var(--sub);font-size:17px;line-height:1.8}
.cs-grid{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:48px;padding-bottom:80px;align-items:start}
.cs-cards{display:grid;gap:12px;margin-bottom:36px}
.cs-card{display:flex;gap:16px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.cs-card img{width:64px;height:64px;object-fit:contain;flex:none}
.cs-card b{display:block;font-size:16.5px;margin-bottom:2px}
.cs-card span{font-size:14.5px;color:var(--sub);line-height:1.6}
.cs-h{font-family:'Noto Serif KR','Noto Serif CJK KR',serif;font-size:22px;margin:0 0 14px}
.cs-steps{list-style:none;margin:0 0 36px;padding:0;display:grid;gap:10px}
.cs-steps li{display:flex;gap:14px;align-items:flex-start;font-size:15.5px;line-height:1.6}
.cs-steps i{font-style:normal;flex:none;width:30px;height:30px;border-radius:999px;background:var(--ink);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:14px}
.cs-steps small{display:block;color:var(--sub);font-size:13.5px}
.cs-faq details{border-top:1px solid var(--line);padding:14px 0}
.cs-faq details:last-child{border-bottom:1px solid var(--line)}
.cs-faq summary{cursor:pointer;font-weight:700;font-size:15.5px}
.cs-faq p{margin:8px 0 0;color:var(--sub);font-size:14.5px;line-height:1.75}
.cs-form{position:sticky;top:20px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:24px;box-shadow:0 8px 30px rgba(27,27,31,.05)}
.cs-form h2{font-family:'Noto Serif KR','Noto Serif CJK KR',serif;font-size:21px;margin:0 0 4px}
.cs-form .lead{font-size:13.5px;color:var(--sub);margin:0 0 18px}
.fld{margin-bottom:14px}
.fld>label,.fld>.lb{display:block;font-size:13.5px;font-weight:700;margin-bottom:6px}
.fld>label em,.fld>.lb em{font-style:normal;color:#C0392B;margin-left:2px}
.fld input[type=text],.fld input[type=tel],.fld select,.fld textarea{width:100%;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font:inherit;font-size:14.5px;background:var(--bg);color:var(--ink)}
.fld textarea{height:88px;resize:vertical}
.fld input:focus,.fld select:focus,.fld textarea:focus{outline:2px solid #7FD6CF;background:#fff}
.chips2{display:flex;flex-wrap:wrap;gap:6px}
.chips2 label{position:relative}
.chips2 input{position:absolute;opacity:0;inset:0;cursor:pointer}
.chips2 span{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:7px 13px;font-size:13.5px;background:#fff;cursor:pointer}
.chips2 input:checked+span{background:var(--ink);color:#fff;border-color:var(--ink)}
.chips2 input:focus-visible+span{outline:2px solid #7FD6CF}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.agree{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:6px 0 10px;font-size:13.5px}
.agree label{display:flex;gap:8px;align-items:flex-start;cursor:pointer;line-height:1.55}
.agree label+label{margin-top:8px}
.agree input{margin-top:3px;flex:none;width:16px;height:16px}
.agree details{margin:6px 0 0 24px;color:var(--sub);font-size:12.5px;line-height:1.7}
.agree summary{cursor:pointer;color:var(--accent);font-weight:700}
.agree table{border-collapse:collapse;width:100%;margin-top:6px}
.agree td{border-top:1px solid var(--line);padding:5px 0;vertical-align:top}
.agree td:first-child{width:70px;font-weight:700;color:var(--ink)}
.cs-form .hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}
.cs-submit{width:100%;border:0;border-radius:10px;background:var(--ink);color:#fff;font:inherit;font-weight:700;font-size:16px;padding:14px;cursor:pointer;margin-top:4px}
.cs-submit:disabled{opacity:.5;cursor:default}
.cs-msg{margin:10px 0 0;font-size:14px;font-weight:700;color:#A0522D;min-height:1px}
.cs-done{text-align:center;padding:24px 8px}
.cs-done img{width:120px;margin:0 auto 10px}
.cs-done h2{margin-bottom:8px}
.cs-done p{color:var(--sub);font-size:14.5px;line-height:1.75}
@media (max-width:900px){.cs-grid{grid-template-columns:1fr;gap:32px}.cs-form{position:static}.cs-hero h1{font-size:30px}.cs-hero{padding-top:36px}}
"""

def consult_page(head_html, foot_html, api, site):
    form = f"""
<div class="cs-form" id="csBox">
 <form id="csForm" novalidate autocomplete="on">
  <h2>전문 상담 신청</h2>
  <p class="lead">남겨 주시면 담당 선생님이 직접 연락드려요.</p>
  <div class="fld"><span class="lb">신청하시는 분<em>*</em></span><div class="chips2">
   <label><input type="radio" name="who" value="학생" required><span>학생</span></label>
   <label><input type="radio" name="who" value="학부모"><span>학부모</span></label></div></div>
  <div class="row2">
   <div class="fld"><label for="csName">이름 또는 호칭<em>*</em></label><input type="text" id="csName" name="name" maxlength="20" placeholder="예: 김OO / OO 어머니" required></div>
   <div class="fld"><label for="csGrade">학생 학년<em>*</em></label><select id="csGrade" name="grade" required><option value="">선택</option><option>중3</option><option>고1</option><option>고2</option><option>고3</option><option>N수</option><option>기타</option></select></div>
  </div>
  <div class="fld"><label for="csTrack">관심 계열</label><select id="csTrack" name="track"><option value="">선택 안 함</option><option>인문·사회</option><option>상경</option><option>자연·공학</option><option>의약</option><option>예체능</option><option>아직 모르겠어요</option></select></div>
  <div class="fld"><span class="lb">상담받고 싶은 내용</span><div class="chips2">
   <label><input type="checkbox" name="topics" value="세특 작성법"><span>세특 작성법</span></label>
   <label><input type="checkbox" name="topics" value="내신 공부법"><span>내신 공부법</span></label>
   <label><input type="checkbox" name="topics" value="수행평가"><span>수행평가</span></label>
   <label><input type="checkbox" name="topics" value="과목 선택"><span>과목 선택</span></label>
   <label><input type="checkbox" name="topics" value="대학·전형"><span>대학·전형</span></label>
   <label><input type="checkbox" name="topics" value="기타"><span>기타</span></label></div></div>
  <div class="fld"><label for="csQ">가장 궁금한 점</label><textarea id="csQ" name="question" maxlength="500" placeholder="지금 가장 고민되는 것을 한두 줄로 적어 주세요. (학교 이름, 성적표 사진 등은 적지 않아도 돼요)"></textarea></div>
  <div class="fld"><span class="lb">연락받을 방법<em>*</em></span><div class="chips2">
   <label><input type="radio" name="method" value="전화" required><span>전화</span></label>
   <label><input type="radio" name="method" value="문자"><span>문자</span></label>
   <label><input type="radio" name="method" value="카카오톡"><span>카카오톡</span></label></div></div>
  <div class="row2">
   <div class="fld"><label for="csContact" id="csContactLb">연락처<em>*</em></label><input type="tel" id="csContact" name="contact" maxlength="40" placeholder="010-0000-0000" required></div>
   <div class="fld"><label for="csTime">연락 편한 시간</label><select id="csTime" name="time"><option value="">상관없음</option><option>평일 낮</option><option>평일 저녁</option><option>주말</option></select></div>
  </div>
  <input class="hp" name="website" tabindex="-1" aria-hidden="true" autocomplete="off">
  <div class="agree">
   <label><input type="checkbox" name="agree_privacy" required><span><b>[필수]</b> 개인정보 수집·이용에 동의합니다.</span></label>
   <details><summary>내용 보기</summary><table>
    <tr><td>수집 항목</td><td>신청자 구분, 이름(호칭), 학생 학년, 관심 계열, 상담 희망 내용, 연락 방법·연락처, 연락 희망 시간</td></tr>
    <tr><td>이용 목적</td><td>상담 신청 확인 및 상담 연락</td></tr>
    <tr><td>보유 기간</td><td>신청일로부터 180일 후 자동 삭제 (요청 시 즉시 삭제)</td></tr>
    <tr><td>동의 거부</td><td>동의하지 않을 수 있으며, 이 경우 상담 신청이 어려워요.</td></tr>
    <tr><td>운영</td><td>강남에듀플랜 · 02-459-4945</td></tr></table></details>
   <label><input type="checkbox" name="agree_age" required><span><b>[필수]</b> 만 14세 이상이에요. <small style="color:var(--sub)">(만 14세 미만이면 보호자가 신청해 주세요)</small></span></label>
  </div>
  <button type="submit" class="cs-submit">전문 상담 신청하기</button>
  <p class="cs-msg" id="csMsg" role="alert"></p>
 </form>
</div>"""
    body = f"""<div class="wrap">
<section class="cs-hero">
 <div class="k">HAKJONG FIGHTER CONSULTING</div>
 <h1 class="serif">지금 학생부를 함께 보고,<br><mark>다음 1년의 방향</mark>을 잡아 드려요</h1>
 <p>세특 설계부터 내신 공부법까지. 학생마다 다른 학교, 과목, 기록을 놓고 학종 전문 선생님이 1:1로 상담해 드려요.</p>
</section>
<div class="cs-grid">
 <div>
  <h2 class="cs-h">이런 상담을 해 드려요</h2>
  <div class="cs-cards">
   <div class="cs-card"><img src="/images/characters/blueprint.png" alt=""><div><b>세특 작성법 상담</b><span>지금보다 1~2단계 높은 대학을 목표로, 과목별 세특이 한 방향으로 쌓이도록 설계해요.</span></div></div>
   <div class="cs-card"><img src="/images/characters/boxing.png" alt=""><div><b>내신 등급 올리는 공부법</b><span>지금 성적에서 바로 시작할 수 있는 방법으로, 과목별 공부 루틴을 잡아 드려요.</span></div></div>
   <div class="cs-card"><img src="/images/characters/idea.png" alt=""><div><b>수행평가 · 과목 선택</b><span>수행평가를 남들과 다르게 만드는 법, 2·3학년 과목을 고르는 기준까지 함께 봐요.</span></div></div>
  </div>
  <h2 class="cs-h">상담은 이렇게 진행돼요</h2>
  <ol class="cs-steps">
   <li><i>1</i><div>신청서 남기기<small>오른쪽 신청서에 학년과 궁금한 점을 남겨 주세요.</small></div></li>
   <li><i>2</i><div>담당 선생님 연락<small>남겨 주신 연락 방법과 시간에 맞춰 직접 연락드려요.</small></div></li>
   <li><i>3</i><div>1:1 전문 상담<small>지금 위치를 함께 점검하고, 학기별로 무엇을 할지 정리해 드려요.</small></div></li>
  </ol>
  <h2 class="cs-h">자주 묻는 질문</h2>
  <div class="cs-faq">
   <details><summary>부모님이 신청해도 되나요?</summary><p>네. 학생과 학부모 모두 신청할 수 있어요. 고민이 서로 다를 때가 많아서, 가능하면 상담에는 함께 참여하시길 권해요.</p></details>
   <details><summary>미리 준비할 게 있나요?</summary><p>없어도 괜찮아요. 최근 성적, 학교 교육과정 편성표, 가장 궁금한 것 한두 가지를 적은 메모가 있으면 이야기가 더 빨라져요.</p></details>
   <details><summary>언제 상담받는 게 좋아요?</summary><p>선택 폭이 가장 넓은 때는 2학년 과목을 신청하기 전이에요. 고3이라면 남은 학기에 맞춰 지금 할 일부터 다시 정리해요.</p></details>
   <details><summary>신청 정보는 어떻게 관리되나요?</summary><p>상담 연락에만 쓰고, 신청일로부터 180일이 지나면 자동으로 삭제돼요. 그 전에 지우고 싶으면 02-459-4945로 요청해 주세요.</p></details>
  </div>
 </div>
 {form}
</div>
</div>
<script>
(function(){{
 var API={api!r}.replace(/[/]$/,''), f=document.getElementById('csForm'), msg=document.getElementById('csMsg');
 var ct=document.getElementById('csContact'), lb=document.getElementById('csContactLb');
 f.addEventListener('change',function(e){{ if(e.target.name==='method'){{ var k=e.target.value==='카카오톡';
   ct.type=k?'text':'tel'; ct.placeholder=k?'카카오톡 아이디 또는 휴대폰 번호':'010-0000-0000'; lb.firstChild.nodeValue=k?'카카오톡 아이디':'연락처'; }} }});
 function v(n){{var el=f.querySelector('[name="'+n+'"]:checked');return el?el.value:''}}
 f.addEventListener('submit',function(e){{
  e.preventDefault(); msg.textContent='';
  var d={{who:v('who'),name:f.name.value,grade:f.grade.value,track:f.track.value,question:f.question.value,method:v('method'),contact:f.contact.value,time:f.time.value,website:f.website.value,
   topics:[].map.call(f.querySelectorAll('[name=topics]:checked'),function(x){{return x.value}}),agree_privacy:f.agree_privacy.checked,agree_age:f.agree_age.checked}};
  var need=!d.who?'신청하시는 분을 골라 주세요.':!d.name.trim()?'이름(또는 호칭)을 적어 주세요.':!d.grade?'학년을 골라 주세요.':!d.method?'연락받을 방법을 골라 주세요.':!d.contact.trim()?'연락처를 적어 주세요.':!d.agree_privacy?'개인정보 수집·이용에 동의해 주세요.':!d.agree_age?'만 14세 이상인지 확인해 주세요.':'';
  if(need){{msg.textContent=need;return}}
  var b=f.querySelector('.cs-submit'); b.disabled=true; b.textContent='보내는 중…';
  fetch(API+'/api/consult',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}})
   .then(function(r){{return r.json().then(function(j){{return {{ok:r.ok,j:j}}}})}})
   .then(function(x){{ if(!x.ok) throw new Error(x.j.error||'');
     try{{window.hfTrack&&hfTrack('consult_submit',{{who:d.who,grade:d.grade}})}}catch(_){{}}
     document.getElementById('csBox').innerHTML='<div class="cs-done"><img src="/images/characters/salute.png" alt=""><h2 class="serif">신청이 접수됐어요</h2><p>담당 선생님이 남겨 주신 연락처로 직접 연락드릴게요.<br>조금만 기다려 주세요.</p></div>';
     window.scrollTo({{top:document.getElementById('csBox').getBoundingClientRect().top+scrollY-20,behavior:'smooth'}}); }})
   .catch(function(er){{ msg.textContent=(er.message&&/[가-힣]/.test(er.message))?er.message:'잠시 후 다시 시도해 주세요. 급하시면 02-459-4945로 연락 주세요.'; b.disabled=false; b.textContent='전문 상담 신청하기'; }});
 }});
}})();
</script>
"""
    return head_html.replace("</head>", f"<style>{CONSULT_CSS}</style>\n</head>", 1) + body + foot_html


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
