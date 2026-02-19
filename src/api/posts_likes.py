from fastapi import APIRouter, Request, UploadFile, Form

from src.models.users import User
from src.models.posts import Post, PostLike, PostComment
from src.schemas.users import UserLoginSchema
from src.schemas.posts import (
    PostLikeSchema,
    PostCommentSchema,
    PostCommentUpdateSchema,
    PostCommentDeleteSchema
)
from src.database import select, update, delete
from src.dependencies import SessionDep, PaginationDep

router = APIRouter()


@router.get("/posts/likes")
async def get_likes(session: SessionDep, post_id: int = None):
	if post_id:
		query = select(PostLike).filter_by(post=post_id)
		likes = await session.execute(query)
		return likes.scalars().all()
	
	query = select(PostLike)
	likes = await session.execute(query)
	return likes.scalars().all()


@router.post("/posts/likes")
async def create_like(request: Request, data: PostLikeSchema, session: SessionDep):
	query = select(Post).where(Post.id==data.post_id)
	post = await session.execute(query)
	post = post.scalars().first()
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not post:
		return {"ok": False, "error": "post not found"}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "auth error"}
	
	like = select(PostLike).where(PostLike.user==request.state.user.id)
	like = await session.execute(like)
	like = like.scalars().first()
	if like:
		smtp = delete(PostLike).where(PostLike.id==like.id)
		await session.execute(smtp)
		await session.commit()
		return {"ok": True, "msg": "like was deleted"}
	like = PostLike(user=request.state.user.id, post=post.id)
	session.add(like)
	await session.commit()
	return {"ok": True, "msg": "like was created"}
	