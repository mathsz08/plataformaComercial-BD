import subprocess
import sys

import streamlit as st

from db_config import DB_CONFIG


def _pip(pkg):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    _pip("psycopg2-binary")
    import psycopg2
    import psycopg2.extras


@st.cache_resource
def get_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Erro de conexão: {e}")
        st.stop()

class DB:
    def __init__(self, conn):
        self.conn = conn

    def q(self, sql, p=(), fetch=True):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as c:
            c.execute(sql, p)
            if fetch:
                return c.fetchall()
            self.conn.commit()
            return c.rowcount

    def run(self, sql, p=()):
        try:
            return self.q(sql, p, fetch=False)
        except Exception as e:
            self.conn.rollback()
            raise e
