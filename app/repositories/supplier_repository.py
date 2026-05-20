from datetime import datetime
from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import Supplier


class SupplierRepository:
    def create(self, name: str, document: str, email: str, phone: str) -> Supplier:
        with SessionLocal() as session:
            supplier = Supplier(
                name=name,
                document=document,
                email=email,
                phone=phone
            )
            session.add(supplier)
            session.commit()
            session.refresh(supplier)
            return supplier

    def list_all(self) -> list[Supplier]:
        with SessionLocal() as session:
            return list(session.scalars(select(Supplier).order_by(Supplier.id.desc())))

    def update(
        self,
        supplier_id: int,
        name: str,
        document: str,
        email: str,
        phone: str
    ) -> None:
        with SessionLocal() as session:
            supplier = session.get(Supplier, supplier_id)

            if not supplier:
                raise ValueError("Fornecedor não encontrado.")

            supplier.name = name
            supplier.document = document
            supplier.email = email
            supplier.phone = phone
            supplier.updated_at = datetime.utcnow()

            session.commit()

    def delete(self, supplier_id: int) -> None:
        with SessionLocal() as session:
            supplier = session.get(Supplier, supplier_id)
            if supplier:
                session.delete(supplier)
                session.commit()