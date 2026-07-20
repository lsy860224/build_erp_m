"""`docs/품목코드_260720.xlsx`(289건, 15컬럼) 실데이터를 Item 마스터로 임포트.

배경·설계 근거는 `docs/item-doctype-design.md`(Item DocType 필드 매핑) +
`docs/decisions.md`(2026.07.20 항목들, Serial/Batch·Item Group·stock_uom 공백 처리
확정)를 그대로 따른다 — 이 patch는 그 결정을 코드로 옮기는 것뿐이며 재판단하지 않는다.

**원본 데이터를 이 파일에 리터럴로 박아넣지 않는다.** `create_finished_goods_qi_template_
shells.py`(2026.07.20, 완제품 21건 QI Template 껍데기) 선례는 품목코드·항목명만 다뤄
민감도가 낮았지만, 이번엔 실제 매출/매입단가(원화 금액)가 포함돼 있어 성격이 다르다.
`docs/decisions.md`가 "실제 영업기밀(단가 등)이 담긴 원본 데이터 파일은 이 저장소가
public인 한 절대 커밋하지 않는다"고 명시했는데, 코드에 값을 리터럴로 박아넣는 것도 같은
정보를 다른 형태로 커밋하는 것과 동일한 위험이라고 판단했다. 대신 이 patch는 런타임에
`./data/item_master_260720.xlsx`(이 파일과 같은 디렉토리, `.gitignore` 등록됨, 원본을
그대로 복사해둔 작업용 사본)를 직접 읽는다. 그 사본이 없는 환경(공개 clone, CI 등)에서는
조용히 스킵한다 — 이 프로젝트에서 이미 확립된 "원본 xlsx는 로컬 전용" 원칙과 동일한 결을
유지하되, 289건 전체를 코드로 재현하지 않는 방식으로 확장했다.

임포트 규칙 요약(전부 사용자 확정, 여기서 재판단하지 않음):
1. 품목구분 → item_group (Level 1 그대로 + 반제품/원재료 中 중분류가 '일반반제품'
   또는 'PCB ASSY'인 경우만 하위 그룹으로 승격 — `docs/item-doctype-design.md` §1.2).
2. Serial/Batch — 완제품 21건=Serial, 나머지=Batch, 단 스퀴지 2건
   (`A6160-00001`/`A6160-00002`)은 둘 다 0.
3. stock_uom — 원본 값 있으면 그대로(EA/g), 공백이면 전부 "EA"로 일괄 기본값. "EA"/"g"
   UOM 마스터가 사이트에 없으면 먼저 만든다.
4. 매출/매입단가 → Item Price(Standard Selling/Standard Buying). 외주단가는 289건 전부
   공백이라 생성 없음.
5. 고객품번(customer_items) — 289건 전부 공백이라 아무것도 하지 않음.
6. Custom Field 11개 매핑.
7. inspection_required_before_delivery/purchase — 검사구분이 '무검사'가 아니면 1.
8. 완제품 21건의 quality_inspection_template — 선행 patch
   (`create_finished_goods_qi_template_shells.py`)가 만든 템플릿과 품목코드+항목명으로
   1:1 매칭(템플릿 이름 규칙이 `<품목코드> - <항목명>`이라 동적으로 계산 가능, 재하드코딩
   불필요).

멱등성: 이미 존재하는 Item/Item Price/UOM은 건너뛴다(`frappe.db.exists`). 재실행해도
안전하다 — `create_finished_goods_qi_template_shells.py`와 같은 패턴.
"""

import os

import frappe

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "item_master_260720.xlsx")

EXPECTED_HEADER = [
	"품목구분",
	"제조유형",
	"고객품번",
	"품목코드",
	"항목명(품명)",
	"중분류",
	"모델",
	"규격",
	"단위",
	"매출단가",
	"매입단가",
	"외주단가",
	"검사구분",
	"작업공정",
	"Array수량(캐비티)",
]

DEFAULT_STOCK_UOM = "EA"

# 추적 대상에서 제외되는 소모성 도구 2건 (2026.07.20 사용자 확인, docs/decisions.md 참조).
SERIAL_BATCH_EXCLUDED = {"A6160-00001", "A6160-00002"}


def execute():
	if not frappe.db.exists("DocType", "Item"):
		return

	if not os.path.exists(DATA_FILE):
		frappe.logger().warning(
			"[import_item_master_260720] %s 없음 — 이 환경에는 원본 사본이 없어 289건 "
			"Item 임포트를 건너뜁니다. 로컬 개발 사이트에서만 실행되는 것이 정상입니다.",
			DATA_FILE,
		)
		return

	try:
		import openpyxl
	except ImportError:
		frappe.logger().warning(
			"[import_item_master_260720] openpyxl 모듈이 없어 289건 Item 임포트를 "
			"건너뜁니다."
		)
		return

	rows = _read_rows(openpyxl)
	if rows is None:
		return

	_ensure_uom_masters(rows)

	created, skipped = 0, 0
	for row in rows:
		if _create_item(row):
			created += 1
		else:
			skipped += 1

	frappe.logger().info(
		"[import_item_master_260720] Item 임포트 완료: 생성 %d건, 기존/스킵 %d건",
		created,
		skipped,
	)


