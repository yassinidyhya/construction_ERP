frappe.ui.form.on("Cheque", {
	refresh(frm) {
		if (frm.is_new()) return;

		const call = (method, label) => {
			frm.add_custom_button(__(label), () => {
				frm.call({
					doc: frm.doc,
					method: method,
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			});
		};

		if (frm.doc.direction === "Received") {
			if (frm.doc.status === "Deposited") {
				call("collect", "Collect");
				call("reject", "Reject");
			}
			if (frm.doc.status === "Rejected") {
				call("redeposit", "Redeposit");
				call("mark_returned", "Mark Returned");
			}
		}
		if (frm.doc.direction === "Issued" && frm.doc.status === "Issued") {
			call("encash", "Encash");
		}
	},
});
