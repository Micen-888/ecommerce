from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from src.config import settings
from src.database import get_pg_engine, get_mongo_db

ROOT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"

EXPECTED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Customer_Name",
    "Customer_Segment",
    "Country",
    "Region",
    "Product_Category",
    "Product_Name",
    "Quantity",
    "Unit_Price",
    "Discount_Percent",
    "Total_Sales",
    "Shipping_Cost",
    "Profit",
    "Payment_Method",
]


def load_csv() -> pd.DataFrame:
    csv_path = Path(settings.csv_path)
    if not csv_path.is_absolute():
        csv_path = ROOT_DIR / csv_path

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[EXPECTED_COLUMNS].copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%m/%d/%Y", errors="raise")

    text_columns = [
        "Order_ID",
        "Customer_Name",
        "Customer_Segment",
        "Country",
        "Region",
        "Product_Category",
        "Product_Name",
        "Payment_Method",
    ]
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()

    numeric_columns = [
        "Quantity",
        "Unit_Price",
        "Discount_Percent",
        "Total_Sales",
        "Shipping_Cost",
        "Profit",
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="raise")

    if df["Order_ID"].duplicated().any():
        duplicated = df.loc[df["Order_ID"].duplicated(), "Order_ID"].head().tolist()
        raise ValueError(f"Duplicated Order_ID found: {duplicated}")

    return df


def reset_postgres_schema() -> None:
    engine = get_pg_engine()
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in schema_sql.split(";") if statement.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def load_postgres(df: pd.DataFrame) -> None:
    engine = get_pg_engine()

    customers = (
        df[["Customer_Name", "Customer_Segment", "Country", "Region"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(
            columns={
                "Customer_Name": "customer_name",
                "Customer_Segment": "customer_segment",
                "Country": "country",
                "Region": "region",
            }
        )
    )
    customers.insert(0, "customer_id", range(1, len(customers) + 1))

    products = (
        df[["Product_Category", "Product_Name", "Unit_Price"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(
            columns={
                "Product_Category": "product_category",
                "Product_Name": "product_name",
                "Unit_Price": "unit_price",
            }
        )
    )
    products.insert(0, "product_id", range(1, len(products) + 1))

    orders = df.merge(
        customers,
        left_on=["Customer_Name", "Customer_Segment", "Country", "Region"],
        right_on=["customer_name", "customer_segment", "country", "region"],
        how="left",
    ).merge(
        products,
        left_on=["Product_Category", "Product_Name", "Unit_Price"],
        right_on=["product_category", "product_name", "unit_price"],
        how="left",
    )

    orders = orders[
        [
            "Order_ID",
            "Order_Date",
            "customer_id",
            "product_id",
            "Quantity",
            "Total_Sales",
            "Profit",
        ]
    ].rename(
        columns={
            "Order_ID": "order_id",
            "Order_Date": "order_date",
            "Quantity": "quantity",
            "Total_Sales": "total_sales",
            "Profit": "profit",
        }
    )

    with engine.begin() as conn:
        customers.to_sql("customers", conn, if_exists="append", index=False)
        products.to_sql("products", conn, if_exists="append", index=False)
        orders.to_sql("orders", conn, if_exists="append", index=False)


def load_mongodb(df: pd.DataFrame) -> None:
    db = get_mongo_db()
    loaded_at = datetime.now(timezone.utc)

    db.transaction_logs.delete_many({})
    db.shipping_details.delete_many({})

    transaction_logs = []
    shipping_details = []

    for row in df.to_dict("records"):
        order_id = row["Order_ID"]
        transaction_logs.append(
            {
                "order_id": order_id,
                "payment": {
                    "method": row["Payment_Method"],
                },
                "pricing": {
                    "discount_percent": float(row["Discount_Percent"]),
                },
                "audit": {
                    "source": "global_ecommerce_sales.csv",
                    "loaded_at": loaded_at,
                },
            }
        )

        shipping_details.append(
            {
                "order_id": order_id,
                "destination": {
                    "country": row["Country"],
                    "region": row["Region"],
                },
                "shipping": {
                    "cost": float(row["Shipping_Cost"]),
                },
                "audit": {
                    "source": "global_ecommerce_sales.csv",
                    "loaded_at": loaded_at,
                },
            }
        )

    if transaction_logs:
        db.transaction_logs.insert_many(transaction_logs)
    if shipping_details:
        db.shipping_details.insert_many(shipping_details)

    db.transaction_logs.create_index("order_id", unique=True)
    db.transaction_logs.create_index("payment.method")
    db.transaction_logs.create_index("pricing.discount_percent")
    db.shipping_details.create_index("order_id", unique=True)
    db.shipping_details.create_index("destination.region")
    db.shipping_details.create_index("shipping.cost")


def run_etl() -> None:
    df = load_csv()
    reset_postgres_schema()
    load_postgres(df)
    load_mongodb(df)
    print("ETL completed successfully.")
    print(f"Rows loaded: {len(df):,}")
    print("PostgreSQL tables: customers, products, orders")
    print("MongoDB collections: transaction_logs, shipping_details")


if __name__ == "__main__":
    run_etl()
