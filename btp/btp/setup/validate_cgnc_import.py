import frappe
import os
from frappe.utils import get_site_path
from frappe.utils.file_manager import save_file

COMPANY = "RIJAL TRAVAUX (Demo)"
LOCAL_CSV = "/workspace/development/frappe-bench/apps/btp/btp/fixtures/chart_of_accounts/plan_comptable_marocain.csv"


def run():
    # Ensure the demo company exists
    if not frappe.db.exists("Company", COMPANY):
        print(f"Demo company {COMPANY} not found")
        return

    # Read CSV content and save as File
    with open(LOCAL_CSV, "rb") as f:
        content = f.read()

    file_doc = save_file(
        fname="plan_comptable_marocain.csv",
        content=content,
        dt="Chart of Accounts Importer",
        dn="Chart of Accounts Importer",
        folder=None,
        is_private=1,
    )
    file_url = file_doc.file_url
    print(f"File saved: {file_url}")

    # Validate columns first (lightweight check)
    from erpnext.accounts.doctype.chart_of_accounts_importer.chart_of_accounts_importer import (
        get_file,
        validate_accounts,
    )

    file_doc, extension = get_file(file_url)
    validate_accounts(file_doc, extension)
    print("CSV validation passed")

    # Import the chart
    from erpnext.accounts.doctype.chart_of_accounts_importer.chart_of_accounts_importer import (
        import_coa,
    )

    import_coa(file_url, COMPANY)
    print(f"CGNC imported successfully into {COMPANY}")
