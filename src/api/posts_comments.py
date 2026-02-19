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


@router.get("/posts/comments")
async def get_comments(session: SessionDep, post_id: int = None):
	if post_id:
		query = select(Post).where(Post.id==post_id)
		post = await session.execute(query)
		post = post.scalars().first()
		if not post:
			return {"ok": False, "error": "post not found"}
		
		query = select(PostComment).where(PostComment.post==post.id)
	else:
		query = select(PostComment)
	comments = await session.execute(query)
	return comments.scalars().all()


@router.post("/posts/comments")
async def create_comment(request: Request, data: PostCommentSchema, session: SessionDep):
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "auth error"}
	
	query = select(Post).where(Post.id==data.post_id)
	post = await session.execute(query)
	post = post.scalars().first()
	if not post or post.is_deleted:
		return {"ok": False, "error": "post not found"}
	
	comment = PostComment(user_id=request.state.user.id, post=data.post_id, text=data.text)
	session.add(comment)
	await session.commit()
	return {"ok": True, "msg": "comment was created", "data": comment}


@router.put("/posts/comments")
async def update_comment(request: Request, data: PostCommentUpdateSchema, session: SessionDep):
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "auth error"}
	
	query = select(PostComment).where(PostComment.id==data.comment_id)
	comment = await session.execute(query)
	comment = comment.scalars().first()
	
	if comment.user_id != request.state.user.id:
		return {"ok": False, "error": "permission denied"}
	
	smtp = update(PostComment).where(PostComment.id==data.comment_id).values(text=data.text)
	await session.execute(smtp)
	await session.commit()
	
	return {"ok": True, "msg": "comment was updated successfully"}


@router.delete("/posts/comments")
async def update_comment(request: Request, data: PostCommentDeleteSchema, session: SessionDep):
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "auth error"}
	
	query = select(PostComment).where(PostComment.id==data.comment_id)
	comment = await session.execute(query)
	comment = comment.scalars().first()
	if not comment:
		return {"ok": False, "error": "comment not found"}
	
	if comment.user_id != request.state.user.id:
		return {"ok": False, "error": "permission denied"}
	
	query = update(PostComment).where(PostComment.id==data.comment_id).values(is_deleted=True)
	await session.execute(query)
	await session.commit()
	return {"ok": True, "error": "comment was deleted"}
	