from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Violations
from database import get_db
from auth import get_current_user

router = APIRouter()


class Violation(BaseModel):
    student_id: Optional[int] = None
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=250)
    behaviour_point_deduction: int = Field(gt=0, lt=100)
    pink_slip: bool = Field(default=False)
    issued_in: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Title of the New Violation",
                "description": "Description of the issue",
                "behaviour_point_deduction": 10,
                "pink_slip": True
            }
        }


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_violations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Violations).filter(Violations.id == current_user.get("id")).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_violation(violation_data: Violation, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_violation = Violations(**violation_data.model_dump(), author=current_user.get("id"))

    db.add(new_violation)
    db.commit()


@router.get("/{violation_id}", status_code=status.HTTP_200_OK)
async def get_violation_by_id(violation_id: int = Path(gt=0), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    Violation = db.query(Violations).filter(Violations.id == violation_id).first().filter(Violations.name == current_user.get("id"))
    if Violation is not None:
        return Violation
    raise HTTPException(status_code=404, detail=f"Violation with id #{violation_id} was not found")


@router.put("/{violation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_violation_by_id(violation_data: Violation, violation_id: int = Path(gt=0), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    Violation = db.query(Violations).filter(Violations.id == violation_id).filter(Violations.name == current_user.get("id"))

    if Violation is None:
        raise HTTPException(status_code=404, detail=f"Violation with id #{violation_id} was not found")

    Violation.title = violation_data.title
    Violation.issued_by = violation_data.issued_by
    Violation.description = violation_data.description
    Violation.behaviour_point_deduction = violation_data.behaviour_point_deduction
    Violation.pink_slip = violation_data.pink_slip

    db.add(Violation)
    db.commit()


@router.delete("/{violation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_violation_by_id(violation_id: int = Path(gt=0), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    delete_violation = db.query(Violations).filter(Violations.id == violation_id).filter(Violations.name == current_user.get("id"))

    if delete_violation is None:
        raise HTTPException(status_code=404, detail=f"Violation with id #{violation_id} was not found")

    db.query(Violations).filter(Violations.id == violation_id).delete()
    db.commit()