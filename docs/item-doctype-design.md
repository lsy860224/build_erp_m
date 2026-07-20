# Item DocType 설계 — `docs/품목코드_260720.xlsx` 매핑 (2026.07.20)

> 이 문서는 **설계 문서**다. 289건 실데이터의 실제 임포트는 2026.07.20 후속 세션에서
> `frappe-backend`가 완료했다 — 결과·검증은 §7.1 참조, patch는
> `apps/babipa_erp/babipa_erp/patches/v0_0/import_item_master_260720.py`.
> 개발 사이트(`development.localhost`)에서 아래 Custom Field·Item Group을 실제로
> 생성하고, 각 분류(Serial/Batch)당 1건씩 테스트 Item을 넣어 저장까지 검증한 뒤 삭제했다
> (스키마 동작 확인용, 데이터 자체는 남기지 않음) — 이건 설계 단계 검증이고, 실 289건
> 임포트는 별도로 §7.1에 기록.
>
> **`docs/품목코드_260720.xlsx` 원본은 이 저장소에 커밋되지 않는다** — `build_erp_m`은
> GitHub public repo이고 이 파일엔 실제 매출/매입/외주단가·차종 매핑이 들어있는 영업기밀
> 데이터라 `.gitignore`에 등록했다(2026.07.20, `docs/decisions.md` 참조). 로컬 디스크에는
> 그대로 있으니 세션마다 다시 채워 넣을 필요는 없지만, 이 문서·git 이력만으로는 원본을
> 재현할 수 없다는 점을 유의할 것.

## 0. 원본 데이터 재확인 요약

`docs/품목코드_260720.xlsx`, 단일 시트, 289행 15컬럼. 품목구분 분포와 Serial/Batch 결정은
`docs/decisions.md`(2026.07.20 항목)에 이미 확정되어 있으므로 재분석하지 않았다. 이 문서는
그 확정 위에 필드 매핑을 설계한다.

## 1. Item Group 트리 설계

### 1.1 `중분류` 컬럼 분포 재확인 (품목구분별)

| 품목구분 | 중분류 값 분포 |
|---|---|
| 완제품 (21) | 일반반제품 21 |
| 반제품 (125) | 일반반제품 67, PCB ASSY 14, **99** 44 |
| 원재료 (94) | **03** 90, PCB ASSY 4 |
| 부재료 (44) | 일반반제품 17, **97** 20, **99** 3, **98** 2, **09** 1, **10** 1 |
| 상품 (5) | **99** 5 |

`중분류`는 사람이 읽을 수 있는 텍스트(`일반반제품`, `PCB ASSY`)와, 의미를 알 수 없는
2자리 숫자 레거시 코드(`99`/`03`/`97`/`98`/`09`/`10`)가 **한 컬럼에 섞여 있다.** 숫자 코드
쪽은 회사 내부 레거시 시스템(MES/PLM 추정)의 분류 코드로 보이나, 원문 xlsx에는 코드→의미
매핑표가 없다. 항목명으로 내용을 유추할 수는 있으나(예: `97`=SMT 마스크류, `98`=스퀴지,
`09`=코팅액, `10`=솔더크림, `03`=반도체/IC 부품으로 보임) — **이건 어디까지나 추정이고
원문에 없는 해석이므로, 확인 없이 Item Group 이름으로 확정하지 않았다.**

추가로 `완제품`(전부 `일반반제품`)과 `부재료`(`일반반제품` 17건)에도 같은 텍스트값이
찍혀 있는데, "완제품 = 일반반제품"은 의미상 앞뒤가 맞지 않는다 — 이 컬럼이 여러 시스템/
드롭다운을 거치며 기본값이 그대로 남은 잔재일 가능성이 높다고 판단해, 이 값들로는
Item Group 하위 계층을 만들지 않았다(아래 1.2 참조).

### 1.2 확정 트리 (개발 사이트에 실제 생성·검증 완료)

