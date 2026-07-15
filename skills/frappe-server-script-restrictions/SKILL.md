---
name: frappe-server-script-restrictions
description: Server Script(Desk UI에서 작성하는 Python)를 작성하거나 리뷰할 때 항상 사용. RestrictedPython 샌드박스 제약(import 차단 등)으로 인한 AI 생성 코드의 #1 실패 원인을 방지한다.
---

# Server Script는 RestrictedPython 샌드박스에서 실행된다

## 핵심 규칙

Frappe Desk UI의 **Server Script** DocType으로 작성하는 코드는 RestrictedPython
샌드박스 안에서 돌아간다. **모든 `import` 문이 차단**되며, 에러 메시지 없이 조용히
실패하는 경우가 많아 디버깅이 어렵다.

이 제약은 **Server Script에만 적용**되며, Custom App 내부의 일반 `.py` 파일
(Document Controller, hooks.py, `events/*.py`)에는 적용되지 않는다. 이 둘을 반드시
구분해서 작성한다.

## 잘못된 예 / 올바른 예

```python
# ❌ Server Script에서 실패
from frappe.utils import nowdate
import json
today = nowdate()
data = json.loads(payload)

# ✅ Server Script에서 정상 동작
today = frappe.utils.nowdate()
data = frappe.parse_json(payload)
```

## 자주 쓰는 frappe 네임스페이스 대체표

| 하고 싶은 것 | ❌ import 방식 | ✅ frappe 네임스페이스 |
|---|---|---|
| 오늘 날짜 | `from frappe.utils import nowdate` | `frappe.utils.nowdate()` |
| JSON 파싱 | `import json; json.loads(x)` | `frappe.parse_json(x)` |
| 날짜 차이 계산 | `from frappe.utils import date_diff` | `frappe.utils.date_diff(a, b)` |
| 문서 조회 | `import frappe` (이건 허용됨, frappe 자체는 이미 전역 제공) | `frappe.get_doc(...)` |
| HTTP 요청 | `import requests` | **불가** — Server Script로는 외부 HTTP 호출 자체가 막혀있음. Custom App의 `events/*.py`로 옮겨서 `doc_events` 훅으로 처리 |

## 판단 기준: 이 코드를 어디에 작성해야 하는가

- 단순 필드 검증, 값 계산, 알림 → Server Script로 충분 (단, 위 제약 준수)
- 외부 라이브러리 필요(requests, pandas 등), 복잡한 로직, 버전관리 필요 →
  **Custom App 내부 `.py` 파일 + hooks.py 등록**으로 작성 (일반 Python, import 자유)

## 검증 방법

코드 작성 후 아래 정규식으로 자기 점검:
```bash
grep -n "^import\|^from" server_script_draft.py
```
결과가 하나라도 나오면 Server Script 방식이 아니라 Custom App 방식으로 전환한다.
