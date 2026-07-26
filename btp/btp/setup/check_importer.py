import frappe


def run():
    imp = frappe.get_meta("Chart of Accounts Importer")
    for f in imp.fields:
        print(f"{f.fieldname} ({f.fieldtype}): {f.label}")