```
All Item Groups (ERPNext 표준 루트, 기존 데모 그룹 Products/Raw Material 등은 그대로 둠)
├── 완제품                    (leaf)
├── 반제품                    (is_group=1)
│   ├── 일반반제품             (leaf)   ← 중분류='일반반제품' 67건
│   └── PCB ASSY(반제품)       (leaf)   ← 중분류='PCB ASSY' 14건
├── 원재료                    (is_group=1)
│   └── PCB ASSY(원재료)       (leaf)   ← 중분류='PCB ASSY' 4건
├── 부재료                    (leaf)
└── 상품                      (leaf)
```

**Level 1 = `품목구분`을 그대로 사용** — `docs/decisions.md`의 Serial/Batch 확정과 1:1로
맞아떨어지고, 289건 전 행에 빠짐없이 채워져 있어 가장 신뢰할 수 있는 축이다.

**Level 2는 `중분류`가 사람이 읽을 수 있는 텍스트이고, 반제품/원재료 양쪽에서 동일한
의미(`PCB ASSY` = PCB 관련 자재/반제품)로 일관되게 쓰인 경우에만 만들었다.** 그 외
(숫자 레거시 코드 44+90+20+3+2+1+1+5=166건, 그리고 완제품·부재료의 `일반반제품`
21+17=38건)는 **Level 1 그룹에 그대로 남겨두고 하위 그룹을 만들지 않았다** — 확실하지
않은 분류를 임의로 만들지 않는 쪽을 택함.

- `부재료`의 `일반반제품` 17건을 별도 그룹으로 안 만든 이유: 위에서 설명한 "완제품=일반
  반제품"과 같은 성격의 잔재값으로 보여 신뢰도가 낮음.
- `원재료`의 `PCB ASSY` 4건만 하위 그룹을 만들고, 나머지 90건(`03`)은 그대로 둔 이유:
  `03`이 무엇을 뜻하는지 원문에 없어서. `A5210`/`A5231`/`A5232`/`A5251` 등 IC/센서류로
  보이지만 이 역시 추정.

### 1.3 미결정 — 사용자 확인 필요

**`중분류`의 숫자 레거시 코드(`03`, `09`, `10`, `97`, `98`, `99`) 6종이 실제로 무엇을
뜻하는지 원문 근거가 없다.** 사내에 이 코드의 원본 코드표(MES/PLM 등)가 남아있는지 확인
필요. 확인되면:
1. 6개 코드에 대응하는 Item Group을 추가하고,
2. 해당 166건 Item의 `item_group`을 재배치하면 된다 —
   지금 설계는 이 재배치를 막지 않는 구조(Level 1에 두는 것 자체가 유효한 상태)라
   나중에 되돌리기 쉽다.

## 2. 필드 매핑표 (xlsx 15컬럼 → Item DocType)

