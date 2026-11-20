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
