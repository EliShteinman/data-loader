import mysql.connector
from mysql.connector import Error


class DataLoader:
    """
    Data Access Layer (DAL) for connecting to MySQL and fetching data.
    This class handles all direct database interactions.
    """

    def __init__(self, host, user, password, database):
        """
        Initializes the DataLoader with database connection credentials.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the MySQL database.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            self.connection = None  # Ensure connection is None if it fails

    def get_all_data(self):
        """
        Fetches all records from the 'data' table.
        """
        if not self.connection or not self.connection.is_connected():
            print("No connection to database. Attempting to reconnect...")
            self.connect()
            if not self.connection:
                return {"error": "Could not connect to the database."}

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM data")
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error reading data from MySQL table: {e}")
            return {"error": str(e)}
        finally:
            cursor.close()
            # In a real app, you might manage connection closing more carefully.
            # For this service, we can keep it open or close it.
            # self.connection.close()