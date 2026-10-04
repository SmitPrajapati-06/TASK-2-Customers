from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from typing import List
from typing import Optional


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    city: str = Field(..., min_length=2, max_length=100)


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    city: str

    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    city: str = Field(..., min_length=2, max_length=100)


class CustomerPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    city: Optional[str] = Field(None, min_length=2, max_length=100)