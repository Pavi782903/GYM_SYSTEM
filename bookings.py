from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from backend.database import get_db
from backend.models.models import Booking, Class, User
from backend.schemas.schemas import BookingOut
from backend.core.security import get_current_user, require_admin

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/{class_id}", response_model=BookingOut, status_code=201)
def book_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    gym_class = db.query(Class).filter(Class.id == class_id).first()
    if not gym_class:
        raise HTTPException(status_code=404, detail="Class not found")
    if gym_class.available_spots <= 0:
        raise HTTPException(status_code=400, detail="No available spots in this class")

    # Prevent duplicate active booking
    existing = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.class_id == class_id,
        Booking.status == "confirmed",
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have an active booking for this class")

    booking = Booking(user_id=current_user.id, class_id=class_id)
    gym_class.available_spots -= 1
    db.add(booking)
    db.commit()
    db.refresh(booking)

    booking = db.query(Booking).options(
        joinedload(Booking.gym_class), joinedload(Booking.user)
    ).filter(Booking.id == booking.id).first()
    return booking


@router.get("/my", response_model=List[BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.gym_class), joinedload(Booking.user))
        .filter(Booking.user_id == current_user.id)
        .all()
    )
    return bookings


@router.put("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your booking")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")

    booking.status = "cancelled"
    gym_class = db.query(Class).filter(Class.id == booking.class_id).first()
    if gym_class:
        gym_class.available_spots += 1

    db.commit()
    db.refresh(booking)

    booking = db.query(Booking).options(
        joinedload(Booking.gym_class), joinedload(Booking.user)
    ).filter(Booking.id == booking.id).first()
    return booking


@router.get("", response_model=List[BookingOut])
def all_bookings(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.gym_class), joinedload(Booking.user))
        .all()
    )
    return bookings
