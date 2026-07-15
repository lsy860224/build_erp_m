---
name: frappe-hooks-reference
description: hooks.py 작성 시 사용 — 브랜딩, doc_events, scheduler_events, doctype_js, fixtures 등 통합 지점 설정.
---

# hooks.py 핵심 훅 레퍼런스

`hooks.py`는 Custom App이 Frappe/ERPNext의 여러 지점에 개입하는 유일한 진입점이다.

## 브랜딩

```python
app_name = "babipa_erp"
app_title = "BABIPA MES"
app_publisher = "BABIPA"
app_logo_url = "/assets/babipa_erp/images/logo.png"
app_include_css = "/assets/babipa_erp/css/theme.css"
app_include_js = "/assets/babipa_erp/js/global.js"
```

## 문서 이벤트 (doc_events)

특정 DocType의 생명주기(저장/제출/취소 등)에 개입:

```python
doc_events = {
    "Quality Inspection": {
        "on_submit": "babipa_erp.events.reliability.notify_test_result",
        "validate": "babipa_erp.events.reliability.check_calibration"
    },
    "*": {  # 모든 DocType 공통
        "on_update": "babipa_erp.events.audit.log_change"
    }
}
```

## 스케줄러 이벤트

```python
scheduler_events = {
    "hourly": ["babipa_erp.tasks.sync_equipment_status"],
    "daily": ["babipa_erp.tasks.check_calibration_expiry"],
    "cron": {
        "0 2 * * *": ["babipa_erp.tasks.nightly_backup_check"]
    }
}
```
등록 후 반드시 `bench migrate` 실행해야 스케줄러에 반영됨.

## Client Script 등록 (doctype_js)

```python
doctype_js = {
    "Test Equipment": "public/js/test_equipment.js",
    "Quality Inspection": "public/js/quality_inspection_ext.js"
}
```

## Fixture (커스터마이징 영속화)

Custom Field, Property Setter, Workspace 등 Desk UI에서 만든 변경을 Git으로
버전관리하려면 반드시 fixtures에 등록:

```python
fixtures = [
    {"dt": "Custom Field", "filters": [["dt", "in", ["Quality Inspection", "Asset"]]]},
    {"dt": "Property Setter", "filters": [["doc_type", "=", "Sales Order"]]},
    {"dt": "Workspace", "filters": [["name", "=", "Reliability Testing"]]}
]
```
등록 후 `bench --site [사이트] export-fixtures`로 JSON 파일 생성 → Git 커밋.

## 필요한 다른 앱 자동 설치 (required_apps)

```python
required_apps = ["erpnext"]
```

## 자주 하는 실수

- `scheduler_events`/`doc_events` 등록 후 `bench migrate`를 안 돌려서 반영이 안 되는 경우
- Fixture 등록을 빼먹고 Desk UI에서만 커스터마이징해서, 다음 배포 시 변경사항이 사라지는 경우
- `doc_events`에 등록한 함수 경로에 오타가 있어도 즉시 에러가 안 나고 조용히 무시되는 경우
  (반드시 `frappe.get_attr("경로")`로 사전 검증 권장)
