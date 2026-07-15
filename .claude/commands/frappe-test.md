---
description: frappe-qa 에이전트를 호출해 대상 DocType/기능의 테스트를 작성하고 실행 명령을 안내한다
---

테스트 대상: $ARGUMENTS (예: DocType 이름, 또는 방금 작성한 기능)

1. frappe-qa 에이전트에게 위임하여 다음 케이스를 반드시 포함한 테스트를 작성한다:
   - 정상 경로(happy path)
   - 검증 실패 경로 (validate()에서 막아야 하는 조건)
   - 권한 경계 (Role 없는 사용자 접근 차단)
   - 외부 연동이 있다면 실패 시 전체 플로우가 멈추지 않는지
2. 테스트 파일을 Frappe 관례 경로(`<app>/<app>/doctype/<doctype>/test_<doctype>.py`)에 생성한다.
3. 실행 명령을 제시한다:
   ```
   bench --site [사이트명] run-tests --doctype "[DocType명]"
   ```
4. 테스트가 RestrictedPython 제약이나 Fixture 미등록 문제로 실패할 가능성이 있으면
   frappe-debugger 에이전트에게 넘길 것을 제안한다.
