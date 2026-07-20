# ERP 종합 지식 정리 — 자동차 전장부품 제조사 × ERPNext/Frappe 구축 관점

> **문서 상태**: 리서치 참고자료 (AI 딥리서치 보고서, **v15 기준 작성**). 이 프로젝트의 실제
> 결정은 루트 [`CLAUDE.md`](../../CLAUDE.md)와 [`docs/decisions.md`](../decisions.md)를 따른다.
> 같은 폴더의 [`ERPNext_가이드_검토_및_v16_빌드권고_2026-07-16.md`](ERPNext_가이드_검토_및_v16_빌드권고_2026-07-16.md)가
> 이 문서를 v16 기준으로 검토·보정한 후속 문서다 — 특히 **라이선스 서술(GPLv3 일괄 표기는
> 부정확, §3-⑧에서 정정)**과 **Serial and Batch Bundle 구조(§4.3)**는 이 문서만 보고 코드를
> 짜면 틀린다. 두 문서를 함께 읽을 것. 2026.07.20 검토 후 `docs/gplv3-compliance.md` 라이선스
> 서술 정정, `.claude/skills/frappe-v16-breaking-changes/` 신설로 이 문서의 갭을 반영했다.

> **⚠️ 먼저 읽어주세요 — Google Drive `ai_erp` 폴더 접근 결과 (투명성 고지)**
> 요청하신 `내 구글 드라이브/ai_erp` 폴더(ID `1-D518Akh38w4E82uDcI58KNzFd9abSCP`)에 대해 다음을 **모두 시도**했으나 **폴더 내 문서를 읽지 못했습니다.**
> - `'1-D518Akh38w4E82uDcI58KNzFd9abSCP' in parents` 부모-ID 쿼리(페이지네이션 포함) → **결과 0건**
> - 폴더 ID 직접 fetch → 오류(-32000)
> - `ai_erp` / `erp` / `ERPNext` / `Frappe` / `babipa` / 한글 ERP 용어(전표·분개·자재명세서·이력추적·IATF·PPAP 등) fullText 검색 → **모두 0건**
> - 최근 생성 파일·PDF·스프레드시트·소유자 필터 검색 → 해당 폴더 문서 미노출
> - 폴더 웹 링크 직접 접근 → Google 로그인 벽에 막힘
>
> **원인 추정:** 이 커넥터는 **Google Docs 본문만** 읽을 수 있습니다. `ai_erp` 폴더 안의 파일이 **PDF·MS Office·스프레드시트·텍스트 등 비(非)Google-Docs 포맷**이거나, 검색 인덱스에 아직 반영되지 않은 최근 파일일 가능성이 높습니다(폴더 자체가 목록에 전혀 나타나지 않음).
> **결론:** 따라서 이 보고서는 **폴더 문서 내용 기반이 아니라, 귀하의 배경 컨텍스트(HKMC 납품 자동차 전장부품 제조사·55명·ERPNext 커스텀 `babipa_erp` 구축) + 웹 리서치(ERPNext/Frappe 공식 문서, IATF·AIAG 표준, 학술 논문)**로 작성했습니다. 폴더 문서를 반영하려면 **파일을 Google Docs로 변환하거나 본문을 붙여넣어** 다시 요청해 주십시오. 아래 내용은 그 자체로 완결된 ERP 도입 지식 체계로 활용 가능합니다.

---

## TL;DR (핵심 3줄)
- **ERP의 본질은 "하나의 데이터로 회계·구매·재고·생산·품질·영업을 자동 연결"하는 것**이며, ERPNext에서는 모든 거래가 곧바로 **General Ledger(총계정원장) 전표**와 **Stock Ledger(재고원장)**로 자동 전기(posting)되므로, 카테고리별 지식보다 **모듈 간 연결 흐름(Item→BOM→Work Order→Stock→GL)**을 먼저 이해하는 것이 최우선입니다.
- **자동차 전장부품 제조사에게 ERP의 최대 가치는 회계가 아니라 IATF 16949 8.5.2 이력추적(traceability)**입니다 — ERPNext의 **Batch/Serial No 기능이 로트 관리·전후방 추적·리콜 시뮬레이션의 기반**이 되며, 이력추적 누락은 SQ/IATF 심사에서 **Class A 중대 부적합(생산 중단 리스크)**으로 이어집니다.
- **커스텀 개발은 반드시 "코어 미수정 + 별도 커스텀 앱(`babipa_erp`) + hooks/override" 원칙**을 지켜야 upgrade-safe 하며, 학술 연구가 지목하는 SME ERP 실패의 최대 원인은 소프트웨어가 아니라 **경영진 지원 부족·부실한 마스터데이터·과도한 커스터마이징**입니다.

---

## 📂 읽은 문서 목록
- **`ai_erp` 폴더 내 문서: 0건 읽음** (위 고지 참조 — 커넥터가 폴더/비-Docs 파일에 접근 불가)
- 본 보고서 근거: 배경 컨텍스트 + 웹 리서치(Frappe/ERPNext 공식 문서 `docs.frappe.io`·`erpnext.com`, AIAG, IATF 16949 해설, ResearchGate/Springer/Growingscience 학술 논문)

---

