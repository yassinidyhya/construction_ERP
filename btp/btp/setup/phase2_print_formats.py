import os

import frappe
from frappe.utils import get_bench_path

TMP_DIR = os.path.join(get_bench_path(), "sites", "print_formats_tmp")

FORMATS = [
	{
		"name": "Facture Maroc",
		"doc_type": "Sales Invoice",
		"file": os.path.join(TMP_DIR, "facture_maroc.html"),
	},
	{
		"name": "Devis Maroc",
		"doc_type": "Quotation",
		"file": os.path.join(TMP_DIR, "devis_maroc.html"),
	},
]


def run():
	for fmt in FORMATS:
		with open(fmt["file"], encoding="utf-8") as f:
			html = f.read()

		if frappe.db.exists("Print Format", fmt["name"]):
			pf = frappe.get_doc("Print Format", fmt["name"])
			pf.html = html
			pf.module = "BTP"
			pf.save()
			print("updated:", fmt["name"])
		else:
			pf = frappe.get_doc(
				{
					"doctype": "Print Format",
					"name": fmt["name"],
					"doc_type": fmt["doc_type"],
					"module": "BTP",
					"custom_format": 1,
					"print_format_type": "Jinja",
					"standard": "No",
					"html": html,
					"disabled": 0,
					"default_print_language": "fr",
				}
			)
			pf.insert()
			print("created:", fmt["name"])

	frappe.db.commit()
