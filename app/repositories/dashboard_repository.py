import pandas as pd
from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import Product


class DashboardRepository:
    def get_products_dataframe(self) -> pd.DataFrame:
        with SessionLocal() as session:
            products = list(session.scalars(select(Product)))

            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
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

    def get_metrics(self):
        df = self.get_products_dataframe()

        if df.empty:
            return {
                "total_products": 0,
                "total_items": 0,
                "total_stock_value": 0,
                "low_stock_count": 0,
                "df": df,
            }

        return {
            "total_products": len(df),
            "total_items": int(df["stock"].sum()),
            "total_stock_value": float(df["stock_value"].sum()),
            "low_stock_count": int(df["is_low_stock"].sum()),
            "df": df,
        }