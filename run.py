from core import create_app
import os


if 'app.db' in os.listdir('.') and os.path.isfile('app.db'):
    print("Database not found. Please run setup.py to initialize the database.")

    app = create_app()

    if __name__ == "__main__":
        app.run(debug=True)