| # | xlsx 컬럼 | ERPNext 목적지 | 근거/비고 |
|---|---|---|---|
| 1 | 품목구분 | 표준 필드 `item_group` (Link → Item Group) | §1의 Level 1 |
| 2 | 제조유형 | **Custom Field** `custom_manufacturing_type` (Select) | 아래 §3 참조 — 값 7종이 `작업공정`과 강하게 상관관계, BOM/Routing 개념과 가깝지만 이번 범위에서는 Item 속성으로 임시 보관 |
| 3 | 고객품번 | 표준 자식 테이블 `customer_items`(Item Customer Detail, `ref_code` 필드) | **원본 289건 전부 공백(0/289)** — 매핑 경로는 확정하되 지금은 채울 데이터가 없음. §4 HKMC Customer 마스터 선행 이슈 참조 |
| 4 | 품목코드 | 표준 필드 `item_code`, Item의 `autoname` 자체가 이미 `field:item_code`(v16 확인) | 289건 전부 유일값(중복 없음), 최대 13자 — 별도 Naming Series 불필요 |
| 5 | 항목명(품명) | 표준 필드 `item_name` | 최대 46자, 표준 varchar(140) 내 |
| 6 | 중분류 | **Custom Field** `custom_legacy_sub_category` (Data) + 일부는 `item_group` Level 2(§1) | 원본 값을 있는 그대로 보존(감사 대사용) — Item Group으로 승격 여부와 무관하게 항상 원문 그대로 저장 |
| 7 | 모델 | **Custom Field** `custom_vehicle_model` (Data) | 값 종류: JG/MX5/RS/XP2/MO/NE1/MobED + 콤마 조합값(`JG, RS, XP2`)도 존재 → Select 대신 Data로 원문 그대로 보존. 차량 플랫폼별 필터링이 실무에서 자주 필요해지면 별도 "Vehicle Model" 마스터 + Table MultiSelect로 정규화하는 걸 후속 검토(이번 범위 아님) |
| 8 | 규격 | **Custom Field** `custom_specification` (Data) | 47/289건만 채워짐. 값이 `RODS A`/`A TYPE`처럼 옵션·변형 식별자에 가까워 표준 `description`(Text Editor, 서술형)에 욱여넣지 않고 별도 필드로 구조화 |
| 9 | 단위 | 표준 필드 `stock_uom` (Link → UOM) | **189/289건 공백** — `stock_uom`은 Item 저장 시 필수(mandatory) 필드라 이대로는 임포트 불가. §5 미결정 참조 |
| 10 | 매출단가 | 표준 개념 **Item Price**(Price List="Standard Selling", `selling=1`) | Item 자체의 `standard_rate`는 v16에서 신규 생성 시(`__islocal`)에만 노출되는 "Item Price 자동 생성 단축키"일 뿐 지속 저장소가 아님 — 확인 완료. 10/21 완제품(HKMC 납품 최종단위) + 반제품 2건에 값 존재 |
| 11 | 매입단가 | 표준 개념 **Item Price**(Price List="Standard Buying", `buying=1`) | 원재료 67/94, 반제품 5/125, 상품 4/5, 부재료 2/44 |
| 12 | 외주단가 | 표준 개념 **Item Price**(`buying=1` + `supplier`=해당 외주업체) | **원본 289건 전부 공백(0/289)** — Item Price DocType이 이미 `supplier` 링크 필드를 갖고 있어(확인 완료) 별도 Price List 신설 없이도 외주단가 발생 시 바로 쓸 수 있음. 지금은 설계만, 데이터 없음 |
| 13 | 검사구분 | **Custom Field** `custom_inspection_type`(Select: 전수검사/샘플링검사/무검사) + 표준 필드 `inspection_required_before_delivery`/`inspection_required_before_purchase`(Check) | ERPNext 표준은 "검사 필요 여부"만 boolean으로 표현하고 전수/샘플링 구분이 없음 → Custom Field로 한국어 3분류를 보존하고, 완제품처럼 표준 boolean 게이트가 필요한 경우 `무검사=0`, `전수/샘플링=1`로 함께 설정. `quality_inspection_template` 연결은 검사 SOP가 실제로 정의된 뒤(§6 참조) 진행 |
| 14 | 작업공정 | **Custom Field** `custom_default_operation`(Select: PP/AS/QT/PC) | Routing/Operation 개념에 더 가까움 — §3 참조, 이번 범위에서는 Item 속성으로만 임시 보관하고 BOM/Routing 설계는 별도 세션으로 미룸 |
| 15 | Array수량(캐비티) | **Custom Field** `custom_array_qty`(Int) | PCB ASSY(SMT 패널)뿐 아니라 `HOUSING ASSY`/`RADOME ASSY`/`BRACKET` 등 사출 금형 품목에도 값이 있음(19건 전수 확인) — "PCB 패널 전용"이 아니라 "생산 단위당 배열/캐비티 수량"이라는 더 넓은 개념. BOM/backflush 수량 계산의 입력값이 될 수 있는 물리 스펙이라 판단해 Item 레벨 속성으로 유지 |
| - | (xlsx에 없음, `hkmc-compliance` 리뷰 보완) | **Custom Field** `custom_safety_critical`(Check, default 0) | §6 완제품=Serial/그외=Batch 기본규칙의 예외 오버라이드 플래그. HKMC 도면상 특별특성(Special Characteristic) 지정 품목을 개별추적(Serial) 대상으로 전환할 근거 구조 — **지금은 어떤 품목이 해당되는지 판단하지 않고 전부 기본값 0**, 도면 검토는 사용자/품질부서 별도 진행 |
| - | (xlsx에 없음, `hkmc-compliance` 리뷰 보완) | **Custom Field** `custom_es_standard_code`(Data) + `custom_es_standard_revision`(Data) | 이 품목 `custom_inspection_type`(검사구분)의 근거가 된 HKMC ES 표준 코드·개정판을 감사 시 즉시 답하기 위한 참조 필드. 원본 `품목코드_260720.xlsx`에 이 정보가 없어 **필드 구조만 생성, 값은 비워둠**(후속 채움 대상) |

