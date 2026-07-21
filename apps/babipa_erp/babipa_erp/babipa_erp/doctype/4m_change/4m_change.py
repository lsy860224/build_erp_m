from frappe.model.document import Document


class FourMChange(Document):
	pass


# DocType 이름 "4M Change"는 숫자로 시작해 유효한 Python 클래스명이 될 수 없다.
# frappe.model.base_document.import_controller()가 조회하는 속성명은
# doctype.replace(" ", "").replace("-", "") == "4MChange"이므로, 모듈 네임스페이스에
# 그 문자열 이름으로 직접 등록해준다.
globals()["4MChange"] = FourMChange
