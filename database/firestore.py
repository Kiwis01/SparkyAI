from utils.common_imports import *
class Firestore:
    # This class is responsible for interacting with Firestore database.
    def __init__(self,discord_state):
        if not firebase_admin._apps:
            cred = credentials.Certificate("config/firebase_secret.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.collection = None
        self.document = {
            "superior_agent_message": [],
            "discord_agent_message": [],
            "google_agent_message": [],
            "shuttle_status_agent_message": [],
            "courses_agent_message": [],
            "student_club_events_agent_message": [],
            "library_agent_message": [],
            "sports_agent_message": [],
            "scholarship_agent_message": [],
            "news_media_agent_message": [],
            "student_club_agent_message": [],
            "student_jobs_agent_message": [],
            "user_id": "",
            "user_message": "",
            "time": "",
            "category": []
        }
        self.discord_state = discord_state
        print("@firestore.py Firestore initialized @ Firestore")
    # This method is used to update the collection name in Firestore.
    def update_collection(self, collection):
        # get existing collections
        collections = self.db.collections()
        collection_names = [col.id for col in collections]
        print(f"@firestore.py Existing collections: {collection_names}")
        
        print(f"@firestore.py Updating Firestore collection to: {collection}")
        if not collection in collection_names:
            raise ValueError(f"@firestore.py Collection '{collection}' does not exist.")
        
        self.collection = collection
        
        print(f"@firestore.py Firestore collection updated to: {self.collection}")
    # This method is used to update the message in the document.
    def update_message(self, property, value): 
        if property in self.document:
            if isinstance(self.document[property], list):
                print(f"@firestore.py Appending to {property}: {value}")
                self.document[property].append(f"{value}")
            else:
                self.document[property] = f"{value}"
                print(f"@firestore.py Setting {property} to: {value}")
        else:
            raise ValueError(f"@firestore.py Invalid property: {property}")
    # This method is used to push the message to Firestore.
    async def push_message(self):
        
        if not self.collection:
            raise ValueError("@firestore.py Collection not set. Use update_collection() first.")
        
        print(f"@firestore.py Pushing message to Firestore collection: {self.collection}")
        self.document["user_id"] = self.discord_state.get('user_id')
        
        self.document["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        doc_ref = self.db.collection(self.collection).document()
        doc_ref.set(self.document)
        print(f"@firestore.py Document written with ID: {doc_ref.id}")
        await self.check_and_add_user() 
        return doc_ref.id  # Return the document ID for reference
    # This method is used to check if the user exists in Firestore and add them if not.
    async def check_and_add_user(self):
        # Check if the user already exists in the Firestore database
        user_id = self.discord_state.get('user_id')
        if not user_id:
            raise ValueError("@firestore.py User ID not found in discord_state.")
        
        users_collection = self.db.collection("users")
        # Use the where method for filtering in Firestore
        query_results = users_collection.where("user_id", "==", user_id).get()
        print(f"Query result: {query_results}")
        
        # Check if the user already exists in the collection
        if not list(query_results):  # Convert to list to check if empty
            new_user_doc = {
                "user_id": user_id,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_has_mod_role": self.discord_state.get('user_has_mod_role'),
                "user_in_voice_channel": self.discord_state.get('user_in_voice_channel'),
                "request_in_dm": self.discord_state.get('request_in_dm'),
                "guild_user": str(self.discord_state.get('guild_user')),
                "user_voice_channel_id": self.discord_state.get('user_voice_channel_id'),
            }
            users_collection.add(new_user_doc)
            print(f"@firestore.py New user added to Firestore: {new_user_doc}")
