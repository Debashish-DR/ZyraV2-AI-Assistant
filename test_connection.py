from dotenv import dotenv_values
import pymongo
env_vars = dotenv_values(".env")
MONGODB_URI = env_vars.get("MONGODB_URI")
client = pymongo.MongoClient(MONGODB_URI)
try:
    client.admin.command('ping')
    print("Connection successful!")
    db = client["zyra_db"]
    users_collection = db["users"]
    # Insert test user
    test_user = {
        "email": "test@example.com",
        "password": "test123",
        "username": "TestUser",
        "assistantname": "Zyra",
        "assistantvoice": "en-CA-ClaraNeural"
    }
    result = users_collection.insert_one(test_user)
    print(f"Inserted user ID: {result.inserted_id}")
    # Verify
    user = users_collection.find_one({"email": "test@example.com"})
    print(f"Sample user: {user}")
except Exception as e:
    print(f"Operation failed: {e}")