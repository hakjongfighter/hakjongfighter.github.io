// 학종파이터 블로그 공감·댓글 서버 (Cloudflare Worker + D1)
//
// 공개 API
//   GET  /api/post?post=<slug>          공감 수, 내가 눌렀는지, 공개된 댓글 목록
//   POST /api/like      {post}          공감 (같은 방문자는 글마다 1번)
//   POST /api/comments  {post,nick,body,website}  댓글 등록 → 승인 대기
// 관리자 API (헤더 Authorization: Bearer <ADMIN_TOKEN>)
//   GET  /api/admin/comments?status=pending|approved|rejected
//   POST /api/admin/comments/<id>  {action: approve|reject|delete|reply, reply}
//
// 환경 변수: ADMIN_TOKEN(비밀), SALT(비밀), ALLOWED_ORIGINS(쉼표 구분)

const MAX_NICK = 20;
const MAX_BODY = 500;
const COMMENTS_PER_HOUR = 5;
const SLUG_RE = /^[a-z0-9-]{1,80}$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    try {
      const res = await route(request, env, url);
      for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
      return res;
    } catch (e) {
      const res = json({ error: e.status ? e.message : "server_error" }, e.status || 500);
      for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
      if (!e.status) console.error(e);
      return res;
    }
  },
};

async function route(request, env, url) {
  const p = url.pathname;
  const m = request.method;

  if (m === "GET" && p === "/api/post") {
    const post = slug(url.searchParams.get("post"));
    const voter = await voterId(request, env, post);
    const [{ n }] = (await env.DB.prepare("SELECT COUNT(*) AS n FROM likes WHERE post=?").bind(post).all()).results;
    const mine = await env.DB.prepare("SELECT 1 FROM likes WHERE post=? AND voter=?").bind(post, voter).first();
    const { results } = await env.DB.prepare(
      "SELECT id, nick, body, reply, created_at, replied_at FROM comments WHERE post=? AND status='approved' ORDER BY id ASC"
    ).bind(post).all();
    return json({ likes: n, liked: !!mine, comments: results });
  }

  if (m === "POST" && p === "/api/like") {
    const { post: raw } = await body(request);
    const post = slug(raw);
    const voter = await voterId(request, env, post);
    await env.DB.prepare("INSERT OR IGNORE INTO likes (post, voter, created_at) VALUES (?, ?, ?)")
      .bind(post, voter, now()).run();
    const { n } = await env.DB.prepare("SELECT COUNT(*) AS n FROM likes WHERE post=?").bind(post).first();
    return json({ likes: n, liked: true });
  }

  if (m === "POST" && p === "/api/comments") {
    const data = await body(request);
    if (data.website) return json({ ok: true, pending: true }); // 스팸봇용 숨은 칸
    const post = slug(data.post);
    const nick = clean(data.nick, MAX_NICK);
    const text = clean(data.body, MAX_BODY, true);
    if (!nick) throw err(400, "닉네임을 적어 주세요.");
    if (text.length < 2) throw err(400, "댓글 내용을 적어 주세요.");
    const who = await ipHash(request, env);
    const { n } = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM comments WHERE ip_hash=? AND created_at > ?"
    ).bind(who, now() - 3600).first();
    if (n >= COMMENTS_PER_HOUR) throw err(429, "잠시 후 다시 남겨 주세요.");
    await env.DB.prepare(
      "INSERT INTO comments (post, nick, body, status, ip_hash, created_at) VALUES (?, ?, ?, 'pending', ?, ?)"
    ).bind(post, nick, text, who, now()).run();
    return json({ ok: true, pending: true });
  }

  if (p.startsWith("/api/admin/")) {
    requireAdmin(request, env);
    if (m === "GET" && p === "/api/admin/comments") {
      const status = url.searchParams.get("status") || "pending";
      if (!["pending", "approved", "rejected"].includes(status)) throw err(400, "bad_status");
      const { results } = await env.DB.prepare(
        "SELECT id, post, nick, body, reply, status, created_at FROM comments WHERE status=? ORDER BY id DESC LIMIT 200"
      ).bind(status).all();
      return json({ comments: results });
    }
    const mm = p.match(/^\/api\/admin\/comments\/(\d+)$/);
    if (m === "POST" && mm) {
      const id = Number(mm[1]);
      const { action, reply } = await body(request);
      if (action === "approve" || action === "reject") {
        await env.DB.prepare("UPDATE comments SET status=? WHERE id=?").bind(action === "approve" ? "approved" : "rejected", id).run();
      } else if (action === "delete") {
        await env.DB.prepare("DELETE FROM comments WHERE id=?").bind(id).run();
      } else if (action === "reply") {
        const r = clean(reply, MAX_BODY, true);
        await env.DB.prepare("UPDATE comments SET reply=?, replied_at=? WHERE id=?").bind(r || null, r ? now() : null, id).run();
      } else throw err(400, "bad_action");
      return json({ ok: true });
    }
  }

  return json({ error: "not_found" }, 404);
}

// ---------- 도우미 ----------
function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });
}
function err(status, message) { const e = new Error(message); e.status = status; return e; }
function now() { return Math.floor(Date.now() / 1000); }
function slug(v) { if (typeof v !== "string" || !SLUG_RE.test(v)) throw err(400, "bad_post"); return v; }
function clean(v, max, multiline = false) {
  if (typeof v !== "string") return "";
  let s = v.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
  s = multiline ? s.replace(/\r\n?/g, "\n").replace(/\n{3,}/g, "\n\n") : s.replace(/\s+/g, " ");
  return s.trim().slice(0, max);
}
async function body(request) {
  const len = Number(request.headers.get("Content-Length") || 0);
  if (len > 4096) throw err(413, "too_large");
  try { return await request.json(); } catch { throw err(400, "bad_json"); }
}
function corsHeaders(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
  const h = { "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type, Authorization", "Vary": "Origin" };
  if (allowed.includes(origin)) h["Access-Control-Allow-Origin"] = origin;
  return h;
}
function requireAdmin(request, env) {
  const got = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/, "");
  if (!env.ADMIN_TOKEN || got.length !== env.ADMIN_TOKEN.length || !safeEqual(got, env.ADMIN_TOKEN)) throw err(401, "unauthorized");
}
function safeEqual(a, b) { let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
async function sha256(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}
function clientIp(request) { return request.headers.get("CF-Connecting-IP") || "0.0.0.0"; }
// IP 주소 자체는 저장하지 않고, 비밀 SALT를 섞은 해시만 저장해요.
async function ipHash(request, env) { return sha256(`${env.SALT || ""}|ip|${clientIp(request)}`); }
async function voterId(request, env, post) {
  const ua = request.headers.get("User-Agent") || "";
  return sha256(`${env.SALT || ""}|like|${post}|${clientIp(request)}|${ua}`);
}
