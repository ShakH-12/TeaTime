from authx import AuthX, AuthXConfig
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()
ALGORITHM = "HS256"

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = os.getenv("JWT_ACCESS_COOKIE_NAME")
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def make_password(password: str) -> str:
    return pwd_context.hash(password)

def check_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

