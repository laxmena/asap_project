import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

# Function to initialize Firebase
def initialize_firebase(key_path, database_url):
    try:
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Key file not found at {key_path}")

        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        print("Firebase initialized successfully!")
        return True  # Indicate success
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False  # Indicate failure
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

# Function to read data from Realtime Database
def read_data(bots):
    try:
        ref = db.reference("bots")
        snapshot = ref.get()
        if snapshot:
            print("All data:", snapshot)
            return snapshot
        else:
            print("No data found at that location.")
            return None
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

# Function to push data to Realtime Database (commented out)
def push_data(path, data):
    try:
        ref = db.reference(path)
        ref.push(data)
        print("Data pushed successfully!")
    except Exception as e:
        print(f"Error pushing data: {e}")

def upload_bot_data(bot_data):
    try:
        ref = db.reference("bots")  # Reference to the 'bots' node
        for bot in bot_data:
            # Use bot_id as the key
            bot_id = str(bot['bot_id'])
            ref.child(bot_id).set(bot) #sets the bot data under the relevant bot_id
            print(f"Bot data uploaded successfully for bot_id: {bot_id}")
    except Exception as e:
        print(f"Error uploading bot data: {e}")

# Function to delete data from Realtime Database
def delete_data(path):
    try:
        ref = db.reference(path)
        ref.delete()
        print(f"Data at {path} deleted successfully!")
    except Exception as e:
        print(f"Error deleting data at {path}: {e}")

# Main execution block
if __name__ == "__main__":
    key_path = r"C:\\Users\\Padmini\\hackproject\\firdb-2025-firebase-adminsdk-fbsvc-a566cdf29f.json"  # Raw string
    database_url = 'https://firdb-2025-default-rtdb.firebaseio.com/'
    path = '\hackproject'  # Path in the Realtime Database

    bot_metadata = [
    {
        "bot_type": "ground_bot",
        "bot_id": 12,
        "altitude": 22,
        "lat": 12.1212,
        "long": -121.234,
        "battery_level": 78.2,
        "status": "in_mission",
        "contains_aid_kit": False,
        "capabilities": "Search - Scans the target disaster area, and collects information such as Photos, Distress voice signal recognition, Identify toxic gas emissions\nAssist Rescue - Assists human first responder during the rescue task\nDispatch aid package - Dispatches items such as water, food, first aid kit, to the human survivors."
    },
    {
        "bot_type": "ground_bot",
        "bot_id": 13,  # Changed bot_id to be unique
        "altitude": 22,
        "lat": 12.1212,
        "long": -121.234,
        "battery_level": 22.3,
        "status": "available",
        "contains_aid_kit": True,
        "capabilities": "Search - Scans the target disaster area, and collects information such as Photos, Distress voice signal recognition, Identify toxic gas emissions\nAssist Rescue - Assists human first responder during the rescue task\nDispatch aid package - Dispatches items such as water, food, first aid kit, to the human survivors."
    },
    {
        "bot_type": "drone_bot",
        "bot_id": 21,
        "altitude": 22,
        "lat": 12.1212,
        "long": -121.234,
        "battery_level": 78.2,
        "status": "available",
        "capabilities": "Search - Scans the target disaster area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
    },
    {
        "bot_type": "drone_bot",
        "bot_id": 22,  # Changed bot_id to be unique
        "altitude": 22,
        "lat": 12.1212,
        "long": -121.234,
        "battery_level": 78.2,
        "status": "available",
        "capabilities": "Search - Scans the target disaster area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
    }
]
    # Initialize Firebase
    if initialize_firebase(key_path, database_url):
        read_data(path)
        # Example data (if you want to push - uncomment push_data function)
        # push_data(path, bot_metadata)
        upload_bot_data(bot_metadata)
        read_data(path)

