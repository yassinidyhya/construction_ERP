import frappe

from btp.btp.pdc import (
	ISSUED_TRANSIT_ACCOUNT,
	PORTFOLIO_ACCOUNT,
	get_pdc_account,
)


def _is_cheque_payment(doc):
	if not doc.mode_of_payment:
		return False
	return frappe.db.get_value("Mode of Payment", doc.mode_of_payment, "type") == "Cheque"


def force_transit_accounts(doc, method=None):
	"""Route cheque payments through the 511x transit accounts, never the bank."""
	if not _is_cheque_payment(doc):
		return

	def set_account(field, account_name):
		account = get_pdc_account(account_name, doc.company)
		doc.set(field, account)
		doc.set(
			field + "_account_currency",
			frappe.get_cached_value("Account", account, "account_currency"),
		)

	if doc.payment_type == "Receive":
		set_account("paid_to", PORTFOLIO_ACCOUNT)
	elif doc.payment_type == "Pay":
		set_account("paid_from", ISSUED_TRANSIT_ACCOUNT)


def create_cheque_on_submit(doc, method=None):
	"""Register a Cheque record when a cheque Payment Entry is submitted."""
	if not _is_cheque_payment(doc):
		return
	if doc.payment_type not in ("Receive", "Pay"):
		return

	direction = "Received" if doc.payment_type == "Receive" else "Issued"
	cheque = frappe.get_doc(
		{
			"doctype": "Cheque",
			"instrument_type": "Cheque",
			"direction": direction,
			"status": "Portfolio" if direction == "Received" else "Issued",
			"company": doc.company,
			"party_type": doc.party_type,
			"party": doc.party,
			"payment_entry": doc.name,
			"cheque_no": doc.reference_no,
			"cheque_date": doc.reference_date,
			"due_date": doc.reference_date,
			"amount": doc.paid_amount,
		}
	)
	cheque.insert(ignore_permissions=True)
	frappe.msgprint(
		frappe._("Cheque {0} registered in the cheque portfolio.").format(cheque.name),
		indicator="green",
		alert=True,
	)


def cleanup_cheque_on_cancel(doc, method=None):
	"""Cancel of the Payment Entry removes its Cheque if it never moved."""
	cheque_name = frappe.db.get_value("Cheque", {"payment_entry": doc.name}, "name")
	if not cheque_name:
		return

	cheque = frappe.get_doc("Cheque", cheque_name)
	if cheque.status in ("Portfolio", "Issued"):
		frappe.delete_doc("Cheque", cheque_name, force=1, ignore_permissions=True)
	else:
		frappe.throw(
			frappe._(
				"Cannot cancel: cheque {0} already moved (status: {1}). Reverse the cheque first."
			).format(cheque.name, cheque.status)
		)
