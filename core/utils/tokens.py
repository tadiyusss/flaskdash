from itsdangerous import BadSignature, URLSafeTimedSerializer, SignatureExpired
from flask import current_app
from core.models.users import User

def generate_reset_token(user):

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )
    return serializer.dumps({"user_id": user.id, "password_hash": user.password}, salt=current_app.config["SECRET_KEY"])

def verify_reset_token(token, expiration=3600):

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )
    try:

        data = serializer.loads(
            token,
            salt=current_app.config["SECRET_KEY"],
            max_age=expiration
        )
        user = User.query.get(data["user_id"])
        
        if not user:
            return None

        if user.password != data["password_hash"]:
            return None

        return user

    except (SignatureExpired, BadSignature):
        return None
    