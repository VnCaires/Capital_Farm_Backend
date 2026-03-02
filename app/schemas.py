from pydantic import BaseModel

class PlayerCreate(BaseModel):
    username: str
    password: str

class PlayerLogin(BaseModel):
    username: str
    password: str

class PlayerResponse(BaseModel):
    id: int
    username: str
    balance: float

    class Config:
        from_attributes = True