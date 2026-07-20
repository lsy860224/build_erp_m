import frappe
from frappe.model.document import Document


class EquipmentDailyInspection(Document):
	def validate(self):
		has_abnormal = any(row.result == "이상" for row in self.inspection_items)
		if has_abnormal and self.overall_result != "이상":
			frappe.throw("점검항목 중 '이상'이 있으면 종합판정도 '이상'으로 설정해야 합니다.")
