from pydantic import BaseModel


class NewUser(BaseModel):
    username: str
    password1: str
    password2: str


class User(BaseModel):
    username: str
    password: str
