import frappe


@frappe.whitelist()
def get_apps():
	"""Apps screen: non-admins only see BTP (one system, one entry point)."""
	if "System Manager" in frappe.get_roles():
		return frappe.get_attr("frappe.apps.get_apps")()

	apps = frappe.get_hooks("add_to_apps_screen", app_name="btp")
	return [
		{
			"name": "btp",
			"logo": apps[0].get("logo"),
			"title": frappe._(apps[0].get("title")),
			"route": apps[0].get("route"),
		}
	]


def has_app_permission():
	return True
