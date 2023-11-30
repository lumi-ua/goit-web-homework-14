from typing import List
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, extract 
from fastapi import HTTPException, status

from src.database.models import Contacts, User
from src.schemas import ContactModel

async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contacts]:
    """
    The get_contacts function returns a list of contacts for the user.
        
    
    :param skip: int: Skip a number of records in the database
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user_id from the database
    :param db: Session: Pass a database session to the function
    :return: A list of contacts for a specific user
    :doc-author: Trelent
    """
    return db.query(Contacts).filter(Contacts.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contacts:
    """
    The get_contact function returns a contact from the database based on the user's id and contact_id.
        Args:
            contact_id (int): The id of the desired Contact.
            user (User): The User object that is requesting this information. This is used to ensure that only contacts belonging to this user are returned. 
            db (Session): A connection to our database, which we use for querying data from it.
    
    :param contact_id: int: Get the contact by id
    :param user: User: Get the user id from the user object
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    return contact



async def create_contact(body: ContactModel, user: User, db: Session):
    """
    The create_contact function creates a new contact in the database.
        Args:
            body (ContactModel): The contact to create.
            user (User): The current user, who is creating the contact.
            db (Session): A database session object for interacting with the database. 
    
    :param body: ContactModel: Get the data from the request body
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    existing_contact = db.query(Contacts).filter(
            and_(Contacts.phone_number == body.phone_number, Contacts.user_id == user.id)).first()
    if existing_contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Contact is exists!') 

    contact = Contacts(**body.model_dump(), user = user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact





async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session) -> Contacts:
    """
    The update_contact function updates a contact in the database.
        Args:
            body (ContactModel): The updated contact information.
            contact_id (int): The id of the contact to update.
            user (User): The current user making this request, used for authorization purposes.
            db (Session): A connection to the database that will be used for querying and updating data.
    
    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Find the contact in the database
    :param user: User: Get the user_id from the database
    :param db: Session: Access the database
    :return: The contact object
    :doc-author: Trelent
    """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        db.commit()
    return contact



async def remove_contact(contact_id: int, user: User, db: Session) -> Contacts | None:
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who is removing the contact.
            db (Session): A session object for interacting with our database.
        Returns: 
            Contacts | None: If successful, returns a contacts object that was deleted, otherwise returns None.
    
    :param contact_id: int: Identify the contact to be deleted
    :param user: User: Get the user id from the logged in user
    :param db: Session: Access the database
    :return: A contact object if the contact exists, otherwise it returns none
    :doc-author: Trelent
    """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact



async def search_contacts(query: str, user: User, db: Session):
    """
    The search_contacts function searches the database for contacts that match a given query.
        The function takes in three arguments:
            - query: A string containing the search term(s) to be used when searching the database.
            - user: An object representing a User, which is used to filter out contacts belonging to other users.
            - db: A Session object, which is used as an interface between Python and SQLAlchemy.
    
    :param query: str: Search for a contact in the database
    :param user: User: Get the user id of the current logged in user
    :param db: Session: Access the database
    :return: A list of contacts that match the query
    :doc-author: Trelent
    """
    contacts = db.query(Contacts).filter(and_(
        or_(
            Contacts.first_name.ilike(f"%{query}%"),
            Contacts.last_name.ilike(f"%{query}%"),
            Contacts.email.ilike(f"%{query}%"),
        ), Contacts.user_id == user.id
    )
        
    ).all()
    return contacts



async def get_contacts_with_upcoming_birthdays(user: User, db: Session):
    """
    The get_contacts_with_upcoming_birthdays function returns a list of contacts with upcoming birthdays.
        Args:
            user (User): The user whose contacts are being queried.
            db (Session): A database session object to query the database with.
        Returns:
            List[Contacts]: A list of Contacts objects that have upcoming birthdays.
    
    :param user: User: Get the user id from the user model
    :param db: Session: Access the database
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    today = date.today()
    end_date = today + timedelta(days=7)
    contacts = db.query(Contacts).filter(and_(
        and_(
            extract('month', Contacts.birthday) == today.month,
            extract('day', Contacts.birthday) >= today.day,
            extract('day', Contacts.birthday) <= end_date.day,
        ), Contacts.user_id == user.id
    )).all()
    return contacts