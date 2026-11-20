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