## Key Findings (요약)
1. **ERPNext 모듈 구성**: 회계(Accounting)·구매(Buying)·판매(Selling)·재고(Stock)·제조(Manufacturing)·CRM·HR·프로젝트·품질(Quality)이 **단일 DB에서 통합**되며, 30개 이상 모듈이 상호 연동됩니다.
2. **자동 전기 원칙**: 제출(submit)된 거래는 예외 없이 GL 전표(회계)와/또는 Stock Ledger Entry(재고)를 자동 생성 → **수기 이중입력 제거**가 ERP 도입의 핵심 효익.
3. **자동차 부품 특화 요구**(IATF 16949, PPAP/APQP, 로트추적, 4M 변경)는 ERPNext 표준 기능(Batch/Serial, Quality Inspection, BOM 버전)으로 **대부분 커버 가능**하나, **PPAP·APQP·Control Plan 문서관리는 표준 미탑재 → 커스텀 DocType 필요**.
4. **커스터마이징 리스크**: 코어(erpnext/frappe) 소스를 직접 수정하면 업그레이드가 깨지므로, **별도 앱 + `hooks.py` + `override_doctype_class`/`doc_events`** 방식이 유일한 정석. `babipa_erp` 전략이 정확한 방향.
5. **도입 성공요인**(학술 합의): ①최고경영진 지원 ②명확한 목표·범위 ③깨끗한 마스터데이터 ④교육·변화관리 ⑤최소 커스터마이징 ⑥단계적 Go-live. 이 중 하나라도 약하면 실패율 급증.

---

# Details — 카테고리별 정리

---

## ① ERP 기초지식 — 회계(Accounting) 편

### 핵심 개념 요약
ERPNext 회계는 **복식부기(double-entry bookkeeping)** 기반이며, IFRS/GAAP/한국 회계기준 등 어떤 표준에도 맞출 수 있는 **구성 가능한 계정과목표(Chart of Accounts, COA)**를 사용합니다. **모든 재무 거래는 실시간으로 총계정원장(General Ledger)에 기록되어 변경 불가능한(immutable) 감사증적(audit trail)을 유지**합니다.

### 중요한 정보
- **COA는 트리 구조**: **Group 계정**(잔액 요약용, 직접 전기 불가)과 **Ledger 계정**(실제 거래 전기, 트리의 말단 노드)으로 구성. 계정 유형(Asset/Liability/Income/Expense/Equity)으로 분류.
- **모든 모듈이 회계로 흘러든다**: 판매송장·구매송장·급여·재고이동·제조완료가 **자동으로 분개(Journal Entry)를 생성**. 예전처럼 Tally 등에 별도 수기입력하던 이중작업이 사라짐.
- **영구재고(Perpetual Inventory)** 활성화 시 재고자산·COGS·"Stock Received But Not Billed"(입고했으나 미청구) 등의 계정이 재고이동과 **실시간 동기화**.
- **차원(Dimensions)·원가센터(Cost Center)**로 부서·프로젝트·제품군별 수익성 분석 → 계정 수를 늘리지 말고 차원으로 세분화하는 것이 모범.
- **핵심 재무제표**: 재무상태표(BS)·손익계산서(P&L)·시산표(TB)·현금흐름표를 실시간 생성. 은행 거래 자동 조정(reconciliation) 지원.
- **비판적 관점**: 계정을 수백 개로 늘리는 실수(volume≠completeness)를 피하고, **보고 목적에 맞춰 계정은 넓게, 세부는 차원으로** 설계하라. 잘못 분류된 계정은 분기말에 몇 주치 재작업을 유발. 계정 생성·병합·삭제 권한을 제한하고 명명 규칙을 문서화할 것.

### 추가해야 하는 정보 (웹 리서치 보강)
- **한국 특화**: ERPNext 기본 COA에는 한국 세무(부가가치세 매입/매출, 전자세금계산서, 원천징수)가 내장돼 있지 않음 → **한국 계정과목·부가세 템플릿·전자세금계산서(e-Tax) 연동을 커스텀**해야 함. (인도판은 GST/TDS 내장, 한국판은 자체 구현 필요)
- **Go-live 시 기초잔액(Opening Balance)** 이관: Stock Reconciliation(Purpose=Opening Stock)으로 재고 기초·평가액을 세팅하고, Opening Invoice Creation Tool로 미수/미지급 이월.
- **월마감 규율**: 대표 거래 유형별로 샘플 문서를 전기해 GL 전표가 의도한 계정으로 떨어지는지 검증 후 Go-live.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| GL | General Ledger | 총계정원장 | 모든 회계 거래가 계정별로 집계되는 원장. ERPNext에선 모든 제출 거래가 자동 전기 |
| COA | Chart of Accounts | 계정과목표 | 회사가 쓰는 모든 계정의 트리형 목록. ERP 세팅 1단계 |
| AR | Accounts Receivable | 매출채권 | 고객에게 받을 돈. 연령분석(aging) 리포트 제공 |
| AP | Accounts Payable | 매입채무 | 공급사에 줄 돈 |
| P&L | Profit and Loss statement | 손익계산서 | 수익·비용·이익 |
| BS | Balance Sheet | 재무상태표 | 자산=부채+자본 |
| TB | Trial Balance | 시산표 | 전 계정 잔액 목록, 차대변 일치 검증 |
| COGS | Cost of Goods Sold | 매출원가 | 판매 제품의 제조/구매에 든 총원가 |
| CWIP | Capital Work in Progress | 건설중인자산 | 아직 사용 전인 고정자산 원가 집계 계정 |
| Journal Entry | (분개/전표) | 분개장 | 차변·대변 수기 또는 자동 회계 항목 |
| Perpetual Inventory | (영구재고) | 실시간 재고회계 | 재고 이동마다 재고자산·COGS를 실시간 반영 |

