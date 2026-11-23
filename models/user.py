
import uuid

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.storage import read_data, write_data


USERS_FILE = "users.json"


def register_user(name, email, password):

    users = read_data(USERS_FILE)

    email = email.strip().lower()

    # Check whether email already exists
    for user in users:

        if user.get("email", "").lower() == email:
            return None, "Email is already registered."

    # Create new customer
    user = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "email": email,
        "password": generate_password_hash(password),
        "role": "customer"
    }

    users.append(user)

    write_data(USERS_FILE, users)

    return user, "Registration successful."


def authenticate_user(email, password):

    users = read_data(USERS_FILE)

    email = email.strip().lower()

    for user in users:

        if user.get("email", "").lower() == email:

            stored_password = user.get("password")

            if stored_password and check_password_hash(
                stored_password, password
            ):
                return user

    return None


def get_user_by_id(user_id):

    users = read_data(USERS_FILE)

    for user in users:

        if user.get("id") == user_id:
            return user

    return None


def get_all_customers():

    users = read_data(USERS_FILE)

    return [
        user for user in users
        if user.get("role") == "customer"
    ]
