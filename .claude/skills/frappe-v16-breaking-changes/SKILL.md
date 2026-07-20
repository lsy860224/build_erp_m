---
name: frappe-v16-breaking-changes
description: Frappe/ERPNext version-16 코드를 작성·리뷰할 때 항상 사용. v15 관용구를 그대로 쓰면 조용히 틀리는 v16 변경사항(Serial/Batch 데이터 구조, 정렬 기본값, whitelisted method 제약 등)을 다룬다.
---

# v16은 v15와 다르게 동작하는 지점이 있다

이 프로젝트는 `version-16`으로 구축됐다(`docs/dev-environment.md`). 웹에 있는 예시 코드·과거
학습 데이터는 v15 이하 기준인 경우가 많아, 그대로 따라 하면 **에러 없이 조용히 틀린 값을
반환**하는 패턴이 있다. 코드 작성·리뷰 시 아래를 확인한다.

## 1. Serial/Batch는 문서 필드에 직접 없다 — Bundle을 거쳐야 한다

v15부터 거래 문서(Stock Entry, Delivery Note, Sales Invoice 등)의 시리얼/배치 정보는
`Serial and Batch Bundle`이라는 별도 DocType에 저장된다.

```python
# ❌ 틀림 — v15 이전 패턴. 필드 자체가 비어 있어 항상 빈 값을 반환한다
serial_no = doc.items[0].serial_no
batch_no = doc.items[0].batch_no

# ✅ 맞음 — Item Row의 serial_and_batch_bundle 링크를 따라 Bundle의 entries를 조회
bundle_name = doc.items[0].serial_and_batch_bundle
if bundle_name:
    bundle = frappe.get_doc("Serial and Batch Bundle", bundle_name)
    for entry in bundle.entries:
        serial_no = entry.serial_no   # Serial 품목인 경우
        batch_no = entry.batch_no     # Batch 품목인 경우
        qty = entry.qty
```

이력추적(traceability) 커스텀 로직(원자재 로트→완제품 계보 등)은 전부 이 경로로 조회해야
한다 — `babipa_erp`의 추적 관련 코드에서 특히 주의. 전방/후방 추적 자체는 v16의 내장
**Serial & Batch Traceability Report**를 우선 활용하고, 커스텀은 HKMC 제출 양식 변환 등
표준이 못 채우는 부분에만 제한한다.

## 2. 정렬 기본값이 `modified` → `creation`으로 바뀌었다

리스트뷰·`frappe.get_all`/`get_list` 모두 기본 정렬 기준이 바뀌었다. "가장 최근 등록순"을
전제로 한 로직(예: 최신 Batch를 가정하고 `[0]` 인덱스만 사용)은 `order_by`를 명시하지 않으면
의도와 다른 레코드를 집을 수 있다.

```python
# 정렬을 실제로 의존하는 쿼리는 항상 명시
frappe.get_all("Quality Inspection", filters={...}, order_by="modified desc")
```

## 3. `frappe.get_all`/`get_list`가 Query Builder 백엔드로 바뀌었다

동작은 대체로 호환되지만, 복잡한 필터 관용구(중첩 OR, 서브쿼리성 필터 등)를 쓰는 코드는
v16에서 결과가 달라질 수 있다 — 새로 짜는 복잡한 필터는 실제 사이트에서 결과를 확인하고
넘어간다.

## 4. 상태 변경 whitelisted method는 POST 전용이다

```python
# ❌ GET으로 상태를 바꾸는 API — v16에서 거부됨
@frappe.whitelist(methods=["GET"])
def approve_inspection(name): ...

# ✅ 상태를 바꾸는 호출은 POST
@frappe.whitelist(methods=["POST"])
def approve_inspection(name): ...
```

Client Script/프론트엔드에서 `frappe.call`로 상태 변경 API를 호출할 때도 GET을 쓰지 않는다.

## 5. `sanitize_html`이 `nh3` 기반으로 바뀌었다 — 이스케이프가 아니라 통째로 제거

금지된 HTML 태그/속성은 이스케이프(`&lt;script&gt;`)되는 게 아니라 **결과에서 통째로
사라진다.** 사용자 입력을 HTML 필드(Text Editor 등)에 저장·표시하는 코드에서 "왜 태그가
그대로 안 남고 사라지지"라는 증상이 나오면 이 변경 때문일 가능성이 높다 — 이스케이프
버그가 아니라 정책상 정상 동작이다.

## 6. Report/Page JS는 IIFE로 로드된다 — 전역 변수 공유 금지

커스텀 Report나 Page의 JS에서 다른 스크립트와 전역 변수를 공유하도록 짠 코드는 v16에서
스코프가 격리돼 참조가 끊긴다. 스크립트 간 상태 공유가 필요하면 `frappe.provide()` 네임스페이스나
명시적 모듈 패턴을 쓴다.

## 7. 시스템 요구사항 (환경 구성 시 확인)

| 구성요소 | v16 필수 |
|---|---|
| Python | ≥3.14, <3.15 (구버전은 신문법 SyntaxError로 import 자체 불가) |
| Node.js | 24 LTS |
| MariaDB | 10.6+ 권장 |

## 근거

`docs/research/ERPNext_가이드_검토_및_v16_빌드권고_2026-07-16.md` §2.3·§3-③·§6.5.
