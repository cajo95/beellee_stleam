from sqlalchemy import create_engine
from datetime import datetime
import streamlit as st
import polars as pl
import pandas as pd
import psycopg2

#class data_configuration():
def get_database_connection():
    connection_params = {
        'host': '127.0.0.1:5432',
        'database': 'beellee_dev',
        'user': 'postgres',
        'password': '950221'
    }
    
    engine = f'postgresql://{connection_params["user"]}:{connection_params["password"]}@{connection_params["host"]}/{connection_params["database"]}'
    return engine
@st.cache_data(
    ttl=3600,  # Cache for 1 hour
    show_spinner="Loading data...",  # Shows a loading message
    max_entries=1  # Limits cache to most recent execution
)
def process_data(*args):    
    engine = get_database_connection()
    purchases = pl.read_database_uri(query='SELECT * FROM purchases', uri=engine)
    items = pl.read_database_uri(query='SELECT * FROM items', uri=engine)
    types = pl.read_database_uri(query='SELECT * FROM types', uri=engine)
    type_payment = pl.read_database_uri(query='SELECT * FROM type_payment', uri=engine)
    
    purchases_df = purchases.join(
        type_payment,
        left_on="type_payment_id",
        right_on="id",
        how="left"
    )

    items_df = items.join(
        types,
        left_on="type_id",
        right_on="id",
        how="left"
    )
    drop_list = ['type_payment_id', 'invoice_B64', 'created_on', 'user_code_right', 'is_active', 'created_on_right']
    purchases_df = purchases_df.drop(drop_list)
    purchases_df = purchases_df.rename({"name": "type_payment"})
    purchases_df = purchases_df.join(items_df, on="purchase_code", how="inner")
    purchases_df = purchases_df.rename({"name_right": "type"})
    purchase_drop_list = ['id', 'user_code', 'purchase_code', 'id_right', 'type_id', 'user_code_right', 'is_active', 'number_items']
    purchases_df = purchases_df.drop(purchase_drop_list)
    purchases_df = purchases_df.with_columns(
        pl.col("created_on").dt.month().alias("month")
    )
    if len(args) > 2:

        if args[0]:
            purchases_df = purchases_df.filter(pl.col("month").is_in(args[0]))
        if args[1]:
            purchases_df = purchases_df.filter(pl.col("type").is_in(args[1]))
        if args[2]:
            purchases_df = purchases_df.filter(pl.col("type_payment").is_in(args[2]))
    else:
        pass

    return purchases_df, types

def types_barchart(purchases_df):
    purchases_df = purchases_df.group_by("type").agg(
        pl.col("value").sum().alias("Total")
    )
    purchases_df = purchases_df.rename({"type": "Tipo"})
    # Format total_payment as currency
    type_purchases_df = purchases_df.with_columns(
        pl.col("Total").cast(pl.Float64).round(2).map_elements(lambda x: f"${x:,.2f}", return_dtype=pl.String)
    )
    Total = purchases_df["Total"].sum()
    Total = f"${Total:,.2f}"
    return type_purchases_df, Total

def max_spent_data(purchases_df, types_df):

    max_spent_df = purchases_df.group_by("type").agg(
        #pl.col("quantity").sum(),
        pl.col("value").sum().alias("Total"),
        pl.col("max_spent").alias("Gasto maximo permitido").unique().first(),
    )
    max_spent_df = max_spent_df.rename({"type": "Tipo"})
    max_permitted_spend = types_df["max_spent"].sum()
    max_permitted_spend = f"${max_permitted_spend:,.2f}"

    return max_spent_df, max_permitted_spend

def purchases_table(purchases_df):
    # REORGANIZAR LA TABLA purchases_df Y RETORNAR LAS COLUMNAS NECESARIAS.
    return purchases_df