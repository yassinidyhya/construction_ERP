import frappe
from frappe.model.document import Document

from btp.btp.doctype.site_file_folder.site_file_folder import (
    create_site_file_folder,
)


def get_default_company():
    return frappe.defaults.get_defaults().get("company")


class ConstructionSite(Document):
    def after_insert(self):
        self.create_linked_project()
        self.create_linked_cost_center()
        create_site_file_folder(self)

    def create_linked_project(self):
        if self.project:
            return

        company = get_default_company()
        if not company:
            return

        project = frappe.get_doc(
            {
                "doctype": "Project",
                "project_name": self.site_name,
                "project_type": "External",
                "status": "Open",
                "expected_start_date": self.start_date,
                "expected_end_date": self.end_date,
                "customer": self.client,
                "company": company,
            }
        )
        project.insert(ignore_permissions=True)
        self.db_set("project", project.name)

    def create_linked_cost_center(self):
        company = get_default_company()
        if not company:
            return

        # Find the root cost center for the company
        root_cc = frappe.db.get_value(
            "Cost Center",
            {"company": company, "is_group": 1, "parent_cost_center": ""},
            "name",
        )
        if not root_cc:
            root_cc = frappe.db.get_value(
                "Cost Center", {"company": company, "is_group": 1}, "name"
            )
        if not root_cc:
            return

        if frappe.db.exists("Cost Center", {"cost_center_name": self.site_code, "company": company}):
            return

        cost_center = frappe.get_doc(
            {
                "doctype": "Cost Center",
                "cost_center_name": self.site_code,
                "parent_cost_center": root_cc,
                "company": company,
                "is_group": 0,
            }
        )
        cost_center.insert(ignore_permissions=True)
