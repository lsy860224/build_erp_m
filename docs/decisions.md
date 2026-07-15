# 결정 이력

이 프로젝트의 주요 결정을 시간순으로 기록한다. `CLAUDE.md`가 "지금 지켜야 할 규칙"이라면,
이 파일은 "왜 그 규칙이 생겼는가"를 설명하는 배경 로그다. 계속 늘어나는 성격이라 별도
파일로 분리했다 — `CLAUDE.md`가 비대해지는 것을 막기 위함.

| 날짜 | 결정 | 근거 |
|---|---|---|
| 2026.07.15 | ERPNext(Frappe) 기반 확정, Django+FastAPI 자체 구축안 반려 | 리서치 2건 비교 검토. 근거·반려 사유는 `docs/research/Python_ERP_시스템_설계(대안,미채택).md` 상단 배너 참조 |
| 2026.07.15 | `agents/`·`commands/`·`skills/`를 저장소 최상단에서 `.claude/` 하위로 이동 | 기존 위치는 Claude Code가 인식하지 못해 서브에이전트·슬래시커맨드·스킬 10+9+7개가 전부 비활성 상태였음 |
| 2026.07.15 | `commit_log.md`(로컬-GitHub 커밋 동기화 추적) + `docs/build-log.md`(정식 빌드 이후 시스템 조작 이력) 체계 신설 | 커밋이 실제로 push됐는지 매번 눈으로 확인해야 했던 문제 해소, 향후 bench 조작 이력의 감사 추적성 확보 |
| 2026.07.15 | GPLv3/ERPNext 라이선스·상표 준수 가이드라인 명문화 + 빌드 주요사항 발생 시 commit+push를 사용자 승인 없이 수행하도록 사전 승인 | ERPNext 기반 빌드 착수 확정에 따라 실수로 라이선스/상표를 위반하지 않도록 지금 단계부터 습관화, 빌드 이력이 매번 push 확인을 기다리지 않고 즉시 GitHub에 반영되도록 |
| 2026.07.15 | `CLAUDE.md`를 슬림화 — 결정 이력·GPLv3 상세 가이드라인·커밋/빌드 로그 절차·앱 디렉토리 구조를 `docs/`로 분리하고 경로 참조만 남김 | `CLAUDE.md`는 매 세션 최상단에 로드되는 파일이라 비대해지면 토큰 낭비·주의 분산(Attention Dilution)이 생김 — "매 순간 반드시 지켜야 하는 핵심 규칙"과 "배경/절차/성장하는 로그"를 분리 |
| 2026.07.15 | 요구사항 수집 배포보다 기술 인프라(Docker+bench+babipa_erp 스캐폴딩)를 먼저 진행 | 사용자 확정(질문으로 확인) — 업무 데이터 수집을 기다리지 않아도 되는 병렬 가능 작업이라 판단 |
| 2026.07.15 | `frappe_docker`(공식, MIT)를 `build_erp_m` 밖 sibling 디렉토리 `E:\...\00. Claude Code\frappe_docker`에 클론, git 이력 분리 | 빌드 도구이지 우리 저작물이 아님. `apps/babipa_erp`만 `build_erp_m`에 바인드 마운트해 실제 소스는 이 저장소가 버전관리 |
| 2026.07.15 | 개발 컨테이너 볼륨을 `frappe-bench-data`(네이티브 Docker 볼륨) + `apps/babipa_erp`(Windows 바인드 마운트)로 분리 | Windows 호스트 경로 바인드 마운트가 심볼릭 링크·chmod를 지원하지 않아 `bench init`/`git init`이 실패하는 문제 회피. 근거·재현 방법은 `docs/dev-environment.md` |
| 2026.07.15 | Frappe/ERPNext `version-16`(최신 안정) 채택, `develop`(v17, 미출시) 배제 | `bench init` 기본값(`--frappe-branch` 미지정)이 `develop`로 떨어져 erpnext 설치가 깨지는 것을 발견 → 안정 브랜치 명시로 수정 |
| 2026.07.15 | `babipa_erp`을 `bench new-app --no-git`으로 생성 | 자체 `.git`을 만들면 build_erp_m 안에 nested repo가 생기는 문제 + Windows 바인드 마운트의 chmod 실패 문제를 동시에 회피. 버전관리는 build_erp_m 저장소가 그대로 담당 |
