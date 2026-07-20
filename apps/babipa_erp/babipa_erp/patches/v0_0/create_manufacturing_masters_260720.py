"""SMT·후가공·조립 라인 Workstation/Equipment/일일점검 예시 데이터 생성.

배경: 사용자 요청("SMT, 후가공, 조립 전반 + 장비 데이터 + 일일 점검")에 따라 제조 실행
데이터의 기반이 되는 Workstation·Equipment·Equipment Daily Inspection 인스턴스를 생성한다.
Workstation Type/Operation(PP/PC/AS/QT)은 이미 fixture로 반영됐으므로 이 패치는 그 위에
얹히는 1:1 인스턴스 데이터만 다룬다 — Workstation은 production_capacity/status 등 운영 중
실제로 바뀌는 상태 필드를 갖고 있어 fixture가 아니라 patch로 관리한다(매 migrate마다
재동기화되면 실사용 편집이 덮어써지는 문제 회피, QI템플릿 패치와 동일 판단).

장비(Equipment)는 SMT/후가공/조립 도메인에서 실제로 흔히 쓰이는 장비 유형(SMT 마운터,
리플로우 오븐, AOI, SPI, 초음파세정기, 라우터, 압입기, 토크드라이버, 지그)으로 채우되,
제조사/모델/교정성적서번호는 실제 보유 장비를 확인하기 전까지 절대 지어내지 않고 공란으로
남긴다 — 교정대상 장비(AOI/SPI/토크드라이버)만 calibration_required=1로 표시하고 성적서
번호는 비워둔다.
"""

import frappe
from frappe.utils import add_days, nowdate

WORKSTATIONS = [
	("WS-PC-01", "SMT", "PCB ASSY·SMT 1라인"),
	("WS-PC-02", "SMT", "PCB ASSY·SMT 2라인"),
	("WS-PP-01", "후가공", "후가공 1라인"),
	("WS-PP-02", "후가공", "후가공 2라인"),
	("WS-AS-01", "조립", "조립 1라인"),
	("WS-AS-02", "조립", "조립 2라인"),
	("WS-QT-01", "검사·포장", "검사·포장 1라인"),
	("WS-QT-02", "검사·포장", "검사·포장 2라인"),
]

# (장비코드, 장비명, 장비유형, 워크스테이션, 교정대상여부)
EQUIPMENT = [
	("EQ-PC-01", "SMT 마운터 1호기", "SMT 마운터", "WS-PC-01", 0),
	("EQ-PC-02", "리플로우 오븐 1호기", "리플로우 오븐", "WS-PC-01", 0),
	("EQ-PC-03", "AOI 검사기 1호기", "AOI", "WS-PC-02", 1),
	("EQ-PC-04", "SPI 검사기 1호기", "SPI", "WS-PC-02", 1),
	("EQ-PP-01", "초음파세정기 1호기", "초음파세정기", "WS-PP-01", 0),
	("EQ-PP-02", "라우터 1호기", "라우터", "WS-PP-02", 0),
	("EQ-AS-01", "압입기 1호기", "압입기", "WS-AS-01", 0),
	("EQ-AS-02", "토크드라이버 1호기", "토크드라이버", "WS-AS-02", 1),
	("EQ-QT-01", "검사지그 1호기", "지그", "WS-QT-01", 0),
]

TBD_NOTE = "2026.07.20 예시 데이터 생성 — 실제 제조사/모델/교정성적서 확인 전까지 공란 유지, 실사용 전 설비관리 담당자가 채울 것"

# (장비코드, 점검일자 offset, [(점검항목, 기준, 결과, 비고)])
DAILY_INSPECTIONS = [
	("EQ-PC-01", -2, [("외관상태", "이상無", "정상", ""), ("동작상태", "이상無", "정상", ""), ("청결상태", "이상無", "정상", "")]),
	("EQ-PC-01", -1, [("외관상태", "이상無", "정상", ""), ("동작상태", "이상無", "정상", ""), ("청결상태", "이상無", "정상", "")]),
	("EQ-PC-01", 0, [("외관상태", "이상無", "정상", ""), ("동작상태", "이상無", "이상", "노즐 흡착 불량 감지, 정비 요청"), ("청결상태", "이상無", "정상", "")]),
	("EQ-AS-02", -2, [("외관상태", "이상無", "정상", ""), ("동작상태", "이상無", "정상", "")]),
	("EQ-AS-02", -1, [("외관상태", "이상無", "정상", ""), ("동작상태", "이상無", "정상", "")]),
	("EQ-AS-02", 0, [("외관상태", "이상無", "정상", ""), ("동작상태", "이상無", "정상", "")]),
	("EQ-QT-01", -2, [("외관상태", "이상無", "정상", ""), ("청결상태", "이상無", "정상", "")]),
	("EQ-QT-01", -1, [("외관상태", "이상無", "정상", ""), ("청결상태", "이상無", "정상", "")]),
	("EQ-QT-01", 0, [("외관상태", "이상無", "정상", ""), ("청결상태", "이상無", "정상", "")]),
]


def execute():
	if not frappe.db.exists("DocType", "Equipment"):
		return

	_create_workstations()
	_create_equipment()
	_create_daily_inspections()
	frappe.db.commit()


def _create_workstations():
	for workstation_name, workstation_type, description in WORKSTATIONS:
		if frappe.db.exists("Workstation", workstation_name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Workstation",
				"workstation_name": workstation_name,
				"workstation_type": workstation_type,
				"company": "BABIPA",
				"production_capacity": 1,
				"status": "Production",
				"description": description,
			}
		)
		doc.insert(ignore_permissions=True)


def _create_equipment():
	for equipment_code, equipment_name, equipment_type, workstation, calibration_required in EQUIPMENT:
		if frappe.db.exists("Equipment", equipment_code):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Equipment",
				"equipment_code": equipment_code,
				"equipment_name": equipment_name,
				"equipment_type": equipment_type,
				"workstation": workstation,
				"status": "가동",
				"calibration_required": calibration_required,
				"calibration_due_date": add_days(nowdate(), 90) if calibration_required else None,
			}
		)
		doc.insert(ignore_permissions=True)
		doc.add_comment("Comment", TBD_NOTE)


def _create_daily_inspections():
	for equipment_code, day_offset, items in DAILY_INSPECTIONS:
		inspection_date = add_days(nowdate(), day_offset)
		if frappe.db.exists(
			"Equipment Daily Inspection", {"equipment": equipment_code, "inspection_date": inspection_date}
		):
			continue
		has_abnormal = any(result == "이상" for _, _, result, _ in items)
		doc = frappe.get_doc(
			{
				"doctype": "Equipment Daily Inspection",
				"equipment": equipment_code,
				"inspection_date": inspection_date,
				"inspector": "Administrator",
				"overall_result": "이상" if has_abnormal else "정상",
				"inspection_items": [
					{"check_item": check_item, "standard": standard, "result": result, "remarks": remarks}
					for check_item, standard, result, remarks in items
				],
			}
		)
		doc.insert(ignore_permissions=True)
		doc.submit()
