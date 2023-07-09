from fastapi import APIRouter, HTTPException, status ,Request, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
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
    data = supabase.auth.get_user(token)
    data = jsonable_encoder(data)
    
    return data



async def create_profile(user, user_id):
    existing_profile = supabase.table('profiles').select('*').eq('owner_id',user_id).execute()
    
    if len(existing_profile.data) == 0:
        user_profile = supabase.table('profiles').insert({
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'email':user.email,
                    'owner_id': user_id
                }).execute()
    return
    
@router.post('/signup')
async def create_user(user : UserSchema, request:Request):  
    redirect_url = request.headers.get('X-Redirect-URL')  
    
    try:
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
        user_id = response.user.id
        await create_profile(user, user_id)
            
            
    except Exception as e:
        return {'error':str(e)}
    
    
    return {'response':"Signup complete. Please confirm your email."}

@router.post('/signin')
async def login_user(login_form: LoginFormSchema ):
    data = supabase.auth.sign_in_with_password({
        'email':login_form.email,
        "password":login_form.password
    })
    
    return data.session.access_token

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    user_id = user.get('user').get('id')
    try:
        profile = supabase.table('profiles').select('*').eq('owner_id',user_id).execute()
    except Exception as e:
        return {'error':str(e)}
    return profile

async def get_profile_id(user: dict):
    user_id = user.get('user').get('id')
    
    try:
        profile = supabase.table('profiles').select('*').eq('owner_id',user_id).execute()
        profile = jsonable_encoder(profile)['data']
        profile_id = profile[0].get('id')
        
    except Exception as e:
        return {'error':str(e)}
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Your profile do not exist!'
        )
        
    
    return profile_id
    
    
    


        
