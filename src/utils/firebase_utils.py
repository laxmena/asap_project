import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

from src.constants import firebase_auth,path,database_url

key_path = firebase_auth  # key auth

class FirebaseUtil:
    """Utility class for Firebase Realtime Database operations."""

    def __init__(self, key_path, database_url):
        """Initializes the FirebaseUtil with credentials and database URL."""
        self.key_path = key_path
        self.database_url = database_url
        self.initialized = self._initialize_firebase()

    def _initialize_firebase(self):
        """Initializes Firebase app with provided credentials."""
        try:
            if not os.path.exists(self.key_path):
                raise FileNotFoundError(f"Key file not found at {self.key_path}")

            cred = credentials.Certificate(self.key_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': self.database_url
            })
            print("Firebase initialized successfully!")
            return True
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            return False
        
    def _check_initialized(self):
        """Checks if Firebase is initialized and returns False if not."""
        if not self.initialized:
            print("Firebase not initialized. Cannot perform operation.")
            return False
        return True

    def read_data(self, path):
        """Reads data from the specified path in the Realtime Database."""
        if not self._check_initialized():
            return
        try:
            ref = db.reference(path)
            snapshot = ref.get()
            if snapshot:
                print("Data read successfully:", snapshot)
                return snapshot
            else:
                print(f"No data found at {path}.")
                return None
        except Exception as e:
            print(f"Error reading data: {e}")
            return None
        
#psuh any data to be retrived from this path
    def push_data(self, path, data):
        """Pushes data to the specified path in the Realtime Database."""
        if not self._check_initialized():
            return
        try:
            ref = db.reference(path)
            ref.push(data)
            print("Data pushed successfully!")
        except Exception as e:
            print(f"Error pushing data: {e}")

    def upload_bot_data(self, bot_data):
        """Uploads bot data to the 'bots' node in the Realtime Database."""
        if not self._check_initialized():
            return
        try:
            ref = db.reference("bots")
            for bot in bot_data:
                bot_id = str(bot['bot_id'])
                ref.child(bot_id).set(bot)
                print(f"Bot data uploaded successfully for bot_id: {bot_id}")
        except Exception as e:
            print(f"Error uploading bot data: {e}")

#truncate all the data from hackproject. use it with caution
    def delete_data(self, path):
        """Deletes data at the specified path in the Realtime Database."""
        if not self._check_initialized():
            return
        try:
            ref = db.reference(path)
            ref.delete()
            print(f"Data at {path} deleted successfully!")
        except Exception as e:
            print(f"Error deleting data at {path}: {e}")

#uploading drone fleet status to get the gas emission data
    def upload_drone_fleet_status(self, status_data):
        """Uploads drone fleet status data to the 'drone_status' node."""
        if not self._check_initialized():
            return
        try:
            ref = db.reference("drone_status")
            ref.set(status_data)  # Use set() to overwrite existing data
            print("Drone fleet status uploaded successfully!")
        except Exception as e:
            print(f"Error uploading drone fleet status: {e}")
