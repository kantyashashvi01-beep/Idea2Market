import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import Component, PricePoint

logger = logging.getLogger(__name__)


class BOMValidator:
    @staticmethod
    def validate_and_filter_bom(
        db: Session,
        proposed_items: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Enforces closed-world BOM.
        Returns:
            (valid_items_with_details, dropped_items)
        """
        valid_items = []
        dropped_items = []

        # Load all valid component IDs and details
        db_components = (
            db.query(Component, PricePoint)
            .outerjoin(PricePoint, Component.id == PricePoint.component_id)
            .filter(Component.active.is_(True))
            .all()
        )

        component_lookup = {}
        for comp, price in db_components:
            component_lookup[comp.id] = {
                "component_id": comp.id,
                "name": comp.name,
                "category_id": comp.category_id,
                "specs_json": comp.specs_json,
                "typical_use": comp.typical_use,
                "low_inr": price.low_inr if price else 0.0,
                "high_inr": price.high_inr if price else 0.0,
                "price_verified": price.price_verified if price else False,
                "checked_on": str(price.checked_on) if (price and price.checked_on) else None,
                "source_note": price.source_note if price else "placeholder",
            }

        for proposed in proposed_items:
            comp_id = proposed.get("component_id")
            if comp_id is None:
                dropped_items.append({"item": proposed, "reason": "Missing component_id"})
                continue

            try:
                comp_id_int = int(comp_id)
            except (ValueError, TypeError):
                dropped_items.append({"item": proposed, "reason": f"Invalid component_id format: {comp_id}"})
                continue

            if comp_id_int not in component_lookup:
                logger.warning("Closed-world BOM check failed: Unknown component ID %s proposed. Dropping.", comp_id)
                dropped_items.append({"item": proposed, "reason": f"Component ID {comp_id_int} does not exist in catalogue"})
                continue

            # Valid item
            details = dict(component_lookup[comp_id_int])
            qty = max(1, min(100, int(proposed.get("quantity", 1))))
            role = proposed.get("role_in_design", details.get("typical_use") or "Component")
            confidence = proposed.get("confidence", "medium")

            valid_items.append({
                "component_id": comp_id_int,
                "name": details["name"],
                "quantity": qty,
                "role_in_design": role,
                "confidence": confidence,
                "source_type": "catalogue",
                "specs_json": details["specs_json"],
                "low_inr": details["low_inr"],
                "high_inr": details["high_inr"],
                "price_verified": details["price_verified"],
                "checked_on": details["checked_on"],
                "source_note": details["source_note"],
            })

        return valid_items, dropped_items
