from fastapi import APIRouter, HTTPException, status, Depends
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
import os
from Router.auth import get_current_user

router = APIRouter(
    prefix= "/todos",
    tags=['Todo'],
    responses={401:{"error":"You are not authorized to perform this action."}}
)

url:str = os.environ.get("SUPABASE_URL")
key:str = os.environ.get("SUPABASE_KEY")
supabse: Client = create_client(url,key)

@router.get('/')
async def get_all_todos(user:dict = Depends(get_current_user)):
    response = supabse.table('todos').select('*').execute()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized"
        )
    
    return response.data