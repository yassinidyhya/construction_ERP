import frappe

COMPANY = "RIJAL TRAVAUX"
ABBR = "RT"

TAX_RATES = {
    "TVA 20%": 20.0,
    "TVA 14%": 14.0,
    "TVA 10%": 10.0,
    "TVA 7%": 7.0,
}


def get_tax_parent_account():
    """Find a sensible parent account for VAT accounts."""
    candidates = [
        "Taxes - {abbr}",
        "TVA - {abbr}",
        "VAT - {abbr}",
        "Impôts et Taxes - {abbr}",
    ]
    for pattern in candidates:
        name = pattern.format(abbr=ABBR)
        if frappe.db.exists("Account", name):
            return name

    # Fallback: any tax root or liability account
    parent = frappe.db.get_value(
        "Account",
        {"company": COMPANY, "account_type": "Tax", "is_group": 1},
        "name",
    )
    if parent:
        return parent

    raise ValueError(f"Could not find a parent account for VAT in company {COMPANY}")


def ensure_tax_account(account_name, rate):
    """Create or return the VAT account for the given rate."""
    full_name = f"{account_name} - {ABBR}"
    if frappe.db.exists("Account", full_name):
        print(f"Tax account exists: {full_name}")
        return full_name

    parent = get_tax_parent_account()
    account = frappe.get_doc(
        {
            "doctype": "Account",
            "account_name": account_name,
            "company": COMPANY,
            "parent_account": parent,
            "account_type": "Tax",
            "tax_rate": rate,
            "account_currency": "MAD",
        }
    )
    account.insert(ignore_permissions=True)
    print(f"Created tax account: {full_name} under {parent}")
    return full_name


def create_item_tax_templates():
    for template_name, rate in TAX_RATES.items():
        account_name = ensure_tax_account(template_name, rate)

        # Sales template
        sales_title = f"{template_name} (Vente)"
        if not frappe.db.exists("Item Tax Template", {"title": sales_title, "company": COMPANY}):
            sales_tpl = frappe.get_doc(
                {
                    "doctype": "Item Tax Template",
                    "title": sales_title,
                    "company": COMPANY,
                    "taxes": [
                        {
                            "tax_type": account_name,
                            "tax_rate": rate,
                        }
                    ],
                }
            )
            sales_tpl.insert(ignore_permissions=True)
            print(f"Created item tax template: {sales_tpl.name}")
        else:
            print(f"Item tax template exists: {sales_title}")

        # Purchase template
        purchase_title = f"{template_name} (Achat)"
        if not frappe.db.exists("Item Tax Template", {"title": purchase_title, "company": COMPANY}):
            purchase_tpl = frappe.get_doc(
                {
                    "doctype": "Item Tax Template",
                    "title": purchase_title,
                    "company": COMPANY,
                    "taxes": [
                        {
                            "tax_type": account_name,
                            "tax_rate": rate,
                        }
                    ],
                }
            )
            purchase_tpl.insert(ignore_permissions=True)
            print(f"Created item tax template: {purchase_tpl.name}")
        else:
            print(f"Item tax template exists: {purchase_title}")


def run():
    create_item_tax_templates()
    frappe.db.commit()
