from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    user_id: int
    current_price: Optional[float]
    last_checked: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Price History Schemas
class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Price Alert Schemas
class PriceAlertBase(BaseModel):
    product_id: int
    target_price: float = Field(..., gt=0)


class PriceAlertCreate(PriceAlertBase):
    pass


class PriceAlertResponse(PriceAlertBase):
    id: int
    user_id: int
    is_active: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
