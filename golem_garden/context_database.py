import json
import uuid
from typing import Dict, List, Union

from pymongo import MongoClient


class ContextDatabase:
    def __init__(self,
                 database_name: str = "golem_garden",
                 conversation_collection_name: str = "conversations",
                 user_collection_name: str = "users",
                 user_id: str = None,
                 user_name: str = None,
                 user_description: str = None):
        self.client = MongoClient()
        self.db = self.client[database_name]
        self.conversations_collection = self.db[conversation_collection_name]
        self.users_collection = self.db[user_collection_name]

        if user_id is None:
            user_id = str(uuid.uuid4())

        self.user_id = user_id
        self.get_or_create_user(user_id, user_name, user_description)

    def get_or_create_user(self, user_id: str, user_name: str, user_description: str):
        user = self.users_collection.find_one({"user_id": user_id})
        if user is None:
            user = {
                "user_id": user_id,
                "user_name": user_name,
                "user_description": user_description,
                "name_history": [],
                "description_history": []
            }
            self.users_collection.insert_one(user)

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        self._user_name = user_name

    @property
    def user_description(self):
        return self._user_description

    @user_description.setter
    def user_description(self, user_description):
        self._user_description = user_description

    def add_message(self, golem_name: str, role: str, content: str):
        conversation = {
            "user_id": self._user_id,
            "user_name": self._user_name,
            "user_description": self._user_description,
            "golem_id": golem_name,
            "role": role,
            "content": content
        }
        self.conversations_collection.insert_one(conversation)

    def get_history(self, query: dict = None) -> List[Dict[str, str]]:
        """Get chat history for a given query. If no query is provided, return all chat history."""

        include_fields = {"role": 1, "content": 1, "_id": 0}

        if query is None:
            query = {}

        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {"content": "$content", "role": "$role"},
                "doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$project": include_fields}
        ]

        history = list(self.conversations_collection.aggregate(pipeline))
        return history

    def as_json(self):
        conversations = list(self.conversations_collection.find({"user_id": self._user_id}))
        return json.dumps(conversations, indent=4, default=str)

    def print(self):
        print(self.as_json())


if __name__ == "__main__":
    demo_user_id = "John"
    demo_user_name = "John Doe"
    demo_user_description = "A demo user"

    db = ContextDatabase(user_id=demo_user_id, user_name=demo_user_name, user_description=demo_user_description)
    db.add_message("Golem1", "user", "Hello, Golem1!")
    db.add_message("Golem1", "golem", "Hello, John!")
    db.add_message("Golem2", "user", "Hello, Golem2!")
    db.add_message("Golem2", "golem", "Hello, John!")
    db.print()
    print("Chat history with Golem1:")
    print(db.get_history({"golem_id": "Golem1"}))
    print("\nChat history with Golem2:")
    print(db.get_history({"golem_id": "Golem2"}))
    print("\nChat history for user: John")
    print(db.get_history({"user_id": "John"}))
    print("\nChat history for non-existent user: Jane")
    print(db.get_history({"user_id": "Jane"}))
    print("\nChat history for user: John and Golem1")
    print(db.get_history({"user_id": "John", "golem_id": "Golem1"}))

