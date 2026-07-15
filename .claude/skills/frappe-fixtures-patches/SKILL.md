---
name: frappe-fixtures-patches
description: Custom Field, Property Setter, Workspace 등 UI에서 만든 변경을 버전관리하거나(Fixture), 데이터 마이그레이션 스크립트(Patch)를 작성할 때 사용.
---

# Fixtures vs Patches — 언제 무엇을 쓰는가

| 목적 | 도구 |
|---|---|
| 표준 DocType에 커스텀 필드 추가한 걸 Git으로 관리 | **Fixture** |
| Workspace/Print Format/Custom DocType 설정을 배포 시 자동 반영 | **Fixture** |
| 기존 데이터를 일괄 변환/보정 (1회성 스크립트) | **Patch** |
| 신규 사이트 설치 시 초기 데이터(부서 코드, 기본 설정값 등) 생성 | **Patch** |

## Fixture 사용법

`hooks.py`에 export 대상 등록:

```python
fixtures = [
    {"dt": "Custom Field", "filters": [["dt", "in", ["Quality Inspection", "Asset"]]]},
    {"dt": "Property Setter", "filters": [["doc_type", "=", "Sales Order"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Babipa Erp"]]}
]
```

```bash
# Desk UI에서 만든 커스터마이징을 JSON 파일로 내보내기
bench --site erp.internal export-fixtures

# 다른 사이트(또는 재설치 시)에 반영
bench --site new-site.internal migrate
```

- export된 JSON은 `<app>/<app>/fixtures/`에 저장되며 반드시 Git 커밋 대상.
- **필터를 걸지 않으면 전체 시스템의 모든 Custom Field가 다 export되어 노이즈가 심해진다** —
  반드시 자기 앱 관련 항목만 필터링.

## Patch 사용법

```python
# babipa_erp/patches/v1_0/set_default_equipment_status.py
import frappe

def execute():
    frappe.db.set_value(
        "Test Equipment", {"status": ""}, "status", "Active"
    )
```

`patches.txt`에 등록:
```
babipa_erp.patches.v1_0.set_default_equipment_status
```

### Patch 작성 원칙

- **Idempotent(멱등)하게 작성** — 여러 번 실행돼도 결과가 같아야 함 (재실행 사고 방지)
- 대량 데이터 변경 전에는 반드시 스테이징에서 먼저 검증
- `patches.txt`의 순서가 실행 순서 — 의존관계가 있으면 순서 주의

## 실행

```bash
bench --site erp.internal migrate
```
`migrate`는 (1) 스키마 변경 반영 (2) patches.txt 순서대로 미실행 패치 실행 (3) fixture
재적용을 한 번에 처리한다.
