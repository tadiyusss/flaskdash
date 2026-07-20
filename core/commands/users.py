import click

@click.command('create-admin')
@click.option('--username', prompt='Username', help='The username for the new administrator.')
@click.option('--firstname', prompt='First Name', help='The first name of the new administrator.')
@click.option('--lastname', prompt='Last Name', help='The last name of the new administrator.')
@click.option('--email', prompt='Email', help='The email address of the new administrator.')
def create_admin(username, firstname, lastname, email):
    from core import create_app
    from getpass import getpass
    from core.models.users import User, Role, UserRole
    from core.extensions import db

    app, socketio = create_app()

    password = getpass("Password (inputs are hidden): ")
    retype_password = getpass("Retype Password (inputs are hidden): ")

    if password != retype_password:
        click.echo("Passwords do not match.")
        return

    with app.app_context():
        new_user = User(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=email
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        admin_role = Role.query.filter_by(name='Administrator').first()
        user_role = UserRole(user_id=new_user.id, role_id=admin_role.id)
        db.session.add(user_role)
        db.session.commit()

        click.echo(f"Administrator user '{username}' created successfully.")


@click.command('delete-user')
@click.option('--username', prompt='Username', help='The username of the user to delete.')
def delete_user(username):
    click.echo(f"Deleting user: {username}")