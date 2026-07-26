import frappe
from frappe import _


SITE_STOCK_ENTRY_PURPOSES = ("Material Issue", "Material Transfer")


def validate_stock_entry(doc, method=None):
    if doc.purpose not in SITE_STOCK_ENTRY_PURPOSES:
        return

    if not doc.custom_site:
        frappe.throw(
            _("Site is mandatory for Stock Entries of purpose {0}").format(doc.purpose),
            title=_("Missing Site"),
        )

    if not doc.custom_reference_doctype or not doc.custom_reference_name:
        frappe.throw(
            _(
                "Reference DocType and Reference Name are mandatory when a Site is selected for {0}"
            ).format(doc.purpose),
            title=_("Missing Reference"),
        )
