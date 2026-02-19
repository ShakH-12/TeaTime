from src.database import (
    Base, Mapped,
    mapped_column,
    DateTime, func,
    ForeignKey, relationship,
    new_session, delete, select
)
from datetime import datetime
import asyncio


class User(Base):
	__tablename__ = "users"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	username: Mapped[str]
	password: Mapped[str]
	bio: Mapped[str | None]
	email: Mapped[str]
	is_active: Mapped[bool] = mapped_column(default=False)
	is_staff: Mapped[bool] = mapped_column(default=False)
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
	username_changed_at: Mapped[datetime] = mapped_column(
	    DateTime(timezone=True),
	    server_default=func.now()
	)
	
	posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete")
	comments: Mapped[list["PostComment"]] = relationship(back_populates="user", cascade="all, delete")
	subscriptions: Mapped[list["Subscription"]] = relationship(foreign_keys="Subscription.user_id", back_populates="user", cascade="all, delete")
	subscribers: Mapped[list["Subscription"]] = relationship(foreign_keys="Subscription.to_user_id", back_populates="to_user", cascade="all, delete")


class VerifyUser(Base):
	__tablename__ = "verify users"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	user: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
	email: Mapped[str]
	code: Mapped[int]
	is_verifed: Mapped[bool] = mapped_column(default=False)
	created_at: Mapped[datetime] = mapped_column(
	    DateTime(timezone=True),
	    server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
	    DateTime(timezone=True),
	    server_default=func.now(),
	    onupdate=func.now()
	)


class Subscription(Base):
	__tablename__ = "subscribes"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
	to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
	created_at: Mapped[datetime] = mapped_column(
	    DateTime(timezone=True),
	    server_default=func.now()
	)
	
	user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="subscriptions")
	to_user: Mapped["User"] = relationship(foreign_keys=[to_user_id], back_populates="subscribers")


async def delete_not_verifed_user(user_id):
	async with new_session() as session:
		await asyncio.sleep(60)
		query = select(VerifyUser).where(VerifyUser.user==user_id)
		user = await session.execute(query)
		user = user.scalars().first()
		
		if user.is_verifed:
			print(f"\nUSER {user.id} WAS NOT DELETED, BECAUSE IS VERIFED")
			return {"ok": False, "error": "user already verifed"}
		
		query = delete(User).where(User.id==user_id)
		await session.execute(query)
		await session.commit()
		print(f"\nUSER {user.id} WAS DELETED, BECAUSE IS NOT VERIFED")
		return {"ok": True, "msg": "user deleted successfully"}


