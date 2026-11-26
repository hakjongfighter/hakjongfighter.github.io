// 학종파이터 블로그 공감·댓글 서버 (Cloudflare Worker + D1)
//
// 공개 API
//   GET  /api/popular                   블로그 글별 조회수 (목록의 '조회수 높은 글')
//   GET  /api/post?post=<slug>          공감 수, 내가 눌렀는지, 공개된 댓글 목록
//   POST /api/like      {post}          공감 (같은 방문자는 글마다 1번)
//   POST /api/comments  {post,nick,body,website}  댓글 등록 → 승인 대기
//   POST /api/consult   상담 신청 (개인정보 동의 필수)
//   POST /api/t         자체 방문 집계 (assets/hf-track.js가 보냄 · IP 주소는 저장 안 함)
// 관리자 API (헤더 Authorization: Bearer <ADMIN_TOKEN>)
//   GET  /api/admin/comments?status=pending|approved|rejected
//   POST /api/admin/comments/<id>  {action: approve|reject|delete|reply, reply}
//   GET  /api/admin/consults?status=new|contacted|done
//   POST /api/admin/consults/<id>  {action: new|contacted|done|memo|delete, memo}
//   GET  /api/admin/stats?days=28   자체 방문 집계 요약 (방문 현황 페이지용 · STATS_PASSWORD 해시로도 열림)
//
// 환경 변수: ADMIN_TOKEN(비밀), SALT(비밀), ALLOWED_ORIGINS(쉼표 구분), RETENTION_DAYS(선택, 기본 180)

const MAX_NICK = 20;
const MAX_BODY = 500;
const COMMENTS_PER_HOUR = 5;
const CONSULTS_PER_DAY = 10;   // 같은 곳(학교·학원 와이파이 등)에서 여러 명이 신청해도 막히지 않게 넉넉히
const SLUG_RE = /^[a-z0-9-]{1,80}$/;

