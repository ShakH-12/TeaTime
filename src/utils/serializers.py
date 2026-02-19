def user_serializer(data):
	return {
	    "username": data.username,
	    "bio": data.bio,
	    "is_active": data.is_active,
	    "is_staff": data.is_staff,
	    "is_deleted": data.is_deleted,
	    "email": data.email,
	    "created_at": data.created_at,
	    "updated_at": data.updated_at,
	    "username_changed_at": data.username_changed_at,
	    "posts": data.posts if data.posts else [],
	    "subscribers": data.subscribers if data.subscribers else [],
	    "subscriptions": data.subscriptions if data.subscriptions else []
	}