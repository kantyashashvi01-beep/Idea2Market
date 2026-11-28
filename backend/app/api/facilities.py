from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Facility
from app.schemas.api_schemas import FacilityOut

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("", response_model=List[FacilityOut])
def list_facilities(db: Session = Depends(get_db)):
    facilities = db.query(Facility).all()
    return [
        FacilityOut(
            id=f.id,
            name=f.name,
            facility_type=f.facility_type,
            city=f.city,
            url=f.url,
            notes=f.notes,
        )
        for f in facilities
    ]
