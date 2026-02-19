from pydantic import BaseModel, Field


class PostPutSchema(BaseModel):
	post_id: int = Field(ge=0)
	title: str = Field(max_length=32)
	text: str


class PostDeleteSchema(BaseModel):
	post_id: int = Field(ge=0)


class PostLikeSchema(BaseModel):
	post_id: int = Field(ge=0)


class PostCommentSchema(BaseModel):
	post_id: int = Field(ge=0)
	text: str


class PostCommentUpdateSchema(BaseModel):
	comment_id: int = Field(ge=0)
	text: str


class PostCommentDeleteSchema(BaseModel):
	comment_id: int = Field(ge=0)


