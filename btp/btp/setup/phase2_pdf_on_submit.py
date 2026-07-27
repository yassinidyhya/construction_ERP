import frappe


def run():
	settings = frappe.get_single("PDF on Submit Settings")
	settings.create_pdf_in_background = 0
	settings.enabled_for = []
	for document_type, print_format in [
		("Sales Invoice", "Facture Maroc"),
		("Quotation", "Devis Maroc"),
	]:
		settings.append(
			"enabled_for",
			{
				"document_type": document_type,
				"print_format": print_format,
			},
		)
	settings.save()
	frappe.db.commit()
	for row in settings.enabled_for:
		print("enabled:", row.document_type, "->", row.print_format)
	print("PDF ON SUBMIT CONFIG OK")
