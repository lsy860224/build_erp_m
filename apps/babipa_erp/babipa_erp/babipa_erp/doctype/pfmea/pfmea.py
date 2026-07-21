from frappe.model.document import Document


class PFMEA(Document):
	def validate(self):
		for row in self.pfmea_item:
			if row.severity and row.occurrence and row.detection:
				row.rpn = row.severity * row.occurrence * row.detection