export default {
  // 하루 한 번: 보관 기간이 지난 상담 신청·방문 기록을 지워요 (관리 화면을 열지 않아도)
  async scheduled(event, env, ctx) {
    ctx.waitUntil(purgeOld(env));
  },
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

  if (m === "POST" && p === "/api/t") {
    // 집계가 실패해도 방문자 화면에는 아무 영향이 없도록 항상 204로 답해요.
    try { await track(request, env); } catch (e) { console.error("track", e); }
    return new Response(null, { status: 204 });
  }

  if (m === "GET" && p === "/api/popular") {
    // 블로그 글별 조회수 (블로그 목록 '조회수 높은 글'용). 보관 기간(기본 180일) 안의 국내 열람만 세요.
    let rows = [];
    try {
      rows = (await env.DB.prepare(
        "SELECT path, SUM(type='pv') pv FROM hits WHERE type='pv' AND country='KR' AND path LIKE '/blog/%/' GROUP BY path ORDER BY pv DESC LIMIT 50"
      ).all()).results;
    } catch (e) { rows = []; } // 방문 기록 표가 아직 없으면 빈 목록
    const posts = [];
    for (const r of rows) {
      const mm = /^\/blog\/([a-z0-9-]{1,80})\/$/.exec(r.path);
      if (mm && mm[1] !== "admin" && mm[1] !== "category") posts.push({ post: mm[1], pv: r.pv || 0 });
    }
    const res = json({ posts });
    res.headers.set("Cache-Control", "public, max-age=600");
    return res;
  }

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

  if (m === "POST" && p === "/api/consult") {
    const d = await body(request);
    if (d.website) return json({ ok: true }); // 스팸봇용 숨은 칸
    const pick = (v, list) => (list.includes(v) ? v : "");
    const who = pick(d.who, ["학생", "학부모"]);
    const name = clean(d.name, 20);
    const grade = pick(d.grade, ["중3", "고1", "고2", "고3", "N수", "기타"]);
    const track = pick(d.track, ["인문·사회", "상경", "자연·공학", "의약", "예체능", "아직 모르겠어요", ""]);
    // 예전 항목(세특 작성법·수행평가)도 받아 둬요: 열려 있던 옛 화면에서 보낸 신청이 버려지지 않게
    const TOPICS = ["과목 선택", "수행평가·세특", "내신 공부법", "면접 대비", "대학·전형", "기타", "세특 작성법", "수행평가"];
    const topics = (Array.isArray(d.topics) ? d.topics : []).filter(t => TOPICS.includes(t)).slice(0, 8).join(", ");
    const question = clean(d.question, MAX_BODY, true);
    const method = pick(d.method, ["전화", "문자", "카카오톡"]);
    const contact = clean(d.contact, 40);
    const timePref = clean(d.time, 40);
    if (!who) throw err(400, "신청하시는 분을 골라 주세요.");
    if (!name) throw err(400, "이름(또는 호칭)을 적어 주세요.");
    if (!grade) throw err(400, "학년을 골라 주세요.");
    if (!method) throw err(400, "연락받을 방법을 골라 주세요.");
    if (!/^[0-9+\-\s()]{9,20}$/.test(contact) && method !== "카카오톡") throw err(400, "연락처를 정확히 적어 주세요.");
    if (contact.length < 3) throw err(400, "연락처를 적어 주세요.");
    if (d.agree_privacy !== true) throw err(400, "개인정보 수집·이용에 동의해 주세요.");
    if (d.agree_age !== true) throw err(400, "만 14세 이상인지 확인해 주세요.");
    const ip = await ipHash(request, env);
    // 같은 연락처로 하루 안에 다시 보내면 새로 저장하지 않고 '이미 접수됨'으로 알려요
    const digits = contact.replace(/\D/g, "");
    const dup = await env.DB.prepare(
      "SELECT id FROM consults WHERE created_at > ? AND (contact = ? OR (? <> '' AND REPLACE(REPLACE(REPLACE(contact,'-',''),' ',''),'+','') = ?)) LIMIT 1"
    ).bind(now() - 86400, contact, digits.length >= 9 ? digits : "", digits).first();
    if (dup) return json({ ok: true, duplicate: true });
    const { n } = await env.DB.prepare("SELECT COUNT(*) AS n FROM consults WHERE ip_hash=? AND created_at > ?").bind(ip, now() - 86400).first();
    if (n >= CONSULTS_PER_DAY) throw err(429, "지금은 같은 곳에서 신청이 많아 잠시 막혀 있어요. 02-459-4945로 전화 주시면 바로 도와드릴게요.");
    await env.DB.prepare(
      "INSERT INTO consults (who, name, grade, track, topics, question, method, contact, time_pref, status, ip_hash, consent_at, created_at) VALUES (?,?,?,?,?,?,?,?,?, 'new', ?, ?, ?)"
    ).bind(who, name, grade, track, topics, question, method, contact, timePref, ip, now(), now()).run();
    return json({ ok: true });
  }

  // 방문 현황 요약: 관리자 토큰 또는 방문 현황 비밀번호(STATS_PASSWORD)의 해시로 열려요. 신청자는 이름·날짜·상태만 주고 연락처는 주지 않아요.
  if (m === "GET" && p === "/api/admin/stats") {
    await requireStats(request, env);
    const days = Math.max(1, Math.min(90, Number(url.searchParams.get("days")) || 28));
    try { return json(await stats(env, days)); }
    catch (e) { if (!/no such table/i.test(String(e && e.message))) throw e; await ensureHits(env); return json(await stats(env, days)); }
  }

  if (p.startsWith("/api/admin/")) {
    requireAdmin(request, env);
    if (m === "GET" && p === "/api/admin/consults") {
      await purgeOld(env);
      const status = url.searchParams.get("status") || "new";
      if (!["new", "contacted", "done"].includes(status)) throw err(400, "bad_status");
      const { results } = await env.DB.prepare(
        "SELECT id, who, name, grade, track, topics, question, method, contact, time_pref, status, memo, created_at FROM consults WHERE status=? ORDER BY id DESC LIMIT 300"
      ).bind(status).all();
      return json({ consults: results });
    }
    const mc = p.match(/^\/api\/admin\/consults\/(\d+)$/);
    if (m === "POST" && mc) {
      const id = Number(mc[1]);
      const { action, memo } = await body(request);
      if (["new", "contacted", "done"].includes(action)) {
        await env.DB.prepare("UPDATE consults SET status=? WHERE id=?").bind(action, id).run();
      } else if (action === "memo") {
        await env.DB.prepare("UPDATE consults SET memo=? WHERE id=?").bind(clean(memo, MAX_BODY, true) || null, id).run();
      } else if (action === "delete") {
        await env.DB.prepare("DELETE FROM consults WHERE id=?").bind(id).run();
      } else throw err(400, "bad_action");
      return json({ ok: true });
    }
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

// 보관 기간(RETENTION_DAYS, 기본 180일)이 지난 상담 신청은 자동으로 지워요.
async function purgeOld(env) {
  const days = Number(env.RETENTION_DAYS || 180);
  await env.DB.prepare("DELETE FROM consults WHERE created_at < ?").bind(now() - days * 86400).run();
  // 방문 기록은 400일(HITS_RETENTION_DAYS)까지만 보관해요.
  try { await env.DB.prepare("DELETE FROM hits WHERE ts < ?").bind(now() - Number(env.HITS_RETENTION_DAYS || 400) * 86400).run(); } catch (e) {}
}

// ---------- 자체 방문 집계 ----------
// hits 표는 처음 기록이 들어올 때 자동으로 만들어져요 (schema.sql에도 같은 내용이 있어요).
const HITS_SQL = [
  `CREATE TABLE IF NOT EXISTS hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL, day TEXT NOT NULL,
    vid TEXT NOT NULL, sid TEXT NOT NULL,
    type TEXT NOT NULL, path TEXT NOT NULL, title TEXT, prev TEXT,
    name TEXT, params TEXT,
    src TEXT, medium TEXT, campaign TEXT, kw TEXT, landing TEXT,
    device TEXT, country TEXT, ms INTEGER, scroll INTEGER)`,
  "CREATE INDEX IF NOT EXISTS idx_hits_day ON hits (day, type)",
  "CREATE INDEX IF NOT EXISTS idx_hits_vid ON hits (vid, day)",
];
async function ensureHits(env) { await env.DB.batch(HITS_SQL.map(q => env.DB.prepare(q))); }

const BOT_RE = /bot|crawl|spider|slurp|facebookexternalhit|headless|lighthouse|pagespeed|preview|monitor|curl|wget|python|scrapy|yeti|ahrefs|semrush|gptbot/i;
const ID_RE = /^[a-f0-9]{16,32}$/;
const EVENT_RE = /^[a-z0-9_]{1,40}$/;
function kstDay(t) { const d = new Date((t + 32400) * 1000); return d.toISOString().slice(0, 10).replace(/-/g, ""); }

// 어디서 들어왔는지: utm → 이전 페이지 주소 → 앱 안 브라우저 순서로 판단해요.
function sourceOf(ref, us, um, uc, ua) {
  if (us) return { src: us.toLowerCase(), medium: (um || "utm").toLowerCase(), campaign: uc || "", kw: "" };
  let host = "", sp = null;
  try { const u = new URL(ref); host = u.hostname.replace(/^(www|m)\./, ""); sp = u.searchParams; } catch {}
  if (/(^|\.)hakjongfighter\.com$/.test(host)) host = "";
  const o = (src, medium, kw = "") => ({ src, medium, campaign: "", kw: clean(kw, 60) });
  if (!host) {
    if (/Instagram/i.test(ua)) return o("instagram", "app");
    if (/KAKAOTALK/i.test(ua)) return o("kakaotalk", "app");
    if (/FBAN|FBAV|FB_IAB/i.test(ua)) return o("facebook", "app");
    if (/Barcelona/i.test(ua)) return o("threads", "app");
    if (/NAVER\(inapp/i.test(ua)) return o("naver", "app");
    return o("(direct)", "(none)");
  }
  const kw = k => (sp && sp.get(k)) || "";
  if (/(^|\.)blog\.naver\.com$/.test(host)) return o("blog.naver.com", "referral");
  if (/(^|\.)cafe\.naver\.com$/.test(host)) return o("cafe.naver.com", "referral");
  if (/(^|\.)naver\.com$/.test(host)) return o("naver", "organic", kw("query"));
  if (/(^|\.)google\./.test(host)) return o("google", "organic", kw("q"));
  if (/(^|\.)daum\.net$/.test(host)) return o("daum", "organic", kw("q"));
  if (/(^|\.)bing\.com$/.test(host)) return o("bing", "organic", kw("q"));
  if (/instagram\.com$/.test(host)) return o("instagram", "social");
  if (/facebook\.com$/.test(host)) return o("facebook", "social");
  if (/threads\.(net|com)$/.test(host)) return o("threads", "social");
  if (/(youtube\.com|youtu\.be)$/.test(host)) return o("youtube", "social");
  if (/kakao\.com$/.test(host)) return o("kakao", "social");
  if (/^(t\.co|x\.com|twitter\.com)$/.test(host)) return o("x", "social");
  return o(host.slice(0, 60), "referral");
}

async function track(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
  if (!allowed.includes(origin)) return;                       // 우리 사이트에서 온 기록만 받음
  const ua = request.headers.get("User-Agent") || "";
  if (BOT_RE.test(ua)) return;
  const d = await body(request);
  const type = ["pv", "ev", "eng"].includes(d.t) ? d.t : "";
  if (!type || !ID_RE.test(d.v || "") || !ID_RE.test(d.s || "")) return;
  const path = clean(d.p, 200);
  if (!path.startsWith("/") || /^\/(stats|blog\/admin)(\/|$)/.test(path)) return;
  const name = type === "ev" ? String(d.n || "") : null;
  if (type === "ev" && !EVENT_RE.test(name)) return;
  let params = null;
  if (type === "ev" && d.pr && typeof d.pr === "object") {
    const keep = {};
    for (const [k, v] of Object.entries(d.pr).slice(0, 6)) if (/^[a-z_]{1,30}$/.test(k)) keep[k] = clean(String(v), 80);
    params = JSON.stringify(keep);
  }
  const s = sourceOf(clean(d.r, 300), clean(d.us, 60), clean(d.um, 60), clean(d.uc, 80), ua);
  const device = /iPad|Tablet/i.test(ua) ? "tablet" : /Mobi|Android|iPhone/i.test(ua) ? "mobile" : "desktop";
  const country = (request.cf && request.cf.country) || "";
  const t = now();
  const row = [t, kstDay(t), d.v, d.s, type, path, type === "pv" ? clean(d.ti, 120) : null, clean(d.pp, 200) || null, name, params,
    s.src, s.medium, s.campaign, s.kw, clean(d.l, 200) || path, device, country,
    type === "eng" ? Math.max(0, Math.min(1800000, Math.round(Number(d.ms) || 0))) : null,
    type === "eng" ? Math.max(0, Math.min(100, Math.round(Number(d.sc) || 0))) : null];
  const ins = () => env.DB.prepare(
    "INSERT INTO hits (ts, day, vid, sid, type, path, title, prev, name, params, src, medium, campaign, kw, landing, device, country, ms, scroll) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
  ).bind(...row).run();
  try { await ins(); }
  catch (e) { if (!/no such table/i.test(String(e && e.message))) throw e; await ensureHits(env); await ins(); }
}

// 방문 현황 페이지가 그대로 그릴 수 있게, GA4에서 받던 것과 같은 모양으로 돌려줘요.
// 기본은 한국에서 접속한 방문만 세고, 전체·나라별 숫자는 all에 따로 담아요.
// 질의가 수십 개라 하나씩 보내면 10초 넘게 걸려서, 한 묶음(batch)으로 한 번에 보내요.
async function stats(env, days) {
  const t = now();
  const dayAt = i => kstDay(t - i * 86400);
  const c0 = dayAt(days - 1), c1 = dayAt(0), p0 = dayAt(days * 2 - 1), p1 = dayAt(days);
  const KR = "country='KR'";
  const MS = "SUM(CASE WHEN type='eng' THEN ms ELSE 0 END)";
  const SM = "src || ' / ' || medium";
  const W = `${KR} AND day BETWEEN ? AND ?`;

  const jobs = [];
  const Q = (sql, ...b) => jobs.push(env.DB.prepare(sql).bind(...b)) - 1;   // 묶음에 넣고 결과 자리 번호를 돌려줌

  const totalsQ = (a, b, extra = "") => {
    const w = `${KR} AND day BETWEEN ? AND ?${extra}`;
    return [
      Q(`SELECT COUNT(DISTINCT vid) u, COUNT(DISTINCT sid) s, SUM(type='pv') pv, ${MS} ms FROM hits WHERE ${w}`, a, b),
      Q(`SELECT COUNT(*) n FROM (SELECT vid, MIN(day) d FROM hits WHERE ${KR} GROUP BY vid) WHERE d BETWEEN ? AND ?`, a, b),
      Q(`SELECT COUNT(*) n FROM (SELECT sid FROM hits WHERE ${w} GROUP BY sid HAVING SUM(type='pv')>=2 OR SUM(type='ev')>=1 OR ${MS}>=10000)`, a, b),
    ];
  };
  const eventsQ = (a, b) => [
    Q(`SELECT name, COUNT(*) c, COUNT(DISTINCT vid) u FROM hits WHERE type='ev' AND ${KR} AND day BETWEEN ? AND ? GROUP BY name`, a, b),
    // 스크롤: 페이지를 90% 넘게 내려 본 경우 (GA4의 scroll과 같은 기준)
    Q(`SELECT COUNT(DISTINCT sid || path) c, COUNT(DISTINCT vid) u FROM hits WHERE type='eng' AND scroll>=90 AND ${KR} AND day BETWEEN ? AND ?`, a, b),
  ];
  const paramQ = key => Q(
    `SELECT name, json_extract(params, '$.${key}') v, COUNT(*) c FROM hits WHERE type='ev' AND ${W} AND json_extract(params, '$.${key}') IS NOT NULL GROUP BY name, v`, c0, c1);

  const BLOGX = " AND path LIKE '/blog/%'";
  const J = {
    tCur: totalsQ(c0, c1), tPrev: totalsQ(p0, p1), bCur: totalsQ(c0, c1, BLOGX), bPrev: totalsQ(p0, p1, BLOGX),
    eCur: eventsQ(c0, c1), ePrev: eventsQ(p0, p1),
    daily: Q(`SELECT day, COUNT(DISTINCT vid) u FROM hits WHERE ${W} GROUP BY day`, c0, c1),
    dailyEv: Q(`SELECT day, name, COUNT(*) c FROM hits WHERE type='ev' AND ${W} GROUP BY day, name`, c0, c1),
    channels: Q(`SELECT ${SM} sm, COUNT(DISTINCT sid) s FROM hits WHERE ${W} GROUP BY sm ORDER BY s DESC LIMIT 10`, c0, c1),
    channelEv: Q(`SELECT ${SM} sm, name, COUNT(*) c FROM hits WHERE type='ev' AND ${W} GROUP BY sm, name`, c0, c1),
    devices: Q(`SELECT device, COUNT(DISTINCT vid) u FROM hits WHERE ${W} GROUP BY device ORDER BY u DESC`, c0, c1),
    pages: Q(`SELECT path, MAX(title) title, SUM(type='pv') pv, COUNT(DISTINCT vid) u, ${MS} ms FROM hits WHERE ${W} GROUP BY path ORDER BY pv DESC LIMIT 200`, c0, c1),
    pageEv: Q(`SELECT path, name, COUNT(*) c, COUNT(DISTINCT vid) u FROM hits WHERE type='ev' AND ${W} GROUP BY path, name`, c0, c1),
    pageScroll: Q(`SELECT path, COUNT(DISTINCT sid) c, COUNT(DISTINCT vid) u FROM hits WHERE type='eng' AND scroll>=90 AND ${W} GROUP BY path`, c0, c1),
    blogLanding: Q(`SELECT ${SM} sm, COUNT(DISTINCT sid) s FROM hits WHERE ${W} AND landing LIKE '/blog/%' GROUP BY sm ORDER BY s DESC LIMIT 8`, c0, c1),
    // 신청 완료 직전에 보던 페이지 (블로그 글에서 넘어온 신청인지 알 수 있어요)
    consultSrc: Q(`SELECT COALESCE(prev, '') pv, COUNT(*) c FROM hits WHERE type='ev' AND name='consult_submit' AND ${W} GROUP BY pv`, c0, c1),
    // 검색해서 들어온 방문의 검색어 (네이버·다음처럼 검색어를 넘겨주는 곳만 잡혀요)
    search: Q(`SELECT kw, src, COUNT(DISTINCT sid) s FROM hits WHERE kw<>'' AND ${W} GROUP BY kw, src ORDER BY s DESC LIMIT 30`, c0, c1),
    searchVisits: Q(`SELECT src, COUNT(DISTINCT sid) s FROM hits WHERE medium='organic' AND ${W} GROUP BY src ORDER BY s DESC`, c0, c1),
    hours: Q(`SELECT CAST(strftime('%H', ts + 32400, 'unixepoch') AS INTEGER) h, COUNT(DISTINCT sid) s FROM hits WHERE ${W} GROUP BY h`, c0, c1),
    params: { cta_location: paramQ("cta_location"), audience: paramQ("audience"), stage: paramQ("stage"), place: paramQ("place") },
    first: Q("SELECT MIN(day) d, COUNT(*) n FROM hits"),
    allT: Q("SELECT COUNT(DISTINCT vid) u, COUNT(DISTINCT sid) s FROM hits WHERE day BETWEEN ? AND ?", c0, c1),
    countries: Q("SELECT country, COUNT(DISTINCT vid) u, COUNT(DISTINCT sid) s FROM hits WHERE day BETWEEN ? AND ? GROUP BY country ORDER BY u DESC LIMIT 12", c0, c1),
    periods: {},
  };

  // 랜딩페이지·블로그 방문을 오늘/어제/이번 주/이번 달/저번 달로 (한국 시간 기준)
  const kd0 = new Date((t + 32400) * 1000);
  const ymd = d => d.toISOString().slice(0, 10).replace(/-/g, "");
  const at = (y, mo, da) => new Date(Date.UTC(y, mo, da));
  const Y = kd0.getUTCFullYear(), Mo = kd0.getUTCMonth(), Da = kd0.getUTCDate();
  const spans = {
    today: [at(Y, Mo, Da), at(Y, Mo, Da)], yesterday: [at(Y, Mo, Da - 1), at(Y, Mo, Da - 1)],
    week: [at(Y, Mo, Da - ((kd0.getUTCDay() + 6) % 7)), at(Y, Mo, Da)],   // 이번 주 월요일부터
    month: [at(Y, Mo, 1), at(Y, Mo, Da)], last_month: [at(Y, Mo - 1, 1), at(Y, Mo, 0)],
  };
  const GROUPS = [["home", "path IN ('/', '/index.html')"], ["blog", "path LIKE '/blog/%'"]];
  for (const [k, [a, b]] of Object.entries(spans)) for (const [g, cond] of GROUPS)
    J.periods[g + "|" + k] = Q(`SELECT COUNT(DISTINCT vid) u, SUM(type='pv') pv FROM hits WHERE ${KR} AND day BETWEEN ? AND ? AND ${cond}`, ymd(a), ymd(b));

  // 신청 요약 + 최근 신청자 이름·날짜 (연락처·질문 내용은 주지 않아요. 자세한 내용은 관리 페이지에서)
  const consultsP = env.DB.prepare("SELECT name, status, who, grade, topics, created_at FROM consults ORDER BY id DESC").all()
    .then(r => r.results, e => { console.error("consults", e); return []; });

  const [batch, consultRows] = await Promise.all([env.DB.batch(jobs), consultsP]);
  const R = i => batch[i].results || [];
  const one = i => R(i)[0] || {};

  const totals = ([a, b, c]) => {
    const r = one(a), s = r.s || 0, ms = r.ms || 0;
    return { activeUsers: r.u || 0, newUsers: one(b).n || 0, sessions: s, screenPageViews: r.pv || 0,
      engagementRate: s ? (one(c).n || 0) / s : 0, averageSessionDuration: s ? ms / 1000 / s : 0, userEngagementDuration: ms / 1000 };
  };
  const events = ([a, b]) => {
    const ev = {}, eu = {};
    for (const r of R(a)) { ev[r.name] = r.c; eu[r.name] = r.u; }
    const sc = one(b);
    if (sc.c) { ev.scroll = sc.c; eu.scroll = sc.u; }
    return [ev, eu];
  };
  const [evC, euC] = events(J.eCur), [evP, euP] = events(J.ePrev);

  const byDay = {};
  for (const r of R(J.daily)) byDay[r.day] = r.u;
  const daily = [];
  for (let i = days - 1; i >= 0; i--) daily.push({ date: dayAt(i), activeUsers: byDay[dayAt(i)] || 0 });
  const dailyEvents = {};
  for (const r of R(J.dailyEv)) (dailyEvents[r.day] ||= {})[r.name] = r.c;

  const param = key => R(J.params[key]).map(r => ({ eventName: r.name, ["customEvent:" + key]: String(r.v), eventCount: r.c }));
  const sm = i => R(i).map(r => ({ sessionSourceMedium: r.sm, sessions: r.s }));

  const periods = { ranges: {}, home: {}, blog: {} };
  for (const [k, [a, b]] of Object.entries(spans)) {
    periods.ranges[k] = [ymd(a), ymd(b)];
    for (const [g] of GROUPS) { const r = one(J.periods[g + "|" + k]); periods[g][k] = { users: r.u || 0, views: r.pv || 0 }; }
  }

  const consults = { total: 0, total28: 0, status: {}, who: {}, grade: {}, topics: {}, list: [] };
  for (const r of consultRows) {
    consults.total++;
    if (consults.list.length < 30) consults.list.push({ name: r.name, status: r.status, created_at: r.created_at });
    if (r.created_at >= t - days * 86400) consults.total28++;
    consults.status[r.status] = (consults.status[r.status] || 0) + 1;
    consults.who[r.who] = (consults.who[r.who] || 0) + 1;
    consults.grade[r.grade] = (consults.grade[r.grade] || 0) + 1;
    for (const tp of String(r.topics || "").split(",").map(x => x.trim()).filter(Boolean)) consults.topics[tp] = (consults.topics[tp] || 0) + 1;
  }

  const kd = kd0.toISOString();
  return {
    status: "ok", source: "own", scope: "KR",
    updated_at: kd.slice(0, 10) + " " + kd.slice(11, 16),
    first_day: one(J.first).d || null,
    periods, consults,
    period: { cur: [c0, c1] },
    totals: { cur: totals(J.tCur), prev: totals(J.tPrev) },
    events: { cur: evC, prev: evP },
    event_users: { cur: euC, prev: euP },
    daily, daily_events: dailyEvents,
    channels: sm(J.channels),
    channel_events: R(J.channelEv).map(r => ({ sessionSourceMedium: r.sm, eventName: r.name, eventCount: r.c })),
    devices: R(J.devices).map(r => ({ deviceCategory: r.device, activeUsers: r.u })),
    pages: R(J.pages).map(r => ({ pagePath: r.path, pageTitle: r.title || "", screenPageViews: r.pv || 0, activeUsers: r.u, userEngagementDuration: (r.ms || 0) / 1000 })),
    page_events: R(J.pageEv).concat(R(J.pageScroll).map(r => ({ ...r, name: "scroll" })))
      .map(r => ({ pagePath: r.path, eventName: r.name, eventCount: r.c, totalUsers: r.u })),
    blog: { totals: { cur: totals(J.bCur), prev: totals(J.bPrev) }, landing_channels: sm(J.blogLanding) },
    consult_sources: R(J.consultSrc).map(r => ({ pageReferrer: r.pv, eventCount: r.c })),
    search: { status: "ok", source: "referrer", rows: R(J.search).map(r => ({ query: r.kw, engine: r.src, clicks: r.s })) },
    search_visits: R(J.searchVisits).map(r => ({ engine: r.src, sessions: r.s })),
    hours: R(J.hours).map(r => ({ hour: r.h, sessions: r.s })),
    params: { cta_location: param("cta_location"), audience: param("audience"), stage: param("stage"), place: param("place") },
    all: {
      totals: { activeUsers: one(J.allT).u || 0, sessions: one(J.allT).s || 0 },
      countries: R(J.countries).map(r => ({ country: r.country || "(알 수 없음)", activeUsers: r.u, sessions: r.s })),
    },
  };
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
async function requireStats(request, env) {
  const got = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/, "");
  if (env.ADMIN_TOKEN && got.length === env.ADMIN_TOKEN.length && safeEqual(got, env.ADMIN_TOKEN)) return;
  if (env.STATS_PASSWORD && got.startsWith("sp_")) {
    const want = "sp_" + await sha256("hf-stats|" + env.STATS_PASSWORD);
    if (got.length === want.length && safeEqual(got, want)) return;
  }
  throw err(401, "unauthorized");
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
