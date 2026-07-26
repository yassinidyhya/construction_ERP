import frappe


def hide_standard_workspaces_from_custom_roles():
    """Remove all non-Administrator roles from standard (non-custom) workspaces.

    This makes the custom workspaces (Direction, Bureau, Chantier) the only
    visible ones for Comptable / Direction / Chef de Chantier / Magasinier.
    Administrator keeps access to everything.

    Uses direct SQL to avoid writing back to erpnext/frappe/hrms source files
    when developer_mode is enabled.
    """
    standard_workspaces = frappe.get_all(
        "Workspace",
        filters={"module": ("!=", "BTP"), "public": 1},
        fields=["name"],
    )

    for ws_name in standard_workspaces:
        ws_name = ws_name.name

        # Delete existing non-Administrator roles for this workspace.
        frappe.db.sql(
            """
            DELETE FROM `tabHas Role`
            WHERE parenttype = 'Workspace' AND parent = %s AND role != 'Administrator'
            """,
            ws_name,
        )

        # Ensure Administrator role exists for this workspace.
        has_admin = frappe.db.exists(
            "Has Role",
            {"parenttype": "Workspace", "parent": ws_name, "role": "Administrator"},
        )
        if not has_admin:
            frappe.db.sql(
                """
                INSERT INTO `tabHas Role` (name, parenttype, parent, role)
                VALUES (%s, 'Workspace', %s, 'Administrator')
                """,
                (frappe.generate_hash("Has Role", 10), ws_name),
            )

        print(f"Updated workspace '{ws_name}': only Administrator can see it")


def run():
    hide_standard_workspaces_from_custom_roles()
    frappe.db.commit()
