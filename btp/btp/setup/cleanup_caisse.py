import frappe


def run():
	cj_name = frappe.db.get_value("Caisse Journal", {"date": "2026-07-27"}, "name")
	if cj_name:
		je_name = frappe.db.get_value("Caisse Journal", cj_name, "journal_entry")
		frappe.delete_doc("Caisse Journal", cj_name, force=1)
		if je_name:
			frappe.delete_doc("Journal Entry", je_name, force=1)
		frappe.db.commit()
		print("cleaned:", cj_name, je_name)
	else:
		print("nothing to clean")
