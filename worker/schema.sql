-- 학종파이터 블로그 공감·댓글 데이터베이스 (Cloudflare D1)
CREATE TABLE IF NOT EXISTS likes (
  post       TEXT    NOT NULL,
  voter      TEXT    NOT NULL,  -- IP·브라우저 정보를 비밀값과 섞은 해시 (원래 IP는 저장 안 함)
  created_at INTEGER NOT NULL,
  PRIMARY KEY (post, voter)
);

CREATE TABLE IF NOT EXISTS comments (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  post       TEXT    NOT NULL,
  nick       TEXT    NOT NULL,
  body       TEXT    NOT NULL,
  status     TEXT    NOT NULL DEFAULT 'pending',  -- pending(승인 대기) / approved(공개) / rejected(거절)
  reply      TEXT,                                -- 운영자 답글
  ip_hash    TEXT    NOT NULL,                    -- 도배 방지용 해시
  created_at INTEGER NOT NULL,
  replied_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_comments_post   ON comments (post, status);
CREATE INDEX IF NOT EXISTS idx_comments_ip     ON comments (ip_hash, created_at);
CREATE INDEX IF NOT EXISTS idx_comments_status ON comments (status, id);

-- 상담 신청 (보관 기간이 지나면 자동 삭제)
CREATE TABLE IF NOT EXISTS consults (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  who        TEXT    NOT NULL,   -- 학생 / 학부모
  name       TEXT    NOT NULL,
  grade      TEXT    NOT NULL,
  track      TEXT,
  topics     TEXT,
  question   TEXT,
  method     TEXT    NOT NULL,   -- 전화 / 문자 / 카카오톡
  contact    TEXT    NOT NULL,
  time_pref  TEXT,
  status     TEXT    NOT NULL DEFAULT 'new',  -- new(새 신청) / contacted(연락함) / done(완료)
  memo       TEXT,               -- 운영자 메모
  ip_hash    TEXT    NOT NULL,
  consent_at INTEGER NOT NULL,   -- 개인정보 동의 시각
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_consults_status ON consults (status, id);
CREATE INDEX IF NOT EXISTS idx_consults_ip     ON consults (ip_hash, created_at);

-- 자체 방문 집계 (assets/hf-track.js → POST /api/t)
-- 이 표는 첫 방문 기록이 들어올 때 서버가 자동으로 만들어요. 직접 실행하지 않아도 돼요.
-- IP 주소는 저장하지 않고, 브라우저에 둔 무작위 번호(vid)와 접속 국가만 남겨요.
CREATE TABLE IF NOT EXISTS hits (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  ts       INTEGER NOT NULL,
  day      TEXT    NOT NULL,   -- 한국 시간 YYYYMMDD
  vid      TEXT    NOT NULL,   -- 방문자 (무작위 번호)
  sid      TEXT    NOT NULL,   -- 방문(세션)
  type     TEXT    NOT NULL,   -- pv(페이지 열람) / ev(버튼 등 행동) / eng(머문 시간·스크롤)
  path     TEXT    NOT NULL,
  title    TEXT,
  prev     TEXT,               -- 사이트 안에서 바로 전에 보던 페이지
  name     TEXT,               -- 행동 이름 (ev)
  params   TEXT,               -- 행동 부가 정보 (JSON)
  src      TEXT,               -- 들어온 곳 (naver, instagram, (direct) …)
  medium   TEXT,
  campaign TEXT,
  kw       TEXT,               -- 검색어 (검색엔진이 넘겨준 경우만)
  landing  TEXT,               -- 이번 방문에서 처음 연 페이지
  device   TEXT,
  country  TEXT,
  ms       INTEGER,            -- 머문 시간 (eng)
  scroll   INTEGER             -- 가장 깊이 내려간 위치 % (eng)
);
CREATE INDEX IF NOT EXISTS idx_hits_day ON hits (day, type);
CREATE INDEX IF NOT EXISTS idx_hits_vid ON hits (vid, day);
