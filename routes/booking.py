
import uuid
from datetime import datetime, date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import login_required, current_user

from models.storage import read_data, write_data


booking_bp = Blueprint(
    "booking",
    __name__,
    url_prefix="/booking"
)


def dates_overlap(start1, end1, start2, end2):
    """Check whether two booking date ranges overlap."""
    return start1 < end2 and start2 < end1


def is_room_available(room_id, check_in, check_out):
    """Check room availability for the requested dates."""

    bookings = read_data("bookings.json")

    for booking in bookings:

        if (
            booking.get("room_id") == room_id
            and booking.get("status") == "confirmed"
        ):

            existing_check_in = datetime.strptime(
                booking["check_in"], "%Y-%m-%d"
            ).date()

            existing_check_out = datetime.strptime(
                booking["check_out"], "%Y-%m-%d"
            ).date()

            if dates_overlap(
                check_in,
                check_out,
                existing_check_in,
                existing_check_out
            ):
                return False

    return True


# Create a new booking
@booking_bp.route("/create/<room_id>", methods=["GET", "POST"])
@login_required
def create_booking(room_id):

    rooms = read_data("rooms.json")
    hotels = read_data("hotels.json")

    room = next(
        (
            item for item in rooms
            if item.get("id") == room_id
            and item.get("status", "active") == "active"
        ),
        None
    )

    if not room:
        abort(404)

    hotel = next(
        (
            item for item in hotels
            if item.get("id") == room.get("hotel_id")
            and item.get("status", "active") == "active"
        ),
        None
    )

    if not hotel:
        abort(404)

    if request.method == "POST":

        check_in_text = request.form.get("check_in", "")
        check_out_text = request.form.get("check_out", "")
        guests_text = request.form.get("guests", "1")

        try:
            check_in = datetime.strptime(
                check_in_text, "%Y-%m-%d"
            ).date()

            check_out = datetime.strptime(
                check_out_text, "%Y-%m-%d"
            ).date()

            guests = int(guests_text)

        except (ValueError, TypeError):
            flash("Please enter valid booking details.", "error")

            return redirect(
                url_for("booking.create_booking", room_id=room_id)
            )

        if check_in < date.today():
            flash("Check-in date cannot be in the past.", "error")

        elif check_out <= check_in:
            flash("Check-out must be after check-in.", "error")

        elif guests < 1 or guests > int(room.get("capacity", 1)):
            flash("Invalid number of guests for this room.", "error")

        elif not is_room_available(
            room_id, check_in, check_out
        ):
            flash(
                "This room is already booked for the selected dates.",
                "error"
            )

        else:

            nights = (check_out - check_in).days
            price = float(room.get("price", 0))
            total_price = nights * price

            booking = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.id,
                "user_name": current_user.name,
                "user_email": current_user.email,
                "hotel_id": hotel["id"],
                "hotel_name": hotel["name"],
                "room_id": room["id"],
                "room_name": room["name"],
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "guests": guests,
                "nights": nights,
                "price_per_night": price,
                "total_price": total_price,
                "status": "confirmed",
                "created_at": datetime.now().isoformat(
                    timespec="seconds"
                )
            }

            bookings = read_data("bookings.json")
            bookings.append(booking)
            write_data("bookings.json", bookings)

            flash("Your booking has been confirmed!", "success")

            return redirect(
                url_for(
                    "booking.booking_confirmation",
                    booking_id=booking["id"]
                )
            )

    return render_template(
        "booking/create.html",
        room=room,
        hotel=hotel
    )


# Booking confirmation
@booking_bp.route("/confirmation/<booking_id>")
@login_required
def booking_confirmation(booking_id):

    bookings = read_data("bookings.json")

    booking = next(
        (
            item for item in bookings
            if item.get("id") == booking_id
            and item.get("user_id") == current_user.id
        ),
        None
    )

    if not booking:
        abort(404)

    return render_template(
        "booking/confirmation.html",
        booking=booking
    )


# Customer booking history
@booking_bp.route("/my-bookings")
@login_required
def my_bookings():

    bookings = read_data("bookings.json")

    customer_bookings = [
        booking for booking in bookings
        if booking.get("user_id") == current_user.id
    ]

    customer_bookings.sort(
        key=lambda booking: booking.get("created_at", ""),
        reverse=True
    )

    return render_template(
        "booking/my_bookings.html",
        bookings=customer_bookings
    )


# Cancel a booking
@booking_bp.route("/cancel/<booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):

    bookings = read_data("bookings.json")

    booking = next(
        (
            item for item in bookings
            if item.get("id") == booking_id
            and item.get("user_id") == current_user.id
        ),
        None
    )

    if not booking:
        abort(404)

    if booking.get("status") != "confirmed":

        flash("This booking cannot be cancelled.", "error")

    else:

        booking["status"] = "cancelled"

        write_data("bookings.json", bookings)

        flash("Your booking has been cancelled.", "success")

    return redirect(url_for("booking.my_bookings"))
