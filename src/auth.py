from flask import Blueprint, render_template, request, flash
from .utils import validate_email
auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    data = request.form
    return render_template("login.html")


@auth.route("/logout")
def logout():
    return "<p>Logout</p>"


@auth.route("/sign-up",  methods=['GET', 'POST'])
def sign_up():
    data = request.form.get("email")
    try:
        validate_email.validate_email(data)
    except ValueError as e:
        flash(f"Invalid email: {e}", category="error")
    except ImportError as e:
        flash(f"Cannot verify email: {e}", category="error")
    except Exception as e:
        flash(f"Error validating email: {e}", category="error")
    return render_template("sign_up.html")


@auth.route("/home")
def home():
    return render_template("home.html")
