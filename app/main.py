from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import models, schemas, database, crud, auth

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.PlayerResponse)
def register(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player_by_username(db, player.username)
    if db_player:
        raise HTTPException(status_code=400, detail="Username already registered")

    return crud.create_player(db, player.username, player.password)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_player = crud.get_player_by_username(db, form_data.username)

    if not db_player:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth.verify_password(form_data.password, db_player.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = auth.create_access_token(
        data={"sub": db_player.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.PlayerResponse)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = auth.verify_token(token)
    db_player = crud.get_player_by_username(db, username)

    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    return db_player