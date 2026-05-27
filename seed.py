from app.database.connection import SessionLocal
from app.database.init_db import init_db
from app.database.models import User
import bcrypt

init_db()


def create_admin():
    with SessionLocal() as session:
        if not session.query(User).first():
            hashed = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            admin = User(
                full_name="Sérgio Administrador",
                email="sergio@armazem4irmaos.com",
                username="admin",
                password=hashed,
                role="GERENTE"
            )
            session.add(admin)
            session.commit()
            print("Usuário administrador criado com sucesso!")


if __name__ == "__main__":
    create_admin()