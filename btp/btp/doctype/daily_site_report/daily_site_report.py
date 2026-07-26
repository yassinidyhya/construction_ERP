import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class DailySiteReport(Document):
    def on_submit(self):
        for row in self.workers:
            self.create_or_update_attendance(row)
        self.link_photos_to_site_folder()

    def link_photos_to_site_folder(self):
        if not self.photos:
            return

        year = str(getdate(self.report_date).year)
        folder_path = frappe.db.get_value(
            "Site File Folder",
            {"construction_site": self.site, "year": year},
            "folder_path",
        )
        if not folder_path:
            return

        photo_urls = {row.photo for row in self.photos if row.photo}
        attached_files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Daily Site Report",
                "attached_to_name": self.name,
            },
            pluck="name",
        )

        for file_name in attached_files:
            file_doc = frappe.get_doc("File", file_name)
            if file_doc.file_url in photo_urls:
                file_doc.folder = folder_path
                file_doc.save(ignore_permissions=True)

    def create_or_update_attendance(self, row):
        if not row.worker or not self.report_date:
            return

        status = row.attendance_status or "Present"
        company = frappe.defaults.get_defaults().get("company")

        existing = frappe.db.get_value(
            "Attendance",
            {"employee": row.worker, "attendance_date": self.report_date},
            "name",
        )

        if existing:
            attendance = frappe.get_doc("Attendance", existing)
            if attendance.docstatus == 1:
                attendance.db_set("custom_site", self.site)
                return

            attendance.status = status
            attendance.custom_site = self.site
            attendance.company = attendance.company or company
            attendance.save(ignore_permissions=True)
            attendance.submit()
        else:
            attendance = frappe.get_doc(
                {
                    "doctype": "Attendance",
                    "employee": row.worker,
                    "attendance_date": self.report_date,
                    "status": status,
                    "custom_site": self.site,
                    "company": company,
                }
            )
            attendance.insert(ignore_permissions=True)
            attendance.submit()
