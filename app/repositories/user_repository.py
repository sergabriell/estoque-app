import re
import bcrypt
from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import User


class UserRepository:
    def _is_valid_email(self, email: str) -> bool:
        # Padrão básico para validar formato: texto@texto.texto
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    def create(self, full_name: str, email: str, username: str, password: str, role: str) -> User:
        # --- VALIDAÇÃO DE E-MAIL ---
        if not self._is_valid_email(email):
            raise ValueError("O formato do e-mail é inválido.")

        if len(password) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")

        with SessionLocal() as session:
            existing_user = session.scalars(
                select(User).where((User.username == username) | (User.email == email))
            ).first()

            if existing_user:
                raise ValueError("Usuário ou e-mail já cadastrado.")

            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            user = User(
                full_name=full_name,
                email=email,
                username=username,
                password=hashed_pw,
                role=role
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def list_all(self) -> list[User]:
        with SessionLocal() as session:
            stmt = select(User).order_by(User.id.desc())
            users = list(session.scalars(stmt))

            # Desconecta todos os usuários da sessão antes de fechar
            session.expunge_all()

            return users

    def update_profile(self, user_id: int, full_name: str, email: str, username: str, role: str,
                       new_password: str = None) -> User:
        # --- VALIDAÇÃO DE E-MAIL ---
        if not self._is_valid_email(email):
            raise ValueError("O formato do e-mail é inválido.")

        if new_password and len(new_password) < 6:
            raise ValueError("A nova senha deve ter pelo menos 6 caracteres.")

        with SessionLocal() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("Usuário não encontrado.")

            user.full_name = full_name
            user.email = email
            user.username = username
            user.role = role

            if new_password:
                user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            session.commit()
            session.refresh(user)
            return user

    def update_role(self, user_id: int, new_role: str) -> None:
        with SessionLocal() as session:
            user = session.get(User, user_id)
            if user:
                user.role = new_role
                session.commit()

    def delete(self, user_id: int) -> None:
        with SessionLocal() as session:
            user = session.get(User, user_id)
            if user:
                session.delete(user)
                session.commit()