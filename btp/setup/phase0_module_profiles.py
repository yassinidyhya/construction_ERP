import frappe

ALLOWED = {
    "BTP Comptable": {"Accounts", "Buying", "Selling", "Stock", "HR", "Payroll", "Projects"},
    "BTP Direction": {"Accounts", "Selling", "Projects", "CRM"},
    "BTP Chantier": {"Projects", "Stock"},
    "BTP Magasinier": {"Stock", "Buying"},
}


def create_or_update_module_profiles():
    all_modules = {m.name for m in frappe.get_all("Module Def", fields=["name"])}

    for name, allowed in ALLOWED.items():
        if not frappe.db.exists("Module Profile", name):
            mp = frappe.get_doc({"doctype": "Module Profile", "module_profile_name": name})
        else:
            mp = frappe.get_doc("Module Profile", name)
            mp.block_modules = []

        blocked = sorted(all_modules - allowed)
        for mod in blocked:
            mp.append("block_modules", {"module": mod})

        if mp.is_new():
            mp.insert(ignore_permissions=True)
            print(f"Created module profile: {name}")
        else:
            mp.save(ignore_permissions=True)
            print(f"Updated module profile: {name}")

        print(f"  Allowed: {sorted(allowed)}")
        print(f"  Blocked: {len(blocked)} modules")


def run():
    create_or_update_module_profiles()
    frappe.db.commit()
