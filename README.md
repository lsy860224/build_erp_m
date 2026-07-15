# build_erp_m — babipa_erp (ERPNext 커스텀 앱) 구축 프로젝트

자동차 전장품 1차 협력사(HKMC 대응)의 사내 ERP/MES/POP을 **ERPNext(Frappe) 기반**으로
self-host, 화이트라벨링하여 구축하는 프로젝트. 실제 개발 원칙과 서브에이전트 라우팅은
루트 [`CLAUDE.md`](CLAUDE.md)가 정의하며, 이 README는 저장소 전체의 지도 역할만 한다.

## 현재 단계

**Phase 1 — 로컬 개발 환경 구축 완료.** Docker Desktop(WSL2 백엔드) 위에 Frappe bench
컨테이너를 띄우고, ERPNext(version-16)와 커스텀 앱 `apps/babipa_erp/`를 실제로 스캐폴딩·설치
완료했다. 지금까지 확정된 것:

1. 기술 방향 확정 — ERPNext(Frappe) 기반, 커스텀 앱명 `babipa_erp` (2026.07.15, [`docs/decisions.md`](docs/decisions.md) 참조)
2. Claude Code 개발 툴킷 완성 — 서브에이전트 10개 + 슬래시커맨드 9개 + 스킬 7개 (`.claude/` 아래, 아래 §1 참조)
3. Git/GitHub 연결 완료 (`lsy860224/build_erp_m`)
4. 이력 관리 체계 신설 — 커밋-push 동기화 추적(`commit_log.md`), 정식 빌드 이후 시스템 조작 이력(`docs/build-log.md`), 위험 명령 차단(`.claude/settings.json`) — 아래 §4 참조
5. 로컬 개발 환경 구축 — Docker Desktop 설치, `frappe_docker`(sibling 디렉토리) 기반 bench 컨테이너 기동, `development.localhost` 사이트에 ERPNext 16.28.0 + `babipa_erp` 0.0.1 설치, 로그인·Setup Wizard 도달까지 브라우저로 검증 완료. 실행 방법·아키텍처 결정 근거는 [`docs/dev-environment.md`](docs/dev-environment.md) 참조

다음 단계는 요구사항수집 xlsx를 유관 부서에 배포해 실 데이터를 걷는 것과 병행해,
`babipa_erp`에 실제 DocType(시험 장비, ES 매트릭스 등) 설계를 시작하는 것.

## 디렉토리 구조

```
build_erp_m/
├── CLAUDE.md                       # 운영 지침(확정) — 세션마다 최상단에 로드됨
├── README.md                       # 이 문서 — 프로젝트 지도
├── commit_log.md                   # 자동 생성 — 로컬 커밋의 GitHub push 여부 추적 (§4)
├── .claude/                        # Claude Code가 실제로 인식하는 서브에이전트/커맨드/스킬
│   ├── settings.json                # 위험 명령 차단(deny) — §4
│   ├── agents/                     # 10개 — 아래 §1 참조
│   ├── commands/                   # 9개 — 슬래시커맨드
│   └── skills/                     # 7개 — 모델이 자동 판단해 로드
├── .githooks/
│   └── post-commit                 # 커밋 시 commit_log.md 자동 갱신 (§4)
├── scripts/
│   └── update-commit-log.sh        # commit_log.md 재생성 스크립트 (§4)
├── docs/
│   ├── decisions.md                 # 프로젝트 결정 이력 (계속 늘어나는 로그)
│   ├── gplv3-compliance.md          # GPLv3/ERPNext 라이선스·상표 준수 상세 가이드라인
│   ├── commit-push-policy.md        # 커밋 로그 메커니즘 + 커밋/Push 필수 규칙·절차·예외
│   ├── build-log.md                 # 정식 빌드 이후 시스템 조작 이력 (§4, 아직 항목 없음)
│   ├── app-directory-structure.md   # babipa_erp 앱 디렉토리 구조
│   ├── dev-environment.md           # 로컬 Docker+bench 개발 환경 실행법·아키텍처 결정 근거
│   └── research/                   # AI 딥리서치 보고서(참고자료, 미확정 문서 포함)
│       ├── ERPNext_및_Claude_Code_가이드.md            # 채택안의 근거자료
│       └── Python_ERP_시스템_설계(대안,미채택).md        # 검토 후 반려된 대안
├── 요구사항수집/                    # babipa_erp 설계 착수 전 부서별 데이터 요구사항 수집
│   ├── 데이터_요구사항_수집_방법론.md
│   └── 데이터요구사항수집_템플릿_ERP_MES_POP.xlsx        # 실제 배포용 산출물 (아직 미배포)
└── apps/babipa_erp/                 # 실제 커스텀 앱 코드 (2026.07.15 스캐폴딩 완료).
                                      # bench 컨테이너에 바인드 마운트되어 즉시 반영됨
```

