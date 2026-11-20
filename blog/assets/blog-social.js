// 학종파이터 블로그 공감 · 댓글
(function () {
  var root = document.getElementById('social');
  if (!root) return;
  var API = root.dataset.api.replace(/\/$/, ''), POST = root.dataset.post;
  var likeBtn = root.querySelector('.like'), likeN = likeBtn.querySelector('b');
  var list = root.querySelector('.clist'), countEl = root.querySelector('.ccount');
  var form = root.querySelector('.cform'), msg = root.querySelector('.cmsg');
  var ta = form.querySelector('textarea'), len = form.querySelector('.len');

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function day(t) { var d = new Date(t * 1000); return (d.getMonth() + 1) + '월 ' + d.getDate() + '일'; }
  function track(n, p) { try { window.hfTrack && window.hfTrack(n, p); } catch (e) {} }
  function setLiked(on, n) { likeBtn.setAttribute('aria-pressed', on ? 'true' : 'false'); if (n != null) likeN.textContent = n; }

  function render(cs) {
    countEl.textContent = cs.length;
    if (!cs.length) { list.innerHTML = '<p class="cempty">아직 댓글이 없어요. 첫 댓글을 남겨 주세요.</p>'; return; }
    list.innerHTML = cs.map(function (c) {
      var re = c.reply ? '<div class="re"><div class="h"><img src="/images/character.jpg" alt=""><b>학종파이터</b><span class="tag">운영자</span><span>' + day(c.replied_at || c.created_at) + '</span></div><p>' + esc(c.reply) + '</p></div>' : '';
      return '<div class="cm"><div class="h"><span class="av">' + esc(c.nick.charAt(0)) + '</span><b>' + esc(c.nick) + '</b><span>' + day(c.created_at) + '</span></div><p>' + esc(c.body) + '</p>' + re + '</div>';
    }).join('');
  }

  fetch(API + '/api/post?post=' + encodeURIComponent(POST))
    .then(function (r) { return r.json(); })
    .then(function (d) { setLiked(d.liked, d.likes); render(d.comments || []); root.hidden = false; })
    .catch(function () { /* 서버가 안 되면 조용히 숨겨 둠 */ });

  likeBtn.addEventListener('click', function () {
    if (likeBtn.getAttribute('aria-pressed') === 'true') return;
    setLiked(true, Number(likeN.textContent || 0) + 1);
    fetch(API + '/api/like', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ post: POST }) })
      .then(function (r) { return r.json(); }).then(function (d) { if (d.likes != null) setLiked(true, d.likes); }).catch(function () {});
    track('blog_like', { post: POST });
  });

  ta.addEventListener('input', function () { len.textContent = ta.value.length + ' / 500자'; });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var btn = form.querySelector('button'), fd = new FormData(form);
    msg.className = 'cmsg'; msg.textContent = '';
    btn.disabled = true;
    fetch(API + '/api/comments', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ post: POST, nick: fd.get('nick'), body: fd.get('body'), website: fd.get('website') }) })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (x) {
        if (!x.ok) throw new Error(x.d.error || '');
        form.reset(); len.textContent = '0 / 500자';
        msg.textContent = '댓글이 접수됐어요. 확인 후 공개될 거예요.';
        track('blog_comment', { post: POST });
      })
      .catch(function (er) { msg.className = 'cmsg err'; msg.textContent = (er.message && /[가-힣]/.test(er.message)) ? er.message : '잠시 후 다시 시도해 주세요.'; })
      .then(function () { btn.disabled = false; });
  });
})();
