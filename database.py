import sqlite3
import hashlib
import os

DB_FILENAME = os.path.join(os.path.dirname(__file__), "finance.db")

class Database:
    def __init__(self, db_name=None):
        self.db_name = db_name or DB_FILENAME
        self.conn = sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        q_users = (
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "username TEXT UNIQUE NOT NULL,"
            "password TEXT NOT NULL"
            ")"
        )
        q_transactions = (
            "CREATE TABLE IF NOT EXISTS transactions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER NOT NULL,"
            "type TEXT NOT NULL,"
            "category TEXT NOT NULL,"
            "amount REAL NOT NULL,"
            "date TEXT NOT NULL,"
            "note TEXT,"
            "FOREIGN KEY(user_id) REFERENCES users(id)"
            ")"
        )
        q_budgets = (
            "CREATE TABLE IF NOT EXISTS budgets ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER NOT NULL,"
            "category TEXT NOT NULL,"
            "monthly_limit REAL NOT NULL,"
            "UNIQUE(user_id, category),"
            "FOREIGN KEY(user_id) REFERENCES users(id)"
            ")"
        )
        self.conn.execute(q_users)
        self.conn.execute(q_transactions)
        self.conn.execute(q_budgets)
        self.conn.commit()

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> bool:
        try:
            self.conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                              (username, self.hash_password(password)))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username: str, password: str):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=? AND password=?",
                    (username, self.hash_password(password)))
        row = cur.fetchone()
        return row["id"] if row else None

    def add_transaction(self, user_id:int, t_type:str, category:str, amount:float, date:str, note:str=None):
        self.conn.execute(
            "INSERT INTO transactions (user_id, type, category, amount, date, note) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, t_type, category, amount, date, note)
        )
        self.conn.commit()

    def update_transaction(self, trans_id:int, user_id:int, **kwargs):
        allowed = ['type','category','amount','date','note']
        fields = []
        vals = []
        for k,v in kwargs.items():
            if k in allowed:
                fields.append(f"{k}=?")
                vals.append(v)
        if not fields:
            return False
        vals.extend([trans_id, user_id])
        q = "UPDATE transactions SET " + ", ".join(fields) + " WHERE id=? AND user_id=?"
        self.conn.execute(q, vals)
        self.conn.commit()
        return True

    def delete_transaction(self, trans_id:int, user_id:int):
        self.conn.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (trans_id, user_id))
        self.conn.commit()

    def get_transactions(self, user_id:int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
        return cur.fetchall()

    def get_transaction(self, trans_id:int, user_id:int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE id=? AND user_id=?", (trans_id, user_id))
        return cur.fetchone()

    def set_budget(self, user_id:int, category:str, monthly_limit:float):
        self.conn.execute("INSERT OR REPLACE INTO budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)",
                          (user_id, category, monthly_limit))
        self.conn.commit()

    def get_budgets(self, user_id:int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM budgets WHERE user_id=?", (user_id,))
        return cur.fetchall()

    def get_budget_for_category(self, user_id:int, category:str):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM budgets WHERE user_id=? AND category=?", (user_id, category))
        return cur.fetchone()

    def monthly_summary(self, user_id:int, year:int, month:int):
        cur = self.conn.cursor()
        start = f"{year:04d}-{month:02d}-01"
        if month==12:
            end = f"{year+1:04d}-01-01"
        else:
            end = f"{year:04d}-{month+1:02d}-01"
        cur.execute("""SELECT type, category, SUM(amount) as total FROM transactions
                    WHERE user_id=? AND date>=? AND date<? GROUP BY type, category""", (user_id, start, end))
        return cur.fetchall()

    def yearly_summary(self, user_id:int, year:int):
        cur = self.conn.cursor()
        start = f"{year:04d}-01-01"
        end = f"{year+1:04d}-01-01"
        cur.execute("""SELECT type, category, SUM(amount) as total FROM transactions
                    WHERE user_id=? AND date>=? AND date<? GROUP BY type, category""", (user_id, start, end))
        return cur.fetchall()

    def close(self):
        self.conn.close()
