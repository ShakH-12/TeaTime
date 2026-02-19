from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def make_password(password) -> str:
	return pwd.hash(password)

def check_password(password, hashed_password) -> bool:
	return pwd.verify(password, hashed_password)

def create_jwt_token(user_id) -> dict:
	if not key:
		raise ValueError("SECRET KEY not set")
	
	if not algorithm:
		raise ValueError("ALGORITHM not set")
	
	payload = {
	    "sub": str(user_id),
	    "exp": datetime.utcnow()+timedelta(minutes=10),
	    "iat": datetime.utcnow(),
	    "type": "access",
	    # "nbf": datetime.utcnow()+timedelta(seconds=1),
	    "iss": "shaxcoder"
	}
	refresh_payload = {
	    "sub": str(user_id),
	    "type": "refresh",
	    "exp": datetime.utcnow()+timedelta(days=30)
	}
	
	access_token = jwt.encode(payload, key, algorithm=algorithm)
	refresh_token = jwt.encode(refresh_payload, key, algorithm=algorithm)
	return {"access_token": access_token, "refresh_token": refresh_token}

def decode_jwt_token(token, allow_refresh=False) -> dict:
	if not key:
		raise ValueError("SECRET KEY not set")
	
	if not algorithm:
		raise ValueError("ALGORITHM not set")
	
	try:
		data = jwt.decode(token, key=key, algorithms=[algorithm]) # специально не добавил algorithm=[algorithm]
		if data.get("type") != "access" and not allow_refresh:
			return {"ok": False, "error": "Wrong token type"}
		
		return {"ok": True, "data": data}
	
	except ExpiredSignatureError:
		return {"ok": False, "error": "Token Expired"}
	
	except JWTError as e:
		return {"ok": False, "error": "Invalid Token"}

