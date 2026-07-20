import frappe
from frappe.utils import time_diff_in_hours
from frappe.model.document import Document


class ProductionDowntimeLog(Document):
	def validate(self):
		if self.end_datetime:
			if self.end_datetime <= self.start_datetime:
				frappe.throw("종료일시는 시작일시보다 이후여야 합니다.")
			self.duration_minutes = round(time_diff_in_hours(self.end_datetime, self.start_datetime) * 60, 1)
