
import os
from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models.user import get_user_by_id

from routes.auth import auth_bp, User
from routes.hotel import hotel_bp
from routes.booking import booking_bp
from routes.admin import admin_bp


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."


def create_app():

    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)

    # Create data directory if it does not exist
    os.makedirs(app.config["DATA_DIR"], exist_ok=True)

    # Initialize JSON files
    json_files = [
        "users.json",
        "hotels.json",
        "rooms.json",
        "bookings.json"
    ]

    for filename in json_files:

        filepath = os.path.join(
            app.config["DATA_DIR"],
            filename
        )

        if not os.path.exists(filepath):

            with open(filepath, "w", encoding="utf-8") as file:
                file.write("[]")

    # Initialize Flask-Login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):

        user_data = get_user_by_id(user_id)

        if user_data:
            return User(user_data)

        return None

    # Register application routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(hotel_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)

    # Homepage
    @app.route("/")
    def home():

        from models.storage import read_data

        hotels = read_data("hotels.json")

        active_hotels = [
            hotel for hotel in hotels
            if hotel.get("status", "active") == "active"
        ]

        return render_template(
            "index.html",
            hotels=active_hotels[:3]
        )

    # Custom 404 error page
    @app.errorhandler(404)
    def page_not_found(error):

        return render_template("404.html"), 404

    return app


# Create application
app = create_app()


if __name__ == "__main__":

    app.run(debug=True)
