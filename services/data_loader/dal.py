import mysql.connector
from mysql.connector import pooling, Error
from .models import ItemCreate


class DataLoader:
    """
    Data Access Layer (DAL).
    This class is responsible for all direct communication with the MySQL database,
    using a connection pool for enhanced performance and reliability.
    """

    def __init__(self, host, user, password, database):
        """
        Initializes the DataLoader with database configuration for the pool.
        """
        self.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }
        self.pool = None

    def connect(self):
        """
        Creates a MySQL connection pool.
        """
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="fastapi_pool",
                pool_size=5,  # Number of connections to keep ready
                **self.db_config,
            )
            print("Successfully created MySQL connection pool")
        except Error as e:
            print(f"Error while creating connection pool: {e}")
            self.pool = None

    def close(self):
        """
        Connection pool management is handled by its lifecycle.
        No explicit close action is needed for the pool itself.
        """
        print("Connection pool lifecycle is managed automatically.")

    def get_all_data(self):
        """
        Fetches all records from the 'data' table using a connection from the pool.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        connection = None
        try:
            # Get a ready connection from the pool
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM data")
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error reading data from MySQL table: {e}")
            return {"error": str(e)}
        finally:
            # Always close the cursor and return the connection to the pool
            if connection and connection.is_connected():
                # For a pool, connection.close() returns it to the pool, it doesn't close it.
                connection.close()

    def get_item_by_id(self, item_id: int):
        """
        Fetches a single record by its ID.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        query = "SELECT * FROM data WHERE ID = %s"
        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error fetching item by ID: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def create_item(self, item: ItemCreate):
        """
        Creates a new record and returns it with the new ID.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        query = "INSERT INTO data (first_name, last_name) VALUES (%s, %s)"
        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (item.first_name, item.last_name))
            connection.commit()
            new_id = cursor.lastrowid
            return {"ID": new_id, **item.model_dump()}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error creating item: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def update_item(self, item_id: int, item: ItemCreate):
        """
        Updates an existing record.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        query = "UPDATE data SET first_name = %s, last_name = %s WHERE ID = %s"
        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (item.first_name, item.last_name, item_id))
            connection.commit()
            if cursor.rowcount == 0:
                return None  # No record found to update
            return {"ID": item_id, **item.model_dump()}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error updating item: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()

    def delete_item(self, item_id: int):
        """
        Deletes an existing record.
        """
        if not self.pool:
            return {"error": "Connection pool is not available."}

        query = "DELETE FROM data WHERE ID = %s"
        connection = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (item_id,))
            connection.commit()
            if cursor.rowcount == 0:
                return None  # No record found to delete
            return {"message": "Item deleted successfully"}
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error deleting item: {e}")
            return {"error": str(e)}
        finally:
            if connection and connection.is_connected():
                connection.close()
