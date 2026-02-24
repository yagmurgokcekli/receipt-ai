from pydantic import BaseModel, EmailStr


class UserInfo(BaseModel):
    user_id: str  # Microsoft oid 
    email: EmailStr  
    name: str | None = None  
    
