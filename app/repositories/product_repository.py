from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database.connection import SessionLocal
from app.database.models import Product


class ProductRepository:
    def create(
        self,
        name: str,
        sku: str,
        category: str,
        cost_price: float,
        sale_price: float,
        stock: int,
        min_stock: int,
        supplier_id: int
    ) -> Product:
        with SessionLocal() as session:
            product = Product(
                name=name,
                sku=sku,
                category=category,
                cost_price=cost_price,
                sale_price=sale_price,
                stock=stock,
                min_stock=min_stock,
                supplier_id=supplier_id
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            return product

    def list_all(self) -> list[Product]:
        with SessionLocal() as session:
            stmt = (
                select(Product)
                .options(joinedload(Product.supplier))
                .order_by(Product.id.desc())
            )
            return list(session.scalars(stmt))

    def delete(self, product_id: int) -> None:
        with SessionLocal() as session:
            product = session.get(Product, product_id)
            if product:
                session.delete(product)
                session.commit()