## 3. `제조유형`·`작업공정` — Item 마스터 범위 밖(BOM/Routing) 판단 근거

`제조유형`(7종)과 `작업공정`(PP/AS/QT/PC, 4종+공백)은 교차표를 보면 사실상 같은 개념의
다른 표현이다:

| 제조유형 | 작업공정 |
|---|---|
| 후가공 | PP 42건 100% |
| PCB ASSY | PC 14건 100% |
| 조립/검사/포장 | AS 25건 + QT 21건 (완제품 21건 전부 QT) |
| 원재료/부재료/상품(구매품)/일반반제품 | 공백(해당 없음) |

이건 **Routing/Operation**(작업 흐름·공정 순서) 개념이지 Item 정적 속성이 아니다.
ERPNext에는 이미 `default_bom`, `is_sub_contracted_item` 같은 BOM 연동 필드가 Item
Manufacturing 탭에 표준으로 있고, 실제 공정 흐름은 BOM/Operation/Workstation
DocType으로 설계하는 게 맞다. 이번 세션은 그 설계까지 포함하지 않으므로:

- 두 컬럼 모두 **Custom Field로 원문 값만 보존**(Select) — 향후 BOM/Routing 설계 시
  Operation 마스터로 정식 이관하고, 이 두 필드는 레거시 참조용으로 남기거나 폐기.
- 이 판단은 설계 승인용으로 기록해둔다: **BOM/Routing 정식 설계는 별도 세션 범위.**

## 4. 미결정 — HKMC Customer 마스터

`customer_items`(Item Customer Detail)로 고객품번을 담으려면 선행조건으로 **Customer
DocType에 HKMC 쪽 거래선(예: 현대자동차/기아 법인 각각, 또는 대표 계정 1개)이 최소 1건
있어야 한다.** 개발 사이트를 직접 조회해 확인했다 — 현재 `Customer`에는 ERPNext 데모
데이터(`Palmer Productions Ltd.` 등)만 있고 **HKMC 관련 Customer 레코드는 0건.**

다만 원본 `고객품번` 컬럼 자체가 **289건 전부 공백**이라 지금 당장 이 마스터가 없어도
막히는 데이터는 없다. 우선순위는 낮지만, 실제 고객품번을 확보하는 시점에는 반드시
선행되어야 한다. **사용자 판단 필요**: HKMC 법인을 Customer 몇 건으로 나눠 등록할지
(예: 현대자동차/기아 별도 vs 통합 1건), 계정 정보(사업자번호 등)는 누가 갖고 있는지.

## 5. 미결정 — `stock_uom` 공백 189/289건

`단위` 컬럼이 원재료(91/94 = EA) 외에는 대부분 공백이다(반제품 125건, 상품 5건, 완제품
21건 전부 공백, 부재료도 31/44 공백). `stock_uom`은 ERPNext에서 **Item 저장 시 필수
필드**라 이 상태 그대로는 임포트가 막힌다.

일반적으로 조립품·완제품류는 개수 단위(`Nos`)로 보는 게 합리적 추정이지만, **이건 원문에
없는 판단이라 확정하지 않았다.** 두 가지 옵션을 제시한다:
1. 사용자가 189건 전부 "Nos"(EA)로 봐도 되는지 확인 후 일괄 기본값 적용, 또는
2. 회사 담당자가 원본 정보(단위가 실제 관리되는 시스템이 따로 있는지)를 다시 확인.

