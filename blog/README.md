# 학종파이터 블로그 글쓰기 안내

블로그 주소: https://hakjongfighter.com/blog/

## 새 글 올리는 법

1. `blog/posts/` 폴더에 새 파일을 만들어요. 파일 이름은 `날짜-영어주소.md` 형식이에요.
   예: `2026-11-27-subject-choice.md` → 글 주소는 `hakjongfighter.com/blog/subject-choice/`
2. 파일 맨 위에 글 정보를 적고, 그 아래에 본문을 써요.
3. main에 올리면(커밋) 몇 분 뒤 블로그에 자동으로 나타나요.

```
---
title: 글 제목
date: 2026-11-27
category: 진로·과목 선택
summary: 목록과 검색 결과에 보일 한두 문장 요약
thumbnail: /images/step1.jpg
caption: 대표 이미지 아래 설명 (없어도 돼요)
tags: 세특, 고교학점제
featured: false
pick: false
draft: false
---

## 소제목

본문을 씁니다. **굵게**, <mark>형광펜</mark>도 쓸 수 있어요.
```

## 글 정보 항목

| 항목 | 설명 |
|---|---|
| title | 글 제목 (필수) |
| date | 날짜, `2026-11-27` 형식 (필수). 최신 날짜가 목록 맨 위에 와요 |
| category | 아래 카테고리 중 하나 (필수) |
| summary | 요약. 목록, 검색, 공유 미리보기에 쓰여요 |
| thumbnail | 대표 이미지 경로. 이미지는 `/images/` 폴더에 넣어요. 없으면 ✏️ 아이콘이 보여요 |
| tags | 쉼표로 구분 |
| featured | `true`면 메인 맨 위 '추천 글' 자리에 크게 보여요 (하나만) |
| pick | `true`면 사이드바 '추천 글' 목록에 들어가요 |
| draft | `true`면 사이트에 올라가지 않아요 (임시 저장) |

카테고리: 진로·과목 선택 / 수행평가·세특 / 심화탐구 / 내신 공부법 / 학부모 가이드 / 4컷 만화

## 본문에 쓸 수 있는 꾸밈 요소

- 소제목: `## 소제목` (2개 이상이면 '이 글의 순서' 목차가 자동으로 생겨요)
- 인용구: 줄 앞에 `> `
- 이미지: `![설명](/images/파일이름.jpg)`
- 번호 질문 박스, 예시 박스, 팁 박스는 `2026-11-20-seteuk-3-questions.md`의 `<div class="q">`, `<div class="ex">`, `<div class="note">` 부분을 복사해서 쓰면 돼요.

## 미리 보기 (선택)

```
pip install markdown
python .github/scripts/build_blog.py
```

만들어진 `blog/index.html`, `blog/<주소>/index.html`은 배포 때 자동으로 다시 만들어지므로 저장소에 올리지 않아요.
