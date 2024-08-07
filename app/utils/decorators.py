from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Check if the current user is authenticated and an admin
        if not current_user.is_admin:
            # Flash a message if the user is not an admin
            flash("You do not have permission to access this page.", "danger")
            # Redirect to the homepage or an appropriate page
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