### 📚 참고자료 / 논문
- ERPNext 공식 — *Chart Of Accounts*: https://docs.frappe.io/erpnext/chart-of-accounts
- Frappe 공식 — *ERP Guide: Accounting System*: https://frappe.io/erpnext/erp-guide/accounting-system
- Davenport, T. H. (1998), "Putting the Enterprise into the Enterprise System," *Harvard Business Review* — ERP 통합 회계의 고전.

---

## ② ERP 기초지식 — 제조(Manufacturing) 편 (⭐자동차 부품 핵심)

### 핵심 개념 요약
제조 모듈의 중심은 **BOM(자재명세서)**입니다. BOM에서 **Production Plan(생산계획) → Work Order(작업지시) → Job Card(작업표) → Stock Entry(재고이동)**로 흐르며, 완성품은 **backflush(역소요, BOM 기준 원자재 자동 차감)** 됩니다.

### 중요한 정보
- **다단계 BOM(Multi-level BOM)**: 완제품 BOM이 자기 자신의 BOM을 가진 하위조립품을 포함 → 트리 구조로 폭발(explode). 자동차 전장 어셈블리(PCB+하우징+커넥터+와이어)에 필수.
- **BOM 버전관리·유효일(effectivity date)**: 어떤 버전을 생산에 쓸지 통제. **제출된 BOM은 직접 수정 불가 → 취소 또는 복제** (이력추적·원가·재공 무결성 보호). 이는 **4M 변경관리(설계변경 이력)와 직결**.
- **Work Order**: 생산의 "지휘자". 원자재 이송·Job Card 생성·완성품 backflush를 트리거. 원천창고/재공(WIP)창고/목표창고/스크랩창고를 각각 지정.
- **Routing/Workstation/Operation**: 공정 순서·설비·시간·시간당 원가 정의 → **정확한 제조원가 산정 및 능력계획(capacity planning)**.
- **스크랩/공정손실(Process Loss)**: BOM에 스크랩 품목·비율 지정 가능. 실제 소비량이 BOM 계획을 초과하면 **변동(variance)으로 가시화** → 낭비 식별.
- **Quality Inspection**: 입고·공정·완성 단계에서 검사 파라미터를 정의해 품질 기준 충족 여부 확인 → 초도품/수입검사 워크플로우에 활용.
- **Subcontracting(외주가공)**: 도금·표면처리 등 공정을 외주. 원자재 이송·회수·원가를 추적.

### 추가해야 하는 정보 (자동차 부품 특화 보강)
- **이력추적(Traceability)은 Batch/Serial로 구현**: 원자재 로트 → 완제품 계보(genealogy)를 자동 캡처. IATF 16949 8.5.2 대응의 핵심(③재고 편·⑦품질 편 참조).
- **Heat Number(강재 히트번호) 추적**: 금속 부품은 소재 밀 시트(MTR)의 히트번호를 Batch로 관리하는 사례 존재.
- **표준 미탑재 → 커스텀 필요**: **PPAP 제출관리·APQP 게이트·Control Plan·PFMEA**는 ERPNext 표준에 없음 → `babipa_erp`에 커스텀 DocType으로 구축 권장.
- **MES/장비 데이터 연계**: APQP Phase 4·5(양산 검증·관리)와 PPAP의 초기공정능력(Ppk) 증빙은 **공정 실측 데이터**가 필요 → 장비 데이터 수집(MES) 연동 고려.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| BOM | Bill of Materials | 자재명세서 | 완제품 제조에 필요한 원자재·수량·공정 목록. 제조의 근간 |
| MRP | Material Requirements Planning | 자재소요계획 | BOM×수요로 필요 자재량·부족량 산출 |
| MRP II | Manufacturing Resource Planning | 제조자원계획 | MRP에 설비·인력·재무 자원 계획을 확장 |
| WIP | Work In Progress | 재공품 | 생산 진행 중 미완성 재고. 별도 WIP 창고로 관리 |
| Work Order | (작업지시서) | 작업지시 | 특정 수량 제조 지시. Job Card·자재이송 트리거 |
| Job Card | (작업표) | 작업표 | 공정별 실제 시간·인력·소비 기록 → 실제원가 |
| Routing | (라우팅) | 공정경로 | 재사용 가능한 공정 순서 세트 |
| Backflush | (백플러시) | 역소요 차감 | 완성 시 BOM 기준으로 원자재 자동 소진 처리 |
| Process Loss | (공정손실) | 공정손실 | 산출품 중 불량으로 손실된 수량 |
| S&OP | Sales and Operations Planning | 판매·운영계획 | 수요·공급 통합 계획 (ERPNext는 부분 지원) |

### 📚 참고자료 / 논문
- Frappe 공식 — *Open Source ERP for Manufacturing*: https://frappe.io/erpnext/open-source-manufacturing-erp-software
- ClefinCode — *Manufacturing in ERPNext v15* (스크랩·다단계 BOM 상세): https://clefincode.com/blog/global-digital-vibes/en/utilizing-and-handling-manufacturing-in-erpnext-v15
- Zikpro — *Bill of Materials BOM* (변형 BOM·라우팅): https://zikpro.com/erpnextdocs/bill-of-materials-bom/

---

## ③ ERP 기초지식 — 재고/창고(Stock & Warehouse) 편 (⭐이력추적 기반)

### 핵심 개념 요약
ERPNext는 **영구재고(perpetual)** 방식으로 **모든 재고이동(입고·출고·이송·제조)이 Stock Ledger를 통해 수량과 금액을 실시간 갱신**합니다. 이중 구조(상세 원장 SLE + 집계 뷰 Bin)로 성능과 감사성을 동시 확보.

