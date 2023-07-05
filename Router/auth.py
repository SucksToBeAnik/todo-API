from fastapi import APIRouter, HTTPException, status ,Request, Depends
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client,Client

from dotenv import load_dotenv
load_dotenv()
import os
from pydantic import BaseModel, Field, EmailStr

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

url:str = os.environ.get("SUPABASE_URL")
key:str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url,key)

#----------------------------------------#

class UserSchema(BaseModel):
    email : EmailStr = Field(...)
    password: str = Field(...)
    first_name: str 
    last_name: str
    
    class Config:
        schema_extra = {
            "example":{
                "email": "anik.islam1494@gmail.com",
                "password":"anik12345",
                "first_name":"Jami Islam",
                "last_name":"Anik"
            }
        }
        
class LoginFormSchema(BaseModel):
    email : EmailStr = Field(...)
    password: str = Field(...)


#----------------------------------------#

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='signin')
async def get_current_user(token: str = Depends(oauth2_bearer)):
    user = supabase.auth.get_user(token)
    return user

@router.post('/signup')
async def create_user(user : UserSchema, request:Request):
    redirect_url = request.headers.get('X-Redirect-URL')
    
    response = supabase.auth.sign_up({
        "email":user.email,
        "password":user.password,
        "options":{
            "data":{
                "first_name":user.first_name,
                "last_name":user.last_name
            },
            "redirect_to":redirect_url
        },
    }
    )
    if not response.user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid credentials provided"
        )
    
    return response.user

@router.post('/signin')
async def login_user(login_form: LoginFormSchema ):
    data = supabase.auth.sign_in_with_password({
        'email':login_form.email,
        "password":login_form.password
    })
    
    return data.session.access_token

@router.get("/account")
async def get_account(user: dict = Depends(get_current_user)):
    return user
    


        
