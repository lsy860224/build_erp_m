"""완제품 21건(검사구분=전수검사, 품목구분=완제품) Quality Inspection Template 껍데기 생성.

배경: `docs/item-doctype-design.md` §2 검사구분(`custom_inspection_type`) 매핑 리뷰에서
`hkmc-compliance`가 "실제 검사기록 생성을 강제하지 않는 라벨뿐인 상태"를 지적. 실제 검사
파라미터(측정 항목, 규격 상하한, 샘플링 사이즈/AQL)를 담은 원본 자료(도면/Control Plan/
검사기준서)가 아직 없어(2026.07.20 사용자 확인) 값은 절대 채우지 않고, 완제품 21건과 1:1
대응하는 템플릿 껍데기만 생성한다.

- Quality Inspection Template의 `item_quality_inspection_parameter`(Table)는 reqd=1이라
  빈 테이블로는 저장이 막힌다(2026.07.20 개발 사이트에서 실제 저장 시도로 확인).
  `Item Quality Inspection Parameter.specification`도 reqd=1이며 Data가 아니라
  `Quality Inspection Parameter`(마스터)로의 Link다. 따라서 21건이 공유하는 placeholder
  마스터 Parameter 1건을 먼저 만들고, 각 템플릿에 그 placeholder를 참조하는 행 1개씩만
  넣는다 — 실제 값처럼 보이지 않도록 value 필드에 "TBD" 문구를 명시.
- 완제품 21건 목록은 `docs/품목코드_260720.XLSX`(품목구분=완제품 AND 검사구분=전수검사)에서
  재확인한 값을 그대로 옮겼다 — 이 xlsx는 `.gitignore` 대상이라 이 패치가 유일한 소스가
  된다(`docs/decisions.md` 2026.07.20 항목 참조).
- 실 Item 레코드(289건 임포트)는 아직 없어 Item.quality_inspection_template 연결은 여기서
  하지 않는다 — `docs/item-doctype-design.md` §6 참조, 완제품 임포트 시 frappe-backend가
  이 21개 템플릿과 연결한다.
- fixtures가 아니라 patch로 실행하는 이유는 이 패치 docstring이 아니라
  `docs/item-doctype-design.md`(버전관리 판단 절)에 기록했다.
"""

import frappe

PLACEHOLDER_PARAMETER = "TBD - 검사 파라미터 미정"
PLACEHOLDER_VALUE = "TBD — 실제 검사 파라미터 미정, 품질부서 확인 필요"
SHELL_NOTE = (
	"2026.07.20 껍데기 생성 — 도면/Control Plan 확보 후 품질부서가 실제 파라미터 채울 것"
)

# (품목코드, 항목명) — docs/품목코드_260720.XLSX 중 품목구분='완제품' AND 검사구분='전수검사'
# 21건 전부(2026.07.20 재확인, docs/decisions.md 참조).
FINISHED_GOODS_FULL_INSPECTION = [
	("JGP26-A0301", "SENSOR ASSY - FR DR, LH (SWING DOOR)"),
	("JGP26-A0302", "SENSOR ASSY - FR DR, LH (COACH DOOR)"),
	("JGP26-B0301", "SENSOR ASSY - FR DR, RH (SWING DOOR)"),
	("JGP26-B0302", "SENSOR ASSY - FR DR, RH (COACH DOOR)"),
	("JGP26-C0301", "SENSOR ASSY - RR DR, LH (SWING DOOR)"),
	("JGP26-C0302", "SENSOR ASSY - RR DR, LH (COACH DOOR)"),
	("JGP26-D0301", "SENSOR ASSY - RR DR, RH (SWING DOOR)"),
	("JGP26-D0302", "SENSOR ASSY - RR DR, RH (COACH DOOR)"),
	("MOP25-M0301", "UNIT - RADAR MASTER"),
	("MOP25-S0301", "UNIT - RADAR SLAVE"),
	("MXP26-E0301", "SENSOR ASSY - TAIL GATE"),
	("NEP27-A0301", "SENSOR ASSY - FR DR, LH (NE1)"),
	("NEP27-B0301", "SENSOR ASSY - FR DR, RH (NE1)"),
	("NEP27-C0301", "SENSOR ASSY - RR DR, LH (NE1)"),
	("NEP27-D0301", "SENSOR ASSY - RR DR, RH (NE1)"),
	("RSP26-A0302", "SENSOR ASSY - FR DR, LH (RS4 PE)"),
	("RSP26-B0302", "SENSOR ASSY - FR DR, RH (RS4 PE)"),
	("RSP26-C0303", "SENSOR ASSY - RR DR, LH (RS4 PE)"),
	("RSP26-C0304", "SENSOR ASSY - RR DR, LH (RS4 PE LWB)"),
	("RSP26-D0303", "SENSOR ASSY - RR DR, RH (RS4 PE)"),
	("RSP26-D0304", "SENSOR ASSY - RR DR, RH (RS4 PE LWB)"),
]


def execute():
	if not frappe.db.exists("DocType", "Quality Inspection Template"):
		# ERPNext 미설치 사이트 방어(babipa_erp 단독 설치 시나리오는 없지만 안전하게).
		return

	_ensure_placeholder_parameter()

	for item_code, item_name in FINISHED_GOODS_FULL_INSPECTION:
		_create_template_shell(item_code, item_name)


def _ensure_placeholder_parameter():
	if frappe.db.exists("Quality Inspection Parameter", PLACEHOLDER_PARAMETER):
		return

	doc = frappe.get_doc(
		{
			"doctype": "Quality Inspection Parameter",
			"parameter": PLACEHOLDER_PARAMETER,
			"description": SHELL_NOTE,
		}
	)
	doc.insert(ignore_permissions=True)


def _create_template_shell(item_code: str, item_name: str):
	template_name = f"{item_code} - {item_name}"
	if frappe.db.exists("Quality Inspection Template", template_name):
		return

	doc = frappe.get_doc(
		{
			"doctype": "Quality Inspection Template",
			"quality_inspection_template_name": template_name,
			"item_quality_inspection_parameter": [
				{
					"specification": PLACEHOLDER_PARAMETER,
					"numeric": 0,
					"value": PLACEHOLDER_VALUE,
				}
			],
		}
	)
	doc.insert(ignore_permissions=True)
	doc.add_comment("Comment", SHELL_NOTE)
