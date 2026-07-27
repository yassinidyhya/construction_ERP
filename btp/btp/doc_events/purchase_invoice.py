import frappe
from frappe.utils import flt


RETENTION_PAYABLE_ACCOUNT = "Retention Payable"


def validate_purchase_invoice(doc, method=None):
	"""Compute retention amount from percent (base: grand total TTC)."""
	doc.custom_retention_amount = flt(doc.grand_total) * flt(doc.custom_retention_percent) / 100


def on_submit_purchase_invoice(doc, method=None):
	"""Move retention from Creditors to Retention Payable on submit."""
	if flt(doc.custom_retention_amount) <= 0:
		return

	retention_account = _get_retention_account(doc.company)
	amount = flt(doc.custom_retention_amount)

	je = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": doc.company,
			"posting_date": doc.posting_date,
			"user_remark": f"Retention {doc.name}",
		}
	)
	je.append(
		"accounts",
		{
			"account": doc.credit_to,
			"party_type": "Supplier",
			"party": doc.supplier,
			"reference_type": "Purchase Invoice",
			"reference_name": doc.name,
			"debit_in_account_currency": amount,
			"cost_center": doc.cost_center,
			"project": doc.project,
		},
	)
	je.append(
		"accounts",
		{
			"account": retention_account,
			"party_type": "Supplier",
			"party": doc.supplier,
			"credit_in_account_currency": amount,
			"cost_center": doc.cost_center,
			"project": doc.project,
		},
	)
	je.insert(ignore_permissions=True)
	je.submit()
	doc.db_set("custom_retention_journal_entry", je.name)


def on_cancel_purchase_invoice(doc, method=None):
	"""Cancel the retention JE when the invoice is cancelled."""
	if doc.custom_retention_journal_entry:
		je = frappe.get_doc("Journal Entry", doc.custom_retention_journal_entry)
		if je.docstatus == 1:
			je.flags.ignore_permissions = True
			je.cancel()


@frappe.whitelist()
def release_retention(purchase_invoice):
	"""Move retention back to Creditors so it can be paid via Payment Entry."""
	doc = frappe.get_doc("Purchase Invoice", purchase_invoice)
	frappe.has_permission("Purchase Invoice", "write", doc, throw=True)

	if doc.docstatus != 1:
		frappe.throw(frappe._("Purchase Invoice must be submitted."))
	if flt(doc.custom_retention_amount) <= 0:
		frappe.throw(frappe._("No retention held on this invoice."))
	if doc.custom_retention_released:
		frappe.throw(frappe._("Retention already released."))

	retention_account = _get_retention_account(doc.company)
	amount = flt(doc.custom_retention_amount)

	je = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": doc.company,
			"posting_date": frappe.utils.today(),
			"user_remark": f"Release retention {doc.name}",
		}
	)
	je.append(
		"accounts",
		{
			"account": retention_account,
			"party_type": "Supplier",
			"party": doc.supplier,
			"debit_in_account_currency": amount,
			"cost_center": doc.cost_center,
			"project": doc.project,
		},
	)
	je.append(
		"accounts",
		{
			"account": doc.credit_to,
			"party_type": "Supplier",
			"party": doc.supplier,
			"reference_type": "Purchase Invoice",
			"reference_name": doc.name,
			"credit_in_account_currency": amount,
			"cost_center": doc.cost_center,
			"project": doc.project,
		},
	)
	je.insert(ignore_permissions=True)
	je.submit()
	doc.db_set("custom_retention_released", 1)
	doc.db_set("custom_retention_release_journal_entry", je.name)
	return je.name


def _get_retention_account(company):
	account = frappe.db.get_value(
		"Account",
		{"account_name": RETENTION_PAYABLE_ACCOUNT, "company": company, "is_group": 0},
		"name",
	)
	if not account:
		frappe.throw(
			frappe._("Retention Payable account missing for company {0}.").format(company)
		)
	return account
