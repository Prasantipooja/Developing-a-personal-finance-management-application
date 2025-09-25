import customtkinter as ctk
import ttkbootstrap as tb
from tkinter import messagebox, ttk
from transactions_gui import TransactionsWindow
from reports_gui import ReportsWindow
from budgets_gui import BudgetsWindow
from database import Database
from utils import today_str

class Dashboard:
    def __init__(self, master, user_id, username):
        self.master = master
        self.user_id = user_id
        self.username = username
        self.db = Database()
        self.window = tb.Toplevel(master)
        self.window.title('Dashboard - Personal Finance')
        self.window.geometry('800x520')
        self._build()

    def _build(self):
        top = tb.Frame(self.window, padding=10)
        top.pack(fill='x')
        tb.Label(top, text=f'Logged in as: {self.username}', font=('Helvetica', 12)).pack(side='left')
        tb.Button(top, text='Logout', command=self.logout).pack(side='right')

        body = tb.Frame(self.window, padding=10)
        body.pack(fill='both', expand=True)

        left = tb.Frame(body)
        left.pack(side='left', fill='y', padx=10, pady=10)
        tb.Button(left, text='Add / Manage Transactions', width=25, command=self.open_transactions).pack(pady=6)
        tb.Button(left, text='Reports (Monthly/Yearly)', width=25, command=self.open_reports).pack(pady=6)
        tb.Button(left, text='Budgets', width=25, command=self.open_budgets).pack(pady=6)
        tb.Button(left, text='Backup DB', width=25, command=self.backup_db).pack(pady=6)
        tb.Button(left, text='Restore DB', width=25, command=self.restore_db).pack(pady=6)

        right = tb.Frame(body)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Quick summary card
        income, expense = self._compute_totals()
        summary = tb.LabelFrame(right, text='Quick Summary', padding=10)
        summary.pack(fill='x')
        tb.Label(summary, text=f'Total Income: {income}').pack(anchor='w')
        tb.Label(summary, text=f'Total Expense: {expense}').pack(anchor='w')
        tb.Label(summary, text=f'Balance: {income - expense}').pack(anchor='w')

        # Recent transactions treeview
        tree_frame = tb.LabelFrame(right, text='Recent Transactions', padding=10)
        tree_frame.pack(fill='both', expand=True, pady=8)
        columns = ('id','date','type','category','amount','note')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for c in columns:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=100)
        self.tree.pack(fill='both', expand=True)
        self._load_recent()

    def _compute_totals(self):
        rows = self.db.get_transactions(self.user_id)
        income = sum(r['total'] if 'total' in r.keys() else (r['amount'] if r['type'].lower()=='income' else 0) for r in rows)
        expense = sum((r['amount'] if r['type'].lower()=='expense' else 0) for r in rows)
        return income, expense

    def _load_recent(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.db.get_transactions(self.user_id)[:10]
        for r in rows:
            self.tree.insert('', 'end', values=(r['id'], r['date'], r['type'], r['category'], r['amount'], r['note']))

    def open_transactions(self):
        TransactionsWindow(self.window, self.user_id, on_close=self._load_recent)

    def open_reports(self):
        ReportsWindow(self.window, self.user_id)

    def open_budgets(self):
        BudgetsWindow(self.window, self.user_id)

    def backup_db(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('SQLite DB','*.db')])
        if not path:
            return
        try:
            self.db.conn.commit()
            self.db.conn.close()
            import shutil
            shutil.copy(self.db.db_name, path)
            self.db = Database()  # reopen
            messagebox.showinfo('Backup', 'Backup successful')
        except Exception as e:
            messagebox.showerror('Error', f'Backup failed: {e}')

    def restore_db(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[('SQLite DB','*.db')])
        if not path:
            return
        try:
            self.db.conn.close()
            import shutil
            shutil.copy(path, self.db.db_name)
            self.db = Database()
            messagebox.showinfo('Restore', 'Restore successful')
            self._load_recent()
        except Exception as e:
            messagebox.showerror('Error', f'Restore failed: {e}')

    def logout(self):
        self.window.destroy()
