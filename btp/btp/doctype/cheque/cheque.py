import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

from btp.btp.pdc import (
	PORTFOLIO_ACCOUNT,
	UNDER_COLLECTION_ACCOUNT,
	ISSUED_TRANSIT_ACCOUNT,
	get_pdc_account,
	make_pdc_journal_entry,
)


class Cheque(Document):
	@frappe.whitelist()
	def collect(self, posting_date=None, bank_account=None):
		"""Bank cleared a deposited received cheque: Dr Bank / Cr Under Collection."""
		self._check_transition("Collected", ["Deposited"])
		posting_date = posting_date or today()
		bank_account = bank_account or self._bordereau_bank_account()
		under_collection = get_pdc_account(UNDER_COLLECTION_ACCOUNT, self.company)

		je = make_pdc_journal_entry(
			self.company,
			posting_date,
			[
				{
					"account": bank_account,
					"debit_in_account_currency": flt(self.amount),
					"user_remark": f"Collect {self.name}",
				},
				{
					"account": under_collection,
					"credit_in_account_currency": flt(self.amount),
					"user_remark": f"Collect {self.name}",
				},
			],
			f"Collect cheque {self.cheque_no} ({self.name})",
		)
		self.db_set("status", "Collected")
		return je

	@frappe.whitelist()
	def reject(self, posting_date=None):
		"""Cheque bounced: reopen the customer debt (Dr Debtors / Cr Under Collection)."""
		self._check_transition("Rejected", ["Deposited"])
		posting_date = posting_date or today()
		under_collection = get_pdc_account(UNDER_COLLECTION_ACCOUNT, self.company)
		party_account = self._party_account()

		je = make_pdc_journal_entry(
			self.company,
			posting_date,
			[
				{
					"account": party_account,
					"party_type": self.party_type,
					"party": self.party,
					"debit_in_account_currency": flt(self.amount),
					"user_remark": f"Reject {self.name}",
				},
				{
					"account": under_collection,
					"credit_in_account_currency": flt(self.amount),
					"user_remark": f"Reject {self.name}",
				},
			],
			f"Reject cheque {self.cheque_no} ({self.name})",
		)
		self.db_set("status", "Rejected")
		return je

	@frappe.whitelist()
	def redeposit(self):
		"""Re-present a rejected cheque: Dr Portfolio / Cr Debtors (paper is ours again)."""
		self._check_transition("Portfolio", ["Rejected"])
		portfolio = get_pdc_account(PORTFOLIO_ACCOUNT, self.company)
		party_account = self._party_account()

		je = make_pdc_journal_entry(
			self.company,
			today(),
			[
				{
					"account": portfolio,
					"debit_in_account_currency": flt(self.amount),
					"user_remark": f"Redeposit {self.name}",
				},
				{
					"account": party_account,
					"party_type": self.party_type,
					"party": self.party,
					"credit_in_account_currency": flt(self.amount),
					"user_remark": f"Redeposit {self.name}",
				},
			],
			f"Redeposit cheque {self.cheque_no} ({self.name})",
		)
		self.db_set("status", "Portfolio")
		self.db_set("bordereau", None)
		return je

	@frappe.whitelist()
	def mark_returned(self):
		"""Hand the bounced paper back to the customer (status only; debt already reopened)."""
		self._check_transition("Returned", ["Rejected"])
		self.db_set("status", "Returned")

	@frappe.whitelist()
	def encash(self, posting_date=None, bank_account=None):
		"""Issued cheque cleared by the bank: Dr Issued Transit / Cr Bank."""
		self._check_transition("Encashed", ["Issued"])
		posting_date = posting_date or today()
		transit = get_pdc_account(ISSUED_TRANSIT_ACCOUNT, self.company)
		if not bank_account:
			bank_account = frappe.db.get_value(
				"Account",
				{"account_type": "Bank", "company": self.company, "is_group": 0,
				 "account_name": ["not in", [PORTFOLIO_ACCOUNT, UNDER_COLLECTION_ACCOUNT, ISSUED_TRANSIT_ACCOUNT]]},
				"name",
			)
		if not bank_account:
			frappe.throw(frappe._("No bank account found for encashment."))

		je = make_pdc_journal_entry(
			self.company,
			posting_date,
			[
				{
					"account": transit,
					"debit_in_account_currency": flt(self.amount),
					"user_remark": f"Encash {self.name}",
				},
				{
					"account": bank_account,
					"credit_in_account_currency": flt(self.amount),
					"user_remark": f"Encash {self.name}",
				},
			],
			f"Encash cheque {self.cheque_no} ({self.name})",
		)
		self.db_set("status", "Encashed")
		return je

	def _check_transition(self, target, allowed_from):
		if self.status not in allowed_from:
			frappe.throw(
				frappe._("Cannot move cheque {0} from {1} to {2}.").format(
					self.name, self.status, target
				)
			)

	def _party_account(self):
		party_account = frappe.db.get_value(
			"Party Account",
			{"parenttype": self.party_type, "parent": self.party, "company": self.company},
			"account",
		)
		if not party_account:
			company_doc = frappe.get_doc("Company", self.company)
			party_account = (
				company_doc.default_receivable_account
				if self.party_type == "Customer"
				else company_doc.default_payable_account
			)
		if not party_account:
			frappe.throw(frappe._("No party account for {0} {1}.").format(self.party_type, self.party))
		return party_account

	def _bordereau_bank_account(self):
		if self.bordereau:
			return frappe.db.get_value("Deposit Slip", self.bordereau, "bank_account")
		# fallback: first non-transit bank account
		bank = frappe.db.get_value(
			"Account",
			{"account_type": "Bank", "company": self.company, "is_group": 0,
			 "account_name": ["not in", [PORTFOLIO_ACCOUNT, UNDER_COLLECTION_ACCOUNT, ISSUED_TRANSIT_ACCOUNT]]},
			"name",
		)
		if not bank:
			frappe.throw(frappe._("No bank account found."))
		return bank
