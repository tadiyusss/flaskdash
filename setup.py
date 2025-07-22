from core import create_app
from getpass import getpass
from core.models import User
from core.extensions import db

app = create_app()

if __name__ == "__main__":
    print(f"Initial Setup for FlaskDash")
    print("Please create an admin user to manage the application.")
    username = input("Username: ")
    firstname = input("First Name: ")
    lastname = input("Last Name: ")
    email = input("Email: ")
    password = getpass("Password: ")
    retype_password = getpass("Retype Password: ")

    if password != retype_password:
        print("Passwords do not match.")
    else:
        new_user = User(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=email
        )
        new_user.set_password(password)

        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
            print(f"Admin user '{username}' created successfully.")

    