> `frappe_docker`(bench/Docker 인프라)와 실제 Frappe 코어(`apps/frappe`, `apps/erpnext`)는 이
> 저장소 밖에 있다 — 위치와 이유는 `docs/dev-environment.md` 참조.

> `agents/`·`commands`·`skills/`는 원래 저장소 최상단에 있었으나 그 위치에서는
> Claude Code가 인식하지 못한다 — 2026.07.15 `.claude/` 아래로 이동해 실제로 작동하도록 수정.

## §1. `.claude/` 툴킷 구성

```
.claude/
├── agents/                    # 10개 서브에이전트
│   ├── frappe-architect.md        # DocType/데이터 모델 설계
│   ├── frappe-backend.md          # Python/hooks/Server Script
│   ├── frappe-frontend.md         # Client Script/Desk UI
│   ├── frappe-branding.md         # 화이트라벨 브랜딩
│   ├── frappe-integration.md      # 외부 시스템(REST/웹훅) 연동
│   ├── frappe-devops.md           # 배포/인트라넷/백업
│   ├── frappe-debugger.md         # 트러블슈팅
│   ├── frappe-reviewer.md         # 코드 리뷰/라이선스 점검
│   ├── frappe-qa.md               # 테스트
│   └── hkmc-compliance.md         # HKMC ES/SQ 감사 대응 검토
├── commands/                  # 9개 슬래시커맨드
│   ├── frappe-plan.md
│   ├── frappe-app-init.md
│   ├── frappe-doctype-create.md
│   ├── frappe-branding-setup.md
│   ├── frappe-integration-bridge.md
│   ├── frappe-deploy-intranet.md
│   ├── frappe-review.md
│   ├── frappe-test.md
│   └── frappe-debug.md
└── skills/                    # 7개 스킬 (모델이 자동으로 판단해 로드)
    ├── frappe-server-script-restrictions/SKILL.md   # RestrictedPython 함정 (가장 중요)
    ├── frappe-doctype-json/SKILL.md
    ├── frappe-hooks-reference/SKILL.md
    ├── frappe-rest-api-integration/SKILL.md
    ├── frappe-custom-app-structure/SKILL.md
    ├── frappe-whitelabel-branding/SKILL.md
    └── frappe-fixtures-patches/SKILL.md
```

## 사용 예시

```
/frappe-plan HKMC ES91500 대응용 커넥터 씰 변형 시험 데이터를 관리하고 싶어
/frappe-app-init babipa_erp
/frappe-doctype-create 시험 장비 마스터 — 장비명, 모델번호, 통신 프로토콜, 교정 만기일
/frappe-branding-setup 회사명 BABIPA, 컬러 #1a3c6e, 메뉴 한글화
/frappe-integration-bridge reliability-alt-toolkit(localhost:8001)에 Weibull 계산 요청
/frappe-deploy-intranet 서버 8코어/16GB, 인터넷 되는 스테이징 PC 있음
/frappe-review
/frappe-test Test Equipment
/frappe-debug 저장할 때 500 에러 나요
```

## 운영 원칙

