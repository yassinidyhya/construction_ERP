import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CaisseJournal(Document):
	def validate(self):
		self.set_defaults()
		self.set_site_links()
		self.compute_totals()

	def set_defaults(self):
		if not self.company:
			self.company = frappe.defaults.get_defaults().get("company")

	def set_site_links(self):
		if not self.site:
			self.project = None
			self.cost_center = None
			return

		site_code, project = frappe.db.get_value(
			"Construction Site", self.site, ["site_code", "project"]
		)
		self.project = project
		self.cost_center = frappe.db.get_value(
			"Cost Center",
			{"cost_center_name": site_code, "company": self.company, "is_group": 0},
			"name",
		)

	def compute_totals(self):
		self.total_in = 0
		self.total_out = 0
		for row in self.lines:
			if row.type == "In":
				self.total_in += flt(row.amount)
			else:
				self.total_out += flt(row.amount)
		self.closing_balance = flt(self.opening_balance) + self.total_in - self.total_out

	def on_submit(self):
		if not self.lines:
			frappe.throw(frappe._("Cannot submit a Caisse Journal without lines."))

		je = frappe.get_doc(
			{
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"company": self.company,
				"posting_date": self.date,
				"user_remark": f"Caisse Journal {self.name}",
			}
		)

		for row in self.lines:
			amount = flt(row.amount)
			line_context = {
				"cost_center": self.cost_center,
				"project": self.project,
				"user_remark": row.description,
			}
			if row.type == "In":
				je.append(
					"accounts",
					{
						"account": self.cash_account,
						"debit_in_account_currency": amount,
						**line_context,
					},
				)
				je.append(
					"accounts",
					{
						"account": row.account,
						"credit_in_account_currency": amount,
						**line_context,
					},
				)
			else:
				je.append(
					"accounts",
					{
						"account": row.account,
						"debit_in_account_currency": amount,
						**line_context,
					},
				)
				je.append(
					"accounts",
					{
						"account": self.cash_account,
						"credit_in_account_currency": amount,
						**line_context,
					},
				)

		je.insert(ignore_permissions=True)
		je.submit()
		self.db_set("journal_entry", je.name)

	def on_cancel(self):
		if self.journal_entry:
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.flags.ignore_permissions = True
				je.cancel()