## 6. Serial/Batch 플래그 반영 방식

`docs/decisions.md`(2026.07.20) 확정 분류를 실제 Item 레코드에 반영하는 방법:

- ERPNext는 **Item Group에 "이 그룹은 Serial/Batch를 쓴다"는 기본값 상속 기능이 없다**
  (Item Group은 순수 분류/리포팅 트리일 뿐, `has_serial_no`/`has_batch_no`를 자동
  전파하지 않음 — 확인 완료). 따라서 Item Group 설계만으로는 플래그가 자동 반영되지
  않는다.
- 대신 **임포트 스크립트(patch)가 품목구분별로 직접 설정**하는 방식을 권장한다 —
  Item Group에 의존하는 훅(`validate` 이벤트 등)을 따로 만들 필요 없이, 마이그레이션
  시점에 1회성으로 명확하게 처리하는 편이 더 단순하고 감사 추적이 쉽다.

| 품목구분 | `has_serial_no` | `has_batch_no` |
|---|---|---|
| 완제품 (21건) | 1 | 0 |
| 반제품(125)·원재료(94)·부재료 中 스퀴지 제외(42)·상품(5) | 0 | 1 |
| 스퀴지 2건(`A6160-00001`/`A6160-00002`) | 0 | 0 |

개발 사이트에서 완제품 1건(Serial)·반제품 PCB ASSY 1건(Batch)을 실제로 저장해 이 조합이
스키마 오류 없이 동작함을 확인했다(검증 후 삭제).

## 6.1 완제품 21건 Quality Inspection Template 껍데기 (2026.07.20 후속)

`hkmc-compliance` 리뷰가 지적한 문제: `custom_inspection_type`(검사구분)이 "전수검사"라고
표시돼 있어도 표준 `quality_inspection_template` 연결이 없으면 실제 Quality Inspection
문서 생성을 강제하지 않는 라벨뿐인 상태였다. 이를 보완하기 위해 완제품 21건
(`품목구분=완제품` AND `검사구분=전수검사`, `docs/품목코드_260720.XLSX` 재확인 —
`JGP26-A0301` 등 SENSOR ASSY/RADAR UNIT 계열)에 대응하는 **Quality Inspection Template
껍데기 21건**을 만들었다.

**여기서도 실제 검사 파라미터(측정 항목, 규격 상하한, 샘플링 사이즈/AQL)는 채우지 않았다** —
도면/Control Plan/검사기준서 원본 자료가 아직 없다고 사용자가 명시적으로 확인했다
(CLAUDE.md 임의 데이터 위·변조/추정 금지 원칙). "껍데기"의 구체적 내용:

- **템플릿 이름**: `<품목코드> - <항목명>` 형식(예: `JGP26-A0301 - SENSOR ASSY - FR DR, LH
  (SWING DOOR)`) — Quality Inspection Template DocType 자체에는 Item을 가리키는 Link
  필드가 없어(`quality_inspection_template_name` + `item_quality_inspection_parameter`
  Table 두 개뿐), 이름에 품목코드를 포함시켜 대응관계를 명시했다.
- **빈 검사 파라미터 테이블 저장 여부 확인**: 개발 사이트에서 실제로 시도한 결과
  `item_quality_inspection_parameter`(Table 필드)가 **`reqd=1`이라 빈 테이블로는
  `MandatoryError`가 나서 저장이 막힌다**는 것을 확인했다. 게다가 자식 테이블
  `Item Quality Inspection Parameter`의 `specification` 필드는 겉보기와 달리 Data가
  아니라 **`Quality Inspection Parameter`(마스터 DocType)로의 Link**이고 이것도
  `reqd=1`이다. 따라서:
  - 21건이 공유하는 placeholder 마스터 `Quality Inspection Parameter` 1건을 먼저
    생성(`parameter`(=name) = `TBD - 검사 파라미터 미정`, `description`에 아래 껍데기
    문구 기재).
  - 각 템플릿에 그 placeholder를 참조하는 행을 정확히 1개씩만 넣고, `numeric=0`(체크
    해제 — 안 그러면 `min_value`/`max_value` Float 필드가 기본값 0.0으로 채워져 마치
    "규격 0~0"처럼 보일 위험이 있어 의도적으로 껐다), `value`(Acceptance Criteria
    Value) 필드에 `TBD — 실제 검사 파라미터 미정, 품질부서 확인 필요`를 명시적으로
    적어 절대 실제 값처럼 보이지 않게 했다.
