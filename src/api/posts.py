from fastapi import APIRouter, HTTPException, Request, UploadFile, Form
from fastapi.responses import FileResponse

from src.models.users import User
from src.models.posts import Post, PostLike, PostComment
from src.schemas.users import UserLoginSchema
from src.schemas.posts import (
    PostPutSchema,
    PostDeleteSchema,
    PostLikeSchema,
    PostCommentSchema,
    PostCommentUpdateSchema,
    PostCommentDeleteSchema
)
from src.database import select, update, delete, joinedload
from src.dependencies import SessionDep, PaginationDep
from src.utils.search import search_data
import secrets

router = APIRouter()


@router.get("/posts")
async def get_posts(session: SessionDep, pagination: PaginationDep):
	query = select(Post).options(joinedload(Post.author)).filter_by(is_deleted=False).limit(pagination.limit).offset(pagination.offset)
	posts = await session.execute(query)
	return posts.scalars().all()


@router.post("/posts")
async def create_post(
    session: SessionDep,
    request: Request,
    image: UploadFile,
    title: str = Form(),
    text: str = Form()
):
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "permission denied"}
	
	if len(title) > 32:
		return {"ok": False, "error": "title so long"}
	
	key = secrets.token_urlsafe(5)
	filename = f"{key}_{image.filename}"
	path = f"src/media/images/{filename}"
	
	with open(path, "wb") as file:
		file.write(image.file.read())
	
	post = Post(image=filename, author_id=request.state.user.id, title=title, text=text)
	session.add(post)
	await session.commit()
	return post


@router.put("/posts")
async def update_post(request: Request, data: PostPutSchema, session: SessionDep):
	query = select(Post).filter_by(id=data.post_id)
	post = await session.execute(query)
	post = post.scalars().first()
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not post or post.is_deleted:
		return {"ok": False, "error": "post not found"}
	
	if not request.state.user or post.author_id != request.state.user.id or not request.state.user.is_active:
		return {"ok": False, "error": "auth error"}
	
	query = update(Post).where(Post.id==data.post_id).values(title=data.title, text=data.text)
	post = await session.execute(query)
	await session.commit()
	return post


@router.delete("/posts")
async def delete_post(request: Request, data: PostDeleteSchema, session: SessionDep):
	query = select(Post).filter_by(id=data.post_id)
	post = await session.execute(query)
	post = post.scalars().first()
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not post:
		return {"ok": False, "error": "post not found"}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "auth error"}
	
	if post.author_id != request.state.user.id:
		return {"ok": False, "error": "permission denied"}
	
	query = update(Post).where(Post.id==post.id).values(is_deleted=True)
	await session.execute(query)
	await session.commit()
	return {"ok": True}


@router.get("/file/{filename}")
async def get_file(filename):
	return FileResponse(f"src/media/images/{filename}")


@router.get("/search")
async def get_posts(session: SessionDep, q: str):
    posts = await search_data(
        session=session,
        model=Post,
        search_fields=["title", "text"],
        query_text=q,
        limit=20,
        offset=0,
        extra_filters={"is_deleted": False},
        join_relations=["author"]  # если хочешь сразу подгрузить автора
    )#
    return posts

