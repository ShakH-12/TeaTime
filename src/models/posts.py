from src.database import (
    Base, Mapped,
    mapped_column,
    DateTime, func,
    ForeignKey, relationship
)
from datetime import datetime


class Post(Base):
	__tablename__ = "posts"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
	image: Mapped[str]
	title: Mapped[str]
	text: Mapped[str]
	is_active: Mapped[bool] = mapped_column(default=True)
	is_deleted: Mapped[bool] = mapped_column(default=False)
	created_at: Mapped[datetime] = mapped_column(
	   DateTime(timezone=True),
	   server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
	    DateTime(timezone=True),
	    server_default=func.now(),
	    onupdate=func.now()
	)
	
	author: Mapped["User"] = relationship(back_populates="posts")


class PostLike(Base):
	__tablename__ = "post likes"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	user: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
	post: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
	created_at: Mapped[datetime] = mapped_column(
	   DateTime(timezone=True),
	   server_default=func.now()
	)


class PostComment(Base):
	__tablename__ = "post comments"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
	post: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
	text: Mapped[str]
	is_deleted: Mapped[bool] = mapped_column(default=False)
	created_at: Mapped[datetime] = mapped_column(
	   DateTime(timezone=True),
	   server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
	    DateTime(timezone=True),
	    server_default=func.now(),
	    onupdate=func.now()
	)
	user: Mapped["User"] = relationship(back_populates="comments")