def _read_rows(openpyxl):
	wb = openpyxl.load_workbook(DATA_FILE, data_only=True)
	ws = wb.active
	all_rows = list(ws.iter_rows(values_only=True))
	header = list(all_rows[0])

	if header != EXPECTED_HEADER:
		frappe.logger().warning(
			"[import_item_master_260720] xlsx 헤더가 설계 시점과 다릅니다(%s) — "
			"임포트를 중단합니다. 컬럼 매핑을 다시 확인하세요.",
			header,
		)
		return None

	rows = []
	for raw in all_rows[1:]:
		record = dict(zip(header, raw))
		if not record.get("품목코드"):
			continue
		rows.append(record)
	return rows


def _ensure_uom_masters(rows):
	needed = {DEFAULT_STOCK_UOM}
	for row in rows:
		unit = row.get("단위")
		if unit:
			needed.add(str(unit).strip())

	for uom_name in needed:
		if frappe.db.exists("UOM", uom_name):
			continue
		doc = frappe.get_doc({"doctype": "UOM", "uom_name": uom_name})
		doc.insert(ignore_permissions=True)


def _resolve_item_group(item_type: str, sub_category):
	sub_category = (sub_category or "").strip() if isinstance(sub_category, str) else sub_category

	if item_type == "반제품":
		if sub_category == "일반반제품":
			return "일반반제품"
		if sub_category == "PCB ASSY":
			return "PCB ASSY(반제품)"
		return "반제품"
	if item_type == "원재료":
		if sub_category == "PCB ASSY":
			return "PCB ASSY(원재료)"
		return "원재료"
	if item_type == "완제품":
		return "완제품"
	if item_type == "부재료":
		return "부재료"
	if item_type == "상품":
		return "상품"

	frappe.throw(f"알 수 없는 품목구분: {item_type!r} — docs/decisions.md 확정 분류(완제품/반제품/원재료/부재료/상품)에 없음")


def _resolve_serial_batch(item_code: str, item_type: str):
	if item_code in SERIAL_BATCH_EXCLUDED:
		return 0, 0
	if item_type == "완제품":
		return 1, 0
	return 0, 1


def _create_item(row: dict) -> bool:
	item_code = str(row["품목코드"]).strip()
	if frappe.db.exists("Item", item_code):
		return False

	item_type = row.get("품목구분")
	item_name = row.get("항목명(품명)") or item_code
	sub_category = row.get("중분류")
	inspection_type = row.get("검사구분")

	stock_uom = row.get("단위")
	stock_uom = str(stock_uom).strip() if stock_uom else DEFAULT_STOCK_UOM

	has_serial_no, has_batch_no = _resolve_serial_batch(item_code, item_type)
	inspection_required = 0 if inspection_type == "무검사" else 1

	array_qty = row.get("Array수량(캐비티)")

	doc = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item_name,
			"item_group": _resolve_item_group(item_type, sub_category),
			"stock_uom": stock_uom,
			"has_serial_no": has_serial_no,
			"has_batch_no": has_batch_no,
			"inspection_required_before_delivery": inspection_required,
			"inspection_required_before_purchase": inspection_required,
			"custom_manufacturing_type": row.get("제조유형") or None,
			"custom_legacy_sub_category": sub_category or None,
			"custom_vehicle_model": row.get("모델") or None,
			"custom_specification": row.get("규격") or None,
			"custom_inspection_type": inspection_type or None,
			"custom_default_operation": row.get("작업공정") or None,
			"custom_array_qty": array_qty if array_qty is not None else 0,
		}
	)

	if item_type == "완제품":
		template_name = f"{item_code} - {item_name}"
		if frappe.db.exists("Quality Inspection Template", template_name):
			doc.quality_inspection_template = template_name

	doc.insert(ignore_permissions=True)

	_create_item_prices(row, item_code, stock_uom)

	return True


def _create_item_prices(row: dict, item_code: str, stock_uom: str):
	sell_rate = row.get("매출단가")
	if sell_rate is not None:
		_create_item_price(item_code, "Standard Selling", sell_rate, stock_uom, selling=1)

	buy_rate = row.get("매입단가")
	if buy_rate is not None:
		_create_item_price(item_code, "Standard Buying", buy_rate, stock_uom, buying=1)

	# 외주단가(공급업체별 매입단가)는 원본 289건 전부 공백이라 생성하지 않는다
	# (docs/item-doctype-design.md §2 #12 참조).


def _create_item_price(item_code, price_list, rate, uom, selling=0, buying=0):
	if frappe.db.exists(
		"Item Price",
		{"item_code": item_code, "price_list": price_list, "selling": selling, "buying": buying},
	):
		return

	doc = frappe.get_doc(
		{
			"doctype": "Item Price",
			"item_code": item_code,
			"price_list": price_list,
			"price_list_rate": rate,
			"uom": uom,
			"selling": selling,
			"buying": buying,
			"currency": "KRW",
		}
	)
	doc.insert(ignore_permissions=True)
