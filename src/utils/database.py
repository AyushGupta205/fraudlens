import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from src.utils.config import DATABASE_PATH, DATABASE_URL
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def get_engine():
    return create_engine(DATABASE_URL)

def execute_query(query: str, params=None) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()

def execute_script(script_path: str):
    conn = get_db_connection()
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        cursor = conn.cursor()
        cursor.executescript(sql_content)
        conn.commit()
        logger.info(f'Executed SQL script: {script_path}')
    finally:
        conn.close()
