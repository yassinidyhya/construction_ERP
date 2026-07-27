import frappe
from frappe.utils import flt


def run():
	from btp.btp.doc_events.purchase_invoice import release_retention

	src_name = frappe.db.get_value("Purchase Invoice", {"docstatus": 1}, "name")
	src = frappe.get_doc("Purchase Invoice", src_name)

	# --- Flow A: retention held on submit, then cancelled (no release) ---
	pi = frappe.copy_doc(src)
	pi.posting_date = "2026-07-27"
	pi.set_posting_time = 1
	pi.custom_retention_percent = 7
	pi.insert()
	pi.submit()

	expected_ret = flt(pi.grand_total) * 0.07
	print("PI:", pi.name, "grand:", pi.grand_total, "retention:", pi.custom_retention_amount)
	assert abs(flt(pi.custom_retention_amount) - expected_ret) < 0.01
	je_name = pi.custom_retention_journal_entry
	assert je_name, "no retention JE"
	je = frappe.get_doc("Journal Entry", je_name)
	assert je.docstatus == 1
	pi.reload()
	print("outstanding after retention:", pi.outstanding_amount)
	assert abs(flt(pi.outstanding_amount) - (flt(pi.grand_total) - expected_ret)) < 0.01

	# --- Flow B: release retention ---
	je2_name = release_retention(pi.name)
	pi.reload()
	assert pi.custom_retention_released == 1
	pi.reload()
	print("outstanding after release:", pi.outstanding_amount)
	assert abs(flt(pi.outstanding_amount) - flt(pi.grand_total)) < 0.01

	# --- cancel: retention JE must cancel automatically ---
	pi.cancel()
	je.reload()
	assert je.docstatus == 2, "retention JE not cancelled with PI"
	# release JE needs manual cancel before full delete
	frappe.get_doc("Journal Entry", je2_name).cancel()

	# cleanup
	pi.reload()
	frappe.delete_doc("Purchase Invoice", pi.name, force=1)
	frappe.delete_doc("Journal Entry", je_name, force=1)
	frappe.delete_doc("Journal Entry", je2_name, force=1)
	frappe.db.commit()
	print("RETENTION TEST OK")
