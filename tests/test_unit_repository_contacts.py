import unittest
from unittest.mock import MagicMock
from datetime import date
from fastapi import HTTPException

from sqlalchemy.orm import Session

from src.database.models import Contacts, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts, 
    get_contact, 
    create_contact, 
    update_contact, 
    remove_contact, 
    search_contacts, 
    get_contacts_with_upcoming_birthdays,

)

class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contacts(), Contacts(), Contacts()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contacts(self):
        body = ContactModel(
            first_name="Jhon", 
            last_name="Dou", 
            email="test@ex.uk", 
            phone_number="09822233311", 
            birthday=date(2002, 12, 12)
            )
        self.session.query().filter().first.return_value = None
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

        self.session.query().filter().first.return_value = Contacts(phone_number=body.phone_number)
        with self.assertRaises(HTTPException) as context:
            await create_contact(body=body, db=self.session, user=self.user)
        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, 'Contact is exists!')

    
    async def test_update_contact_found(self):
        contact_id = 1
        contact = Contacts(id=contact_id, user_id=self.user.id)
        body = ContactModel(
            first_name="Jora", 
            last_name="Dyadya", 
            email="update@ex.uk", 
            phone_number="0987654321", 
            birthday=date(2002, 11, 11)
            )
        self.session.query().filter().first.return_value = contact
        result = await update_contact(contact_id=contact_id, body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)


    async def test_update_contact_not_found(self):
        body = ContactModel(
            first_name="Jora", 
            last_name="Dyadya", 
            email="update@ex.uk", 
            phone_number="0987654321", 
            birthday=date(2002, 11, 11)
            )
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_contacts_found(self):
        query = "John"
        contacts = [Contacts(id=i, user_id=self.user.id, first_name=f"John {i}") for i in range(1, 6)]
        self.session.query().filter().all.return_value = contacts
        result = await search_contacts(query=query, user=self.user, db=self.session)
        self.assertEqual(result, contacts)


    async def test_search_contacts_not_found(self):
        query = "John"
        self.session.query().filter().all.return_value = None
        result = await search_contacts(query=query, user=self.user, db=self.session)
        self.assertIsNone(result)


    async def test_get_contacts_with_upcoming_birthdays(self):
        upcoming_birthdays_contacts = [Contacts(id=i, user_id=self.user.id) for i in range(1, 6)]
        self.session.query().filter().all.return_value = upcoming_birthdays_contacts
        result = await get_contacts_with_upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, upcoming_birthdays_contacts)




if __name__ == '__main__':
    unittest.main()
