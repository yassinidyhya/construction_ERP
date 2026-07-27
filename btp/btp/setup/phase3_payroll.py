import frappe

G = "(SB + INDTR + PP + HS)"

COMPONENTS = [
	# Earnings
	{"salary_component": "Salaire de base", "salary_component_abbr": "SB", "type": "Earning",
	 "depends_on_payment_days": 1},
	{"salary_component": "Indemnité de transport", "salary_component_abbr": "INDTR", "type": "Earning",
	 "depends_on_payment_days": 0},
	{"salary_component": "Prime de panier", "salary_component_abbr": "PP", "type": "Earning",
	 "depends_on_payment_days": 0},
	{"salary_component": "Heures supplémentaires", "salary_component_abbr": "HS", "type": "Earning",
	 "depends_on_payment_days": 0},
	# Employee deductions (statutory rates — to validate with accountant)
	{"salary_component": "CNSS employé", "salary_component_abbr": "CNSS", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0,
	 "formula": f"{G} * 0.0448 if {G} <= 6000 else 6000 * 0.0448"},
	{"salary_component": "AMO employé", "salary_component_abbr": "AMO", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "formula": f"{G} * 0.0226"},
	{"salary_component": "Frais professionnels", "salary_component_abbr": "FP", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "statistical_component": 1,
	 "formula": f"{G} * 0.35 if {G} * 0.35 <= 2500 else 2500"},
	{"salary_component": "Salaire net imposable", "salary_component_abbr": "SNI", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "statistical_component": 1,
	 "formula": f"{G} - FP - CNSS - AMO"},
	{"salary_component": "IR", "salary_component_abbr": "IR", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0,
	 "formula": (
	 	"0 if SNI <= 2500 else (SNI * 0.10 - 250) if SNI <= 4166.67 else (SNI * 0.20 - 666.67) "
	 	"if SNI <= 5000 else (SNI * 0.30 - 1166.67) if SNI <= 6666.67 else (SNI * 0.34 - 1433.33) "
	 	"if SNI <= 15000 else (SNI * 0.38 - 2033.33)"
	 )},
	{"salary_component": "Avance sur salaire", "salary_component_abbr": "AVS", "type": "Deduction",
	 "depends_on_payment_days": 0},
	# Employer contributions (statistical — not deducted from net)
	{"salary_component": "CNSS employeur", "salary_component_abbr": "CNSS_EMP", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "statistical_component": 1,
	 "formula": f"{G} * 0.0898 if {G} <= 6000 else 6000 * 0.0898"},
	{"salary_component": "Prestation familiale", "salary_component_abbr": "ALFAM", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "statistical_component": 1, "formula": f"{G} * 0.064"},
	{"salary_component": "AMO employeur", "salary_component_abbr": "AMO_EMP", "type": "Deduction",
	 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "statistical_component": 1, "formula": f"{G} * 0.0411"},
	{"salary_component": "Formation professionnelle", "salary_component_abbr": "FORPRO",
	 "type": "Deduction", "amount_based_on_formula": 1, "depends_on_payment_days": 0,
	 "statistical_component": 1,
	 "formula": f"{G} * 0.016"},
]


def _ensure_components():
	for comp in COMPONENTS:
		if frappe.db.exists("Salary Component", comp["salary_component"]):
			doc = frappe.get_doc("Salary Component", comp["salary_component"])
			doc.update(comp)
			doc.save()
			print("updated component:", doc.name)
		else:
			doc = frappe.get_doc({"doctype": "Salary Component", **comp})
			doc.insert(ignore_permissions=True)
			print("created component:", doc.name)


def _ensure_structure(name, panier_formula):
	if frappe.db.exists("Salary Structure", name):
		doc = frappe.get_doc("Salary Structure", name)
		changed = False
		for row in doc.earnings:
			if row.salary_component == "Salaire de base" and row.formula != "base":
				row.amount_based_on_formula = 1
				row.formula = "base"
				changed = True
		if changed:
			doc.save()
			print("updated structure:", name)
		else:
			print("structure exists:", name)
		return
	company = frappe.defaults.get_defaults().get("company")

	def _row(component_name):
		"""Structure row carrying the component's formula (server-side insert
		does not fetch it from the component like the Desk UI does)."""
		comp = frappe.get_doc("Salary Component", component_name)
		return {
			"salary_component": component_name,
			"amount_based_on_formula": comp.amount_based_on_formula,
			"formula": comp.formula if comp.amount_based_on_formula else None,
		}

	doc = frappe.get_doc(
		{
			"doctype": "Salary Structure",
			"name": name,
			"company": company,
			"payroll_frequency": "Monthly",
			"is_active": "Yes",
			"currency": "MAD",
			"earnings": [
				{"salary_component": "Salaire de base",
				 "amount_based_on_formula": 1, "formula": "base"},
				{"salary_component": "Indemnité de transport",
				 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "formula": "500"},
				{"salary_component": "Prime de panier",
				 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "formula": panier_formula},
				{"salary_component": "Heures supplémentaires",
				 "amount_based_on_formula": 1, "depends_on_payment_days": 0, "formula": "0"},
			],
			"deductions": [
				_row("CNSS employé"),
				_row("AMO employé"),
				_row("Frais professionnels"),
				_row("Salaire net imposable"),
				_row("IR"),
				_row("CNSS employeur"),
				_row("Prestation familiale"),
				_row("AMO employeur"),
				_row("Formation professionnelle"),
			],
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	print("created structure:", name)


def run():
	# 3.1 employment types
	for et in ["Ouvrier", "Personnel", "Cadre"]:
		if not frappe.db.exists("Employment Type", et):
			frappe.get_doc({"doctype": "Employment Type", "employee_type_name": et}).insert(
				ignore_permissions=True
			)
			print("created employment type:", et)

	# 3.2 attendance-based payroll
	settings = frappe.get_doc("Payroll Settings")
	settings.payroll_based_on = "Attendance"
	settings.consider_unmarked_attendance_as = "Absent"
	settings.save()
	print("payroll settings: Attendance-based, unmarked=Absent")

	# 3.3 components
	_ensure_components()

	# 3.5 structures
	_ensure_structure("Ouvriers Mensuel", "300")
	_ensure_structure("Personnel Mensuel", "0")

	frappe.db.commit()
	print("PHASE 3 SETUP OK")
