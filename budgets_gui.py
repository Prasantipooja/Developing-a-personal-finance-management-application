import ttkbootstrap as tb
from tkinter import messagebox, ttk
from database import Database

class BudgetsWindow:
    def __init__(self, master, user_id):
        self.master = master
        self.user_id = user_id
        self.db = Database()
        self.window = tb.Toplevel(master)
        self.window.title('Budgets')
        self.window.geometry('640x420')
        self._build()

    def _build(self):
        frm = tb.Frame(self.window, padding=10)
        frm.pack(fill='both', expand=True)
        left = tb.Frame(frm)
        left.pack(side='left', fill='y', padx=8)
        tb.Label(left, text='Category').pack(anchor='w')
        self.cat = tb.Entry(left)
        self.cat.pack(fill='x', pady=4)
        tb.Label(left, text='Monthly Limit').pack(anchor='w')
        self.limit = tb.Entry(left)
        self.limit.pack(fill='x', pady=4)
        tb.Button(left, text='Set Budget', command=self.set_budget).pack(pady=6)
        tb.Button(left, text='Refresh', command=self.load_budgets).pack(pady=6)

        right = tb.Frame(frm)
        right.pack(side='left', fill='both', expand=True, padx=8)
        cols = ('id','category','monthly_limit')
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c.title())
        self.tree.pack(fill='both', expand=True)
        self.load_budgets()

    def set_budget(self):
        category = self.cat.get().strip().capitalize()
        try:
            limit = float(self.limit.get().strip())
        except Exception:
            messagebox.showwarning('Invalid', 'Enter a valid numeric limit')
            return
        if not category:
            messagebox.showwarning('Missing', 'Category required')
            return
        self.db.set_budget(self.user_id, category, limit)
        messagebox.showinfo('Saved', 'Budget saved')
        self.load_budgets()

    def load_budgets(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.db.get_budgets(self.user_id)
        for r in rows:
            self.tree.insert('', 'end', values=(r['id'], r['category'], r['monthly_limit']))
