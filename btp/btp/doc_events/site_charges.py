import frappe


def warn_if_missing_site(doc, method=None):
	"""Warn when a construction expense is saved without Project/Cost Center.

	Site charges must post to a Project + Cost Center (= site). Company
	overhead can legitimately skip this, so we warn instead of blocking.
	"""
	if doc.project or doc.cost_center:
		return

	frappe.msgprint(
		frappe._(
			"Warning: no Project or Cost Center set. "
			"If this is a site expense, select the site Project/Cost Center."
		),
		indicator="orange",
		alert=True,
	)
