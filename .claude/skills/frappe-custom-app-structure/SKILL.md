---
name: frappe-custom-app-structure
description: 새 Frappe Custom App의 디렉토리 구조, bench 명령, 앱 생명주기(생성/설치/업데이트)를 다룰 때 사용.
---

# Custom App 구조 표준

## 생성/설치 명령

```bash
bench new-app babipa_erp
bench --site erp.internal install-app babipa_erp
bench --site erp.internal list-apps      # 설치 확인
```

## 표준 디렉토리 구조

```
babipa_erp/
├── license.txt
├── README.md
├── requirements.txt          # Python 의존성
├── package.json              # Node 의존성 (JS 빌드용)
├── setup.py
└── babipa_erp/
    ├── __init__.py
    ├── hooks.py               # 통합 지점 (frappe-hooks-reference 참조)
    ├── modules.txt
    ├── patches.txt            # 데이터 마이그레이션 순서 정의
    ├── babipa_erp/
    │   └── doctype/           # 커스텀 DocType들
    │       └── test_equipment/
    │           ├── test_equipment.json
    │           ├── test_equipment.py
    │           └── test_test_equipment.py
    ├── events/                 # doc_events에 연결되는 Python 함수
    ├── tasks/                  # scheduler_events에 연결되는 함수
    ├── patches/                # 실제 마이그레이션 스크립트
    ├── fixtures/                # export된 Custom Field/Workspace 등 JSON
    └── public/
        ├── css/
        ├── js/
        └── images/
```

## 개발 모드 vs 프로덕션

```bash
# 개발 사이트에서만
bench --site dev.local set-config developer_mode 1
bench --site dev.local clear-cache

# 프로덕션에서는 절대 켜지 않음 — UI에서 만든 스키마 변경이
# 파일로 저장되어 예기치 않게 배포될 수 있음
```

## 패치(마이그레이션) 작성

```python
# babipa_erp/patches/v1_0/create_default_workspace.py
import frappe

def execute():
    if not frappe.db.exists("Workspace", "Reliability Testing"):
        frappe.get_doc({
            "doctype": "Workspace",
            "name": "Reliability Testing",
            "label": "신뢰성 시험"
        }).insert()
```
`patches.txt`에 `babipa_erp.patches.v1_0.create_default_workspace` 등록 후
`bench migrate` 시 1회 실행됨 (재실행 방지를 위해 idempotent하게 작성).

## 버전관리 원칙

- 모든 코드/fixture는 Git에 커밋
- `.gitignore`에 `__pycache__/`, `*.pyc`, `node_modules/`, `.env` 포함
- 배포는 Git bundle 또는 Docker 이미지로 폐쇄망 반입 (frappe-devops 참조)
