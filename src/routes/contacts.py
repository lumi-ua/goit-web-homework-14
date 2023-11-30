from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=List[ContactResponse], description="Requests are limited", 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), 
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contacts function returns a list of contacts.

        get:
          summary: Returns a list of contacts.
          description: This can only be done by the logged in user.
          operationId: read_contacts
          tags: [contacts]
          parameters: Parameters are optional, but if you have them, they must be defined here!  Otherwise Swagger UI will not display them correctly!  
    
    :param skip: int: Skip a number of contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description="Requests are limited", 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), 
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by id.
        If the user is not logged in, they will receive an HTTP 401 error.
        If the user does not have permission to view this contact, they will receive an HTTP 403 error.
        If no such contact exists with that id, then it returns a 404 Not Found response.
    
    :param contact_id: int: Get the contact_id from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post("/", response_model=ContactResponse, description="Requests are limited", dependencies=[Depends(RateLimiter(times=5, seconds=60))], 
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)):    
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input and returns the newly created contact.
    
    
    :param body: ContactModel: Pass the request body to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user id of the current logged in user
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact
    


@router.put("/{contact_id}", response_model=ContactResponse, description="Requests are limited", 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes in a ContactModel object, which is used to update the contact's information.
        It also takes an optional parameter of contact_id, which is used to identify the specific 
        contact that will be updated. If no id is provided, then it will default to 1.
    
    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Specify the id of the contact to be updated
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(body, contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete("/{contact_id}", description="Requests are limited", dependencies=[Depends(RateLimiter(times=10, seconds=60))], 
               status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
        The function takes in an integer representing the id of the contact to be removed, 
        and returns a dictionary containing information about that contact.
    
    :param contact_id: int: Specify the type of data that will be passed to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A contact object, which is a dictionary
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/search/", response_model=List[ContactResponse], description="Requests are limited", 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_contacts(query: str, db: Session = Depends(get_db), 
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    The search_contacts function searches for contacts in the database.
        Args:
            query (str): The search term to be used when searching for contacts.
            db (Session, optional): SQLAlchemy Session instance. Defaults to Depends(get_db).
            current_user (User, optional): User object containing information about the user making the request. 
            Defaults to Depends(auth_service.get_current_user). Returns: A list of Contact objects that match 
            the search criteria.
    
    :param query: str: Search for a contact by name or email
    :param db: Session: Access the database
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.search_contacts(query, current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse], description="Requests are limited", 
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts_with_upcoming_birthdays(db: Session = Depends(get_db), 
                                               current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_with_upcoming_birthdays function returns a list of contacts with upcoming birthdays.
        The function takes in the current user and database as parameters, then calls the get_contacts_with_upcoming_birthdays 
        function from repository/repository.py to retrieve all contacts with upcoming birthdays for that user.
    
    :param db: Session: Pass the database session to the repository function
    :param current_user: User: Get the user id of the current logged in user
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts_with_upcoming_birthdays(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts

