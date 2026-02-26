from pydantic import BaseModel, ValidationError, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    email: str

    @field_validator('email')
    def email_must_contain_symbol(cls, v):
        if '@' not in v:
            raise ValueError('must contain @ symbol')
        return v