from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta

from src.models.users import User, VerifyUser, Subscription, delete_not_verifed_user
from src.schemas.users import (
    UserRegisterSchema,
    UserLoginSchema,
    VerfiyCodeSchema,
    SubscriptionSchema,
    UserUpdateSchema,
    ChangeEmailSchema,
    ChangePasswordSchema
)
from src.database import select, update, delete, joinedload, new_session
from src.dependencies import SessionDep
from src.auth.security import (
    make_password,
    check_password,
    create_jwt_token,
    decode_jwt_token
)
from src.utils.send_email import send_verify_code
from src.utils.serializers import user_serializer
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
import asyncio, os

router = APIRouter()
load_dotenv()


@router.get("/users")
async def get_users(session: SessionDep):
	query = select(User)
	users = await session.execute(query)
	users = users.scalars().all() # scalars().unique().all() if joinedload, elss just scalars().all()
	# users = [user_serializer(i) for i in users]
	return users


@router.put("/users")
async def update_user(request: Request, data: UserUpdateSchema, session: SessionDep):
	user = request.state.user
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not user or not user.is_active:
		return {"ok": False, "error": "auth error"}
	
	db_user = select(User).where(User.username==data.username)
	db_user = await session.execute(db_user)
	db_user = db_user.scalars().first()
	if db_user:
		return {"ok": False, "error": f"username '{data.username}' already taked"}
	
	smtp = update(User).where(User.id==user.id).values(
	    username=data.username,
	    bio=data.bio,
	    username_changed_at=datetime.now()
	)
	await session.execute(smtp)
	await session.commit()
	return {"ok": True, "msg": "updated successfully"}


@router.post("/register")
async def register(data: UserRegisterSchema, session: SessionDep):
	query = select(User).where((User.username == data.username) | (User.email == data.email))
	user = await session.execute(query)
	user = user.scalars().first()
	if user:
		return {"ok": False, "error": "username or email already taked"}
	
	email_response = send_verify_code(data.email)
	if not email_response["ok"]:
		return {"ok": False, "error": email_response["error"]}
	
	user = User(
	    username=data.username,
	    password=make_password(data.password),
	    email=data.email,
	    is_staff=True if data.username == "shaxrux" else False
	)
	session.add(user)
	await session.commit()
	
	asyncio.create_task(delete_not_verifed_user(user.id))
	verify_user = VerifyUser(user=user.id, email=data.email, code=email_response["msg"])
	session.add(verify_user)
	await session.commit()
	
	return {"ok": True, "msg": f"code sent to {data.email}", "verify_id": verify_user.id}


@router.post("/verify_email")
async def verfiy_number(request: Request, data: VerfiyCodeSchema, session: SessionDep):
	query = select(VerifyUser).filter_by(id=data.verify_id)
	verify = await session.execute(query)
	verify = verify.scalars().first()
	
	if not verify or verify.is_verifed:
		return {"ok": False, "error": "uncorrect verify_id"}
	
	if datetime.now() > verify.created_at + timedelta(seconds=60):
		return {"ok": False, "error": "time"}
	
	if data.change_email:
		if not request.state.user or not request.state.user.is_active:
			return {"ok": False, "error": "permission denied"}
		
		if request.state.auth_error:
			return {"ok": False, "error": request.state.auth_error}
		
		if data.code != verify.code:
			return {"ok": False, "error": "uncorrect code"}
		
		query = update(User).where(User.id==request.state.user.id).values(email=verify.email)
		await session.execute(query)
		
		query = update(VerifyUser).where(VerifyUser.user==request.state.user.id).values(is_verifed=True)
		await session.execute(query)
		await session.commit()
		return {"ok": True, "msg": "email changed successfully"}
	
	query = select(User).filter_by(email=verify.email)
	user = await session.execute(query)
	user = user.scalars().first()
	if not user:
		return {"ok": False, "error": "user not found"}
	
	if data.code == verify.code:
		query = update(User).where(User.id==user.id).values(is_active=True)
		await session.execute(query)
		
		query = update(VerifyUser).where(VerifyUser.user==user.id).values(is_verifed=True)
		await session.execute(query)
		await session.commit()
		tokens = create_jwt_token(user.id)
		return {"ok": True, "msg": f"welcome {user.username}", "tokens": tokens}
	return {"ok": False, "error": "Uncorrect code"}


@router.post("/login")
async def login(data: UserLoginSchema, session: SessionDep):
	query = select(User).filter_by(username=data.username)
	user = await session.execute(query)
	user = user.scalars().first()
	if not user or not user.is_active:
		return {"ok": False, "error": "user not found"}
	
	if check_password(data.password, user.password):
		tokens = create_jwt_token(user.id)
		return tokens
	return {"ok": False, "error": "password didn't match"}


