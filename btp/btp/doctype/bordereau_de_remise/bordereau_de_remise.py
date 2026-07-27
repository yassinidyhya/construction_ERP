import frappe
from frappe.model.document import Document
from frappe.utils import flt

from btp.btp.pdc import (
	PORTFOLIO_ACCOUNT,
	UNDER_COLLECTION_ACCOUNT,
	get_pdc_account,
	make_pdc_journal_entry,
)


class BordereaudeRemise(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().get("company")
		self.total_amount = sum(flt(row.amount) for row in self.cheques)

	def on_submit(self):
		if not self.cheques:
			frappe.throw(frappe._("Cannot submit a Bordereau de Remise without cheques."))

		portfolio = get_pdc_account(PORTFOLIO_ACCOUNT, self.company)
		under_collection = get_pdc_account(UNDER_COLLECTION_ACCOUNT, self.company)

		rows = []
		for row in self.cheques:
			cheque = frappe.get_doc("Cheque", row.cheque)
			if cheque.status != "Portfolio" or cheque.direction != "Received":
				frappe.throw(
					frappe._("Cheque {0} is not in Portfolio (status: {1}).").format(
						cheque.name, cheque.status
					)
				)
			rows.append(
				{
					"account": under_collection,
					"debit_in_account_currency": flt(cheque.amount),
					"user_remark": f"Deposit {cheque.cheque_no} ({cheque.name})",
				}
			)
			rows.append(
				{
					"account": portfolio,
					"credit_in_account_currency": flt(cheque.amount),
					"user_remark": f"Deposit {cheque.cheque_no} ({cheque.name})",
				}
			)

		je_name = make_pdc_journal_entry(
			self.company, self.posting_date, rows, f"Bordereau de remise {self.name}"
		)
		self.db_set("journal_entry", je_name)

		for row in self.cheques:
			cheque = frappe.get_doc("Cheque", row.cheque)
			cheque.db_set("status", "Deposited")
			cheque.db_set("bordereau", self.name)

	def on_cancel(self):
		if self.journal_entry:
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.flags.ignore_permissions = True
				je.cancel()

		for row in self.cheques:
			if not frappe.db.exists("Cheque", row.cheque):
				continue
			cheque = frappe.get_doc("Cheque", row.cheque)
			if cheque.status == "Deposited":
				cheque.db_set("status", "Portfolio")
				cheque.db_set("bordereau", None)
