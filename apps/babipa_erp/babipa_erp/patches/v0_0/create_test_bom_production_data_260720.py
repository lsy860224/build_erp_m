"""BOM 정전개/역전개 + 생산실행(Work Order/Job Card/다운타임) 데모용 TEST 데이터 생성.

배경: 사용자 요청("정전개/역전개 전부 가능하도록")에 따라 BOM Explosion(정전개)·Where Used
Report(역전개)를 실제로 시연할 수 있는 최소 BOM 트리가 필요하다. 실제 임포트된 289개
부품코드(docs/decisions.md 2026.07.20 Serial/Batch 결정 참조)에는 아직 실제 자재구성이
확정되지 않았으므로, 그 위에 가짜 BOM을 지어내지 않고 `TEST-` 접두사 전용 Item Group/
Item으로 완전히 분리된 2단 BOM(TEST-FG-0001 → TEST-SFG-0001 → TEST-RM-0001/0002,
TEST-FG-0001 자체도 TEST-RM-0003/0004 소모)을 만든다 — 이 패치가 실 Item 마스터를
전혀 건드리지 않는지는 `docs/decisions.md`의 검증 절차대로 Item 개수(299건) 불변 여부로
확인한다.

Work Order/Job Card는 create_manufacturing_masters_260720.py가 먼저 만든 Workstation/
Operation을 그대로 사용한다. Job Card 1건(PC 공정)은 실적차이(48/50, 2 loss)를 반영해
`Completed`로 마감해 생산실행 데이터의 실적-계획 차이 리포팅을 시연하고, 나머지 3건은
`Open` 상태로 남겨 진행중 생산 상태를 보여준다 — Job Card 완료에는 최소 1개의
`time_logs` 행이 있어야 하며(ERPNext v16 확인, `employee`는 자식 테이블 레벨에서
필수가 아님, `Manufacturing Settings.enforce_time_logs`도 이 사이트는 비활성으로 확인),
가짜 Employee/HR 데이터를 지어내지 않기 위해 employee 필드는 비워둔다.
"""

import frappe
from frappe.utils import add_to_date, now_datetime, nowdate

TEST_ITEM_GROUPS = [
	("테스트용 (TEST DATA)", "All Item Groups", 1),
	("TEST-완제품", "테스트용 (TEST DATA)", 0),
	("TEST-반제품", "테스트용 (TEST DATA)", 0),
	("TEST-원재료", "테스트용 (TEST DATA)", 0),
	("TEST-부재료", "테스트용 (TEST DATA)", 0),
]

TEST_ITEMS = [
	("TEST-FG-0001", "테스트 완제품 A", "TEST-완제품"),
	("TEST-SFG-0001", "테스트 반제품 PCB ASSY", "TEST-반제품"),
	("TEST-RM-0001", "테스트 원재료 PCB 기판", "TEST-원재료"),
	("TEST-RM-0002", "테스트 원재료 커넥터", "TEST-원재료"),
	("TEST-RM-0003", "테스트 원재료 하우징", "TEST-원재료"),
	("TEST-RM-0004", "테스트 부재료 나사", "TEST-부재료"),
]


def execute():
	if not frappe.db.exists("DocType", "Equipment"):
		return

	_create_test_item_groups()
	_create_test_items()
	bom_a = _create_bom_a()
	bom_b = _create_bom_b()
	wo_a = _create_work_order("TEST-SFG-0001", bom_a, 50)
	wo_b = _create_work_order("TEST-FG-0001", bom_b, 20)
	job_cards_a = _create_job_cards(wo_a)
	job_cards_b = _create_job_cards(wo_b)
	if job_cards_a:
		_complete_job_card_with_shortfall(job_cards_a[0], produced_qty=48, loss_qty=2)
	pc_job_card = job_cards_a[0] if job_cards_a else None
	as_job_card = frappe.db.get_value("Job Card", {"work_order": wo_b, "operation": "조립 (AS)"}, "name")
	_create_downtime_logs(pc_job_card, as_job_card)
	frappe.db.commit()


def _create_test_item_groups():
	for name, parent, is_group in TEST_ITEM_GROUPS:
		if frappe.db.exists("Item Group", name):
			continue
		frappe.get_doc(
			{"doctype": "Item Group", "item_group_name": name, "parent_item_group": parent, "is_group": is_group}
		).insert(ignore_permissions=True)


def _create_test_items():
	for item_code, item_name, item_group in TEST_ITEMS:
		if frappe.db.exists("Item", item_code):
			continue
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_name,
				"item_group": item_group,
				"stock_uom": "EA",
				"is_stock_item": 1,
			}
		).insert(ignore_permissions=True)


