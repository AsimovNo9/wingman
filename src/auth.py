from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .utils import validate_email
from . import db


from .models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        print("help")
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash("Successful Login", category="success")
                    login_user(user, remember=True)
                    print(f"Current user: {current_user.is_authenticated}")
                    return redirect(url_for("views.home"))

                else:
                    flash("Incorrect password, try again", category="error")
            else:
                flash("Incorrect password or email, try again", category="error")

        except ValueError as e:
            flash(f"Invalid email: {e}", category="error")
        except Exception as e:
            flash(f"Error validating email: {e}", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up",  methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Track if all validations pass
        validation_successful = True

        # Validate email
        try:
            if not email:
                flash("Email is required", category="error")
                validation_successful = False
            else:
                validate_email.validate_email(email)

                # Check if email already exists in database
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash("Email already in use", category="error")
                    validation_successful = False
        except ValueError as e:
            flash(f"Invalid email: {e}", category="error")
            validation_successful = False
        except ImportError as e:
            flash(f"Cannot verify email: {e}", category="error")
            validation_successful = False
        except Exception as e:
            flash(f"Error validating email: {e}", category="error")
            validation_successful = False

        # Validate name
        if not firstName:
            flash("First name is required", category="error")
            validation_successful = False
        elif len(firstName) < 2:
            flash("First name must be at least 2 characters", category="error")
            validation_successful = False

        # Validate password
        try:
            if not password1 or not password2:
                flash("Password is required", category="error")
                validation_successful = False
            elif password1 != password2:
                flash("Passwords don't match", category="error")
                validation_successful = False
            elif len(password1) < 8:
                flash("Password must be at least 8 characters", category="error")
                validation_successful = False
        except Exception as e:
            flash(f"Error validating password: {e}", category="error")
            validation_successful = False

        # If all validations pass, create the user
        if validation_successful:
            new_user = User(
                email=email,
                firstName=firstName,
                password=generate_password_hash(
                    password1, method='pbkdf2:sha256')
            )

            # Add user to database
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully!", category="success")
                login_user(new_user, remember=True)
                return redirect(url_for('views.home'))

            except Exception as e:
                db.session.rollback()
                flash(f"Error creating account: {e}", category="error")

    return render_template("sign_up.html", user=current_user)
