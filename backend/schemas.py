from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class userLogin(BaseModel):
    username: str
    password: str
    rememberMe: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class file(BaseModel):
    value: str | None

class SaveRequest(BaseModel):
    dataset: str
    filename: str
    content: str

class ProjectCreate(BaseModel):
    project_name: str
    description: str

class ProjectDelete(BaseModel):
    project_name: str

class ModelName(BaseModel):
    model_name: str