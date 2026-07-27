import json
import random
import string

import frappe


def _block_id():
	return "".join(random.choices(string.ascii_letters + string.digits, k=10))


def _card_block(name, col="4"):
	return {
		"id": _block_id(),
		"type": "number_card",
		"data": {"number_card_name": name, "col": col},
	}


def _chart_block(name):
	return {
		"id": _block_id(),
		"type": "chart",
		"data": {"chart_name": name, "col": 6},
	}


def _add_cards(workspace_name, cards, charts=None):
	ws = frappe.get_doc("Workspace", workspace_name)
	content = json.loads(ws.content)
	existing = {
		b.get("data", {}).get("number_card_name")
		for b in content
		if b.get("type") == "number_card"
	}
	existing_charts = {
		b.get("data", {}).get("chart_name") for b in content if b.get("type") == "chart"
	}
	new_blocks = [_card_block(c) for c in cards if c not in existing]
	new_blocks += [_chart_block(c) for c in (charts or []) if c not in existing_charts]
	if not new_blocks:
		print(workspace_name, ": cards already present")
		return
	ws.content = json.dumps(new_blocks + content)
	ws.save()
	print(workspace_name, ": added", [b["data"] for b in new_blocks])


def run():
	_add_cards(
		"Direction",
		["Outstanding Customer Invoices", "Supplier Invoices Due This Week"],
		charts=["Monthly Revenue", "Expenses by Site"],
	)
	_add_cards("Chantier", ["Today Reports Submitted"])
	frappe.db.commit()
	print("WORKSPACE CARDS OK")
