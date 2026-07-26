import frappe
import json
from frappe.utils import random_string


def make_content(shortcuts):
    blocks = [
        {
            "id": random_string(10),
            "type": "header",
            "data": {"text": "<span class=\"h4\"><b>Shortcuts</b></span>", "col": 12},
        }
    ]
    for sc in shortcuts:
        blocks.append(
            {
                "id": random_string(10),
                "type": "shortcut",
                "data": {"shortcut_name": sc["label"], "col": 3},
            }
        )
    return json.dumps(blocks, separators=(",", ":"))


def create_workspace(label, icon, shortcuts, roles, sequence_id):
    if frappe.db.exists("Workspace", label):
        print(f"Workspace exists: {label}")
        return
    ws = frappe.get_doc(
        {
            "doctype": "Workspace",
            "label": label,
            "name": label,
            "title": label,
            "icon": icon,
            "module": "BTP",
            "public": 1,
            "is_hidden": 0,
            "sequence_id": sequence_id,
            "content": make_content(shortcuts),
            "shortcuts": shortcuts,
            "roles": [{"role": r} for r in roles],
            "charts": [],
            "number_cards": [],
            "quick_lists": [],
            "links": [],
        }
    )
    ws.insert(ignore_permissions=True)
    print(f"Created workspace: {label}")


def run():
    # Direction: dashboards + financial reports
    create_workspace(
        "Direction",
        "dashboard",
        [
            {"label": "Projects", "link_to": "Project", "type": "DocType"},
            {"label": "Sales Invoices", "link_to": "Sales Invoice", "type": "DocType"},
            {"label": "Payment Entries", "link_to": "Payment Entry", "type": "DocType"},
            {"label": "Purchase Invoices", "link_to": "Purchase Invoice", "type": "DocType"},
        ],
        ["Direction"],
        1.0,
    )

    # Bureau: accounting + buying + selling + stock + HR
    create_workspace(
        "Bureau",
        "desk",
        [
            {"label": "Purchase Invoices", "link_to": "Purchase Invoice", "type": "DocType"},
            {"label": "Payment Entries", "link_to": "Payment Entry", "type": "DocType"},
            {"label": "Journal Entries", "link_to": "Journal Entry", "type": "DocType"},
            {"label": "Employees", "link_to": "Employee", "type": "DocType"},
            {"label": "Attendance", "link_to": "Attendance", "type": "DocType"},
            {"label": "Payroll Entry", "link_to": "Payroll Entry", "type": "DocType"},
            {"label": "Material Request", "link_to": "Material Request", "type": "DocType"},
        ],
        ["Comptable"],
        2.0,
    )

    # Chantier: site reports + material requests (v1 placeholders)
    create_workspace(
        "Chantier",
        "construction",
        [
            {"label": "Material Request", "link_to": "Material Request", "type": "DocType"},
        ],
        ["Chef de Chantier", "Magasinier"],
        3.0,
    )

    frappe.db.commit()
