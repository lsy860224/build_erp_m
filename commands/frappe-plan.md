---
description: 새 기능/DocType/연동 작업을 코딩 전에 먼저 계획하고 담당 에이전트를 배분한다
---

다음 요청에 대해 코드를 바로 작성하지 말고 먼저 계획을 세워라: $ARGUMENTS

1. 이 요청이 CLAUDE.md의 "절대 원칙"(코어 미수정, RestrictedPython 제약, GPL 준수 등)과
   충돌하는 부분이 있는지 먼저 점검한다.
2. 필요한 작업을 다음 카테고리로 분해한다: 데이터 모델(frappe-architect) / 백엔드
   (frappe-backend) / 프론트엔드(frappe-frontend) / 브랜딩(frappe-branding) / 외부연동
   (frappe-integration) / 배포(frappe-devops).
3. HKMC 감사 대상이 될 가능성이 있는 데이터(시험 이력, 트레이서빌리티 등)가 포함되면
   hkmc-compliance 에이전트 검토를 계획에 포함한다.
4. 각 항목을 표로 정리해 제시하고, 사용자 확인을 받은 뒤에만 실제 구현(다른 슬래시커맨드
   또는 서브에이전트 호출)으로 진행한다.

출력 형식:
| 순서 | 작업 | 담당 에이전트 | 비고 |
|---|---|---|---|
