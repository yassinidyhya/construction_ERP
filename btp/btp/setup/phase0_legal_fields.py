import frappe


LEGAL_FIELDS = [
    {"label": "ICE", "fieldname": "custom_ice", "insert_after": "tax_id", "fieldtype": "Data", "length": 15},
    {"label": "IF", "fieldname": "custom_if", "insert_after": "custom_ice", "fieldtype": "Data", "length": 8},
    {"label": "RC", "fieldname": "custom_rc", "insert_after": "custom_if", "fieldtype": "Data", "length": 20},
    {"label": "TP", "fieldname": "custom_tp", "insert_after": "custom_rc", "fieldtype": "Data", "length": 20},
    {"label": "CNSS", "fieldname": "custom_cnss", "insert_after": "custom_tp", "fieldtype": "Data", "length": 20},
]


def create_custom_field(doctype, field_def):
    fieldname = field_def["fieldname"]
    if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
        print(f"Custom field exists: {doctype}.{fieldname}")
        return

    cf = frappe.get_doc(
        {
            "doctype": "Custom Field",
            "dt": doctype,
            "label": field_def["label"],
            "fieldname": fieldname,
            "fieldtype": field_def["fieldtype"],
            "insert_after": field_def["insert_after"],
            "length": field_def.get("length"),
            "module": "BTP",
        }
    )
    cf.insert(ignore_permissions=True)
    print(f"Created custom field: {doctype}.{fieldname}")


def run():
    for doctype in ("Company", "Customer"):
        insert_after = "tax_id"
        for field_def in LEGAL_FIELDS:
            fd = dict(field_def)
            fd["insert_after"] = insert_after
            create_custom_field(doctype, fd)
            insert_after = fd["fieldname"]

    frappe.db.commit()
