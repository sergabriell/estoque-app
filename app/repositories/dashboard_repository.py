import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database.connection import SessionLocal
from app.database.models import Product, Supplier, StockMovement


class DashboardRepository:
    def get_products_dataframe(self) -> pd.DataFrame:
        with SessionLocal() as session:
            products = list(
                session.scalars(
                    select(Product).options(joinedload(Product.supplier))
                )
            )
            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku or "—",
                    "category": p.category or "—",
                    "supplier": p.supplier.name if p.supplier else "—",
                    "cost_price": p.cost_price,
                    "sale_price": p.sale_price,
                    "stock": p.stock,
                    "min_stock": p.min_stock,
                    "stock_value": p.cost_price * p.stock,
                    "is_low_stock": p.stock <= p.min_stock,
                }
                for p in products
            ]
            return pd.DataFrame(data)

    def get_supplier_count(self) -> int:
        with SessionLocal() as session:
            return len(list(session.scalars(select(Supplier))))

    def get_recent_movements(self, limit: int = 5):
        with SessionLocal() as session:
            stmt = (
                select(StockMovement)
                .options(joinedload(StockMovement.product))
                .order_by(StockMovement.id.desc())
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def get_metrics(self):
        df = self.get_products_dataframe()
        supplier_count = self.get_supplier_count()

        if df.empty:
            return {
                "total_products": 0,
                "total_suppliers": supplier_count,
                "total_items": 0,
                "total_stock_value": 0.0,
                "total_sale_value": 0.0,
                "low_stock_count": 0,
                "df": df,
                "low_stock_df": pd.DataFrame(),
            }

        df["sale_value"] = df["sale_price"] * df["stock"]

        return {
            "total_products": len(df),
            "total_suppliers": supplier_count,
            "total_items": int(df["stock"].sum()),
            "total_stock_value": float(df["stock_value"].sum()),
            "total_sale_value": float(df["sale_value"].sum()),
            "low_stock_count": int(df["is_low_stock"].sum()),
            "df": df,
            "low_stock_df": df[df["is_low_stock"]].copy(),
        }
