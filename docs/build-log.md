# Build Log — babipa_erp 시스템 동작 이력

정식 빌드(= `bench new-app babipa_erp` 이후 실제 Frappe 인스턴스에 대한 조작) 시작 시점부터,
시스템 상태를 변경하는 작업을 이 파일에 기록한다. Frappe 자체의 런타임 로그
(`sites/*/logs/`, git 추적 대상 아님)와는 별개로, "누가 언제 무엇을 했고 결과가 어땠는가"를
사람이 읽을 수 있는 히스토리로 남기는 것이 목적이다 — 감사 대응(SQ/HKMC)과 장애 발생 시
원인 추적에 그대로 쓸 수 있다.

## 기록 대상 (트리거)

다음 작업을 실행한 직후 반드시 아래 "이력" 표에 한 줄을 추가한다:

- `bench new-app` / `bench get-app` / `bench install-app` / `bench uninstall-app`
- `bench --site * migrate` / `bench --site * set-config`
- DocType/Custom Field/Property Setter 등 스키마 변경 후 `bench export-fixtures`
- 배포·재기동(`bench restart`, Docker 컨테이너 재기동/재빌드)
- `bench backup` 및 복구 작업
- 그 외 되돌리기 어렵거나 여러 명에게 영향이 가는 시스템 상태 변경

일상적인 코드 편집(Python 함수 수정, 프론트엔드 스타일 조정 등)은 기록 대상이 아니다 —
git 커밋 이력으로 충분하다.

## 기록 형식

| 날짜/시각 | 작업자 | 명령/작업 | 대상(사이트/앱) | 결과 | 비고 |
|---|---|---|---|---|---|
| 2026-08-01 10:00 (예시) | Claude Code | `bench new-app babipa_erp` | - | 성공 | 최초 앱 스캐폴딩 |

- **작업자**: 실제 실행한 주체 (사람 이름 또는 "Claude Code" — 세션에서 대신 실행한 경우)
- **결과**: 성공 / 실패(원인 요약) / 롤백함
- 실패했거나 롤백한 경우 비고에 원인과 후속 조치를 반드시 남긴다

## 이력

