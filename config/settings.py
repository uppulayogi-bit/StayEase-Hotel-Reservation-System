
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)

load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "stayease-development-secret-key"
    )

    DATA_DIR = os.path.join(BASE_DIR, "data")

    USERS_FILE = os.path.join(DATA_DIR, "users.json")
    HOTELS_FILE = os.path.join(DATA_DIR, "hotels.json")
    ROOMS_FILE = os.path.join(DATA_DIR, "rooms.json")
    BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")

    ADMIN_EMAIL = os.getenv(
        "ADMIN_EMAIL",
        "admin@stayease.com"
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@123"
    )