### 중요한 정보
- **평가방법(Valuation Method)**: FIFO / Moving Average / LIFO / Standard Cost 지원. 품목별·회사별·전역 설정 가능(가장 구체적 설정 우선).
  - **FIFO**: 오래된 로트부터 소진. 실제 취득원가에 근접 → **로트추적·유통기한·세무보고에 적합**. 단, 계층 관리 부담 + 소급전기 시 reposting 발생.
  - **Moving Average**: 단일 혼합단가. 단순·평활 → 대량 범용품에 적합. 단, 개별 로트 실원가 추적 불가.
- **Batch/Serial 추적**: 배치(로트)·시리얼 번호로 **입고~판매 전 구간 추적** → 리콜·보증·품질관리·규제대응의 핵심. 자동차 전장부품은 **안전관련 부품은 시리얼, 범용품은 로트** 방식이 일반적.
- **재주문(Reorder)·안전재고**: 임계치 하락 시 자동 Material Request 생성 → 결품 방지.
- **Stock Reconciliation**: 실사(cycle count)와 시스템 대조, 조정 시 GL 전표 자동 생성.
- **비판적 관점**: **Allow Negative Stock는 원칙적으로 OFF** — 켜면 데이터 무결성·평가액이 왜곡됨. 창고 트리(원자재/WIP/완성품/스크랩)를 Go-live 전에 확정할 것. 재고는 대부분 Go-live에서 가장 어려운 부분으로, 잘못된 설정이 몇 주 후 "GL과 안 맞는 재고평가액"으로 드러남.

### 추가해야 하는 정보 (보강)
- **전방/후방 추적(Forward/Backward trace)**: 원자재 로트 → 이를 소비한 모든 완제품·고객(전방), 완제품 → 투입 로트(후방). ERPNext Batch 기능으로 구현하되, **리콜 시뮬레이션을 정기 실시**해 추적 완결성을 검증하라(감사 대비).
- **바코드/QR 스캔** 지원으로 입출고 정확도·속도 향상 → 현장 작업자 부담 최소화.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| SKU | Stock Keeping Unit | 재고관리단위 | 개별 관리 품목 코드 |
| FIFO | First In, First Out | 선입선출 | 먼저 들어온 재고 먼저 소진 |
| LIFO | Last In, First Out | 후입선출 | 나중 재고 먼저 소진(한국 회계기준 인정 제한적) |
| EOQ | Economic Order Quantity | 경제적 주문량 | 주문·보관 비용 최소화 주문량 |
| SLE | Stock Ledger Entry | 재고원장항목 | 모든 재고이동의 불변 기록 |
| Bin | (빈) | 재고집계 | 품목-창고별 수량 집계 뷰 |
| Batch | (배치/로트) | 로트 | 동일 조건 생산/입고 묶음. 유통기한·추적 관리 |
| Serial No | (시리얼) | 개체번호 | 개별 품목 고유번호. 안전부품 추적 |
| Traceability | (추적성) | 이력추적 | 소재~완제품 전 이력 추적 (IATF 필수) |
| Genealogy | (계보) | 자재계보 | 어느 로트가 어느 제품에 들어갔는지의 관계망 |

### 📚 참고자료 / 논문
- Frappe 공식 — *FIFO and Moving Average*: https://docs.frappe.io/erpnext/fifo-and-moving-average
- DeepWiki — *frappe/erpnext Inventory Management* (SLE/Bin/평가 소스코드 레벨): https://deepwiki.com/frappe/erpnext/5-inventory-management
- Acube — *ERPNext Warehouse & Inventory Go-Live Checklist*: https://acubeinnovations.com/resources/checklists/erpnext-warehouse-inventory-golive-checklist/

---

## ④ ERP 기초지식 — 구매/조달(Buying / Procure-to-Pay) 편

### 핵심 개념 요약
조달 흐름은 **Material Request(구매요청) → RFQ(견적요청) → Supplier Quotation(공급사 견적) → Purchase Order(발주) → Purchase Receipt(입고) → Purchase Invoice(매입송장) → Payment(지급)**의 **Procure-to-Pay(P2P)** 사이클이며, 각 단계가 재고·회계와 연동됩니다.

### 중요한 정보
- **Material Request**는 재고 재주문 레벨에 따라 자동 생성 가능하며, 승인 워크플로우를 거쳐 RFQ/PO/Supplier Quotation으로 원클릭 전환.
- **RFQ → 다수 공급사 비교**: Supplier Portal로 공급사가 직접 견적 입력 → 가격·납기 나란히 비교 → 최적안을 PO로 전환. **단독소싱(과다가격) 방지**.
- **3-Way Matching(3자 대사)**: PO ↔ 입고(GRN) ↔ 매입송장 대조 → 과지급·중복송장·공급사 부정 방지.
- **Supplier Scorecard(공급사 평가표)**: 납기·품질 성과 정기 추적 → **IATF의 공급사 관리 요구와 연결**.
- **Landed Cost(부대비용)**: 운임·관세 등을 입고품 원가에 배분 → 정확한 재고평가.

