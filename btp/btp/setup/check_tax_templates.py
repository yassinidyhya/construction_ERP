import frappe


def run():
    templates = frappe.get_all(
        "Item Tax Template",
        filters={"company": "RIJAL TRAVAUX", "name": ("like", "TVA%")},
        fields=["name"],
    )
    for t in templates:
        tpl = frappe.get_doc("Item Tax Template", t.name)
        print(f"{tpl.name}:")
        for tax in tpl.taxes:
            print(f"  {tax.tax_type} @ {tax.tax_rate}%")
