# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask import flash
# # from src import app
# from app.models import User
# from app.extensions import db
# from werkzeug.security import generate_password_hash
# from flask_bcrypt import Bcrypt
# from flask import current_app
# from app import create_app

# app = create_app
# bcrypt = Bcrypt


# def add_admin(username, email, password):
#     with app.app_context():
#         if isinstance(password, bytes):
#             password = password.decode('utf-8')

#         # hashed_password = generate_password_hash(password) # .decode('utf-8')

#         admin_user = User(username=username, email=email,
#                           password=password, is_admin=True)
#         db.session.add(admin_user)
#         db.session.commit()


# if __name__ == '__main__':
#     # app.run(debug=True)

#     username = input("Enter admin username: ")
#     email = input("Enter admin email: ")
#     password = input("Enter admin password: ")
#     add_admin(username, email, password)

from flask import Flask
from app.models import User
from app.extensions import db
from werkzeug.security import generate_password_hash
from app import create_app
from flask_bcrypt import Bcrypt

# Create an app instance
app = create_app()

# Initialize Bcrypt with the app context
bcrypt = Bcrypt(app)

def add_admin(username, email, password):
    # Ensure the application context is pushed
    with app.app_context():
        # Ensure the password is hashed
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create the admin user
        admin_user = User(username=username, email=email, password=hashed_password, is_admin=True)

        # Add and commit the user to the database
        db.session.add(admin_user)
        db.session.commit()

if __name__ == '__main__':
    # Prompt the user for admin credentials
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    # Add the admin user to the database
    add_admin(username, email, password)
    print(f"Admin user '{username}' added successfully.")