### 추가해야 하는 정보 (자동차 부품 특화 보강)
- **고객사 EDI/공급사 EDI**: HKMC 등 OEM은 발주·납품·대금을 EDI로 처리 → ERPNext에 **EDI 연동(커스텀 API/파일 인터페이스)**이 별도 필요(표준 미탑재).
- **공급사 PPAP 관리**: IATF 8.5.2.1은 **하청/2차 공급사 부품까지 추적성** 요구 → 공급사 품질인증서(CoC/MTR)를 입고·로트와 링크하는 커스텀 필요.
- **한국 세무**: 매입 전자세금계산서·원천징수(사업소득 등) 자동화는 커스텀 대상.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| RFQ | Request for Quotation | 견적요청서 | 여러 공급사에 가격·납기 요청 |
| PO | Purchase Order | 구매발주서 | 확정 발주 문서 |
| GRN | Goods Receipt Note | 입고증 | 입고 기록(ERPNext=Purchase Receipt) |
| P2P | Procure-to-Pay | 구매-지급 | 요청~지급 전 사이클 |
| 3-Way Match | (3자 대사) | 3방향 대조 | PO·입고·송장 일치 검증 |
| MR | Material Request | 구매요청 | 부서의 자재 필요 요청(구매요구) |
| Landed Cost | (부대원가) | 도착원가 | 운임·관세 포함 실입고원가 |
| CoC | Certificate of Conformance | 적합성증명서 | 공급품이 규격 충족함을 증명 |
| MTR | Mill Test Report | 소재시험성적서 | 강재 등 소재의 성분·기계적 성질 증명 |
| EDI | Electronic Data Interchange | 전자문서교환 | OEM-공급사 간 발주/납품 자동 전송 |

### 📚 참고자료 / 논문
- Frappe 공식 — *Procurement Cycle Overview*: https://docs.frappe.io/erpnext/procurement-cycle-overview
- Frappe 공식 — *Request for Quotation*: https://docs.frappe.io/erpnext/v14/user/manual/en/buying/request-for-quotation

---

## ⑤ ERP 기초지식 — 판매/CRM(Selling & CRM / Quote-to-Cash) 편

### 핵심 개념 요약
CRM은 **Lead(잠재고객) → Opportunity(영업기회) → Quotation(견적) → Sales Order(수주) → Delivery Note(납품) → Sales Invoice(매출송장)**로 이어지는 **Quote-to-Cash** 파이프라인을 관리합니다. ERPNext CRM은 6개 핵심 오브젝트(Lead, Opportunity, Prospect, Customer, Contact, Quotation)를 사용.

### 중요한 정보
- **Sales Pipeline(Kanban 보드)**: Lead→Opportunity→Quotation→Customer 여정을 한 화면에서 추적. 정체된 딜 식별.
- **Lead 상태 자동전환**: Replied/Opportunity/Quotation/Converted 등 액션에 따라 자동 갱신.
- **모범**: Lead 추가 시 항상 Contact 생성, **Customer는 결제 확정 후에만 생성** → DB 정합성 유지.
- **CRM ↔ 회계·재고 연동**: 고객정보·주문이력·재고가용성이 항상 정합 → 정확한 납기 약속.
- **B2B 특화**: 하나의 Lead에 여러 담당자(구매·품질·개발) 등록 가능 → OEM 대응에 적합.
- **주의(출처 신뢰성)**: 일부 벤더 블로그의 "파이프라인 가시성 40% 향상", "매출 28% 증가" 등 수치는 **마케팅성 사례로, 검증된 통계가 아님** → 참고만.

### 추가해야 하는 정보 (자동차 부품 특화 보강)
- **자동차 부품 B2B는 "수주가 곧 양산 요청"**: OEM의 발주계획(EDI/포캐스트)이 Sales Order·Production Plan을 구동 → CRM보다 **수주-생산 연계**가 중요.
- **BANT 프레임워크**(Budget/Authority/Need/Timeline)로 리드 스코어링 가능하나, OEM 단일고객 구조에선 CRM 비중이 낮을 수 있음.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| CRM | Customer Relationship Management | 고객관계관리 | 리드·기회·고객 소통 통합 관리 |
| SO | Sales Order | 수주(판매주문) | 고객 확정 주문. 생산·납품 트리거 |
| DO | Delivery Note | 납품서 | 출하 기록, 재고 차감 |
| Q2C | Quote-to-Cash | 견적-수금 | 견적~대금회수 전 과정 |
| Lead | (리드) | 잠재고객 | 아직 검증 안 된 잠재 매출원 |
| Opportunity | (기회) | 영업기회 | 검증된 리드(qualified) |
| BANT | Budget/Authority/Need/Timeline | 예산/결정권/필요/시기 | 리드 자격 판단 프레임워크 |
| KPI | Key Performance Indicator | 핵심성과지표 | 전환율·사이클타임 등 성과 측정 |

### 📚 참고자료 / 논문
- ERPNext 공식 — *Introduction to CRM*: https://docs.erpnext.com/docs/user/manual/en/CRM
- ERPNext 공식 — *Lead* / *Opportunity*: https://docs.erpnext.com/docs/user/manual/en/lead

---

## ⑥ ERP 기초지식 — HR / 인사·급여 편

### 핵심 개념 요약
Frappe HR(구 HRMS)는 직원마스터·근태·휴가·급여(Payroll)·경비를 관리하며, 급여는 **급여·기여금·부채 계정으로 자동 전기**되어 회계와 연동됩니다.

### 중요한 정보
- 55명 규모에서는 **근태(출퇴근)·연차관리·급여명세·4대보험 처리**가 핵심.
- 제조 현장 연계: 직원 근태·생산성을 Work Order/Job Card와 연결해 **실제 노무원가** 산정.

### 추가해야 하는 정보 (한국 특화 — 매우 중요)
- **한국 급여(4대보험·소득세·연말정산·퇴직금)는 ERPNext 표준 미탑재** → **한국 급여 로직을 커스텀 앱으로 구현하거나, 급여는 국산 급여SW를 유지하고 ERP엔 회계 결과만 전기**하는 하이브리드가 현실적. (초기엔 후자 권장)
- 55명 소기업은 **HR 모듈을 최소 범위(근태·연차·조직도)로 시작**하고, 급여는 단계적으로.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| HR/HRMS | Human Resource (Management System) | 인사관리 | 직원·근태·급여 통합 |
| Payroll | (급여) | 급여처리 | 급여계산·명세·회계전기 |
| Salary Slip | (급여명세서) | 급여명세 | 개인별 급여 계산서 |

