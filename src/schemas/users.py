from pydantic import BaseModel, Field, EmailStr


class UserRegisterSchema(BaseModel):
	username: str = Field(min_length=3, max_length=32)
	password: str = Field(min_length=3, max_length=32)
	email: EmailStr


class UserLoginSchema(BaseModel):
	username: str = Field(min_length=3, max_length=32)
	password: str = Field(min_length=3, max_length=32)


class UserUpdateSchema(BaseModel):
	username: str = Field(min_length=3, max_length=32)
	bio: str = Field(min_length=10, max_length=1000)


class UserSchema(UserLoginSchema):
	id: int = Field(ge=0)
	bio: str = Field(max_length=1000)
	is_active: bool
	is_deleted: bool
	created_at: str


class VerfiyCodeSchema(BaseModel):
	verify_id: int = Field(ge=0)
	code: int
	change_email: bool = Field(default=None)


class SubscriptionSchema(BaseModel):
	user_id: int = Field(ge=0)


class ChangeEmailSchema(BaseModel):
	email: EmailStr


class ChangePasswordSchema(BaseModel):
	new_password: str = Field(min_length=3)
	password: str = Field(min_length=3, default=None)
	email: EmailStr = Field(default=None)
	code: int = Field(default=None)
	verify_id: int = Field(default=None)

