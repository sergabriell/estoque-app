from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import Product, StockMovement


class StockMovementRepository:
    def create(self, product_id: int, movement_type: str, quantity: int):
        with SessionLocal() as session:
            product = session.get(Product, product_id)

            if not product:
                raise ValueError("Produto não encontrado.")

            if quantity <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")

            if movement_type == "SAIDA":
                if product.stock < quantity:
                    raise ValueError("Estoque insuficiente para saída.")
                product.stock -= quantity

            elif movement_type == "ENTRADA":
                product.stock += quantity

            else:
                raise ValueError("Tipo de movimentação inválido.")

            movement = StockMovement(
                product_id=product_id,
                movement_type=movement_type,
                quantity=quantity
            )

            session.add(movement)
            session.commit()
            session.refresh(movement)
            return movement

    def list_all(self):
        with SessionLocal() as session:
            return list(
                session.scalars(
                    select(StockMovement).order_by(StockMovement.id.desc())
                )
            )