# Frappe/ERPNext 커스터마이징 프로젝트 — 루트 지침

이 파일은 Claude Code가 이 저장소에서 작업할 때 항상 먼저 읽는 최상위 컨텍스트입니다.
**매 순간 반드시 지켜야 하는 핵심 규칙만** 담습니다 — 배경 설명, 상세 절차, 계속 늘어나는
이력(로그)은 모두 `docs/`로 분리해 이 파일이 비대해지지 않도록 합니다. 각 원칙 옆의
경로는 그 상세 버전입니다.

저장소 전체 구조는 [`README.md`](README.md)가 지도 역할을 합니다.

## 프로젝트 개요

- **베이스**: ERPNext (GPL v3, Frappe Framework 기반)
- **목적**: 사내 인트라넷 전용으로 self-host, 자체 브랜드(Custom App)로 화이트라벨링
- **커스텀 앱 이름**: `babipa_erp` (예시 — 실제 앱 이름으로 교체)
- **도메인 특화 요구사항**:
  - HKMC(현대기아) ES 표준 대응 — 신뢰성 시험, 트레이서빌리티, SQ 감사 대응
  - 시험 장비/센서 Endpoint 파라미터 관리
  - `reliability-alt-toolkit`(FastAPI 기반 ALT 계산 서버)와 REST/웹훅 연동
- **배포 환경**: 외부 인터넷 차단 사내망(인트라넷), Docker Compose 기반

## 절대 원칙 (모든 에이전트 공통, 예외 없이 항상 적용)

1. **코어 미수정** — `apps/erpnext/`, `apps/frappe/` 직접 수정 금지. 모든 커스터마이징은
   `apps/babipa_erp/` 안에서만. (`bench update` 시 코어 변경사항 충돌·소실 방지)
   → 앱 디렉토리 구조: [`docs/app-directory-structure.md`](docs/app-directory-structure.md)
2. **RestrictedPython 준수** — Server Script는 모든 `import` 문 차단, `frappe.` 네임스페이스로만
   접근. (`frappe-server-script-restrictions` 스킬 참조)
3. **DocType/필드 리네임 금지** — 표준 스키마는 그대로 두고, 화면 표시명만 Translation으로 변경.
4. **GPLv3/상표 준수** — 코어 미수정(#1과 동일), ERPNext/Frappe 상표를 제품명·마케팅에
   사용 금지, 저작권 고지 보존, 신규 pip/npm 의존성 라이선스 확인.
   → 상세(제3자 배포 시 의무 등): [`docs/gplv3-compliance.md`](docs/gplv3-compliance.md)
5. **`developer_mode=1`은 개발 환경 전용** — 프로덕션에서는 절대 켜지 않는다.
6. **커스터마이징은 Fixture로 export** — Custom Field/DocType/Workspace 등을 Git 버전관리
   대상에 포함시킨다.
7. **시스템 상태를 바꾸는 작업 후에는 commit+push 필수** — 사용자 확인 없이 즉시 수행
   (이 문서가 사전 승인). 강제 push·제3자 배포·파괴적 작업은 예외 — 항상 먼저 확인.
   → 상세 절차/예외/커밋로그 메커니즘: [`docs/commit-push-policy.md`](docs/commit-push-policy.md)

## 에이전트 라우팅 가이드

| 요청 유형 | 담당 에이전트 |
|---|---|
| 새 DocType/데이터 모델 설계 | `frappe-architect` |
| Python 컨트롤러, hooks.py, Server Script | `frappe-backend` |
| Client Script, Desk UI, Workspace | `frappe-frontend` |
| 로고/명칭/메뉴 라벨 등 화이트라벨링 | `frappe-branding` |
| 외부 시스템(reliability-alt-toolkit 등) 연동 | `frappe-integration` |
| bench/Docker 배포, 인트라넷 오프라인 설치, 백업 | `frappe-devops` |
| 에러 로그 분석, 원인 불명 버그 | `frappe-debugger` |
| 코드 리뷰, 라이선스/보안 점검 | `frappe-reviewer` |
| 테스트 작성/실행 | `frappe-qa` |
| HKMC ES 표준/SQ 감사 관점 요구사항 검토 | `hkmc-compliance` |

## 작업 시작 전 체크리스트 (모든 에이전트 공통)

- [ ] 코어 파일을 건드리는가? → 중단하고 Custom App 방식으로 재설계
- [ ] Server Script에 import 문이 있는가? → `frappe.` 네임스페이스로 치환
- [ ] 새 DocType/필드를 fixtures에 등록했는가?
- [ ] HKMC 감사 대응 데이터(시험 이력, 트레이서빌리티)와 관련 있는가? → `hkmc-compliance` 리뷰 필요
- [ ] 새 pip/npm 의존성을 추가하는가? → GPLv3 충돌 여부 확인 ([`docs/gplv3-compliance.md`](docs/gplv3-compliance.md))
- [ ] 시스템 상태를 변경하는 작업(bench 조작, 배포, 백업 등)을 완료했는가? → `docs/build-log.md`에
      기록하고 [`docs/commit-push-policy.md`](docs/commit-push-policy.md)에 따라 commit+push까지 수행

## 참고 문서 (`docs/`)

| 문서 | 내용 |
|---|---|
| [`docs/decisions.md`](docs/decisions.md) | 프로젝트 결정 이력 (계속 늘어나는 로그) |
| [`docs/gplv3-compliance.md`](docs/gplv3-compliance.md) | GPLv3/ERPNext 라이선스·상표 준수 상세 가이드라인 |
| [`docs/commit-push-policy.md`](docs/commit-push-policy.md) | 커밋 로그 메커니즘 + 커밋/Push 필수 규칙·절차·예외 |
| [`docs/build-log.md`](docs/build-log.md) | 정식 빌드 이후 시스템 조작 이력 (기록 대상/형식 스펙 겸함) |
| [`docs/app-directory-structure.md`](docs/app-directory-structure.md) | babipa_erp 앱 디렉토리 구조 |
| [`docs/research/`](docs/research/) | 착수 전 리서치 참고자료 (미확정 문서 포함, `CLAUDE.md`와 상충 시 이 파일이 우선) |
