from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.models import Class
from backend.schemas.schemas import ClassCreate, ClassUpdate, ClassOut
from backend.core.security import get_current_user, require_admin
from backend.models.models import User

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=List[ClassOut])
def get_classes(
    category: Optional[str] = Query(None),
    instructor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Class)
    if category:
        query = query.filter(Class.category.ilike(f"%{category}%"))
    if instructor:
        query = query.filter(Class.instructor.ilike(f"%{instructor}%"))
    return query.all()


@router.get("/{class_id}", response_model=ClassOut)
def get_class(class_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    gym_class = db.query(Class).filter(Class.id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return gym_class


@router.post("", response_model=ClassOut, status_code=201)
def create_class(
    payload: ClassCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    gym_class = Class(
        title=payload.title,
        instructor=payload.instructor,
        category=payload.category,
        capacity=payload.capacity,
        available_spots=payload.capacity,
        schedule_time=payload.schedule_time,
    )
    db.add(gym_class)
    db.commit()
    db.refresh(gym_class)
    return gym_class


@router.put("/{class_id}", response_model=ClassOut)
def update_class(
    class_id: int,
    payload: ClassUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    gym_class = db.query(Class).filter(Class.id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")

    update_data = payload.dict(exclude_unset=True)

    # If capacity is being updated, adjust available_spots proportionally
    if "capacity" in update_data:
        booked = gym_class.capacity - gym_class.available_spots
        new_spots = update_data["capacity"] - booked
        if new_spots < 0:
            raise HTTPException(status_code=400, detail="New capacity is less than current bookings")
        gym_class.available_spots = new_spots

    for field, value in update_data.items():
        setattr(gym_class, field, value)

    db.commit()
    db.refresh(gym_class)
    return gym_class


@router.delete("/{class_id}", status_code=204)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    gym_class = db.query(Class).filter(Class.id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(gym_class)
    db.commit()
