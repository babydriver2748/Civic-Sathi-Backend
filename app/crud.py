from sqlalchemy.orm import Session
from . import models, schemas, auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Hash the user's password before saving it
    hashed_password = auth.get_password_hash(user.password)
    # Create a new database User object
    db_user = models.User(
        email=user.email,
        phone_number=user.phone_number,
        full_name=user.full_name, 
        hashed_password=hashed_password
    )
    # Add the new user to the database and commit the change
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def create_issue(db: Session, issue: schemas.IssueCreate, user_id: int, photo_path: str, audio_path: str):
    """
    Creates a new issue record in the database.
    """
    db_issue = models.Issue(
        **issue.dict(), 
        user_id=user_id, 
        photo_url=photo_path, 
        audio_url=audio_path
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue
def get_issues_by_user(db: Session, user_id: int):
    """
    Fetches all issues from the database for a specific user.
    """
    return db.query(models.Issue).filter(models.Issue.user_id == user_id).all()