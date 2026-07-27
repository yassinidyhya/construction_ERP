frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		if (
			frm.doc.docstatus === 1 &&
			flt(frm.doc.custom_retention_amount) > 0 &&
			!frm.doc.custom_retention_released
		) {
			frm.add_custom_button(__("Release Retention"), () => {
				frappe.confirm(
					__("Release the retention of {0} back to Accounts Payable?", [
						format_currency(frm.doc.custom_retention_amount, frm.doc.currency),
					]),
					() => {
						frm.call({
							method: "btp.btp.doc_events.purchase_invoice.release_retention",
							args: { purchase_invoice: frm.doc.name },
							freeze: true,
							callback: () => frm.reload_doc(),
						});
					}
				);
			});
		}
	},
});
