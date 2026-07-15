---
description: 새 Frappe Custom App을 스캐폴딩하고 브랜딩 기본값을 설정한다
---

앱 이름: $ARGUMENTS (예: babipa_erp)

1. `bench new-app <app_name>` 실행 명령과 인터랙티브 입력값(App Title, Publisher, Email,
   License 등)을 제시한다. License는 GPLv3로 맞추거나, 사내 전용이면 Proprietary로 지정
   가능함을 안내한다 (Custom App 자체는 GPL 의무 없음 — ERPNext/Frappe 코어만 GPL v3).
2. `bench --site <site> install-app <app_name>` 명령을 제시한다.
3. `hooks.py`에 기본 브랜딩 골격(app_title, app_logo_url, app_include_css)을 채워 넣는다
   (frappe-branding 에이전트 스타일 참조).
4. 아래 디렉토리 구조를 기본으로 생성 제안한다:
   ```
   <app_name>/
   ├── <app_name>/
   │   ├── doctype/
   │   ├── events/
   │   ├── fixtures/
   │   ├── patches/
   │   └── public/{css,js,images}/
   ```
5. `developer_mode`를 개발 사이트에서만 켜는 명령을 안내하고, 프로덕션에서는 끄도록
   경고 문구를 포함한다.
6. 마지막으로 CLAUDE.md의 "절대 원칙" 요약을 다시 한번 출력해 이후 작업의 기준으로 삼는다.
