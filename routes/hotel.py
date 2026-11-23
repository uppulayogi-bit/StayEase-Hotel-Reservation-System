
from flask import (
    Blueprint,
    render_template,
    request,
    abort
)

from models.storage import read_data


hotel_bp = Blueprint(
    "hotel",
    __name__,
    url_prefix="/hotels"
)


# Display all available hotels
@hotel_bp.route("/")
def hotel_list():

    hotels = read_data("hotels.json")

    # Display only active hotels
    hotels = [
        hotel for hotel in hotels
        if hotel.get("status", "active") == "active"
    ]

    # Search filters
    search = request.args.get("search", "").strip().lower()
    location = request.args.get("location", "").strip().lower()

    if search:

        hotels = [
            hotel for hotel in hotels
            if search in hotel.get("name", "").lower()
            or search in hotel.get("location", "").lower()
        ]

    if location:

        hotels = [
            hotel for hotel in hotels
            if location in hotel.get("location", "").lower()
        ]

    return render_template(
        "hotels/list.html",
        hotels=hotels,
        search=search,
        location=location
    )


# Display individual hotel details
@hotel_bp.route("/<hotel_id>")
def hotel_details(hotel_id):

    hotels = read_data("hotels.json")
    rooms = read_data("rooms.json")

    hotel = next(
        (
            item for item in hotels
            if item.get("id") == hotel_id
            and item.get("status", "active") == "active"
        ),
        None
    )

    if not hotel:
        abort(404)

    # Get rooms belonging to this hotel
    hotel_rooms = [
        room for room in rooms
        if room.get("hotel_id") == hotel_id
        and room.get("status", "active") == "active"
    ]

    return render_template(
        "hotels/details.html",
        hotel=hotel,
        rooms=hotel_rooms
    )
