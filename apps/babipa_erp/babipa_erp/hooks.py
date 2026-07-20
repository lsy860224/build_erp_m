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
	# 경리 Role: docs/decisions.md §5.4 권한 Role Matrix(5개 역할) 중 1번째 구현.
	# 초기 권한 범위는 §4.5·§5.4에서 명시적으로 결정된 "내부 정합용 전표"에 한정 —
	# Journal Entry/Payment Entry는 RWCD+Submit/Cancel/Amend(경리가 직접 전표를 확정),
	# GL Entry는 Read-only(시스템이 자동 생성하는 원장이라 수동 생성 대상 아님).
	# Purchase/Sales Invoice, Supplier, Customer 등 나머지 DocType 접근 범위는
	# 아직 미결정 — 후속 확인 필요.
	{"doctype": "Role", "filters": [["name", "=", "경리"]]},
	{"doctype": "Custom DocPerm", "filters": [["role", "=", "경리"]]},
]

