import frappe


def run():
	company = frappe.defaults.get_defaults().get("company")
	cash = frappe.db.get_value(
		"Account", {"account_type": "Cash", "company": company, "is_group": 0}, "name"
	)
	expense = "Miscellaneous Expenses - " + frappe.db.get_value("Company", company, "abbr")
	bank = frappe.db.get_value(
		"Account", {"account_type": "Bank", "company": company, "is_group": 0}, "name"
	)
	assert cash and frappe.db.exists("Account", expense) and bank, (cash, expense, bank)

	cj = frappe.get_doc(
		{
			"doctype": "Caisse Journal",
			"company": company,
			"date": "2026-07-27",
			"cash_account": cash,
			"opening_balance": 1000,
			"lines": [
				{
					"type": "In",
					"category": "Alimentation",
					"description": "Alimentation caisse depuis banque",
					"account": bank,
					"amount": 5000,
				},
				{
					"type": "Out",
					"category": "Fuel",
					"description": "Gasoil groupe electrogene",
					"account": expense,
					"amount": 800,
				},
				{
					"type": "Out",
					"category": "Transport",
					"description": "Transport materiel",
					"account": expense,
					"amount": 200,
				},
			],
		}
	)
	cj.insert()
	cj.submit()

	print("CJ:", cj.name, "closing:", cj.closing_balance, "JE:", cj.journal_entry)
	assert cj.closing_balance == 5000, cj.closing_balance

	je = frappe.get_doc("Journal Entry", cj.journal_entry)
	print("JE docstatus:", je.docstatus, "posting_date:", je.posting_date, "total:", je.total_debit)
	assert je.docstatus == 1
	assert float(je.total_debit) == 6000, je.total_debit
	for a in je.accounts:
		print("  ", a.account, float(a.debit), float(a.credit))

	gl = frappe.get_all("GL Entry", filters={"voucher_no": je.name}, fields=["account", "debit", "credit"])
	print("GL entries:", len(gl))
	assert len(gl) == 6

	cj.cancel()
	je.reload()
	print("after cancel CJ docstatus:", cj.docstatus, "JE docstatus:", je.docstatus)
	assert je.docstatus == 2

	frappe.db.commit()
	print("TEST OK")
