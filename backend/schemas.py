from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class userLogin(BaseModel):
    username: str
    password: str
    rememberMe: bool = False

class file(BaseModel):
    value: str | None