### 📚 참고자료 / 논문
- Frappe HR 공식: https://frappe.io/hr (표준 기능 확인용)
- *한국 급여는 반드시 노무/세무 검토 병행* — 표준 ERP만으로 부족.

---

## ⑦ ERP 기초지식 — 품질관리(Quality) 편 (⭐IATF 16949 / SQ 심사 핵심)

### 핵심 개념 요약
ERPNext Quality 모듈은 **Quality Inspection(검사)·Quality Inspection Template·Quality Goal/Procedure**를 제공하며, 입고·공정·완성 단계에서 검사 파라미터를 정의합니다. 그러나 **자동차 산업 특유의 문서체계(APQP/PPAP/Control Plan/FMEA)는 표준 미탑재**입니다.

### 중요한 정보 — IATF 16949 이력추적(8.5.2)
- **IATF 16949 8.5.2.1**: 조직은 **내부·고객·규제 추적성 요구를 분석**하고, **위험/고장 심각도 기반의 추적성 계획(traceability plan)**을 문서화해야 함.
- 실무적으로 **ERP + Control Plan + FMEA**로 추적성 계획을 충족할 수 있음(업계 통설).
- **보존기간**: 부품 계보 데이터는 **통상 10~15년**(차량 서비스 수명 + 규제), 안전부품은 더 길게 요구되기도 함.
- **최대 리스크**: 이력추적 결여/불완전은 **IATF 심사의 대표적 Class A(중대) 부적합** → 생산 중단·재심사·납품 중단·최악의 경우 **인증 상실(= OEM 공급사 자격 상실)**.

### 중요한 정보 — APQP / PPAP (AIAG Core Tools)
- **APQP 5단계**: ①계획(Planning) ②제품 설계·개발 ③공정 설계·개발 ④제품·공정 검증(양산검증) ⑤피드백·평가·지속개선. Phase 1~3은 양산 전 엔지니어링, **Phase 4~5는 양산 데이터 필요**.
- **PPAP는 APQP의 최종 산출물** — 공정이 요구 부품을 일관 생산할 수 있음을 고객에게 **객관적 증거**로 제출. **PPAP 18개 요소 중 최소 5개(PFMEA·Control Plan·초기공정능력·양산 샘플·CSR)가 공정 실측 데이터**를 사용.
- **5대 Core Tools**: APQP, PPAP, FMEA, MSA, SPC — IATF 16949의 근간.
- **양산 전환 준비 중인 귀사에 직접적**: R&D→양산 전환 = APQP Phase 3→4→5 진행 + PPAP 제출. ERP는 이 데이터의 **저장·추적·증빙 인프라** 역할.

### 추가해야 하는 정보 (커스텀 설계 제안)
- `babipa_erp`에 **PPAP Submission / APQP Gate / Control Plan / PFMEA / 초도품(FAI) / 4M 변경관리** 커스텀 DocType을 만들고, Batch/Serial·Quality Inspection과 링크.
- **Excel 기반 추적은 감사에서 무너진다** — IATF 8.5.2의 "공정단계·작업자·설비파라미터·소재로트별 추적" 요구를 Excel로는 충족 어려움 → ERP화가 정답.
- **CSR(고객특정요구)**: OEM별로 IATF를 확장(예: 각 OEM의 품질시스템 요구) → HKMC의 SQ/ES 표준을 커스텀 필드로 반영.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| IATF 16949 | International Automotive Task Force 16949 | 자동차 품질경영 표준 | 자동차 부품사 필수 인증 |
| APQP | Advanced Product Quality Planning | 사전제품품질계획 | 신제품 개발 5단계 게이트 프로세스 |
| PPAP | Production Part Approval Process | 양산부품승인절차 | 양산 승인 증빙 제출(APQP 최종산출물) |
| PFMEA | Process Failure Mode and Effects Analysis | 공정 고장모드영향분석 | 공정 위험 분석 |
| DFMEA | Design FMEA | 설계 FMEA | 설계 위험 분석 |
| Control Plan | (관리계획서) | 관리계획 | 공정 관리 항목·방법 정의 |
| SPC | Statistical Process Control | 통계적공정관리 | 공정 산포 통계 관리 |
| MSA | Measurement System Analysis | 측정시스템분석 | 측정 신뢰성 검증 |
| CSR | Customer Specific Requirements | 고객특정요구사항 | OEM별 추가 요구 |
| FAI | First Article Inspection | 초도품검사 | 첫 양산품 전수 규격 검증 |
| CoC | Certificate of Conformance | 적합성증명서 | 규격 충족 증명 |
| 4M | Man/Machine/Material/Method | 4M(변경관리) | 4대 변경요소 관리 |
| RMA | Return Merchandise Authorization | 반품승인 | 불량 반품 처리 절차 |
| AIAG | Automotive Industry Action Group | 미국자동차산업협회 | Core Tools 매뉴얼 발행 |

