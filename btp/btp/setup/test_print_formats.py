import frappe


def run():
	sinv = frappe.db.get_value("Sales Invoice", {"docstatus": 1}, "name")
	assert sinv, "no submitted sales invoice found"
	html = frappe.get_print("Sales Invoice", sinv, print_format="Facture Maroc")
	checks = ["ICE", "IF", "RC", "FACTURE", "Total TTC", "items-table"]
	missing = [c for c in checks if c not in html]
	print("invoice:", sinv, "len:", len(html), "missing:", missing)
	assert not missing, missing

	# quotation may not exist in demo data; render only if present
	quot = frappe.db.get_value("Quotation", {}, "name")
	if quot:
		html = frappe.get_print("Quotation", quot, print_format="Devis Maroc")
		missing = [c for c in ["ICE", "DEVIS", "Total TTC"] if c not in html]
		print("quotation:", quot, "len:", len(html), "missing:", missing)
		assert not missing, missing
	else:
		print("no quotation in demo data; skipping Devis render check")

	print("RENDER OK")
