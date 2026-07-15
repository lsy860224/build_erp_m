# Frappe/ERPNext 전용 Claude Code 툴킷

babipa_erp(사내 ERPNext 커스텀 앱) 개발을 위한 CLAUDE.md + 서브에이전트(10개) +
슬래시커맨드(9개) + 스킬(7개) 모음입니다. Zipai/AI 에이전트 회사 아키텍처에서 쓰신 것과
동일한 "루트 CLAUDE.md → 서브에이전트 라우팅 → 슬래시커맨드" 패턴을 따릅니다.

## 구성

```
frappe-erpnext-toolkit/
├── CLAUDE.md                  # 루트 오케스트레이터 (프로젝트 원칙, 라우팅 규칙)
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

## 설치 방법

### 방법 A — 이 프로젝트(babipa_erp 개발 레포)에만 적용

레포 루트에 그대로 복사:

```bash
cp -r frappe-erpnext-toolkit/CLAUDE.md   your-repo/CLAUDE.md
cp -r frappe-erpnext-toolkit/agents      your-repo/.claude/agents
cp -r frappe-erpnext-toolkit/commands    your-repo/.claude/commands
cp -r frappe-erpnext-toolkit/skills      your-repo/.claude/skills
```

### 방법 B — 모든 프로젝트에서 전역으로 사용

```bash
cp -r frappe-erpnext-toolkit/agents/*    ~/.claude/agents/
cp -r frappe-erpnext-toolkit/commands/*  ~/.claude/commands/
cp -r frappe-erpnext-toolkit/skills/*    ~/.claude/skills/
```
(CLAUDE.md는 프로젝트마다 다를 수 있으므로 전역 적용은 권장하지 않습니다. 프로젝트별로
방법 A를 쓰시고, CLAUDE.md의 앱 이름(`babipa_erp`)만 실제 값으로 바꾸세요.)

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

## 시작하기 전 필수 확인 (CLAUDE.md 요약)

1. ERPNext/Frappe **코어 파일은 절대 직접 수정하지 않는다** — 모든 커스터마이징은
   Custom App(`babipa_erp`) 안에서.
2. **Server Script는 import 전부 차단** — `frappe.` 네임스페이스로만 접근.
3. 표준 DocType/필드는 **리네임 금지**, 라벨만 Translation으로 변경.
4. **GPL v3**: 사내 전용은 소스 공개 의무 없음. "ERPNext" 이름/로고는 상표라 제품명에
   못 씀. 제3자(AU Co. 등) 배포 계획이 생기면 재확인 필요.
5. Custom Field/Workspace 등은 반드시 **Fixture로 export**해 Git 버전관리.

## 참고 — 이 툴킷의 설계 배경

Frappe/ERPNext + Claude Code 조합은 이미 커뮤니티에서 검증된 패턴입니다
(`frappe-claude`, `Frappe_Claude_Skill_Package` 등 공개 프로젝트 존재). 이 툴킷은
그 구조를 참고하되, 귀사의 특수 요구사항(HKMC ES 표준 대응, 인트라넷 전용 배포,
reliability-alt-toolkit 연동, 화이트라벨 브랜딩)에 맞춰 처음부터 새로 작성한
독립적인 결과물입니다.
