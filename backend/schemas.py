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

class SaveRequest(BaseModel):
    dataset: str
    filename: str
    content: str