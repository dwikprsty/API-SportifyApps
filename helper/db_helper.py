"""DB Helper"""
import os
from mysql.connector.pooling import MySQLConnectionPool

# DB_HOST = os.environ.get('DB_HOST')
# DB_NAME = os.environ.get('DB_NAME')
# DB_USER = os.environ.get('DB_USER')
# DB_PASSWORD = os.environ.get('DB_PASSWORD')
# DB_POOLNAME = os.environ.get('DB_POOLNAME')
# # POOL_SIZE = int(os.environ.get('POOL_SIZE'))
# POOL_SIZE = int(os.getenv('POOL_SIZE', 5))


db_pool = MySQLConnectionPool(
    host='localhost',          # Your DB host, e.g., 'localhost'
    user='root',               # Your DB user, e.g., 'root'
    password='',               # Your DB password, e.g., ''
    database='sportify',       # Your DB name, e.g., 'sportify'
    pool_size=15,               # Pool size, e.g., 5
    pool_name='pool_sportify'  # Pool name, e.g., 'pool_sportify'
    
)

def get_connection():
    """
    Get connection db connection from db pool
    """
    connection = db_pool.get_connection()
    connection.autocommit = True
    return connection
