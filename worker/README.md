# 블로그 공감 · 댓글 서버 설정 안내

블로그 글 아래 **공감 버튼**과 **댓글**을 켜는 방법이에요. Cloudflare 무료 기능(Workers + D1)을 써요.
아래 순서를 한 번만 따라 하면 돼요. 10~20분 정도 걸려요.

## 1. 데이터베이스 만들기 (D1)

1. Cloudflare 대시보드 → 왼쪽 메뉴 **Storage & Databases → D1** → **Create**
2. 이름: `hakjongfighter-blog` → 만들기
3. 만든 데이터베이스 → **Console** 탭 → 이 폴더의 `schema.sql` 내용을 전부 붙여 넣고 실행

## 2. 서버 만들기 (Worker)

1. 왼쪽 메뉴 **Workers & Pages → Create → Worker**
2. 이름: `hakjongfighter-blog-api` → **Deploy**
3. **Edit code** → 원래 코드를 모두 지우고 `src/index.js` 내용을 붙여 넣기 → **Deploy**

## 3. 서버와 데이터베이스 연결

Worker 화면 → **Settings**

- **Bindings → Add → D1 database**
  - Variable name: `DB`
  - D1 database: `hakjongfighter-blog`
- **Variables and Secrets → Add**
  | 종류 | 이름 | 값 |
  |---|---|---|
  | Text | `ALLOWED_ORIGINS` | `https://hakjongfighter.com,https://www.hakjongfighter.com` |
  | Secret | `ADMIN_TOKEN` | 아무도 모르는 긴 문자열 (댓글 관리할 때 쓰는 비밀번호) |
  | Secret | `SALT` | 또 다른 긴 문자열 (방문자 구분용, 한 번 정하면 바꾸지 않기) |

저장하면 Worker 주소가 보여요. 예: `https://hakjongfighter-blog-api.이름.workers.dev`

## 4. 블로그에 서버 주소 알려 주기

1. GitHub `hakjongfighter.github.io` 저장소 → **Settings → Secrets and variables → Actions → Variables 탭**
2. **New repository variable**
   - Name: `BLOG_API`
   - Value: 3번에서 복사한 Worker 주소
3. **Actions → Deploy to GitHub Pages → Run workflow** 로 한 번 다시 배포

몇 분 뒤 블로그 글 아래에 공감 버튼과 댓글 칸이 나타나요.

## 5. 댓글 관리

- 주소: `https://hakjongfighter.com/blog/admin/`
- `ADMIN_TOKEN` 값을 넣고 **불러오기**
- **승인**한 댓글만 블로그에 보여요. 답글을 달면 '운영자' 표시와 함께 보여요.
- 검색엔진에는 이 페이지가 나오지 않게 막아 두었어요.

## 끄고 싶을 때

GitHub 저장소 변수 `BLOG_API`를 지우고 다시 배포하면 공감·댓글 칸이 사라져요. 데이터는 D1에 그대로 남아요.

## 지켜지는 것

- 공감: 같은 방문자는 글마다 1번만 (IP·브라우저 정보를 비밀값과 섞은 값으로 구분, **IP 주소 자체는 저장하지 않음**)
- 댓글: 닉네임 20자, 내용 500자까지 · 승인 전에는 공개 안 됨 · 같은 곳에서 1시간에 5개까지 · 스팸봇 차단용 숨은 칸
- 다른 사이트에서는 이 서버를 호출할 수 없음 (`ALLOWED_ORIGINS`에 적은 주소만 허용)
