import frappe
from frappe.model.document import Document


class SiteFileFolder(Document):
    def validate(self):
        if not self.folder_path:
            self.folder_path = f"Home/Chantiers/{self.site_code}/{self.year}"

    def after_insert(self):
        self.ensure_folder_exists(self.folder_path)

    @staticmethod
    def ensure_folder_exists(folder_path):
        if frappe.db.exists("File", folder_path):
            return folder_path

        parts = folder_path.split("/")
        current_path = ""
        for part in parts:
            if not part:
                continue
            parent_path = current_path or ""
            current_path = f"{parent_path}/{part}".lstrip("/") if parent_path else part
            if frappe.db.exists("File", current_path):
                continue
            folder = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": part,
                    "is_folder": 1,
                    "folder": parent_path,
                }
            )
            folder.insert(ignore_permissions=True)
        return current_path


def create_site_file_folder(construction_site, year=None):
    if not year:
        from frappe.utils import now

        year = str(now()).split("-")[0]

    folder_path = f"Home/Chantiers/{construction_site.site_code}/{year}"
    if frappe.db.exists("Site File Folder", {"construction_site": construction_site.name, "year": year}):
        return frappe.get_doc("Site File Folder", {"construction_site": construction_site.name, "year": year})

    site_folder = frappe.get_doc(
        {
            "doctype": "Site File Folder",
            "construction_site": construction_site.name,
            "site_code": construction_site.site_code,
            "year": year,
            "folder_path": folder_path,
        }
    )
    site_folder.insert(ignore_permissions=True)
    return site_folder
