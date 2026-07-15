---
description: frappe-debugger 에이전트를 호출해 에러 로그를 분석하고 원인을 좁혀 수정안을 제시한다
---

증상 설명: $ARGUMENTS

1. frappe-debugger 에이전트에게 위임하여 다음 순서로 진행한다:
   - `sites/[사이트]/logs/web.error.log`, `worker.error.log` 최근 로그 확인
   - 흔한 원인 체크리스트(Server Script import, 권한 누락, Fixture 미등록,
     developer_mode 미설정, timeout 미설정 등)와 대조
   - `bench console`에서 최소 재현 시도
2. 보고 형식을 따른다: 증상 → 로그 근거 → 원인 → 수정 코드(파일 경로 포함) → 재발 방지책
3. 수정이 완료되면 frappe-reviewer에게 리뷰를, frappe-qa에게 회귀 테스트 추가를 제안한다.
