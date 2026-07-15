# babipa_erp 앱 디렉토리 구조

`CLAUDE.md` 절대 원칙 #1("코어 미수정")의 상세 버전 — `bench new-app babipa_erp` 실행 후
실제로 만들어질 커스텀 앱 내부 구조를 미리 정의해 둔다. 아직 앱이 생성되지 않은 Phase 0
단계에서는 참고용 목표 구조다.

```
apps/babipa_erp/
├── babipa_erp/
│   ├── hooks.py              # 브랜딩, 이벤트 훅, 스케줄러
│   ├── babipa_erp/doctype/   # 커스텀 DocType
│   ├── fixtures/             # export된 Custom Field/Property Setter/Workspace
│   ├── patches/              # 데이터 마이그레이션 스크립트
│   └── public/               # CSS/JS/로고 등 정적 자산
```

- `apps/erpnext/`, `apps/frappe/` — ERPNext/Frappe 코어. 절대 직접 수정하지 않는다.
- `apps/babipa_erp/` — 모든 커스터마이징이 이루어지는 유일한 위치.
