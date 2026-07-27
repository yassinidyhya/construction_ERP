import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def run():
	company = frappe.defaults.get_defaults().get("company")
	abbr = frappe.db.get_value("Company", company, "abbr")

	# 1. Retention Payable account under Accounts Payable
	parent = frappe.db.get_value(
		"Account",
		{"account_name": "Accounts Payable", "company": company, "is_group": 1},
		"name",
	)
	assert parent, "Accounts Payable group not found"

	if not frappe.db.exists(
		"Account", {"account_name": "Retention Payable", "company": company, "is_group": 0}
	):
		account = frappe.get_doc(
			{
				"doctype": "Account",
				"account_name": "Retention Payable",
				"parent_account": parent,
				"company": company,
				"is_group": 0,
				"account_type": "Payable",
				"account_currency": "MAD",
			}
		)
		account.insert(ignore_permissions=True)
		print("created account:", account.name)
	else:
		print("account exists")

	# 2. Retention custom fields on Purchase Invoice
	create_custom_fields(
		{
			"Purchase Invoice": [
				{
					"fieldname": "custom_retention_percent",
					"fieldtype": "Percent",
					"label": "Retention %",
					"insert_after": "taxes_and_charges",
					"module": "BTP",
				},
				{
					"fieldname": "custom_retention_amount",
					"fieldtype": "Currency",
					"label": "Retention Amount",
					"insert_after": "custom_retention_percent",
					"read_only": 1,
					"module": "BTP",
				},
				{
					"fieldname": "custom_retention_journal_entry",
					"fieldtype": "Link",
					"label": "Retention Journal Entry",
					"options": "Journal Entry",
					"insert_after": "custom_retention_amount",
					"read_only": 1,
					"no_copy": 1,
					"module": "BTP",
				},
				{
					"fieldname": "custom_retention_released",
					"fieldtype": "Check",
					"label": "Retention Released",
					"insert_after": "custom_retention_journal_entry",
					"read_only": 1,
					"default": "0",
					"module": "BTP",
				},
				{
					"fieldname": "custom_retention_release_journal_entry",
					"fieldtype": "Link",
					"label": "Retention Release Journal Entry",
					"options": "Journal Entry",
					"insert_after": "custom_retention_released",
					"read_only": 1,
					"no_copy": 1,
					"module": "BTP",
				},
			]
		}
	)
	print("custom fields created")

	frappe.db.commit()
	print("RETENTION SETUP OK")
