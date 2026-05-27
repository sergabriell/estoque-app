from sqlalchemy import text, inspect as sa_inspect
from app.database.connection import Base, engine
from app.database import models  # noqa: F401


def _migrate_sku_nullable() -> None:
    """Garante que a coluna sku em products aceite NULL (migração SQLite)."""
    inspector = sa_inspect(engine)
    if "products" not in inspector.get_table_names():
        return

    columns = {col["name"]: col for col in inspector.get_columns("products")}
    sku_col = columns.get("sku")

    if sku_col is None or sku_col.get("nullable", True):
        return

    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        conn.execute(text("""
            CREATE TABLE products_new (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                sku VARCHAR(60) UNIQUE,
                category VARCHAR(80),
                cost_price FLOAT NOT NULL,
                sale_price FLOAT NOT NULL,
                stock INTEGER NOT NULL,
                min_stock INTEGER NOT NULL,
                supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        conn.execute(text("INSERT INTO products_new SELECT * FROM products"))
        conn.execute(text("DROP TABLE products"))
        conn.execute(text("ALTER TABLE products_new RENAME TO products"))
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _migrate_sku_nullable()
