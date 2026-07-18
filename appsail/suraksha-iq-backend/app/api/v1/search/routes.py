from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def get_search():
    return {'message': 'search endpoint'}
