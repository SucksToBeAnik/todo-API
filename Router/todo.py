from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
import os
from Router.auth import get_current_user, get_profile_id
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter(
    prefix= "/todos",
    tags=['Todo'],
    responses={401:{"error":"You are not authorized to perform this action."}}
)

url:str = os.environ.get("SUPABASE_URL")
key:str = os.environ.get("SUPABASE_KEY")
supabse: Client = create_client(url,key)

# **************************************************** #

class TagEnum(str, Enum):
    academic = "academic"
    personal = "personal"


class TodoSchema(BaseModel):
    title: str = Field(...,min_length=2)
    body: str
    tags: list[TagEnum]
    
    

@router.get('/')
async def get_all_todos(user:dict = Depends(get_current_user)):
    profile_id = await get_profile_id(user)
    
    try:
        response = supabse.table('todos').select('*,profiles(*)').eq('owner_id',profile_id).execute()
    except Exception as e:
        return {'error':str(e)}
    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized"
        )
    
    return response.data



@router.post('/',status_code=201)
async def create_todos(todo_schema:TodoSchema,user:dict = Depends(get_current_user)): 
    profile_id  = await get_profile_id(user)
        
    try:
        todo = supabse.table('todos').insert({
            'title':todo_schema.title,
            'body':todo_schema.body,
            'tags':todo_schema.tags,
            'owner_id':profile_id
        }).execute()
    except Exception as e:
        return {'error':str(e)}
    
    return todo


        

    