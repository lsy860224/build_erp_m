app_name = "babipa_erp"
app_title = "Babipa Erp"
app_publisher = "BABIPA"
app_description = "HKMC 대응 자동차 전장품 시험평가/ERP 커스터마이징 앱"
app_email = "lsy860224@naver.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "babipa_erp",
# 		"logo": "/assets/babipa_erp/logo.png",
# 		"title": "Babipa Erp",
# 		"route": "/babipa_erp",
# 		"has_permission": "babipa_erp.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/babipa_erp/css/babipa_erp.css"
# app_include_js = "/assets/babipa_erp/js/babipa_erp.js"

# include js, css files in header of web template
# web_include_css = "/assets/babipa_erp/css/babipa_erp.css"
# web_include_js = "/assets/babipa_erp/js/babipa_erp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "babipa_erp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "babipa_erp/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "babipa_erp.utils.jinja_methods",
# 	"filters": "babipa_erp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "babipa_erp.install.before_install"
# after_install = "babipa_erp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "babipa_erp.uninstall.before_uninstall"
# after_uninstall = "babipa_erp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "babipa_erp.utils.before_app_install"
# after_app_install = "babipa_erp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "babipa_erp.utils.before_app_uninstall"
# after_app_uninstall = "babipa_erp.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "babipa_erp.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "babipa_erp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"babipa_erp.tasks.all"
# 	],
# 	"daily": [
# 		"babipa_erp.tasks.daily"
# 	],
# 	"hourly": [
# 		"babipa_erp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"babipa_erp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"babipa_erp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "babipa_erp.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "babipa_erp.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "babipa_erp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "babipa_erp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["babipa_erp.utils.before_request"]
# after_request = ["babipa_erp.utils.after_request"]

# Job Events
# ----------
# before_job = ["babipa_erp.utils.before_job"]
# after_job = ["babipa_erp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"babipa_erp.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# Fixtures
# --------
# Custom Korean translations for Frappe core strings with no upstream ko translation
# (ERPNext app strings already have ko coverage via apps/erpnext's own translation catalog).
# Item Custom Fields: docs/item-doctype-design.md 필드 매핑 설계 반영
# (품목코드_260720.xlsx 15개 컬럼 중 표준 Item 필드로 커버되지 않는 항목).
# Item Group: 품목코드_260720.xlsx 품목구분/중분류 분석 기반 초기 트리(설계 문서 참조).
# ERPNext 데모 Item Group(Products/Raw Material 등)은 포함하지 않도록 이름으로 필터링.
# Workstation Type / Operation: SMT·후가공·조립·검사포장 공정 분류 — Item 마스터의
# custom_default_operation(PP/PC/AS/QT) 실측 분포와 대응하는 순수 분류 마스터라
# Item Group과 동일하게 fixture로 관리(환경 간 항상 동일해야 함). 기존 ERPNext 기본
# Operation("Assembly")은 포함하지 않도록 이름으로 필터링.
fixtures = [
	{"doctype": "Translation", "filters": [["language", "=", "ko"]]},
	{"doctype": "Custom Field", "filters": [["dt", "=", "Item"]]},
	{
		"doctype": "Item Group",
		"filters": [
			[
				"item_group_name",
				"in",
				["완제품", "반제품", "원재료", "부재료", "상품", "일반반제품", "PCB ASSY(반제품)", "PCB ASSY(원재료)"],
			]
		],
	},
	{"doctype": "Workstation Type", "filters": [["name", "in", ["SMT", "후가공", "조립", "검사·포장"]]]},
	{
		"doctype": "Operation",
		"filters": [
			["name", "in", ["후가공 (PP)", "PCB ASSY·SMT (PC)", "조립 (AS)", "검사·포장 (QT)"]]
		],
	},
	# §5.4 권한 Role Matrix — 5개 역할(경리/관리자/구매/생산/품질) 전부 구현.
	# 경리: 내부 정합용 전표(Journal Entry/Payment Entry) 담당, GL Entry는 Read-only.
	# 구매: Purchase Order RWC(Submit 없음). 생산: Work Order/Job Card/Stock Entry RWC.
	# 품질: Quality Inspection RWC. 넷 다 "실무진은 RWC 위주"(§5.4) 원칙 — 확정 권한은
	# 관리자에 집중. 관리자: Purchase Order·Payment Entry(승인 게이트, §5.5) + Work
	# Order/Job Card/Stock Entry/Quality Inspection까지 RWCD+Submit/Cancel/Amend —
	# 뒤 4개는 별도 Workflow 없이 §5.4 role matrix의 단일 Submit 권한만으로 충분(§5.5
	# 결정, Workflow는 PO·Payment Entry 2개뿐). 경리의 Payment Entry Submit/Cancel/
	# Amend는 §5.5 워크플로우 도입 시 제거(아래 Workflow 항목 참조).
	# 미결정: Item/BOM은 5개 역할 중 누가 담당인지 §5.4 원문에 특정 안 돼 있어 보류.
	{"doctype": "Role", "filters": [["name", "in", ["경리", "관리자", "구매", "생산", "품질"]]]},
	{"doctype": "Custom DocPerm", "filters": [["role", "in", ["경리", "관리자", "구매", "생산", "품질"]]]},
	# Track Changes(감사 추적성, §5.4): Item/BOM/Work Order/Journal Entry/Payment Entry는
	# ERPNext 기본값이 이미 track_changes=1이라 별도 조치 불필요(콘솔 확인 완료).
	# Quality Inspection·GL Entry만 기본값 0이라 Property Setter로 1로 전환.
	{
		"doctype": "Property Setter",
		"filters": [
			["doc_type", "in", ["GL Entry", "Quality Inspection"]],
			["property", "=", "track_changes"],
		],
	},
	# §5.5 전자결재 워크플로우: Purchase Order(발주요청→승인대기→확정), Payment Entry
	# (지급요청→승인대기→실행) 2개만 Frappe Workflow 적용 — 그 외 DocType은 §5.4 role
	# matrix의 단일 Submit 권한만으로 충분하다고 이미 결정됨. 승인(관리자)·반려 전이는
	# allow_self_approval=0으로 설정해 기안자 본인이 자기 문서를 승인할 수 없도록 함.
	# Workflow 저장 시 workflow_state Custom Field가 자동 생성되므로 별도 export.
	{"doctype": "Workflow State", "filters": [["name", "in", ["발주요청", "승인대기", "확정", "지급요청", "실행"]]]},
	{"doctype": "Workflow Action Master", "filters": [["name", "in", ["승인요청", "승인", "반려"]]]},
	{
		"doctype": "Workflow",
		"filters": [["name", "in", ["Purchase Order 발주 승인", "Payment Entry 지급 승인"]]],
	},
	{
		"doctype": "Custom Field",
		"filters": [["dt", "in", ["Purchase Order", "Payment Entry"]], ["fieldname", "=", "workflow_state"]],
		"prefix": "workflow",
	},
]

