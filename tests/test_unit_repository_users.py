import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email, 
    create_user, 
    update_token, 
    confirmed_email, 
    update_avatar
)

class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        
    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = User(email=email)
        self.session.query.return_value.filter.return_value.first.return_value = user
        result = await get_user_by_email(email=email, db=self.session)
        self.assertEqual(result, user)

    
    async def test_create_user(self):
        body = UserModel(
            username="Johnny",
            email="test@example.com",
            password="1234567",
        )
        new_user = User(**body.model_dump())
        created_user = await create_user(body=body, db=self.session)
        self.assertEqual(created_user.username, new_user.username)
        self.assertEqual(created_user.email, new_user.email)
        self.session.commit.assert_called_once()


    async def test_update_token(self):
        user = User()
        token = "new_token"
        await update_token(user=user, token=token, db=self.session)
        self.assertEqual(user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = "test@example.com"
        user = User(email=email)
        self.session.query.return_value.filter.return_value.first.return_value = user
        await confirmed_email(email=email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()


    async def test_update_avatar(self):
        email = "test@example.com"
        url = "img.com"
        user = await update_avatar(email=email, url=url, db=self.session)
        self.assertEqual(user.avatar, url)
        self.session.commit.assert_called_once()