def _create_bom_a():
	existing = frappe.db.exists("BOM", {"item": "TEST-SFG-0001", "is_default": 1})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "BOM",
			"item": "TEST-SFG-0001",
			"company": "BABIPA",
			"quantity": 1,
			"currency": "KRW",
			"conversion_rate": 1,
			"with_operations": 1,
			"items": [
				{"item_code": "TEST-RM-0001", "qty": 1, "uom": "EA", "rate": 5000},
				{"item_code": "TEST-RM-0002", "qty": 4, "uom": "EA", "rate": 500},
			],
			"operations": [
				{"operation": "PCB ASSY·SMT (PC)", "workstation": "WS-PC-01", "time_in_mins": 15},
			],
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


def _create_bom_b():
	existing = frappe.db.exists("BOM", {"item": "TEST-FG-0001", "is_default": 1})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "BOM",
			"item": "TEST-FG-0001",
			"company": "BABIPA",
			"quantity": 1,
			"currency": "KRW",
			"conversion_rate": 1,
			"with_operations": 1,
			"items": [
				{"item_code": "TEST-SFG-0001", "qty": 1, "uom": "EA", "rate": 6000},
				{"item_code": "TEST-RM-0003", "qty": 1, "uom": "EA", "rate": 3000},
				{"item_code": "TEST-RM-0004", "qty": 4, "uom": "EA", "rate": 50},
			],
			"operations": [
				{"operation": "후가공 (PP)", "workstation": "WS-PP-01", "time_in_mins": 10},
				{"operation": "조립 (AS)", "workstation": "WS-AS-01", "time_in_mins": 20},
				{"operation": "검사·포장 (QT)", "workstation": "WS-QT-01", "time_in_mins": 5},
			],
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


def _create_work_order(production_item, bom_no, qty):
	existing = frappe.db.exists("Work Order", {"production_item": production_item, "bom_no": bom_no})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Work Order",
			"production_item": production_item,
			"bom_no": bom_no,
			"qty": qty,
			"company": "BABIPA",
			"planned_start_date": nowdate(),
			"wip_warehouse": "Work In Progress - B",
			"fg_warehouse": "Finished Goods - B",
		}
	)
	doc.set_work_order_operations()
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


def _create_job_cards(work_order):
	existing = frappe.get_all("Job Card", filters={"work_order": work_order}, pluck="name")
	if existing:
		return existing

	from erpnext.manufacturing.doctype.work_order.work_order import make_job_card

	wo = frappe.get_doc("Work Order", work_order)
	operations = [{"name": d.name, "qty": wo.qty} for d in wo.operations]
	try:
		make_job_card(wo.name, operations)
	except frappe.ValidationError:
		# make_job_card는 마지막 반복에서 잔여 배치 계산 중 스퍼리어스 예외를 던지는
		# 경우가 있으나(2026.07.20 개발 사이트에서 직접 확인), 그 시점 이전에 실제
		# Job Card는 이미 정상 생성돼 있어 예외를 무시하고 결과만 재조회한다.
		pass
	return frappe.get_all("Job Card", filters={"work_order": work_order}, pluck="name")


def _complete_job_card_with_shortfall(job_card_name, produced_qty, loss_qty):
	doc = frappe.get_doc("Job Card", job_card_name)
	if doc.docstatus == 1:
		return
	start = add_to_date(now_datetime(), hours=-2)
	end = now_datetime()
	doc.append(
		"time_logs",
		{"from_time": start, "to_time": end, "time_in_mins": 120, "completed_qty": produced_qty},
	)
	doc.total_completed_qty = produced_qty
	doc.process_loss_qty = loss_qty
	doc.save(ignore_permissions=True)
	doc.submit()


def _create_downtime_logs(pc_job_card, as_job_card):
	entries = [
		("WS-PC-01", pc_job_card, "설비고장", -3, 30, "SMT 마운터 노즐 이상으로 30분 정지"),
		("WS-AS-01", as_job_card, "자재대기", -1, 15, "커넥터 자재 입고 지연"),
		("WS-PP-01", None, "정기점검", -5, 20, "정기 예방점검"),
	]
	for workstation, job_card, reason, hours_ago, minutes, remarks in entries:
		# 상대 시각(now 기준)이라 재실행 시마다 값이 달라짐 — workstation+사유+Job Card
		# 조합으로 존재 여부를 판단해 중복 생성을 막는다(정확한 시각 일치가 아님).
		if frappe.db.exists(
			"Production Downtime Log", {"workstation": workstation, "downtime_reason": reason, "job_card": job_card}
		):
			continue
		start = add_to_date(now_datetime(), hours=hours_ago)
		end = add_to_date(start, minutes=minutes)
		frappe.get_doc(
			{
				"doctype": "Production Downtime Log",
				"workstation": workstation,
				"job_card": job_card,
				"downtime_reason": reason,
				"start_datetime": start,
				"end_datetime": end,
				"remarks": remarks,
			}
		).insert(ignore_permissions=True)
