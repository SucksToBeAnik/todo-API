from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
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
supabase: Client = create_client(url,key)

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
    profile_id :int = await get_profile_id(user)
    
    try:
        response = supabase.table('todos').select('*').eq('owner_id',profile_id).execute()
    except Exception as e:
        return {'error':str(e)}
    
    
    return response.data



@router.post('/',status_code=201)
async def create_todos(todo_schema:TodoSchema,user:dict = Depends(get_current_user)): 
    profile_id  = await get_profile_id(user)
    try:
        todo = supabase.table('todos').insert({
            'title':todo_schema.title,
            'body':todo_schema.body,
            'tags':todo_schema.tags,
            'owner_id':profile_id
        }).execute()
    except Exception as e:
        return {'error':str(e)}
    
    return todo


@router.delete('/{id}')
async def delete_todo(id:int = Path(...,gt=0), user:dict = Depends(get_current_user)):
    profile_id = await get_profile_id(user)
    
    try:
        todo = supabase.table('todos').delete().eq('id',id).eq('owner_id',profile_id).execute()
        
    except Exception as e:
        return {'error':str(e)}
    if len(todo.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo does not exist'
        )
    return {"response":todo,}

@router.put('/{todo_id}')
async def update_todo(todo_schema:TodoSchema,todo_id:int = Path(...,gt=0),user:dict = Depends(get_current_user)):
    profile_id  = await get_profile_id(user)
    try:
        todo = supabase.table('todos').select('*').eq('id',todo_id).eq('owner_id',profile_id).execute()
        
    except Exception as e:
        return {"error":str(e)}
    
    if len(todo.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo does not exist'
        )
    
    try:
        todo = supabase.table('todos').update({
            'title':todo_schema.title,
            'body':todo_schema.body,
            'tags':todo_schema.tags
        }).eq('id',todo_id).execute()
    except Exception as e:
        return {'error':str(e)}
    
    
    return todo.data
    
    
    
    
    
    


    
    

    