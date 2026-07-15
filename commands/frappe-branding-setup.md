---
description: frappe-branding 에이전트를 호출해 화이트라벨 브랜딩(로고/명칭/색상/메뉴 라벨)을 일괄 적용한다
---

브랜딩 요구사항: $ARGUMENTS (예: 회사명, 로고 파일 경로, 브랜드 컬러 코드, 한글화할 메뉴 목록)

1. frappe-branding 에이전트에게 위임하여 GPL v3 상표/라이선스 준수 여부를 먼저 확인한다
   ("ERPNext" 문자열이 신규 제품명에 들어가지 않는지 등).
2. `hooks.py`에 app_title, app_logo_url, app_include_css를 반영한다.
3. 브랜드 컬러를 CSS 변수로 정리한 `public/css/<company>_theme.css`를 생성한다.
4. 요청된 메뉴/필드 한글화 목록을 `translations/ko.csv` 형식으로 정리하고,
   `bench import-translations` 명령을 안내한다.
5. 로그인 페이지 커스터마이징이 필요하면 Website Settings 변경 가이드를 제시한다.
6. 마지막에 frappe-branding의 "확인 사항" 체크리스트를 결과에 포함해 사용자가 검증할 수
   있게 한다.