- **비고**: Quality Inspection Template DocType 자체엔 설명/비고 필드가 없어(Data+Table
  두 필드뿐), 대신 각 템플릿 문서에 Frappe Comment로
  `2026.07.20 껍데기 생성 — 도면/Control Plan 확보 후 품질부서가 실제 파라미터 채울 것`을
  남겼다(감사 시 즉시 확인 가능).
- **Item 연결은 아직 하지 않음**: 완제품 21건의 실 Item 레코드가 아직 없다(289건 임포트는
  §5 `stock_uom` 공백 189건 등 미결정 이슈로 아직 진행 중이 아님). **완제품 임포트 시
  frappe-backend가 이 21개 템플릿을 해당 Item의 `quality_inspection_template` 필드로
  연결할 것** — 템플릿 이름이 품목코드를 포함하므로 매칭은 기계적으로 가능하다.

**버전관리 방식 — fixtures가 아니라 patch로 결정**: `apps/babipa_erp/babipa_erp/patches/
v0_0/create_finished_goods_qi_template_shells.py`(post_model_sync)로 구현하고
`hooks.py`의 `fixtures` 목록에는 넣지 않았다. 근거:

1. 이 21건은 Item Group(§7의 8건, 완제품/반제품/원재료/부재료/상품 등 분류 체계)이나
   Custom Field처럼 **앱이 항상 동일하게 보유해야 하는 스키마/분류 구성**이 아니라,
   개별 품목코드 1:1에 대응하는 **인스턴스 데이터**다 — 이번 289건 Item 레코드 자체를
   "설계만 하고 실제 임포트는 후속 patch/스크립트로 넘긴다"(본 문서 최상단, §5, §7)고
   이미 정한 것과 같은 성격이라 동일한 경로를 따르는 것이 일관적이다.
2. fixtures는 `bench migrate`/`bench install-app` 때마다 **정확히 같은 상태로 동기화**되는
   것을 전제로 한다(설정값·분류 체계처럼 "항상 이래야 하는" 데이터에 적합). 반면 이 21건은
   품질부서가 도면 확보 후 실제 파라미터로 **직접 수정할 대상**이다 — 만약 fixtures로
   등록해두면, 향후 개발 사이트에서 `bench export-fixtures`를 실행하는 시점에 운영에서
   이미 채워둔 실제 파라미터가 스냅샷 시점의 구조로 덮어써지거나, 반대로 운영 쪽
   `bench migrate` 시 fixtures가 재적용되며 껍데기 상태로 되돌아갈 위험이 있다. patch는
   `Patch Log`에 기록되어 정상적으로는 한 번만 실행되고(멱등성 가드도 코드에 포함:
   `frappe.db.exists`로 이미 있으면 건너뜀), 이후 문서 내용 편집과 무관하게 재실행되지
   않는다.
3. 개발 사이트에서 `bench --site development.localhost migrate`로 최초 실행·21건 생성을
   확인했고, 재실행(2회차 `migrate`)에서도 중복 생성이나 에러 없이 안전함을 확인했다.

## 7. 산출물 반영 상태

- **Custom Field 11개**(9개 + `hkmc-compliance` 리뷰 보완 2건, 2026.07.20 후속) —
  `apps/babipa_erp/babipa_erp/fixtures/custom_field.json`으로 export 완료(`dt=Item` 필터,
  hooks.py 필터 변경 없이 기존 필터가 신규 필드도 그대로 포착).
  - 보완분: `custom_safety_critical`(Check, default 0), `custom_es_standard_code`(Data),
    `custom_es_standard_revision`(Data) — 기존 9개와 같은 섹션에 `insert_after` 체인으로
    이어붙임(`custom_array_qty` → `custom_safety_critical` → `custom_es_standard_code` →
    `custom_es_standard_revision`). 값은 채우지 않고 구조만 생성.
