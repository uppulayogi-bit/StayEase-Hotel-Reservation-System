
from app import app
from models.storage import add_record, read_data

with app.app_context():
    test_user = {
        "id": "TEST001",
        "name": "Test Customer",
        "email": "test@example.com"
    }

    add_record("users.json", test_user)

    users = read_data("users.json")

    print("JSON Storage Test Successful!")
    print("Saved users:", users)
