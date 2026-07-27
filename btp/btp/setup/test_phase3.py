import frappe
from frappe.utils import flt


def run():
	company = frappe.defaults.get_defaults().get("company")
	ppa = frappe.db.get_value("Company", company, "default_payroll_payable_account")

	# fixed test employees: a laborer (Ouvrier) and an engineer (Personnel)
	emp_ouvrier = "HR-EMP-00008"  # Rachid Tazi, Laborer
	emp_personnel = "HR-EMP-00005"  # Khalid Benjelloun, Design Engineer

	# cleanup leftover slips + payroll entries for July
	for slip in frappe.get_all(
		"Salary Slip", filters={"start_date": "2026-07-01"}, pluck="name"
	):
		doc = frappe.get_doc("Salary Slip", slip)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Salary Slip", slip, force=1, ignore_permissions=True)
	for entry in frappe.get_all(
		"Payroll Entry", filters={"start_date": "2026-07-01"}, pluck="name"
	):
		doc = frappe.get_doc("Payroll Entry", entry)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Payroll Entry", entry, force=1, ignore_permissions=True)

	# reset SSAs for the 2 employees: cancel everything, assign Moroccan structures
	for emp, struct, base, etype in [
		(emp_ouvrier, "Ouvriers Mensuel", 4000, "Ouvrier"),
		(emp_personnel, "Personnel Mensuel", 8000, "Personnel"),
	]:
		for old in frappe.get_all(
			"Salary Structure Assignment", filters={"employee": emp, "docstatus": 1}, pluck="name"
		):
			old_doc = frappe.get_doc("Salary Structure Assignment", old)
			old_doc.flags.ignore_permissions = True
			old_doc.cancel()
		frappe.db.set_value("Employee", emp, "employment_type", etype)
		ssa = frappe.get_doc(
			{
				"doctype": "Salary Structure Assignment",
				"employee": emp,
				"salary_structure": struct,
				"company": company,
				"base": base,
				"from_date": "2026-06-01",
				"payroll_payable_account": ppa,
			}
		)
		ssa.insert(ignore_permissions=True)
		ssa.submit()
		print("assigned:", emp, "->", struct, "base", base)

	frappe.db.commit()

	# expected payment days from July attendance
	def present_days(emp):
		return frappe.db.sql(
			"""
			SELECT SUM(CASE WHEN status='Present' THEN 1 WHEN status='Half Day' THEN 0.5 ELSE 0 END)
			FROM tabAttendance
			WHERE docstatus = 1 AND employee = %s
			  AND attendance_date BETWEEN '2026-07-01' AND '2026-07-31'
			""",
			emp,
		)[0][0] or 0

	expected = {emp_ouvrier: present_days(emp_ouvrier), emp_personnel: present_days(emp_personnel)}
	print("expected days:", expected)

	# Payroll Entry for July, limited to the 2 employees
	pe = frappe.get_doc(
		{
			"doctype": "Payroll Entry",
			"company": company,
			"payroll_frequency": "Monthly",
			"start_date": "2026-07-01",
			"end_date": "2026-07-31",
			"posting_date": "2026-07-31",
			"currency": "MAD",
			"payroll_payable_account": ppa,
			"salary_slip_based_on_timesheet": 0,
			"exchange_rate": 1,
		}
	)
	pe.fill_employee_details()
	pe.employees = [e for e in pe.employees if e.employee in (emp_ouvrier, emp_personnel)]
	assert len(pe.employees) == 2, [e.employee for e in pe.employees]
	pe.insert(ignore_permissions=True)
	pe.submit()
	frappe.db.commit()
	print("payroll entry:", pe.name)

	brackets = [(2500, 0, 0), (4166.67, 0.10, 250), (5000, 0.20, 666.67),
	            (6666.67, 0.30, 1166.67), (15000, 0.34, 1433.33), (1e18, 0.38, 2033.33)]

	for emp, exp_days in expected.items():
		slip_name = frappe.db.get_value(
			"Salary Slip",
			{"employee": emp, "start_date": "2026-07-01", "docstatus": 0},
			"name",
		)
		assert slip_name, emp
		slip = frappe.get_doc("Salary Slip", slip_name)
		print("slip:", slip.name, slip.salary_structure, "days:", slip.payment_days, "/",
		      slip.total_working_days, "net:", slip.net_pay)
		assert "Mensuel" in slip.salary_structure, slip.salary_structure
		assert flt(slip.payment_days) == flt(exp_days), (slip.payment_days, exp_days)

		earn = {d.salary_component: flt(d.amount) for d in slip.earnings}
		ded = {d.salary_component: flt(d.amount) for d in slip.deductions}
		assert "Salaire de base" in earn, sorted(earn)
		gross = sum(earn.get(c, 0) for c in
		            ["Salaire de base", "Indemnité de transport", "Prime de panier", "Heures supplémentaires"])

		exp_cnss = min(gross, 6000) * 0.0448
		exp_amo = gross * 0.0226
		exp_fp = min(gross * 0.35, 2500)
		sni = gross - exp_fp - exp_cnss - exp_amo
		exp_ir = 0
		for cap, rate, deduction in brackets:
			if sni <= cap:
				exp_ir = sni * rate - deduction
				break

		# statistical components (FP, SNI, employer contribs) are eval-time only
		# on v16 — not persisted as slip rows
		print("  G:", gross, "CNSS:", ded.get("CNSS employé"), "AMO:", ded.get("AMO employé"),
		      "IR:", ded.get("IR", 0), "| expected IR:", round(exp_ir, 2))
		assert abs(ded["CNSS employé"] - exp_cnss) < 0.05, (ded["CNSS employé"], exp_cnss)
		assert abs(ded["AMO employé"] - exp_amo) < 0.05
		assert abs(flt(ded.get("IR", 0)) - exp_ir) < 0.05, (ded.get("IR"), exp_ir)
		assert abs(flt(slip.net_pay) - (flt(slip.gross_pay) - exp_cnss - exp_amo - exp_ir)) < 0.1
		slip.submit()
		print("  submitted:", slip.name)

	frappe.db.commit()
	print("PHASE 3 PAYROLL TEST OK")