- **Item Group 8건** — `apps/babipa_erp/babipa_erp/fixtures/item_group.json`으로 export
  완료(생성한 이름만 명시적으로 필터, ERPNext 데모 그룹은 미포함).
- `apps/babipa_erp/babipa_erp/hooks.py`의 `fixtures` 목록에 위 두 항목 추가.
- 289건 데이터 자체는 임포트하지 않음 — 이번 세션 범위 밖.
- **Quality Inspection Template 껍데기 21건**(2026.07.20 후속, §6.1) —
  `apps/babipa_erp/babipa_erp/patches/v0_0/create_finished_goods_qi_template_shells.py`
  (patch, fixtures 아님) + placeholder `Quality Inspection Parameter` 마스터 1건.
  `bench --site development.localhost migrate`로 실행·검증 완료. 완제품 Item 임포트 시
  `quality_inspection_template` 연결은 후속.

## 7.1 289건 실데이터 임포트 완료 (2026.07.20 후속)

`docs/품목코드_260720.xlsx` 289건 전체를
`apps/babipa_erp/babipa_erp/patches/v0_0/import_item_master_260720.py`(patch,
post_model_sync)로 임포트했다. §1~§7의 설계를 그대로 코드화했을 뿐 재판단은 없다.

**구현 방식이 §6.1(QI Template 껍데기) 선례와 다른 점 — 원본 데이터를 patch에 리터럴로
넣지 않음.** QI 껍데기 patch는 품목코드·항목명 21건만 다뤄 상대적으로 민감도가 낮았지만,
이번 289건에는 실제 매출/매입단가(원화 금액)가 포함된다. `docs/decisions.md`가 이미
"실제 영업기밀(단가 등)이 담긴 원본 데이터 파일은 이 저장소가 public인 한 절대 커밋하지
않는다"고 확정했는데, 그 값을 patch 코드에 리터럴로 옮기는 것도 형태만 다를 뿐 같은
위반이라고 판단했다. 그래서:

- `apps/babipa_erp/babipa_erp/patches/v0_0/data/item_master_260720.xlsx`(원본을 그대로
  복사한 작업용 사본, `.gitignore` 등록)를 patch가 **런타임에 직접 읽는다.**
- 이 사본이 없는 환경(공개 clone, CI 등)에서는 조용히 스킵하고 로그만 남긴다 — 크래시 없음.
- `apps/babipa_erp`가 개발 컨테이너에 bind mount돼 있어 호스트에 파일을 두면 컨테이너에서
  바로 보인다(`docs/dev-environment.md` 구조 그대로 활용, 별도 `docker cp` 불필요).

### 임포트 규칙 적용 요약 (전부 사용자 확정 사항 그대로 적용, §1~§7 참조)

1. `item_group` — §1.2 트리 그대로(반제품/원재료 中 중분류='일반반제품'/'PCB ASSY'만 하위
   그룹 승격, 나머지는 Level 1).
2. Serial/Batch — 완제품 21건 Serial, 나머지 Batch, 스퀴지 2건(`A6160-00001`/`A6160-00002`)
   만 둘 다 0.
3. `stock_uom` — 원본 값 있으면 그대로(EA 103건, g 1건 — 코팅액 `A6000-00002`), 공백
   185건은 "EA"로 일괄 기본값(2026.07.20 사용자 확정). "EA"·"g" UOM 마스터가 사이트에
   없어 patch가 함께 생성.
4. Item Price — 매출단가 12건(Standard Selling)·매입단가 78건(Standard Buying) 생성,
   Currency는 두 Price List 기본값과 일치하는 "KRW". 외주단가는 289건 전부 공백이라
   생성 없음.
