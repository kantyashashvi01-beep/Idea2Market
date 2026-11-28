from typing import List, Dict, Any, Optional

DEFAULT_ALLOWANCES = [
    {"name": "tools_and_consumables", "label": "Tools & Assembly Consumables", "percent": 5.0},
    {"name": "enclosure_and_fabrication", "label": "Custom Mounting & Sheet Metal Fabrication", "percent": 12.0},
    {"name": "shipping_and_taxes", "label": "Inland Freight, GST & Logistics", "percent": 10.0},
    {"name": "rework_contingency", "label": "Engineering Iteration & Rework Contingency", "percent": 15.0},
]


class CostEngine:
    @staticmethod
    def calculate_budget(
        bom_items_with_prices: List[Dict[str, Any]],
        custom_allowances: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Pure Python deterministic arithmetic calculation.
        Computes component base subtotal and applies configurable allowances.
        """
        base_low = 0.0
        base_high = 0.0

        itemized_breakdown = []
        for item in bom_items_with_prices:
            qty = max(1, int(item.get("quantity", 1)))
            low_unit = float(item.get("low_inr", 0.0))
            high_unit = float(item.get("high_inr", 0.0))

            item_low = qty * low_unit
            item_high = qty * high_unit

            base_low += item_low
            base_high += item_high

            itemized_breakdown.append({
                "component_id": item.get("component_id"),
                "name": item.get("name"),
                "quantity": qty,
                "unit_low_inr": round(low_unit, 2),
                "unit_high_inr": round(high_unit, 2),
                "total_low_inr": round(item_low, 2),
                "total_high_inr": round(item_high, 2),
                "price_verified": item.get("price_verified", False),
                "checked_on": item.get("checked_on"),
                "source_note": item.get("source_note", "placeholder, verify before use"),
            })

        allowance_defs = custom_allowances if custom_allowances is not None else DEFAULT_ALLOWANCES

        total_allowance_low = 0.0
        total_allowance_high = 0.0
        allowance_lines = []

        for allow in allowance_defs:
            pct = float(allow.get("percent", 0.0))
            allow_low = (pct / 100.0) * base_low
            allow_high = (pct / 100.0) * base_high

            total_allowance_low += allow_low
            total_allowance_high += allow_high

            allowance_lines.append({
                "name": allow.get("name"),
                "label": allow.get("label", allow.get("name")),
                "percent": pct,
                "amount_low_inr": round(allow_low, 2),
                "amount_high_inr": round(allow_high, 2),
            })

        grand_total_low = round(base_low + total_allowance_low, 2)
        grand_total_high = round(base_high + total_allowance_high, 2)

        return {
            "base_total_inr": [round(base_low, 2), round(base_high, 2)],
            "allowances": allowance_lines,
            "grand_total_inr": [grand_total_low, grand_total_high],
            "items": itemized_breakdown,
            "notice": "Order-of-magnitude estimate, not a quotation. Seed prices are unverified placeholders.",
        }
