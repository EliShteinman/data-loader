import mysql.connector
from mysql.connector import Error

class DataLoader:
    """
    שכבת הגישה לנתונים (Data Access Layer - DAL).
    קלאס זה אחראי על כל התקשורת הישירה עם מסד הנתונים MySQL.
    """

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        יצירת חיבור למסד הנתונים של MySQL.
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
            self.connection = None

    # מתודה לסגירת חיבור מסודרת
    def close(self):
        """
        סוגר את החיבור למסד הנתונים אם הוא קיים ופתוח.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def get_all_data(self):
        """
        שליפת כל הרשומות מטבלת 'data'.
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
            if cursor:
                cursor.close()