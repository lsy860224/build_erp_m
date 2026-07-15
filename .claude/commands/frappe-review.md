---
description: frappe-reviewer 에이전트를 호출해 변경된 코드를 4단계(아키텍처/보안/RestrictedPython/GPL)로 검토한다
---

리뷰 대상: $ARGUMENTS (지정하지 않으면 현재 변경사항 전체를 대상으로 한다)

1. `git diff --name-only`로 변경된 파일 목록을 먼저 확인한다.
2. frappe-reviewer 에이전트에게 위임하여 4개 축으로 순서대로 점검한다:
   - 아키텍처 원칙 (코어 파일 미수정, 스키마 리네임 금지)
   - 보안 (권한 체크, SQL 인젝션, timeout, 민감정보 로그)
   - RestrictedPython/훅 정합성 (Server Script import, hooks.py 경로 유효성)
   - GPL v3 라이선스 준수 (상표 사용, 저작권 고지 유지)
3. 결과를 다음 형식으로 정리한다:
   ```
   ### 🔴 반드시 수정 (Blocking)
   ### 🟡 권장 사항
   ### ✅ 통과 항목
   ```
4. 🔴 Blocking 항목이 하나라도 있으면 배포/커밋을 진행하지 말라고 명시적으로 경고한다.
