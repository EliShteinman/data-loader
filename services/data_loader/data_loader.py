import mysql.connector
from mysql.connector import Error


class DataLoader:
    """
    שכבת הגישה לנתונים (Data Access Layer - DAL).
    קלאס זה אחראי על כל התקשורת הישירה עם מסד הנתונים MySQL.
    """

    def __init__(self, host, user, password, database):
        """
        אתחול האובייקט עם פרטי הגישה למסד הנתונים.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None # אתחול החיבור כ-None. הוא ייווצר בפונקציית connect.

    def connect(self):
        """
        יצירת חיבור למסד הנתונים של MySQL.
        """
        try:
            # שימוש בספריית mysql-connector כדי ליצור את אובייקט החיבור.
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Successfully connected to MySQL database")
        except Error as e:
            # במקרה של כשל, נדפיס שגיאה ונשאיר את החיבור כ-None.
            print(f"Error while connecting to MySQL: {e}")
            self.connection = None

    def get_all_data(self):
        """
        שליפת כל הרשומות מטבלת 'data'.
        """
        # בדיקה שהחיבור קיים ותקין. אם לא, מנסים להתחבר מחדש.
        if not self.connection or not self.connection.is_connected():
            print("No connection to database. Attempting to reconnect...")
            self.connect()
            if not self.connection:
                return {"error": "Could not connect to the database."}

        # יצירת 'סמן' (cursor) שיאפשר לנו להריץ שאילתות.
        # dictionary=True גורם לתוצאות לחזור כמילון (dict) ולא כ-tuple.
        cursor = self.connection.cursor(dictionary=True)
        try:
            # הרצת שאילתת SQL פשוטה.
            cursor.execute("SELECT * FROM data")
            # שליפת כל התוצאות מה-cursor.
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error reading data from MySQL table: {e}")
            return {"error": str(e)}
        finally:
            # חשוב מאוד לסגור את ה-cursor בסיום הפעולה כדי לשחרר משאבים.
            cursor.close()