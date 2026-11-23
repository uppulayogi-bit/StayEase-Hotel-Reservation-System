
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
    abort
)

from flask_login import current_user

from models.storage import read_data, write_data
from models.user import get_all_customers


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# Check administrator access
def admin_required():

    if not session.get("admin_logged_in"):
        return False

    return True


# Admin login
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        admin_email = current_app.config["ADMIN_EMAIL"].lower()
        admin_password = current_app.config["ADMIN_PASSWORD"]

        if email == admin_email and password == admin_password:

            session["admin_logged_in"] = True

            flash("Welcome to the StayEase Admin Dashboard!", "success")

            return redirect(url_for("admin.dashboard"))

        flash("Invalid administrator credentials.", "error")

    return render_template("admin/login.html")


# Admin logout
@admin_bp.route("/logout", methods=["POST"])
def admin_logout():

    session.pop("admin_logged_in", None)

    flash("Admin logged out successfully.", "success")

    return redirect(url_for("admin.admin_login"))


# Admin dashboard
@admin_bp.route("/")
def dashboard():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    hotels = read_data("hotels.json")
    rooms = read_data("rooms.json")
    bookings = read_data("bookings.json")
    customers = get_all_customers()

    confirmed_bookings = [
        booking for booking in bookings
        if booking.get("status") == "confirmed"
    ]

    booking_value = sum(
        float(booking.get("total_price", 0))
        for booking in confirmed_bookings
    )

    stats = {
        "total_hotels": len(hotels),
        "total_rooms": len(rooms),
        "total_bookings": len(bookings),
        "total_customers": len(customers),
        "confirmed_bookings": len(confirmed_bookings),
        "booking_value": booking_value
    }

    recent_bookings = sorted(
        bookings,
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )[:5]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_bookings=recent_bookings
    )


# Display all hotels
@admin_bp.route("/hotels")
def manage_hotels():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    hotels = read_data("hotels.json")

    return render_template(
        "admin/hotels.html",
        hotels=hotels
    )


