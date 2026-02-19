from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable
import time

from jose import jwt, JWTError, ExpiredSignatureError
from src.database import select, new_session, joinedload
from src.models.users import User
from src.dependencies import SessionDep
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class CheckRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start = time.perf_counter()
        '''
        print(f"🛡️ [MIDDLEWARE:{request.url}] Start request for {request.client.host}")

        print("--"*20, "\n\n")
        '''
        response = await call_next(request)
        '''
        print("\n\n", "--"*20)

        end = time.perf_counter() - start
        print(f"🛡️ [MIDDLEWARE:{request.url}] End request for {request.client.host}")
        print(f"🛡️ [MIDDLEWARE:{request.url}] Request time {end:.2f}")
        '''
        return response


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        return AuthCredentials(["authenticated"]), SimpleUser("guest")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None  # по дефолту
        request.state.auth_error = None

        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]
            
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                
                async with new_session() as session:
                	query = select(User).filter_by(id=user_id)
                	user = await session.execute(query)
                	user = user.scalars().first()
                	if user and not user.is_active:
                		user = None
                
                request.state.user = user
                request.state.auth_error = None
             
            except ExpiredSignatureError:
            	request.state.auth_error = "Token Expired"
            
            except JWTError as e:
                print (e)
                request.state.auth_error = "Invalid Token"

        response = await call_next(request)
        return response


class GetMeMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next: Callable, session=SessionDep):
		response = await call_next(request)
		'''
		# TEST MIDDLEWARE
		query = select(UserModel).filter_by(id=request.state.user)
		user = await session.execute(query)
		user = user.scalars().first()
		'''
		
		return response


