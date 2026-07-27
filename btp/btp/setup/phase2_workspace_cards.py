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


def _add_cards(workspace_name, cards):
	ws = frappe.get_doc("Workspace", workspace_name)
	content = json.loads(ws.content)
	existing = {
		b.get("data", {}).get("number_card_name")
		for b in content
		if b.get("type") == "number_card"
	}
	new_blocks = [_card_block(c) for c in cards if c not in existing]
	if not new_blocks:
		print(workspace_name, ": cards already present")
		return
	ws.content = json.dumps(new_blocks + content)
	ws.save()
	print(workspace_name, ": added", [b["data"]["number_card_name"] for b in new_blocks])


def run():
	_add_cards(
		"Direction",
		["Outstanding Customer Invoices", "Supplier Invoices Due This Week"],
	)
	_add_cards("Chantier", ["Today Reports Submitted"])
	frappe.db.commit()
	print("WORKSPACE CARDS OK")