### 📚 참고자료 / 논문
- AIAG — *Quality Core Tools (APQP·CP·PPAP·FMEA·MSA·SPC)*: https://www.aiag.org/expertise-areas/quality/quality-core-tools
- IATF 16949:2016 Clause 8.5.2.1 해설(Pretesh Biswas): https://preteshbiswas.com/2023/08/01/iatf-169492016-clause-8-5-2-1-identification-and-traceability/
- Omnex — *APQP 5 Phases*: https://www.omnex.com/apqp
- Symestic — *APQP: Phases, PPAP, Control Plans and MES*: https://www.symestic.com/en-us/what-is/apqp
- *AIAG APQP 3rd Ed. / PPAP 4th Ed. 매뉴얼* (원문 구매 권장 — GM/Ford/FCA 공동 발행)

---

## ⑧ ERP 기초지식 — 기술 아키텍처 (Frappe/ERPNext 구축) 편

### 핵심 개념 요약
ERPNext는 **Frappe Framework** 위에 구축된 오픈소스 앱입니다. Frappe는 **메타데이터 기반 로우코드 풀스택 프레임워크**로, **모든 것이 DocType**(DB 테이블+폼+클래스)입니다. Python(서버)+JavaScript(클라이언트), MariaDB, Redis(캐시/큐), Jinja(템플릿), WebSocket(실시간) 스택.

### 중요한 정보 — `babipa_erp` 전략 검증
- **"코어 미수정 + 별도 커스텀 앱" 원칙은 정확**: `bench new-app babipa_erp`로 별도 앱 생성 → `hooks.py`에서 `doc_events`(예: `Sales Invoice on_submit`)·`override_doctype_class`로 코어 동작 확장/오버라이드. **erpnext/frappe 소스는 절대 수정하지 않음** → `bench update`가 커스터마이징을 깨지 않음(upgrade-safe).
- **Developer Mode 필수**: 켜야 DocType/Custom Field 변경이 파일시스템의 **JSON으로 기록**되어 **Git 버전관리** 가능. 끄면 UI 변경이 DB에만 저장돼 업데이트 시 소실.
- **다중 테넌시(multi-tenant)**: 한 인스턴스가 사이트별 별도 DB로 다중 사이트 운영 → 망분리 인트라넷 단일 사이트 배포에 적합.
- **REST API·Webhook·Server Script·Client Script·Workflow**: 자동화 스크립트 선호하는 귀하에게 적합한 확장점.
- **Virtual DocType**: DB 테이블 없이 외부 데이터소스(예: 시험장비 DB) 연동 UI 제공 가능.

### 추가해야 하는 정보 — 라이선스·배포
- **GPL v3 준수 원칙 정확**: Frappe/ERPNext는 GPLv3(일부 AGPL 요소 검토 필요). **사내 인트라넷 전용 배포(외부 배포 없음)**면 소스공개 의무가 실질적으로 발생하지 않으나, **화이트라벨(브랜딩 제거)** 시 상표/로고 정책과 GPL 조항을 별도 확인할 것.
- **망분리 환경**: 오프라인 설치(bench 오프라인)·내부 미러 저장소·정기 백업(bench backup)·업데이트 절차를 사전 설계.
- **비판적 관점**: **커스텀 앱이 늘수록 업그레이드·테스트 부담 증가** → 학술 연구가 지목하는 "과도한 커스터마이징" 실패요인. **표준으로 되는 것은 표준으로, 정말 필요한 것만 커스텀**하라. Pre-commit·CI/CD·자동 테스트를 초기부터 도입 권장.

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| DocType | (독타입) | 데이터모델 | Frappe의 기본 빌딩블록(테이블+폼+로직) |
| DocField | (독필드) | 필드 | DocType 내 개별 필드 |
| hooks.py | (훅스) | 훅 파일 | 코어 이벤트에 커스텀 로직 연결 |
| Bench | (벤치) | 관리 CLI | Frappe 사이트/앱 관리 도구 |
| ORM | Object-Relational Mapping | 객체관계매핑 | SQL 없이 DB 조작 |
| GPL v3 | GNU General Public License v3 | 카피레프트 라이선스 | 파생물 소스공개 의무(배포 시) |
| Multi-tenant | (멀티테넌트) | 다중테넌시 | 사이트별 DB 격리 |
| Developer Mode | (개발자모드) | 개발모드 | 스키마를 JSON파일로 기록(Git) |
| upgrade-safe | (업그레이드 안전) | 업그레이드 내성 | 코어 미수정으로 업데이트 안 깨짐 |

### 📚 참고자료 / 논문
- Frappe 공식 — *Framework* / *DocType* / *Apps*: https://frappe.io/framework , https://docs.frappe.io/framework/user/en/basics/apps
- David Muraya — *Mastering ERPNext Development: Custom Apps*: https://davidmuraya.com/blog/develop-erpnext-custom-app/
- Hybrowlabs — *Framework Architecture & Core Concepts* (override 예시): https://hybrowlabs.com/customer-resources/frappe-technical-overview/framework-architecture

---

## ⑨ ERP 기초지식 — 도입 방법론 / 성공·실패요인 편

### 핵심 개념 요약
학술 연구(1998~2019 SME ERP 문헌 리뷰)는 ERP 성공이 **소프트웨어가 아니라 조직·데이터·프로세스**에 달려 있음을 반복 확인합니다.

### 중요한 정보 — 성공요인(CSF) / 실패요인
| 성공요인(CSF) | 실패요인(반대) |
|---|---|
| 최고경영진의 강력한 지원·자금 | 경영진 무관심 |
| 명확한 목표·범위(scope) 정의 | 범위 확장(scope creep) |
| **깨끗한 마스터데이터**(품목·BOM·거래처) | 부정확한 데이터 이관 |
| 교육·변화관리(사용자 수용) | 사용자 저항·미숙련 |
| **최소 커스터마이징**(표준 프로세스 채택) | 과도한 커스터마이징 |
| 단계적 Go-live·프로젝트 관리 | 빅뱅 무리한 전환 |

