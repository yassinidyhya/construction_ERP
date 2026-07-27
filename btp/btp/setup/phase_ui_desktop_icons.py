import frappe

BTP_ICONS = {"Bureau": "Comptable", "Chantier": "Chef de Chantier", "Direction": "Direction"}


def run():
	# hide every desktop icon except the three BTP workspaces
	frappe.db.sql(
		"UPDATE `tabDesktop Icon` SET hidden = 1 WHERE label NOT IN %(labels)s",
		{"labels": tuple(BTP_ICONS)},
	)
	for label, role in BTP_ICONS.items():
		frappe.db.sql(
			"UPDATE `tabDesktop Icon` SET hidden = 0 WHERE label = %s", label
		)
		icon_name = frappe.db.get_value("Desktop Icon", {"label": label}, "name")
		if not icon_name:
			print("missing icon:", label)
			continue
		icon = frappe.get_doc("Desktop Icon", icon_name)
		icon.roles = []
		icon.append("roles", {"role": role})
		icon.save(ignore_permissions=True)
		print("icon:", label, "-> role", role)

	from frappe.desk.doctype.desktop_icon.desktop_icon import clear_desktop_icons_cache

	clear_desktop_icons_cache()
	frappe.db.commit()
	print("DESKTOP ICONS OK")
