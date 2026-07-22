from fastapi import APIRouter, Request

router = APIRouter()

@router.get('/')
async def get_users(request: Request):
    return {'message': 'users endpoint'}
