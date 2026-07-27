import frappe


def run():
	"""Remove PDC test artifacts left behind by crashed test runs."""
	for name in frappe.get_all("Bordereau de Remise", pluck="name"):
		doc = frappe.get_doc("Bordereau de Remise", name)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Bordereau de Remise", name, force=1, ignore_permissions=True)

	for name in frappe.get_all("Cheque", pluck="name"):
		frappe.delete_doc("Cheque", name, force=1, ignore_permissions=True)

	jes = frappe.get_all(
		"Journal Entry",
		filters={"user_remark": ["like", "%cheque%"]},
		pluck="name",
	)
	jes += frappe.get_all(
		"Journal Entry",
		filters={"user_remark": ["like", "%Bordereau%"]},
		pluck="name",
	)
	for name in set(jes):
		doc = frappe.get_doc("Journal Entry", name)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Journal Entry", name, force=1, ignore_permissions=True)

	for name in frappe.get_all(
		"Payment Entry", filters={"reference_no": ["like", "CHQ-%"]}, pluck="name"
	):
		doc = frappe.get_doc("Payment Entry", name)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Payment Entry", name, force=1, ignore_permissions=True)

	frappe.db.commit()
	print("PDC CLEANUP OK")
