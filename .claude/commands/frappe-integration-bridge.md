---
description: frappe-integration 에이전트를 호출해 외부 프로그램(예: reliability-alt-toolkit)과의 REST/웹훅 연동 코드를 생성한다
---

연동 요구사항: $ARGUMENTS (예: 외부 서버 주소/API 스펙, 연동 방향, 트리거 조건)

1. frappe-integration 에이전트에게 위임하여 연동 방식을 결정한다:
   - ERPNext → 외부 호출 / 외부 → ERPNext REST API / Webhook 중 적합한 것 선택
2. ERPNext → 외부 호출이면, `events/` 폴더에 timeout이 설정된 호출 함수와 실패 시
   `frappe.log_error` 처리를 포함한 코드를 생성한다.
3. 외부 → ERPNext 방향이면, 필요한 API Key 발급 절차와 최소 권한 Role 설계를 안내한다.
4. Webhook 방식이면 Desk UI 등록 절차(Doctype/Trigger/URL/전송 필드)를 단계별로 안내한다.
5. 모든 연동이 사내망(인트라넷) 안에서만 이루어지는지 최종 확인 문구를 포함한다.
6. 완료 후 frappe-qa 에이전트에게 "외부 연동 실패 시 동작" 테스트 케이스 작성을 제안한다.