5. `customer_items`(고객품번) — 289건 전부 공백이라 아무 작업 없음.
6. Custom Field 11개 — 원본 컬럼값을 그대로 매핑(§2 표). `custom_safety_critical`은
   기본값 0 그대로(건드리지 않음), `custom_es_standard_code`/`revision`은 공백 유지.
7. `inspection_required_before_delivery`/`purchase` — 검사구분≠'무검사'면 1(전수검사 23건
   [완제품 21 + 스퀴지 2] + 샘플링검사 136건 = 159건 `1`, 무검사 130건은 `0`).
8. 완제품 21건 `quality_inspection_template` — §6.1 patch가 만든 템플릿 이름
   (`<품목코드> - <항목명>`)을 이번 patch가 동일 로직(f-string)으로 다시 계산해
   `frappe.db.exists`로 매칭 — 21건 전부 매칭 성공(원본 xlsx의 항목명이 QI 껍데기 patch가
   하드코딩한 이름과 정확히 일치함을 재확인).

### 검증 결과 (개발 사이트 `development.localhost`, 실측)

| 항목 | 기대값 | 실측 |
|---|---|---|
| 신규 Item 총건수 | 289 | 289 (전체 Item 299 − 기존 demo 10) |
| `has_serial_no=1` | 21 | 21 |
| `has_batch_no=1` | 266 | 266 |
| 둘 다 0(스퀴지 2건, demo 10건 포함 전체) | 12 | 12 (스퀴지 2건 개별 확인: 둘 다 0/0) |
| `stock_uom` 빈 Item | 0 | 0 |
| 완제품 21건 `quality_inspection_template` 채움 | 21/21 | 21/21(샘플 3건 직접 조회로 재확인) |
| Item Price Standard Selling(non-demo) | 12 | 12 |
| Item Price Standard Buying(non-demo) | 78 | 78 |

멱등성: `bench migrate`로 최초 실행 후, `execute()` 함수를 재호출(Patch Log 우회)해도
Item Price 건수(12/78)가 그대로 유지되고 신규 Item·중복 Item Price가 생기지 않음을
확인했다. 이후 `bench migrate` 2회차(정상 Patch Log 경로)에서도 총 Item 건수(299) 불변.

## 8. CLAUDE.md 체크리스트 반영

- [x] 코어 미수정 — `apps/babipa_erp/`에서만 작업(Custom Field/Item Group은 표준
      DocType의 커스터마이징이지 코어 파일 수정이 아님).
- [x] DocType/필드 리네임 금지 — `item_code`/`item_name`/`stock_uom`/`item_group`/
      `has_serial_no`/`has_batch_no`/`customer_items` 등 표준 필드명·구조를 그대로 사용,
      새 개념만 `custom_` 접두사 Custom Field로 추가.
- [x] 새 필드를 fixtures에 등록 — §7.
- [x] HKMC 감사 대응 데이터(트레이서빌리티) 관련 — **그렇다.** Serial/Batch 이력추적의
      기반이 되는 Item 마스터 설계이므로 `hkmc-compliance` 리뷰가 필요하다고 판단한다.
      특히 검토 요청 포인트: (1) §1.3의 숫자 레거시 코드 미해석 상태로 감사 대응에
      문제가 없는지, (2) §6 Serial/Batch 매핑이 HKMC ES가 요구하는 로트 추적 단위와
      맞는지, (3) `custom_inspection_type`(전수/샘플링/무검사) 3분류가 SQ 감사 시
      요구되는 검사기록 체계와 정합적인지.
      → (3)에 대한 후속 보완: `custom_inspection_type`이 실제 검사기록 생성을 강제하지
      않는 라벨뿐이라는 지적을 받아 §6.1에서 완제품 21건 Quality Inspection Template
      껍데기를 만들었다. 실제 검사 파라미터는 도면/Control Plan 확보 전까지 값이 없다 —
      이 상태로 감사 대응이 충분한지(빈 템플릿 존재 자체가 "체계는 있다"는 근거로
      인정되는지, 아니면 파라미터 없이는 불충분한지)는 추가 `hkmc-compliance` 확인 필요.
