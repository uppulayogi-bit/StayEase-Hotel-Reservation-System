
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    UserMixin,
    login_user,
    logout_user,
    current_user
)

from models.user import (
    register_user,
    authenticate_user
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# Flask-Login user class
class User(UserMixin):

    def __init__(self, user_data):

        self.id = user_data["id"]
        self.name = user_data["name"]
        self.email = user_data["email"]
        self.role = user_data.get("role", "customer")


# Customer registration
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not name or not email or not password:
            flash("Please fill in all required fields.", "error")

        elif len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        else:

            user, message = register_user(
                name,
                email,
                password
            )

            if user:

                flash(
                    "Account created successfully! Please log in.",
                    "success"
                )

                return redirect(url_for("auth.login"))

            flash(message, "error")

    return render_template("auth/register.html")


# Customer login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user_data = authenticate_user(email, password)

        if user_data:

            login_user(User(user_data))

            flash(
                f"Welcome back, {user_data['name']}!",
                "success"
            )

            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


# Customer logout
@auth_bp.route("/logout", methods=["POST"])
def logout():

    if current_user.is_authenticated:
        logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("home"))