# Add a new hotel
@admin_bp.route("/hotels/add", methods=["GET", "POST"])
def add_hotel():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":

        try:
            name = request.form.get("name", "").strip()
            location = request.form.get("location", "").strip()
            description = request.form.get("description", "").strip()
            rating = float(request.form.get("rating", 0))
            image = request.form.get("image", "").strip()
            amenities = [
                item.strip()
                for item in request.form.get("amenities", "").split(",")
                if item.strip()
            ]

            if not name or not location:
                raise ValueError

            if not 0 <= rating <= 5:
                raise ValueError

        except (ValueError, TypeError):
            flash("Please enter valid hotel details.", "error")
            return render_template("admin/hotel_form.html", hotel=None)

        hotel = {
            "id": str(uuid.uuid4()),
            "name": name,
            "location": location,
            "description": description,
            "rating": rating,
            "image": image,
            "amenities": amenities,
            "status": "active",
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        hotels = read_data("hotels.json")
        hotels.append(hotel)
        write_data("hotels.json", hotels)

        flash("Hotel added successfully.", "success")

        return redirect(url_for("admin.manage_hotels"))

    return render_template(
        "admin/hotel_form.html",
        hotel=None
    )


# Edit hotel
@admin_bp.route("/hotels/edit/<hotel_id>", methods=["GET", "POST"])
def edit_hotel(hotel_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    hotels = read_data("hotels.json")

    hotel = next(
        (item for item in hotels if item.get("id") == hotel_id),
        None
    )

    if not hotel:
        abort(404)

    if request.method == "POST":

        try:
            name = request.form.get("name", "").strip()
            location = request.form.get("location", "").strip()
            rating = float(request.form.get("rating", 0))

            if not name or not location or not 0 <= rating <= 5:
                raise ValueError

        except (ValueError, TypeError):
            flash("Please enter valid hotel details.", "error")
            return render_template("admin/hotel_form.html", hotel=hotel)

        hotel.update({
            "name": name,
            "location": location,
            "description": request.form.get("description", "").strip(),
            "rating": rating,
            "image": request.form.get("image", "").strip(),
            "amenities": [
                item.strip()
                for item in request.form.get("amenities", "").split(",")
                if item.strip()
            ]
        })

        write_data("hotels.json", hotels)

        flash("Hotel updated successfully.", "success")

        return redirect(url_for("admin.manage_hotels"))

    return render_template(
        "admin/hotel_form.html",
        hotel=hotel
    )


# Delete (deactivate) hotel
@admin_bp.route("/hotels/delete/<hotel_id>", methods=["POST"])
def delete_hotel(hotel_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    hotels = read_data("hotels.json")

    hotel = next(
        (item for item in hotels if item.get("id") == hotel_id),
        None
    )

    if not hotel:
        abort(404)

    hotel["status"] = "inactive"

    write_data("hotels.json", hotels)

    flash("Hotel deactivated successfully.", "success")

    return redirect(url_for("admin.manage_hotels"))


# Display rooms
@admin_bp.route("/rooms")
def manage_rooms():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    rooms = read_data("rooms.json")
    hotels = read_data("hotels.json")

    hotel_names = {
        hotel["id"]: hotel["name"]
        for hotel in hotels
    }

    return render_template(
        "admin/rooms.html",
        rooms=rooms,
        hotel_names=hotel_names,
        hotels=hotels
    )


# Add room
@admin_bp.route("/rooms/add", methods=["GET", "POST"])
def add_room():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    hotels = read_data("hotels.json")

    active_hotels = [
        hotel for hotel in hotels
        if hotel.get("status", "active") == "active"
    ]

    if request.method == "POST":

        try:
            hotel_id = request.form.get("hotel_id", "")
            name = request.form.get("name", "").strip()
            price = float(request.form.get("price", 0))
            capacity = int(request.form.get("capacity", 1))

            hotel_exists = any(
                hotel.get("id") == hotel_id
                and hotel.get("status", "active") == "active"
                for hotel in hotels
            )

            if (
                not hotel_exists
                or not name
                or price <= 0
                or capacity < 1
            ):
                raise ValueError

        except (ValueError, TypeError):
            flash("Please enter valid room details.", "error")
            return render_template(
                "admin/room_form.html",
                room=None,
                hotels=active_hotels
            )

        room = {
            "id": str(uuid.uuid4()),
            "hotel_id": hotel_id,
            "name": name,
            "price": price,
            "capacity": capacity,
            "description": request.form.get("description", "").strip(),
            "status": "active"
        }

        rooms = read_data("rooms.json")
        rooms.append(room)
        write_data("rooms.json", rooms)

        flash("Room added successfully.", "success")

        return redirect(url_for("admin.manage_rooms"))

    return render_template(
        "admin/room_form.html",
        room=None,
        hotels=active_hotels
    )


# Edit room
@admin_bp.route("/rooms/edit/<room_id>", methods=["GET", "POST"])
def edit_room(room_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    rooms = read_data("rooms.json")
    hotels = read_data("hotels.json")

    room = next(
        (item for item in rooms if item.get("id") == room_id),
        None
    )

    if not room:
        abort(404)

    active_hotels = [
        hotel for hotel in hotels
        if hotel.get("status", "active") == "active"
    ]

    if request.method == "POST":

        try:
            hotel_id = request.form.get("hotel_id", "")
            name = request.form.get("name", "").strip()
            price = float(request.form.get("price", 0))
            capacity = int(request.form.get("capacity", 1))

            if (
                not name
                or price <= 0
                or capacity < 1
                or not any(
                    h.get("id") == hotel_id for h in active_hotels
                )
            ):
                raise ValueError

        except (ValueError, TypeError):
            flash("Please enter valid room details.", "error")
            return render_template(
                "admin/room_form.html",
                room=room,
                hotels=active_hotels
            )

        room.update({
            "hotel_id": hotel_id,
            "name": name,
            "price": price,
            "capacity": capacity,
            "description": request.form.get("description", "").strip()
        })

        write_data("rooms.json", rooms)

        flash("Room updated successfully.", "success")

        return redirect(url_for("admin.manage_rooms"))

    return render_template(
        "admin/room_form.html",
        room=room,
        hotels=active_hotels
    )


# Delete (deactivate) room
@admin_bp.route("/rooms/delete/<room_id>", methods=["POST"])
def delete_room(room_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    rooms = read_data("rooms.json")

    room = next(
        (item for item in rooms if item.get("id") == room_id),
        None
    )

    if not room:
        abort(404)

    room["status"] = "inactive"

    write_data("rooms.json", rooms)

    flash("Room deactivated successfully.", "success")

    return redirect(url_for("admin.manage_rooms"))


# Display all bookings
@admin_bp.route("/bookings")
def manage_bookings():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    bookings = read_data("bookings.json")

    bookings.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )

    return render_template(
        "admin/bookings.html",
        bookings=bookings
    )


# Update booking status
@admin_bp.route("/bookings/update/<booking_id>", methods=["POST"])
def update_booking(booking_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    bookings = read_data("bookings.json")

    booking = next(
        (item for item in bookings if item.get("id") == booking_id),
        None
    )

    if not booking:
        abort(404)

    new_status = request.form.get("status", "")

    if new_status not in ["confirmed", "cancelled"]:
        flash("Invalid booking status.", "error")
    else:
        booking["status"] = new_status
        write_data("bookings.json", bookings)
        flash("Booking status updated.", "success")

    return redirect(url_for("admin.manage_bookings"))


# Display registered customers
@admin_bp.route("/customers")
def manage_customers():

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    customers = get_all_customers()

    return render_template(
        "admin/customers.html",
        customers=customers
    )
