import os
import mysql
import mysql.connector


config = {
    "host": os.getenv("DATABASE_HOST"),
    "port": 3306,
    "user": os.getenv("DATABASE_USER", "root"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
    "database": os.getenv("DATABASE_NAME", "eagleEyeDB"),
}