코어 수정 금지, RestrictedPython 제약, GPLv3/ERPNext 상표 준수 가이드라인, Fixture
export 규칙, 빌드 주요사항 발생 시 commit+push 의무화 등 실제 운영 원칙은 중복 없이
[`CLAUDE.md`](CLAUDE.md) 한 곳에서만 관리한다 — 여기서는 반복하지 않는다.

## §2. 리서치/참고자료 (`docs/research/`)

이 프로젝트 착수 전 수행한 AI 딥리서치 보고서 2건. **운영 지침이 아니라 참고자료**이며,
실제 결정은 항상 `CLAUDE.md`가 우선한다.

| 문서 | 상태 | 요지 |
|---|---|---|
| `ERPNext_및_Claude_Code_가이드.md` | 채택안 근거자료 | ERPNext+Claude Code 통합 방법론(Docker 인프라, CLAUDE.md 설계, MariaDB MCP, 서브에이전트/스킬 설계) — `.claude/` 툴킷 설계에 반영됨 |
| `Python_ERP_시스템_설계(대안,미채택).md` | 검토 후 반려 | ERPNext 없이 Django+FastAPI로 처음부터 구축하는 대안 제안. 기각됐지만 MES/POP 현장 데이터(OPC UA/MQTT, ZPL 라벨, 로트 추적성) 설계는 참고 가치 있어 보존 |

## §3. 요구사항 수집 (`요구사항수집/`)

babipa_erp 설계에 들어가기 전, 생산/품질/자재 등 유관 부서로부터 실 데이터 요구사항을
걷기 위한 도구. **아직 배포 전(미실행) 단계.**

- `데이터_요구사항_수집_방법론.md` — 수집 방법론(정형/비정형 분류, 개인정보 처리 기준, 비기능 요구사항 등)
- `데이터요구사항수집_템플릿_ERP_MES_POP.xlsx` — 실제 배포용 Excel 템플릿

## §4. 이력 관리 체계

이 프로젝트는 두 종류의 이력을 성격이 다르다고 보고 분리해서 관리한다 — 하나는 "코드가
GitHub까지 안전하게 도달했는가"(커밋 로그), 다른 하나는 "실제 시스템에 무슨 조작을
했는가"(빌드 로그). 상세 정책은 [`docs/commit-push-policy.md`](docs/commit-push-policy.md) 참조.

| | `commit_log.md` | `docs/build-log.md` |
|---|---|---|
| 추적 대상 | 로컬 git 커밋의 GitHub push 여부 | bench 조작 등 시스템 상태 변경 이력 |
| 갱신 방식 | `scripts/update-commit-log.sh` 자동 재생성 (커밋 시 훅 자동 실행, **push 후엔 수동 1회 재실행 필요**) | 사람이 직접 표에 한 줄씩 추가 |
| 시작 시점 | 지금부터 | `bench new-app babipa_erp` 실행 시점부터 (현재는 비어있음) |
| 최초 설정 | clone 후 1회 `git config core.hooksPath .githooks` 실행 필요 | 별도 설정 불필요 |

`.claude/settings.json`은 `docs/research/ERPNext_및_Claude_Code_가이드.md` §7이 권고한
위험 명령 차단 목록(`bench drop-site`, `rm -rf`, `sudo`, `DROP DATABASE`,
`site_config.json`/`.env` 열람 등)을 deny 규칙으로만 추가한 것 — 기존 승인(allow/ask)
흐름은 건드리지 않았다.

## 참고 — 이 툴킷의 설계 배경

Frappe/ERPNext + Claude Code 조합은 이미 커뮤니티에서 검증된 패턴입니다
(`frappe-claude`, `Frappe_Claude_Skill_Package` 등 공개 프로젝트 존재). 이 툴킷은
그 구조를 참고하되, 귀사의 특수 요구사항(HKMC ES 표준 대응, 인트라넷 전용 배포,
reliability-alt-toolkit 연동, 화이트라벨 브랜딩)에 맞춰 처음부터 새로 작성한
독립적인 결과물입니다.
