import bcrypt
from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import User


class AuthRepository:
    def authenticate(self, username: str, password: str) -> User | None:
        with SessionLocal() as session:
            stmt = select(User).where(User.username == username)
            user = session.scalars(stmt).first()

            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                session.expunge(user)
                return user
            return None