# Frappe/ERPNext 커스터마이징 프로젝트 — 루트 지침

이 파일은 Claude Code가 이 저장소에서 작업할 때 항상 먼저 읽는 최상위 컨텍스트입니다.
서브에이전트/슬래시커맨드가 이 파일의 원칙을 벗어나지 않도록 합니다.

## 프로젝트 개요

- **베이스**: ERPNext (GPL v3, Frappe Framework 기반)
- **목적**: 사내 인트라넷 전용으로 self-host, 자체 브랜드(Custom App)로 화이트라벨링
- **커스텀 앱 이름**: `babipa_erp` (예시 — 실제 앱 이름으로 교체)
- **도메인 특화 요구사항**:
  - HKMC(현대기아) ES 표준 대응 — 신뢰성 시험, 트레이서빌리티, SQ 감사 대응
  - 시험 장비/센서 Endpoint 파라미터 관리
  - `reliability-alt-toolkit`(FastAPI 기반 ALT 계산 서버)와 REST/웹훅 연동
- **배포 환경**: 외부 인터넷 차단 사내망(인트라넷), Docker Compose 기반

## 절대 원칙 (모든 에이전트 공통)

1. **ERPNext 코어 소스(`apps/erpnext/`, `apps/frappe/`) 직접 수정 금지.**
   모든 커스터마이징은 `apps/babipa_erp/` 커스텀 앱 안에서만 이루어진다.
   (이유: `bench update` 시 코어 변경사항이 충돌·소실됨)
2. **Server Script는 RestrictedPython 샌드박스에서 실행된다 — 모든 `import` 문 차단.**
   `frappe.utils.nowdate()`처럼 반드시 `frappe` 네임스페이스로 접근한다.
   (`frappe-server-script-restrictions` 스킬 참조)
3. **DocType/필드를 표준 스키마에서 리네임하지 않는다.** 화면 표시명은 Translation으로만 바꾼다.
4. **GPL v3 준수**: 코드 수정·리브랜딩은 사내 전용이면 소스 공개 의무 없음. 단, 제3자(AU Co. 등)에 동일 커스텀 빌드를 배포하는 순간 GPL 조건이 적용될 수 있으므로, 배포 계획이 생기면 별도 확인 필요. "ERPNext" 이름/로고는 상표이므로 제품명에 사용 금지.
5. **개발모드(`developer_mode=1`)는 개발 환경에서만.** 프로덕션에서는 절대 켜지 않는다.
6. 모든 커스터마이징(Custom Field, Custom DocType, Workspace 변경 등)은 **Fixture로 export**하여 Git 버전관리 대상에 포함시킨다.

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

## 디렉토리 규칙

```
apps/babipa_erp/
├── babipa_erp/
│   ├── hooks.py              # 브랜딩, 이벤트 훅, 스케줄러
│   ├── babipa_erp/doctype/   # 커스텀 DocType
│   ├── fixtures/             # export된 Custom Field/Property Setter/Workspace
│   ├── patches/              # 데이터 마이그레이션 스크립트
│   └── public/               # CSS/JS/로고 등 정적 자산
```

## 작업 시작 전 체크리스트 (모든 에이전트 공통)

- [ ] 이 변경이 코어 파일을 건드리는가? → 건드린다면 중단하고 Custom App 방식으로 재설계
- [ ] Server Script라면 import 문이 있는가? → 있다면 `frappe.` 네임스페이스로 치환
- [ ] 새 DocType/필드라면 fixtures에 등록했는가?
- [ ] HKMC 감사 대응 데이터(시험 이력, 트레이서빌리티)와 관련 있는가? → `hkmc-compliance` 에이전트 리뷰 필요
