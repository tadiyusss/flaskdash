from core import create_app
import os

if not 'app.db' in os.listdir('.') or not os.path.isfile('app.db'):
    print("Database not found. Please run setup.py to initialize the database.")
    exit(1)

if __name__ != "__main__":
    exit(0)

app = create_app()
app.run(debug=True)