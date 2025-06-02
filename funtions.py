from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import polars as pl
import pandas as pd
import psycopg2
import os
import requests
#class data_configuration():
def get_database_connection():
    try:
        load_dotenv(".env")
        DB_HOST = os.environ.get("DB_HOST")
        DB_PORT = os.environ.get("DB_PORT")
        DB_NAME = os.environ.get("DB_NAME")
        DB_USER = os.environ.get("DB_USER")
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        
        engine = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        return engine
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

@st.cache_data(
    ttl=3600,
    show_spinner="Loading data...",
    max_entries=1
)
def process_data(*args):    
    try:
        API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
        response = requests.get(f"{API_BASE_URL}/data_purchases_df")
        
        if response.status_code != 200:
            st.error("Failed to fetch data from API")
            return None, None
            
        # Convert JSON response to Polars DataFrame
        purchases_df = pl.DataFrame(response.json()["purchases"])
        types = pl.DataFrame(response.json()["types"])
        
        if len(args) > 2:
            if args[0]:
                purchases_df = purchases_df.filter(pl.col("month").is_in(args[0]))
            if args[1]:
                purchases_df = purchases_df.filter(pl.col("type").is_in(args[1]))
            if args[2]:
                purchases_df = purchases_df.filter(pl.col("type_payment").is_in(args[2]))
                
        return purchases_df, types
    except Exception as e:
        st.error(f"API request error: {str(e)}")
        return None, None

def types_barchart(purchases_df):
    try:
        if purchases_df is None:
            return None, "$0.00"
            
        purchases_df = purchases_df.group_by("type").agg(
            pl.col("value").sum().alias("Total")
        )
        purchases_df = purchases_df.rename({"type": "Tipo"})
        type_purchases_df = purchases_df.with_columns(
            pl.col("Total").cast(pl.Float64).round(2).map_elements(lambda x: f"${x:,.2f}", return_dtype=pl.String)
        )
        Total = purchases_df["Total"].sum()
        Total = f"${Total:,.2f}"
        return type_purchases_df, Total
    except Exception as e:
        st.error(f"Bar chart processing error: {str(e)}")
        return None, "$0.00"

def max_spent_data(purchases_df, types_df):
    try:
        if purchases_df is None or types_df is None:
            return None, "$0.00"
            
        max_spent_df = purchases_df.group_by("type").agg(
            pl.col("value").sum().alias("Total"),
            pl.col("max_spent").alias("Gasto maximo permitido").unique().first(),
        )
        max_spent_df = max_spent_df.rename({"type": "Tipo"})
        max_permitted_spend = types_df["max_spent"].sum()
        max_permitted_spend = f"${max_permitted_spend:,.2f}"
        return max_spent_df, max_permitted_spend
    except Exception as e:
        st.error(f"Max spent calculation error: {str(e)}")
        return None, "$0.00"

def purchases_table(purchases_df):
    try:
        if purchases_df is None:
            return None
            
        purchases_df = purchases_df.drop('total_payment', 'max_spent', 'month')
        purchases_df = purchases_df.rename({
            "type": "Tipo de gasto", 
            "establishment": "Establecimiento", 
            "type_payment": "Forma de pago", 
            "value": "Valor", 
            "created_on": "Fecha", 
            "name": "Descripción", 
            "quantity": "Cantidad"
        })
        purchases_df = purchases_df.select([
            "Descripción", "Establecimiento", "Forma de pago", 
            "Tipo de gasto", "Valor", "Cantidad", "Fecha"
        ])
        return purchases_df
    except Exception as e:
        st.error(f"Table processing error: {str(e)}")
        return None