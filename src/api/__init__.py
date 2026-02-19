from fastapi import APIRouter

from src.api.users import router as users_router
from src.api.posts import router as posts_router
from src.api.posts_likes import router as posts_likes_router
from src.api.posts_comments import router as posts_comments_router

main_router = APIRouter(prefix="/api")

main_router.include_router(users_router)
main_router.include_router(posts_router)
main_router.include_router(posts_likes_router)
main_router.include_router(posts_comments_router)

