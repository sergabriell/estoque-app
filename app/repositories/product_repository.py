from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import Product

class ProductRepository:
    def create(self, name: str, sku: str, price: float, stock: int) -> Product:
        with SessionLocal() as session:
            product = Product(name=name, sku=sku, price=price, stock=stock)
            session.add(product)
            session.commit()
            session.refresh(product)
            return product

    def list_all(self) -> list[Product]:
        with SessionLocal() as session:
            return list(session.scalars(select(Product).order_by(Product.id.desc())))

    def delete(self, product_id: int) -> None:
        with SessionLocal() as session:
            product = session.get(Product, product_id)
            if product:
                session.delete(product)
                session.commit()
