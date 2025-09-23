from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import shutil
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
# --- THIS IS THE FIX: Import StaticFiles from FastAPI ---
from fastapi.staticfiles import StaticFiles

from . import models, schemas, crud, auth
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Civic Sathi API")

# This ensures the 'uploads' directory exists when the app starts.
os.makedirs("uploads", exist_ok=True)

# This line will now work because we have imported StaticFiles.
# It makes any file inside the 'uploads' folder publicly accessible.
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- The rest of the file is correct and remains the same ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = auth.decode_access_token(token)
    user = None
    if "@" in username:
        user = crud.get_user_by_email(db, email=username)
    else:
        user = crud.get_user_by_phone_number(db, phone_number=username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find user")
    return user

@app.post("/users/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.email:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    if user.phone_number:
        db_user = crud.get_user_by_phone_number(db, phone_number=user.phone_number)
        if db_user:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = None
    if "@" in form_data.username:
        user = crud.get_user_by_email(db, email=form_data.username)
    else:
        user = crud.get_user_by_phone_number(db, phone_number=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email/phone or password")
    subject = user.email if user.email is not None else user.phone_number
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": subject}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user_full_name": user.full_name}

@app.post("/issues/report/", response_model=schemas.Issue)
def create_new_issue(
    request: Request,
    description: str = Form(...),
    department: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    photo: UploadFile = File(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo_filename = f"{current_user.id}_{int(datetime.now().timestamp())}_{photo.filename}"
    photo_path = f"uploads/{photo_filename}"
    with open(photo_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    audio_filename = f"{current_user.id}_{int(datetime.now().timestamp())}_{audio.filename}"
    audio_path = f"uploads/{audio_filename}"
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    base_url = str(request.base_url)
    full_photo_url = f"{base_url}{photo_path}"
    full_audio_url = f"{base_url}{audio_path}"

    issue_data = schemas.IssueCreate(
        description=description,
        department=department,
        latitude=latitude,
        longitude=longitude
    )
    
    return crud.create_issue(
        db=db, 
        issue=issue_data, 
        user_id=current_user.id, 
        photo_path=full_photo_url,
        audio_path=full_audio_url
    )

@app.get("/issues/my-issues/", response_model=List[schemas.Issue])
def get_user_issues(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    issues = crud.get_issues_by_user(db, user_id=current_user.id)
    return issues

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic Sathi Backend!"}