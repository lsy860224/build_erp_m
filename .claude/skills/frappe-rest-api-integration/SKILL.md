---
name: frappe-rest-api-integration
description: ERPNext REST API를 외부 프로그램/장비와 연동하거나, ERPNext에서 외부 API를 호출할 때 사용. 인증, 엔드포인트 규칙, 웹훅 설정을 포함.
---

# Frappe REST API 연동 패턴

## ERPNext 표준 REST 엔드포인트

```
GET    /api/resource/<DocType>              # 목록 조회
GET    /api/resource/<DocType>/<name>       # 단건 조회
POST   /api/resource/<DocType>               # 생성
PUT    /api/resource/<DocType>/<name>       # 수정
DELETE /api/resource/<DocType>/<name>       # 삭제
POST   /api/method/<python.path.to.function> # @frappe.whitelist() 함수 직접 호출
```

## 인증 (API Key/Secret)

Desk UI → 사용자 프로필 → API Access → Generate Keys

```bash
curl -X GET "http://erp.internal/api/resource/Test Equipment" \
  -H "Authorization: token <api_key>:<api_secret>"
```

- 장비/외부 프로그램마다 **별도 사용자 + 별도 API Key**를 발급하고, Role 권한을
  필요한 최소 수준(예: 특정 DocType Create만)으로 제한한다.

## 필터링 쿼리 예시

```bash
curl -G "http://erp.internal/api/resource/Test Equipment" \
  -H "Authorization: token <key>:<secret>" \
  --data-urlencode 'filters=[["calibration_due_date","<","2026-12-31"]]' \
  --data-urlencode 'fields=["name","equipment_name","calibration_due_date"]'
```

## Python(외부 프로그램)에서 호출

```python
import requests

resp = requests.post(
    "http://erp.internal/api/resource/Test Parameter Set",
    headers={"Authorization": f"token {API_KEY}:{API_SECRET}"},
    json={"equipment": "TEQ-2026-00012", "parameter_name": "temperature", "value": 85.3},
    timeout=10
)
resp.raise_for_status()
```

## Webhook (ERPNext → 외부, 코드 없이 Desk UI에서 설정)

Settings → Webhook:
- Doctype, Trigger(on_submit 등), Request URL, 전송할 필드 선택
- HMAC 시크릿으로 서명 검증 가능 (외부 서버에서 위조 요청 방지)

## 체크리스트

- [ ] timeout을 설정했는가? (미설정 시 워커 블로킹 위험)
- [ ] API Key 권한이 필요 이상으로 넓지 않은가?
- [ ] 사내망 밖으로 나가는 호출이 없는가? (인트라넷 전용 요구사항)
- [ ] 실패 시 재시도/로깅 로직이 있는가?