@router.get("/profile")
async def profile(request: Request, session: SessionDep):
	user = request.state.user
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not user:
		return {"ok": False, "error": "auth error"}
	
	smtp = select(User).where(User.id==user.id).options(joinedload(User.subscribers), joinedload(User.subscriptions), joinedload(User.posts))
	user = await session.execute(smtp)
	user = user_serializer(user.scalars().unique().first())
	return user


@router.post("/subscription")
async def subscription(request: Request, data: SubscriptionSchema, session: SessionDep):
	query = select(User).where(User.id==data.user_id)
	user = await session.execute(query)
	user = user.scalars().first()
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "permission denied"}
	
	if user.id == request.state.user.id:
		return {"ok": False, "error": "what??"}
	
	if not user or not user.is_active:
		return {"ok": False, "error": "user not found"}
	
	sub = select(Subscription).where(
	    Subscription.user_id==request.state.user.id,
	    Subscription.to_user_id==data.user_id
	)
	sub = await session.execute(sub)
	sub = sub.scalars().first()
	if sub:
		query = delete(Subscription).where(Subscription.id==sub.id)
		await session.execute(query)
		await session.commit()
		return {"ok": True, "msg": "subs was deleted"}
	
	sub = Subscription(user_id=request.state.user.id, to_user_id=user.id)
	session.add(sub)
	await session.commit()
	return {"ok": True, "msg": "subs was created"}


@router.post("/refresh")
async def refresh_token(request: Request):
	data = await request.json()
	refresh_token = data.get("refresh_token")
	if not refresh_token:
		return {"ok": False, "error": "refresh token missing"}
	
	data = decode_jwt_token(refresh_token, allow_refresh=True)
	if not data["ok"]:
		return {"ok": False, "error": data["error"]}
	
	tokens = create_jwt_token(user_id=data["data"]["sub"])
	return {"access_token": tokens["access_token"]}


@router.post("/change_email")
async def change_email(request: Request, data: ChangeEmailSchema, session: SessionDep):
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "permission denied"}
	
	query = select(User).where(User.email == data.email)
	user = await session.execute(query)
	user = user.scalars().first()
	if user and user.id == request.state.user.id:
		return {"ok": False, "error": "You already have this email"}
	
	if user:
		return {"ok": False, "error": "email already taked"}
	
	email_response = send_verify_code(data.email)
	if not email_response["ok"]:
		return {"ok": False, "error": email_response["error"]}
	
	verify_user = VerifyUser(user=request.state.user.id, email=data.email, code=email_response["msg"])
	session.add(verify_user)
	await session.commit()
	
	return {"ok": True, "msg": f"code sent to {data.email}", "verify_id": verify_user.id, "change_email": True}



@router.post("/change_password")
async def change_password(request: Request, data: ChangePasswordSchema, session: SessionDep):
	auth_error = request.state.auth_error
	if auth_error:
		return {"ok": False, "error": auth_error}
	
	if not request.state.user or not request.state.user.is_active:
		return {"ok": False, "error": "permission denied"}
	
	user = request.state.user
	if data.password:
		if check_password(data.password, user.password):
			query = update(User).where(User.id==user.id).values(password=make_password(data.new_password))
			await session.execute(query)
			await session.commit()
			return {"ok": True, "msg": "password changed successfully"}
		return {"ok": False, "error": "password didn't match"}
	
	elif data.email:
		email_response = send_verify_code(data.email)
		if not email_response["ok"]:
			return {"ok": False, "error": email_response["error"]}
		
		verify_user = VerifyUser(user=request.state.user.id, email=data.email, code=email_response["msg"])
		session.add(verify_user)
		await session.commit()
		return {"ok": True, "msg": f"code sent to {data.email}", "verify_id": verify_user.id, "change_email": True}
	
	elif data.code:
		if not data.verify_id or not data.new_password:
			return {"ok": False, "error": "verify_id and new_password are required with code"}
		
		query = select(VerifyUser).where(VerifyUser.id==data.verify_id)
		verify = await session.execute(query)
		verify = verify.scalars().first()
		if not verify or verify.is_verifed:
			return {"ok": False, "error": "uncorrect verify_id"}
		
		if datetime.now() > verify.created_at + timedelta(seconds=60):
			return {"ok": False, "error": "time"}
		
		if data.code == verify.code:
			query = update(VerifyUser).where(VerifyUser.id==data.verify_id).values(is_verifed=True)
			await session.execute(query)
			
			query = update(User).where(User.id==user.id).values(password=make_password(data.new_password))
			await session.execute(query)
			await session.commit()
			return {"ok": True, "msg": "password changed successfully"}
		return {"ok": False, "error": "uncorrect code"}
	return {"ok": False, "error": "send password and new_password, or email and then verify_id and code with new_password"}

