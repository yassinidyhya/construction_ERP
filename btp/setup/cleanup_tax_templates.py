import frappe


def run():
    """Delete duplicate/ugly item tax templates created with '- RT - RT' suffix."""
    templates = frappe.get_all(
        "Item Tax Template",
        filters={"company": "RIJAL TRAVAUX", "name": ("like", "TVA% - RT - RT")},
        fields=["name"],
    )
    for t in templates:
        frappe.delete_doc("Item Tax Template", t.name, force=True, ignore_permissions=True)
        print(f"Deleted template: {t.name}")
    frappe.db.commit()
