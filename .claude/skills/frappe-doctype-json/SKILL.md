---
name: frappe-doctype-json
description: 새 DocType JSON 정의, 필드타입 선택, naming_rule, permission 배열 작성 시 사용.
---

# DocType JSON 설계 패턴

## 필드타입 선택 기준

| 데이터 성격 | fieldtype |
|---|---|
| 단문 텍스트 | `Data` |
| 장문 텍스트 | `Text` / `Small Text` |
| 다른 DocType 단일 참조 | `Link` (options에 대상 DocType명) |
| 반복되는 하위 행 데이터 | `Table` (Child DocType 별도 정의 필요) |
| 고정된 선택지 | `Select` (options는 개행 구분 문자열) |
| 계산되어 자동 채워지는 값 | `Read Only` + `fetch_from: "link_field.source_field"` |
| 파일 첨부 | `Attach` / `Attach Image` |
| 제출 여부로 상태 관리 필요 | DocType 최상위에 `"is_submittable": 1` |

## naming_rule 선택

- 순번 자동 채번: `"naming_rule": "Expression", "autoname": "TEQ-.YYYY.-.#####"`
- 특정 필드값을 그대로 문서명으로: `"naming_rule": "By fieldname", "autoname": "field:equipment_serial"`

## 기본 골격

```json
{
  "doctype": "DocType",
  "name": "<DocType 표시명>",
  "module": "<커스텀 앱 모듈명>",
  "custom": 0,
  "naming_rule": "Expression",
  "autoname": "PREFIX-.YYYY.-.#####",
  "is_submittable": 0,
  "track_changes": 1,
  "fields": [
    {"fieldname": "example_field", "fieldtype": "Data", "label": "예시 필드", "reqd": 1}
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0}
  ]
}
```

## 체크리스트

- [ ] `module`이 표준 ERPNext 모듈이 아니라 커스텀 앱 모듈로 지정됐는가?
- [ ] `custom: 0`인가? (**주의**: `custom: 1`은 Desk UI로 만드는, 파일시스템 컨트롤러가 없는
      "Custom DocType" 전용 플래그다. 이 값을 1로 두면 `frappe.model.base_document.get_controller()`가
      **무조건 base `Document` 클래스를 반환**하고 앱 코드의 `<doctype>.py` 컨트롤러 클래스를
      아예 import하지 않는다 — `validate()` 등 커스텀 로직이 조용히 실행되지 않는 상태가 된다.
      2026.07.20 Equipment/Equipment Daily Inspection/Production Downtime Log 3개 DocType에서
      `custom: 1`로 만들었다가 컨트롤러 로직이 전혀 동작하지 않는 것을 직접 확인 후 이 항목을
      정정했다. 앱 폴더(`doctype/<name>/<name>.py`)에 실제 컨트롤러 파일을 두는 이번 프로젝트
      방식에서는 항상 `custom: 0`(또는 필드 생략, 기본값 0))
- [ ] 감사·이력 추적이 필요하면 `track_changes: 1`을 켰는가?
- [ ] 제출형 문서(`is_submittable`)라면 permissions에 `submit`/`cancel/amend` 권한도 명시했는가?
