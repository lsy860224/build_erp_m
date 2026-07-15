---
description: frappe-architect 에이전트를 호출해 새 DocType JSON과 기본 컨트롤러를 생성한다
---

생성할 DocType 요구사항: $ARGUMENTS

1. frappe-architect 에이전트에게 위임하여 DocType JSON 스켈레톤을 설계한다.
2. 기존 표준 DocType(Asset, Item, Quality Inspection 등)으로 대체 가능한지 먼저 검토하고,
   대체 불가 시에만 신규 생성으로 진행한다.
3. 설계가 확정되면:
   - `<app>/<app>/doctype/<doctype_snake_case>/<doctype_snake_case>.json`
   - `<app>/<app>/doctype/<doctype_snake_case>/<doctype_snake_case>.py` (frappe-backend
     스타일의 기본 Document 클래스, validate() 스텁 포함)
   - `<app>/<app>/doctype/<doctype_snake_case>/test_<doctype_snake_case>.py` (frappe-qa
     스타일의 최소 테스트 1개)
   세 파일을 함께 생성한다.
4. 감사 대상 데이터일 가능성이 있으면(트레이서빌리티, 시험이력 등) hkmc-compliance 에이전트
   검토를 요청하고 결과를 반영한다.
5. 완료 후 `bench migrate` 명령과, Fixture export가 필요한지 여부를 안내한다.