- **마스터데이터가 최우선**: ERPNext 제조는 깨끗한 Item 데이터(품목코드·UOM·평가방법·창고·로트/시리얼 여부·재주문·리드타임)에 크게 의존 → **품목 정리 후 생산 세팅**.

### 추가해야 하는 정보 (귀사 맞춤 단계 제안 → Recommendations 참조)

### ⚠️ 용어/약어 설명 (필수)
| 약어 | 영문 풀네임 | 한글 뜻 | 실무적 의미 |
|---|---|---|---|
| CSF | Critical Success Factor | 핵심성공요인 | 도입 성공을 좌우하는 요소 |
| ROI | Return on Investment | 투자수익률 | 도입 투자 대비 효과 |
| TCO | Total Cost of Ownership | 총소유비용 | 도입+운영+유지 전체 비용 |
| Go-live | (고라이브) | 본가동 | 실제 운영 전환 시점 |
| Master Data | (마스터데이터) | 기준정보 | 품목·거래처·BOM 등 기초 데이터 |
| Scope Creep | (스코프 크립) | 범위확장 | 통제 안 된 요구 증가(실패요인) |

### 📚 참고자료 / 논문
- *Critical success factors of ERP implementation in SMEs* (2019), Journal of Project Management, Growingscience: https://www.growingscience.com/jpm/Vol4/jpm_2019_17.pdf
- Nah, F. F. H., Lau, J. L. S., & Kuang, J. (2001), "Critical factors for successful implementation of enterprise systems," *Business Process Management Journal*, 7(3), 285–296.
- Leyh, C. (2012/2015), "Critical Success Factors for ERP System Implementation Projects: An Update of Literature Reviews," Springer: https://link.springer.com/chapter/10.1007/978-3-319-17587-4_3
- Koh, S.C.L. & Simpson, M. (2005), "Change and uncertainty in SME manufacturing environments using ERP," *Journal of Manufacturing Technology Management*, 16(6), 629–653.
- Davenport, T. H. (1998), "Putting the Enterprise into the Enterprise System," *Harvard Business Review*.

---

# Recommendations (단계별 실행 권고)

### 0단계 — 폴더 문서 확보(선행)
- `ai_erp` 폴더 파일을 **Google Docs로 변환**하거나 본문을 붙여넣어 재요청 → 실제 문서 기반 정리 반영. (현재 커넥터로는 비-Docs 파일 접근 불가)

### 1단계 (0~1개월) — 기반 설계
- [ ] **마스터데이터 정비 최우선**: 품목코드 체계·UOM·평가방법(FIFO 권장, 로트추적 유리)·창고 트리(원자재/WIP/완성품/스크랩) 확정.
- [ ] 한국 COA·부가세 템플릿 설계, `babipa_erp` 앱 스캐폴딩 + **Developer Mode + Git + Pre-commit** 세팅.
- [ ] **Allow Negative Stock = OFF**, Perpetual Inventory = ON.

### 2단계 (1~3개월) — 핵심 모듈 + 이력추적
- [ ] Item→BOM(다단계)→Work Order→Job Card 흐름 구축, 대표 제품 1종으로 파일럿.
- [ ] **Batch/Serial 이력추적 설계** + 리콜 시뮬레이션 테스트(전방/후방 추적 검증).
- [ ] 구매 P2P(3-way match)·판매 Q2C 세팅. 급여는 국산SW 유지 + 회계 결과만 전기(하이브리드).

### 3단계 (3~6개월) — 자동차 특화 커스텀
- [ ] `babipa_erp`에 **PPAP·APQP·Control Plan·PFMEA·FAI·4M 변경관리** 커스텀 DocType 구축, Batch/Quality Inspection과 링크.
- [ ] HKMC EDI/CSR·전자세금계산서 인터페이스 검토.
- [ ] 망분리 오프라인 설치·백업·업데이트 SOP 문서화.

### 벤치마크(권고를 바꿀 임계치)
- **커스텀 DocType 수 > 표준 대비 과다** → 커스터마이징 재검토(실패요인 신호).
- **재고평가액 vs GL 정기 대사 불일치** → Go-live 전 세팅 오류 → 진행 중단·수정.
- **리콜 시뮬레이션에서 추적 단절** → IATF 8.5.2 미충족 → 심사 전 필수 보완.

---

# Caveats (주의사항)
- **본 보고서는 `ai_erp` 폴더 문서를 반영하지 못했습니다** — 커넥터의 비-Docs 파일 접근 한계 때문. 문서 기반 정리가 필요하면 0단계 참조.
- **한국 세무·급여·4대보험·전자세금계산서는 ERPNext 표준 미탑재** → 커스텀 또는 하이브리드 필수. 반드시 세무사/노무사 검토 병행.
- **PPAP/APQP/Control Plan/FMEA는 ERPNext 표준에 없음** — 커스텀 개발 또는 전용 품질SW(EwQIMS 등) 병행 검토.
- 일부 인용 수치("가시성 40%↑", "매출 28%↑" 등)는 **벤더 마케팅 사례로 검증된 통계가 아님** → 의사결정 근거로 삼지 말 것.
- **GPL v3·화이트라벨·망분리 배포**의 법적 세부는 전문가(오픈소스 라이선스 검토) 확인 권장.
- AIAG Core Tools 매뉴얼(APQP/PPAP 등)은 **유료 원문 구매**가 정확 — 웹 요약은 보조 참고용.