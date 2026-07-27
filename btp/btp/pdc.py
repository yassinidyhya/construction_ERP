"""Shared account resolution for the custom PDC (chèques / effets) flow.

Moroccan CGNC equivalents:
- Cheques in Portfolio      ~ 51111 Chèques en portefeuille
- Cheques Under Collection  ~ 51112 Chèques à l'encaissement
- Cheques Issued Transit    ~ supplier PDC in transit (4415-side)
"""

import frappe

PORTFOLIO_ACCOUNT = "Cheques in Portfolio"
UNDER_COLLECTION_ACCOUNT = "Cheques Under Collection"
ISSUED_TRANSIT_ACCOUNT = "Cheques Issued Transit"


def get_pdc_account(account_name, company):
	account = frappe.db.get_value(
		"Account",
		{"account_name": account_name, "company": company, "is_group": 0},
		"name",
	)
	if not account:
		frappe.throw(
			frappe._("PDC account {0} missing for company {1}. Run the PDC setup.").format(
				account_name, company
			)
		)
	return account


def make_pdc_journal_entry(company, posting_date, rows, remark):
	"""Create and submit a Journal Entry for a PDC transition.

	rows: list of dicts with account, debit/credit and optional party fields.
	"""
	je = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": company,
			"posting_date": posting_date,
			"user_remark": remark,
		}
	)
	for row in rows:
		je.append("accounts", row)
	je.insert(ignore_permissions=True)
	je.submit()
	return je.name