| 날짜/시각 | 작업자 | 명령/작업 | 대상(사이트/앱) | 결과 | 비고 |
|---|---|---|---|---|---|
| 2026-07-15 | Claude Code | `bench init --frappe-branch version-16 frappe-bench` | - | 성공 | 최초 시도는 `--frappe-branch` 미지정으로 `develop`(v17)로 초기화돼 erpnext 설치 불가 → 재시도. 상세 원인은 `docs/dev-environment.md` |
| 2026-07-15 | Claude Code | `bench new-site development.localhost` | development.localhost | 성공 | admin 비밀번호 `admin`(로컬 전용 기본값) |
| 2026-07-15 | Claude Code | `bench --site development.localhost set-config developer_mode 1` | development.localhost | 성공 | |
| 2026-07-15 | Claude Code | `bench get-app --branch version-16 erpnext` + `install-app erpnext` | development.localhost | 성공 | erpnext 16.28.0 |
| 2026-07-15 | Claude Code | `bench new-app --no-git babipa_erp` + `install-app babipa_erp` | development.localhost | 성공 | 최초 앱 스캐폴딩. `--no-git`으로 생성(버전관리는 build_erp_m 저장소가 담당) |
| 2026-07-15 (추정, 2026-07-20 감사 중 발견·소급 기록) | Claude Code (당시 세션, 브라우저 Setup Wizard 진행 추정) | Setup Wizard 완료 — Company `BABIPA`·`BABIPA (Demo)` 생성(국가 Korea, 통화 KRW, Chart of Accounts `Standard`, 계정 각 94건/95건), Fiscal Year `2026`(2026-01-01~2026-12-31) 생성, `Global Defaults.default_company = BABIPA` 설정 | development.localhost | 성공(추정 — 직접 목격 아님) | 원 세션에서 build-log 기록이 누락됨. 2026-07-20 회계모듈 점검 중 `bench mariadb` 직접 조회로 결과 상태만 사후 확인, 정확한 조작 순서(UI 클릭 경로 등)는 재구성 불가. `BABIPA (Demo)` 생성 경위·존치 여부는 미결정(후속 확인 필요) |
| 2026-07-15 | Claude Code | Language `ko` 레코드 `enabled=1`로 수정, Administrator 사용자 language=`ko` 설정 | development.localhost | 성공 | Setup Wizard의 언어 선택 위젯은 "완역" curated 목록이라 한국어가 안 보였을 뿐, Language 자체는 이미 존재 |
| 2026-07-15 | Claude Code | 표준 DocType 이름 425개 + 공통 액션/상태 단어 68개 한국어 Translation 레코드 추가(총 504개) + `bench export-fixtures --app babipa_erp` | development.localhost | 성공 | Frappe 코어 6,225개 미번역 문자열 중 고빈도 노출 계층(DocType명·Save/Submit/Status 등)만 우선 처리. DocType 폼 내부 필드 라벨은 별도의 더 큰 계층으로 미처리 |
| 2026-07-15 | Claude Code | Item/Customer/Supplier/Employee/Sales Order/Purchase Order 6개 DocType 필드 라벨 129개 한국어 Translation 추가(총 633개) + "Item" 기존 오역("목") "품목"으로 override | development.localhost | 성공 | 마스터/거래 데이터 중 실사용 빈도가 가장 높은 6개부터 우선 처리. 나머지 DocType 필드 라벨은 후속 요청 시 확대 |
| 2026-07-15 | Claude Code | Frappe 코어 문구 11개 한국어 Translation 레코드 추가(Home·Notification·Search 등) + `bench export-fixtures --app babipa_erp` | development.localhost | 성공 | ERPNext 앱 문구는 이미 자체 ko 번역(5,848개) 보유, Frappe 코어만 상류에 ko 번역이 없어 직접 채움. `apps/babipa_erp/babipa_erp/fixtures/translation.json`으로 export, `hooks.py`에 `fixtures` 훅 신설 |
| 2026-07-15 | Claude Code | Manufacturing(조작→제조)·Branch(나뭇가지→지점)·Stock Settings(기본 설정→재고 설정) 오역 override | development.localhost | 성공 | 문서 작성 중 발견한 개별 오역을 즉시 수정 |
| 2026-07-15 | Claude Code | 807개 표준 DocType 이름 전체 한국어 번역 전수 점검 → 18건 오역 override(총 655개) | development.localhost | 성공 | Stock Entry(주식 입력→재고 전표), BOM(봄→BOM), Asset(유산→자산), Quotation(인용→견적), Journal Entry(일지 항목→분개 전표) 등. 상세는 커밋 `7e3cfcf` 참조 |
| 2026-07-15 | Claude Code | 전체 DocType 필드 라벨 중복 사용(2회 이상) 522개 한국어 Translation 추가(517건 신규, 총 1,172개) | development.localhost | 성공 | 4,355개 유니크 필드 라벨 중 미번역 2,203개를 재사용 빈도순 정렬 후 상위 522개(전체 노출의 약 54%) 우선 처리. 1회만 쓰이는 나머지 1,681개는 보류 |
| 2026-07-15 | Claude Code | Frappe 코어 버튼/다이얼로그/메시지 문구 244개 한국어 Translation 추가(총 1,416개) | development.localhost | 성공 | `bench get-untranslated`로 뽑은 미번역 목록에서 짧은 명령형 문구만 필터링해 처리. 통합설정 전용 기술 용어(OpenLDAP, StartTLS 등)는 노출 빈도 낮아 제외 |
| 2026-07-16 | Claude Code | 보류했던 1회성 필드 라벨 1,681개 전량 한국어 Translation 추가(1,603건 신규+정리 4건, 총 3,023개) | development.localhost | 성공 | 3개 배치로 나눠 삽입(517+744+342) 후 대소문자 케이스 차이로 남은 33건 중 4건 정리. System Settings·LDAP·OAuth·감가상각 등 남은 필드 라벨 전량 커버. 상세는 커밋 `b3eddf8` 참조 |
| 2026-07-16 | Claude Code | 남은 버튼/다이얼로그/메시지 문구 2,117개 한국어 Translation 추가(4개 배치, 총 5,140개) | development.localhost | 성공 | Frappe 코어 미번역 목록에서 코드 식별자·포맷 토큰·hex 노이즈를 걸러내고 실제 UI 문구만 처리. `{0}`/`{1}` 플레이스홀더가 있는 에러 메시지는 어순 오역 위험으로 의도적으로 제외. 상세는 커밋 `724aecc` 참조 |
| 2026-07-20 | Claude Code | Item DocType에 Custom Field 9개 생성(`custom_manufacturing_type`/`custom_inspection_type`/`custom_default_operation`/`custom_legacy_sub_category`/`custom_vehicle_model`/`custom_specification`/`custom_array_qty` + Section/Column Break 2개) + Item Group 8건 생성(완제품/반제품/원재료/부재료/상품 + 하위 일반반제품·PCB ASSY(반제품)·PCB ASSY(원재료)) + 검증용 테스트 Item 2건(Serial 1·Batch 1) 생성 후 삭제 + `bench export-fixtures --app babipa_erp` | development.localhost | 성공 | `docs/품목코드_260720.xlsx` 289건 기준 Item DocType 필드 매핑 설계. 상세는 `docs/item-doctype-design.md`. 289건 실데이터 임포트는 이번 범위 아님(설계만) |
| 2026-07-20 | Claude Code | Item DocType에 Custom Field 2건 추가(`custom_safety_critical` Check/default 0, `custom_es_standard_code`+`custom_es_standard_revision` Data) — 기존 9개와 같은 섹션에 `insert_after` 체인으로 이어붙임 + `bench export-fixtures --app babipa_erp` | development.localhost | 성공 | `hkmc-compliance` 리뷰 보완 요청 2건 반영. 값은 채우지 않고 필드 구조만 생성(안전특성 플래그는 도면 검토 선행 필요, ES 표준 코드는 원본 xlsx에 없음). 상세는 `docs/item-doctype-design.md`, `docs/decisions.md` |
| 2026-07-20 | Claude Code | patch `babipa_erp.patches.v0_0.create_finished_goods_qi_template_shells` 신설(`patches.txt` post_model_sync 등록) + `bench --site development.localhost migrate` 2회 실행(최초 생성 1회, 재실행 시 멱등성 확인) | development.localhost | 성공 | placeholder `Quality Inspection Parameter` 마스터 1건 + `Quality Inspection Template` 껍데기 21건(완제품 전수검사 대상) 생성. 값 없음(TBD placeholder), 각 문서에 생성 사유 Comment 첨부. 상세는 `docs/item-doctype-design.md` §6.1, `docs/decisions.md` |
| 2026-07-20 | Claude Code | patch `babipa_erp.patches.v0_0.import_item_master_260720` 신설(`patches.txt` post_model_sync 등록) + UOM 마스터 2건("EA"/"g") 생성 + `bench --site development.localhost migrate` 실행(289건 Item + Item Price 최초 생성) → `execute()` 직접 재호출로 멱등성 확인(중복 0건) → `migrate` 재실행(Patch Log 스킵 확인) | development.localhost | 성공 | `docs/품목코드_260720.xlsx` 289건 전량 임포트. Item 299건(demo 10 + 신규 289), `has_serial_no=1` 21건/`has_batch_no=1` 266건/둘다 0(스퀴지 2건) 확인, `stock_uom` 공백 0건, 완제품 21건 전부 `quality_inspection_template` 연결, Item Price Standard Selling 12건·Standard Buying 78건(원본 매출/매입단가 존재 건수와 정확히 일치) 전부 개발 사이트 실측 확인. 단가 리터럴은 patch 코드에 넣지 않고 gitignore된 로컬 사본(`.../patches/v0_0/data/item_master_260720.xlsx`)을 런타임에 읽는 방식 채택 — 근거는 `docs/decisions.md` 해당 항목. 상세는 `docs/item-doctype-design.md` §7.1 |
| 2026-07-20 | Claude Code | Company `BABIPA (Demo)` 정리 — `Transaction Deletion Record`(`TDL0001`) 생성 후 `generate_to_delete_list()` + `submit()`로 연결 트랜잭션 114개 DocType(Sales/Purchase Invoice·Order, Payment Entry, GL Entry 42건, Stock Ledger Entry 16건, Bin 18건 등) 백그라운드 잡으로 삭제 → 삭제 완료(`status=Completed`) 확인 후 `frappe.delete_doc("Company", "BABIPA (Demo)", force=True)`로 Company 및 잔여 Account 95건 cascade 삭제 | development.localhost | 성공 | 회계모듈 점검 중 발견한 잔재 데이터 정리(사용자 확정 지시). 실사용 회사 `BABIPA`(Account 94건, Warehouse 5건, Cost Center 2건)는 그대로 유지 — 법인 실명이 아닌 가칭이지만 지금은 구축·테스트 목적이라 이름은 바꾸지 않기로 사용자 확정. 원시 SQL 삭제 대신 ERPNext 표준 `Transaction Deletion Record` 메커니즘을 사용 — `Company.on_trash()`가 GL Entry 존재 시 Account/Cost Center 삭제를 건너뛰므로, 트랜잭션을 먼저 정리하지 않고 Company부터 지우면 계정과목이 고아 레코드로 남는 문제를 회피하기 위함. `Transaction Deletion Record` 자신은 Company 삭제 시 `on_trash()`에 의해 함께 삭제됨(ERPNext 표준 동작) |
| 2026-07-20 | Claude Code | 커스텀 DocType 3개 신설(`Equipment`/`Equipment Daily Inspection`+child/`Production Downtime Log`) + Workstation Type 4건·Operation 4건 생성 후 `bench export-fixtures --app babipa_erp`(operation.json/workstation_type.json) + patch 2개(`create_manufacturing_masters_260720`: Workstation 8건·Equipment 9건·Equipment Daily Inspection 9건, `create_test_bom_production_data_260720`: TEST Item Group 5건·TEST Item 6건·BOM 2건·Work Order 2건·Job Card 4건·Production Downtime Log 3건) 신설(`patches.txt` post_model_sync 등록) + `bench --site development.localhost migrate` 3회 실행(최초 DocType 스캐폴딩, `custom:1→0` 정정 후 재실행, patch 2 추가 후 재실행 — 마지막 실행으로 전체 재실행해 멱등성 확인·중복 0건) | development.localhost | 성공 | `docs/decisions.md` 2026-07-20 최신 행 참조. 실행 중 `.claude/skills/frappe-doctype-json/SKILL.md`의 `"custom": 1` 골격 지시가 컨트롤러 클래스 로딩을 막는 실제 버그를 유발함을 발견·정정(`custom: 0`으로). BOM 정전개(Explosion)·Where Used Report(역전개) 둘 다 Desk UI에서 직접 열어 확인. 실 Item 289건은 불변(임포트 후 총 305건 = 299+TEST 6건)임을 재확인 |
| 2026-07-20 | Claude Code | `BABIPA` Chart of Accounts(계정 94건, `chart_of_accounts=Standard`) 검토 — 별도 코드 변경 없음, 확인만 수행. `경리` Role 신규 생성(`is_custom=1`, `desk_access=1`) + `Journal Entry`/`Payment Entry`(Read/Write/Create/Submit/Cancel/Amend/Report/Export/Print/Email) · `GL Entry`(Read/Report/Export만) Custom DocPerm 3건을 `frappe.permissions.add_permission`+`update_permission_property`로 생성 → `frappe.core.doctype.data_import.data_import.export_json`을 직접 호출해 `role.json`·`custom_docperm.json`만 개별 export(다른 세션이 작업 중인 `hooks.py`/`operation.json`/`workstation_type.json` 등은 건드리지 않도록 전체 `bench export-fixtures` 대신 대상 한정), `hooks.py` fixtures 목록에 두 항목 추가(git 스테이징도 blob 단위로 분리해 다른 세션의 미커밋 변경과 섞이지 않게 처리) | development.localhost | 성공 | 회계모듈 착수 우선순위 3번(CoA 검토)·4번(경리 role 생성) 진행. CoA는 계정과목 상세가 없는 범용 `Standard` 템플릿이라 §4.5(세무신고는 더존 유지, ERP는 관리회계만)와 충돌할 부가세/전자세금계산서 전용 계정 자체가 없음을 확인 — 별도 조정 불필요로 결론(단, `Tax Assets - B`가 하위 계정 없는 빈 그룹인 점은 템플릿 기본값이라 방치, 추후 필요 시 보완). 경리 role 권한 범위는 `docs/decisions.md` §4.5·§5.4에서 명시된 "내부 정합용 전표"(Journal Entry·Payment Entry)에 한정한 최소 구성 — Purchase/Sales Invoice, Supplier, Customer 등 나머지 DocType 접근 여부는 아직 미결정이라 부여하지 않음(후속 확인 필요). 생산/품질/구매/관리자 4개 Role과 Payment Entry의 Workflow 승인 게이트(§5.5)는 이번 범위 밖 |
