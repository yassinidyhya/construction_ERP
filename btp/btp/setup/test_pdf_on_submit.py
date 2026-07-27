import frappe


def run():
	src_name = frappe.db.get_value("Sales Invoice", {"docstatus": 1}, "name")
	src = frappe.get_doc("Sales Invoice", src_name)
	inv = frappe.copy_doc(src)
	inv.posting_date = "2026-07-27"
	inv.set_posting_time = 1
	inv.insert()
	inv.submit()
	print("submitted:", inv.name)

	files = frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Sales Invoice", "attached_to_name": inv.name},
		fields=["name", "file_name", "file_url", "file_size"],
	)
	print("attachments:", files)
	pdf = [f for f in files if f.file_name and f.file_name.lower().endswith(".pdf")]
	assert pdf, "no PDF attached on submit"
	content = frappe.get_doc("File", pdf[0].name).get_content()
	assert content[:5] == b"%PDF-", "attachment is not a PDF"
	print("PDF OK:", pdf[0].file_name, "size:", pdf[0].file_size)
	frappe.db.commit()
