from .model import User, UserRequest, Connection, UpdateUserRequest

from _exceptions import BadRequestError, NotFoundError
from db.service import sync_db

from utilities.helpers import generate_uuid
from utilities.encryption import SecretCipher

from pymongo import ReturnDocument


from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime


class UserService:
    def __init__(self):
        self.collection = sync_db["users"]

    def create_user(self, user: UserRequest):
        if self.collection.find_one({"email": user.email}):
            raise BadRequestError("User already exists")

        user_data = User(email=user.email, metadata=user.metadata)
        user_data_json = user_data.model_dump()
        try:
            self.collection.insert_one(user_data_json.copy())
            return user_data_json
        except Exception as e:
            raise BadRequestError(str(e))

    def get_user_by_index_id(self, index_id: str) -> Optional[User]:
        """
        Retrieve a user by one of their index_ids.
        """
        user_data = self.collection.find_one({"index_ids": index_id})
        if not user_data:
            raise NotFoundError("User not found")

        return User(**user_data)

    def update_user(self, index_id, updated_data):
        filters = {"index_ids": index_id}

        try:
            validated_data = UpdateUserRequest(**updated_data).model_dump(
                exclude_unset=True
            )
        except Exception as e:
            raise BadRequestError(str(e))

        user_data = self.collection.find_one_and_update(
            filters,
            {"$set": validated_data},
            return_document=ReturnDocument.AFTER,
        )
        if not user_data:
            raise NotFoundError("User not found")
        return user_data

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """
        Retrieve a user by one of their API keys.
        """
        user_data = self.collection.find_one({"api_keys.key": api_key})
        if not user_data:
            raise NotFoundError("User not found")
        return User(**user_data)

    def get_index_ids(self, api_key: str, index_id: str = None):
        """
        Retrieve index_ids by an API key.
        """
        query = {"api_keys.key": api_key}
        if index_id:
            query["index_ids"] = index_id
        user_data = self.collection.find_one(query, {"index_ids": 1, "_id": 0})
        if not user_data:
            raise NotFoundError("User not found")
        return user_data.get("index_ids")[0]  # TODO: temporary fix for now

    def get_user_by_email(self, user: UserRequest) -> Optional[User]:
        """
        Retrieve a user by their email.
        """
        user_data = self.collection.find_one({"email": user.email})
        if not user_data:
            raise NotFoundError("User not found")
        return user_data
