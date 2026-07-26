app_name = "btp"
app_title = "BTP"
app_publisher = "BTP"
app_description = "Construction module for BTP"
app_email = "contact@rijal-travaux.com"
app_license = "mit"

# Fixtures
# ------------------
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "BTP"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "BTP"]]},
    {"dt": "Workspace", "filters": [["module", "=", "BTP"]]},
    {"dt": "Print Format", "filters": [["module", "=", "BTP"]]},
    {"dt": "Role", "filters": [["name", "in", ["Comptable", "Direction", "Chef de Chantier", "Magasinier"]]]},
    {"dt": "Role Profile", "filters": [["name", "in", ["BTP Comptable", "BTP Direction", "BTP Chantier", "BTP Magasinier"]]]},
    {"dt": "Module Profile", "filters": [["name", "in", ["BTP Comptable", "BTP Direction", "BTP Chantier", "BTP Magasinier"]]]},
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "btp",
# 		"logo": "/assets/btp/logo.png",
# 		"title": "BTP",
# 		"route": "/btp",
# 		"has_permission": "btp.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/btp/css/btp.css"
# app_include_js = "/assets/btp/js/btp.js"

# include js, css files in header of web template
# web_include_css = "/assets/btp/css/btp.css"
# web_include_js = "/assets/btp/js/btp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "btp/public/scss/website"

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
# app_include_icons = "btp/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "btp.utils.jinja_methods",
# 	"filters": "btp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "btp.install.before_install"
# after_install = "btp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "btp.uninstall.before_uninstall"
# after_uninstall = "btp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "btp.utils.before_app_install"
# after_app_install = "btp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "btp.utils.before_app_uninstall"
# after_app_uninstall = "btp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "btp.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Stock Entry": {
		"validate": "btp.btp.doc_events.stock_entry.validate_stock_entry"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"btp.tasks.all"
# 	],
# 	"daily": [
# 		"btp.tasks.daily"
# 	],
# 	"hourly": [
# 		"btp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"btp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"btp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "btp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "btp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "btp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["btp.utils.before_request"]
# after_request = ["btp.utils.after_request"]

# Job Events
# ----------
# before_job = ["btp.utils.before_job"]
# after_job = ["btp.utils.after_job"]

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
# 	"btp.auth.validate"
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

