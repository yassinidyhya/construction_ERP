import frappe
from frappe.utils import flt, today


def run():
	from btp.btp.pdc import (
		ISSUED_TRANSIT_ACCOUNT,
		PORTFOLIO_ACCOUNT,
		UNDER_COLLECTION_ACCOUNT,
		get_pdc_account,
	)
	from btp.btp.setup.phase2_pdc import run as setup_run

	setup_run()

	company = frappe.defaults.get_defaults().get("company")
	customer = frappe.db.get_value("Customer", {}, "name")
	supplier = frappe.db.get_value("Supplier", {}, "name")
	bank = frappe.db.get_value(
		"Account",
		{"account_type": "Bank", "company": company, "is_group": 0,
		 "account_name": ["not in", [PORTFOLIO_ACCOUNT, UNDER_COLLECTION_ACCOUNT, ISSUED_TRANSIT_ACCOUNT]]},
		"name",
	)
	portfolio = get_pdc_account(PORTFOLIO_ACCOUNT, company)
	under_collection = get_pdc_account(UNDER_COLLECTION_ACCOUNT, company)
	transit = get_pdc_account(ISSUED_TRANSIT_ACCOUNT, company)

	created = {"pe": [], "cheque": [], "bdr": [], "je": []}

	def make_pe(ptype, party_type, party, amount, ref):
		pe = frappe.get_doc(
			{
				"doctype": "Payment Entry",
				"payment_type": ptype,
				"party_type": party_type,
				"party": party,
				"company": company,
				"mode_of_payment": "Cheque",
				"paid_amount": amount,
				"received_amount": amount,
				"reference_no": ref,
				"reference_date": today(),
			}
		)
		pe.insert(ignore_permissions=True)
		pe.submit()
		created["pe"].append(pe.name)
		return pe

	def get_cheque(pe_name):
		name = frappe.db.get_value("Cheque", {"payment_entry": pe_name}, "name")
		assert name, f"no cheque for {pe_name}"
		created["cheque"].append(name)
		return frappe.get_doc("Cheque", name)

	# --- 1. receive customer cheque ---
	pe1 = make_pe("Receive", "Customer", customer, 10000, "CHQ-RT-001")
	assert pe1.paid_to == portfolio, pe1.paid_to
	ch1 = get_cheque(pe1.name)
	assert ch1.status == "Portfolio" and ch1.direction == "Received"
	print("1. received:", ch1.name, ch1.status, "paid_to:", pe1.paid_to)

	# --- 2. deposit via bordereau ---
	bdr = frappe.get_doc(
		{
			"doctype": "Bordereau de Remise",
			"company": company,
			"posting_date": today(),
			"bank_account": bank,
			"cheques": [{"cheque": ch1.name}],
		}
	)
	bdr.insert(ignore_permissions=True)
	bdr.submit()
	created["bdr"].append(bdr.name)
	created["je"].append(bdr.journal_entry)
	ch1.reload()
	assert ch1.status == "Deposited" and ch1.bordereau == bdr.name
	print("2. deposited via", bdr.name, "JE:", bdr.journal_entry)

	# --- 3. collect ---
	je = ch1.collect()
	created["je"].append(je)
	ch1.reload()
	assert ch1.status == "Collected"
	print("3. collected, JE:", je)

	# --- 4. reject + redeposit ---
	pe2 = make_pe("Receive", "Customer", customer, 5000, "CHQ-RT-002")
	ch2 = get_cheque(pe2.name)
	bdr2 = frappe.get_doc(
		{
			"doctype": "Bordereau de Remise",
			"company": company,
			"posting_date": today(),
			"bank_account": bank,
			"cheques": [{"cheque": ch2.name}],
		}
	)
	bdr2.insert(ignore_permissions=True)
	bdr2.submit()
	created["bdr"].append(bdr2.name)
	created["je"].append(bdr2.journal_entry)
	ch2.reload()
	je = ch2.reject()
	created["je"].append(je)
	ch2.reload()
	assert ch2.status == "Rejected"
	print("4a. rejected, JE:", je)
	je = ch2.redeposit()
	created["je"].append(je)
	ch2.reload()
	assert ch2.status == "Portfolio" and not ch2.bordereau
	print("4b. redeposited, JE:", je)

	# --- 5. issued supplier cheque ---
	pe3 = make_pe("Pay", "Supplier", supplier, 7000, "CHQ-RT-003")
	assert pe3.paid_from == transit, pe3.paid_from
	ch3 = get_cheque(pe3.name)
	assert ch3.status == "Issued" and ch3.direction == "Issued"
	print("5a. issued:", ch3.name, ch3.status, "paid_from:", pe3.paid_from)
	je = ch3.encash()
	created["je"].append(je)
	ch3.reload()
	assert ch3.status == "Encashed"
	print("5b. encashed, JE:", je)

	# --- GL sanity: every JE balanced with GL rows ---
	for je_name in created["je"]:
		rows = frappe.get_all(
			"GL Entry",
			filters={"voucher_no": je_name, "is_cancelled": 0},
			fields=["debit", "credit"],
		)
		assert rows, je_name
		assert abs(sum(flt(r.debit) for r in rows) - sum(flt(r.credit) for r in rows)) < 0.01, je_name
	print("GL balanced for", len(created["je"]), "journal entries")

	# --- cleanup (order matters: bordereaux, JEs, cheques, then PEs) ---
	for b in created["bdr"]:
		doc = frappe.get_doc("Bordereau de Remise", b)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Bordereau de Remise", b, force=1, ignore_permissions=True)
	for j in created["je"]:
		doc = frappe.get_doc("Journal Entry", j)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Journal Entry", j, force=1, ignore_permissions=True)
	for ch in created["cheque"]:
		if frappe.db.exists("Cheque", ch):
			frappe.delete_doc("Cheque", ch, force=1, ignore_permissions=True)
	for p in created["pe"]:
		doc = frappe.get_doc("Payment Entry", p)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Payment Entry", p, force=1, ignore_permissions=True)

	frappe.db.commit()
	print("PDC E2E TEST OK")
