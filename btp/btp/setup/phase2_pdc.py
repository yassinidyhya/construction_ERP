import frappe

from btp.btp.pdc import ISSUED_TRANSIT_ACCOUNT, PORTFOLIO_ACCOUNT, UNDER_COLLECTION_ACCOUNT


def _ensure_account(account_name, parent, company):
	if frappe.db.exists(
		"Account", {"account_name": account_name, "company": company, "is_group": 0}
	):
		return frappe.db.get_value(
			"Account", {"account_name": account_name, "company": company, "is_group": 0}, "name"
		)
	account = frappe.get_doc(
		{
			"doctype": "Account",
			"account_name": account_name,
			"parent_account": parent,
			"company": company,
			"is_group": 0,
			"account_type": "Bank",
			"account_currency": "MAD",
		}
	)
	account.insert(ignore_permissions=True)
	print("created account:", account.name)
	return account.name


def run():
	company = frappe.defaults.get_defaults().get("company")

	bank_group = frappe.db.get_value(
		"Account", {"account_name": "Bank Accounts", "company": company, "is_group": 1}, "name"
	)
	assert bank_group, "Bank Accounts group not found"

	_ensure_account(PORTFOLIO_ACCOUNT, bank_group, company)
	_ensure_account(UNDER_COLLECTION_ACCOUNT, bank_group, company)
	_ensure_account(ISSUED_TRANSIT_ACCOUNT, bank_group, company)

	# Allow "Cheque" as a Mode of Payment type (property setter, upgrade-safe)
	from frappe.custom.doctype.property_setter.property_setter import make_property_setter

	if not frappe.db.exists(
		"Property Setter",
		{"doc_type": "Mode of Payment", "field_name": "type", "property": "options"},
	):
		ps = make_property_setter(
			"Mode of Payment", "type", "options", "Cash\nBank\nGeneral\nPhone\nCheque", "Text"
		)
		ps.module = "BTP"
		ps.save(ignore_permissions=True)
		print("property setter: MoP type options + Cheque")

	# Route the Cheque Mode of Payment to the portfolio account by default
	mop = frappe.get_doc("Mode of Payment", "Cheque")
	if mop.type != "Cheque":
		mop.type = "Cheque"
	portfolio = frappe.db.get_value(
		"Account", {"account_name": PORTFOLIO_ACCOUNT, "company": company, "is_group": 0}, "name"
	)
	if not any(a.company == company for a in mop.accounts):
		mop.append("accounts", {"company": company, "default_account": portfolio})
	mop.save(ignore_permissions=True)
	print("MoP Cheque: type=Cheque, default account set")

	frappe.db.commit()
	print("PDC SETUP OK")
