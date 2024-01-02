from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Subjects
from database import get_db

router = APIRouter()


class Subject(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=2)
    year_of_graduate: int = Field(default=2023, max_digits= 4, max= 2026)
    brief_intro: str = Field(min_length=2, max_length=150)
    community_service: int = Field(default=0)
    credits: int = Field(default=0, max_digits=2, max=30)
    able_to_graduate = Field(default=False)


    class Config:
        json_schema_extra = {
            "Sample": {
                "id: 1"
                "name": "name of a student",
                "year_of_graduate": "number between 2023 and 2026",
                "brief_intro": "brief description of the subject",
                "community_service": "20",
                "credits":"2",
                "able_to_graduate" : False,
            }
        }



@router.get("", status_code=status.HTTP_200_OK)
async def get_subject_registry(db: Session = Depends(get_db)):

    return db.query(Subjects).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subject(subject_data: Subject, db: Session = Depends(get_db)):

    new_subject = Subjects(**subject_data.model_dump())

    db.add(new_subject)
    db.commit()
