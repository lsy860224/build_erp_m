# babipa_erp 앱 디렉토리 구조

`CLAUDE.md` 절대 원칙 #1("코어 미수정")의 상세 버전. 2026.07.15 `bench new-app babipa_erp`로
실제 생성 완료 — 이 문서는 이제 목표 구조가 아니라 실제 구조다.

```
apps/babipa_erp/
├── babipa_erp/
│   ├── hooks.py              # 브랜딩, 이벤트 훅, 스케줄러
│   ├── babipa_erp/doctype/   # 커스텀 DocType
│   ├── fixtures/             # export된 Custom Field/Property Setter/Workspace
│   ├── patches/              # 데이터 마이그레이션 스크립트
│   └── public/               # CSS/JS/로고 등 정적 자산
```

- `apps/erpnext/`, `apps/frappe/` — ERPNext/Frappe 코어. **이 저장소(`build_erp_m`)에는 존재하지
  않는다** — bench 컨테이너 안, 네이티브 Docker 볼륨(`frappe-bench-data`)에만 있고 Windows에는
  바인드 마운트되지 않는다. 절대 직접 수정하지 않는다는 원칙은 그대로 유지.
- `apps/babipa_erp/` — 모든 커스터마이징이 이루어지는 유일한 위치. 컨테이너의
  `/workspace/development/frappe-bench/apps/babipa_erp`에 바인드 마운트돼 있어 여기서 편집한
  내용이 곧바로 bench에 반영된다. `--no-git`으로 생성해 자체 `.git`이 없다 — 버전관리는
  `build_erp_m` 저장소가 그대로 담당한다.
- bench/Docker 인프라 자체(frappe_docker, 개발 컨테이너 구성, 실행 명령)는
  `docs/dev-environment.md` 참조.
