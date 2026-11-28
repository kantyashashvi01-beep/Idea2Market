import csv
import json
import os
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.models import Category, Component, PricePoint, Facility


def seed_database(db: Session) -> None:
    seed_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Seed Facilities
    facilities_csv_path = os.path.join(seed_dir, "facilities.csv")
    if os.path.exists(facilities_csv_path):
        with open(facilities_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing = db.query(Facility).filter(Facility.name == row["name"].strip()).first()
                if not existing:
                    facility = Facility(
                        name=row["name"].strip(),
                        facility_type=row["facility_type"].strip(),
                        city=row["city"].strip(),
                        url=row["url"].strip(),
                        notes=row["notes"].strip(),
                    )
                    db.add(facility)
        db.commit()

    # 2. Seed Categories and Components
    components_csv_path = os.path.join(seed_dir, "components.csv")
    if os.path.exists(components_csv_path):
        with open(components_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat_name = row["category"].strip()
                category = db.query(Category).filter(Category.name == cat_name).first()
                if not category:
                    category = Category(name=cat_name)
                    db.add(category)
                    db.flush()

                comp_name = row["name"].strip()
                component = db.query(Component).filter(
                    Component.name == comp_name,
                    Component.category_id == category.id,
                ).first()

                try:
                    specs = json.loads(row["specs_json"])
                except Exception:
                    specs = {}

                if not component:
                    component = Component(
                        category_id=category.id,
                        name=comp_name,
                        specs_json=specs,
                        typical_use=row["typical_use"].strip(),
                        active=True,
                    )
                    db.add(component)
                    db.flush()

                    price_point = PricePoint(
                        component_id=component.id,
                        low_inr=float(row["low_inr"]),
                        high_inr=float(row["high_inr"]),
                        checked_on=None,
                        source_note="placeholder, verify before use",
                        price_verified=False,
                    )
                    db.add(price_point)
                else:
                    # Update specs/typical use if needed
                    component.specs_json = specs
                    component.typical_use = row["typical_use"].strip()

        db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Seeding database...")
        seed_database(db)
        print("Seeding complete.")
    finally:
        db.close()
