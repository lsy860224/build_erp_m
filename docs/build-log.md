# Build Log — babipa_erp 시스템 동작 이력

정식 빌드(= `bench new-app babipa_erp` 이후 실제 Frappe 인스턴스에 대한 조작) 시작 시점부터,
시스템 상태를 변경하는 작업을 이 파일에 기록한다. Frappe 자체의 런타임 로그
(`sites/*/logs/`, git 추적 대상 아님)와는 별개로, "누가 언제 무엇을 했고 결과가 어땠는가"를
사람이 읽을 수 있는 히스토리로 남기는 것이 목적이다 — 감사 대응(SQ/HKMC)과 장애 발생 시
원인 추적에 그대로 쓸 수 있다.

## 기록 대상 (트리거)

다음 작업을 실행한 직후 반드시 아래 "이력" 표에 한 줄을 추가한다:

- `bench new-app` / `bench get-app` / `bench install-app` / `bench uninstall-app`
- `bench --site * migrate` / `bench --site * set-config`
- DocType/Custom Field/Property Setter 등 스키마 변경 후 `bench export-fixtures`
- 배포·재기동(`bench restart`, Docker 컨테이너 재기동/재빌드)
- `bench backup` 및 복구 작업
- 그 외 되돌리기 어렵거나 여러 명에게 영향이 가는 시스템 상태 변경

일상적인 코드 편집(Python 함수 수정, 프론트엔드 스타일 조정 등)은 기록 대상이 아니다 —
git 커밋 이력으로 충분하다.

## 기록 형식

| 날짜/시각 | 작업자 | 명령/작업 | 대상(사이트/앱) | 결과 | 비고 |
|---|---|---|---|---|---|
| 2026-08-01 10:00 (예시) | Claude Code | `bench new-app babipa_erp` | - | 성공 | 최초 앱 스캐폴딩 |

- **작업자**: 실제 실행한 주체 (사람 이름 또는 "Claude Code" — 세션에서 대신 실행한 경우)
- **결과**: 성공 / 실패(원인 요약) / 롤백함
- 실패했거나 롤백한 경우 비고에 원인과 후속 조치를 반드시 남긴다

## 이력

| 날짜/시각 | 작업자 | 명령/작업 | 대상(사이트/앱) | 결과 | 비고 |
|---|---|---|---|---|---|
| 2026-07-15 | Claude Code | `bench init --frappe-branch version-16 frappe-bench` | - | 성공 | 최초 시도는 `--frappe-branch` 미지정으로 `develop`(v17)로 초기화돼 erpnext 설치 불가 → 재시도. 상세 원인은 `docs/dev-environment.md` |
| 2026-07-15 | Claude Code | `bench new-site development.localhost` | development.localhost | 성공 | admin 비밀번호 `admin`(로컬 전용 기본값) |
| 2026-07-15 | Claude Code | `bench --site development.localhost set-config developer_mode 1` | development.localhost | 성공 | |
| 2026-07-15 | Claude Code | `bench get-app --branch version-16 erpnext` + `install-app erpnext` | development.localhost | 성공 | erpnext 16.28.0 |
| 2026-07-15 | Claude Code | `bench new-app --no-git babipa_erp` + `install-app babipa_erp` | development.localhost | 성공 | 최초 앱 스캐폴딩. `--no-git`으로 생성(버전관리는 build_erp_m 저장소가 담당) |
| 2026-07-15 | Claude Code | Language `ko` 레코드 `enabled=1`로 수정, Administrator 사용자 language=`ko` 설정 | development.localhost | 성공 | Setup Wizard의 언어 선택 위젯은 "완역" curated 목록이라 한국어가 안 보였을 뿐, Language 자체는 이미 존재 |
| 2026-07-15 | Claude Code | 표준 DocType 이름 425개 + 공통 액션/상태 단어 68개 한국어 Translation 레코드 추가(총 504개) + `bench export-fixtures --app babipa_erp` | development.localhost | 성공 | Frappe 코어 6,225개 미번역 문자열 중 고빈도 노출 계층(DocType명·Save/Submit/Status 등)만 우선 처리. DocType 폼 내부 필드 라벨은 별도의 더 큰 계층으로 미처리 |
| 2026-07-15 | Claude Code | Frappe 코어 문구 11개 한국어 Translation 레코드 추가(Home·Notification·Search 등) + `bench export-fixtures --app babipa_erp` | development.localhost | 성공 | ERPNext 앱 문구는 이미 자체 ko 번역(5,848개) 보유, Frappe 코어만 상류에 ko 번역이 없어 직접 채움. `apps/babipa_erp/babipa_erp/fixtures/translation.json`으로 export, `hooks.py`에 `fixtures` 훅 신설 |
