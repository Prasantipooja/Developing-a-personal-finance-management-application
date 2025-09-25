import ttkbootstrap as tb
from tkinter import messagebox, ttk
from database import Database
from utils import today_str, parse_float

class TransactionsWindow:
    def __init__(self, master, user_id, on_close=None):
        self.master = master
        self.user_id = user_id
        self.on_close = on_close
        self.db = Database()
        self.window = tb.Toplevel(master)
        self.window.title('Transactions')
        self.window.geometry('720x480')
        self._build()

    def _build(self):
        frm = tb.Frame(self.window, padding=10)
        frm.pack(fill='both', expand=True)

        left = tb.Frame(frm)
        left.pack(side='left', fill='y', padx=8, pady=8)
        tb.Label(left, text='Type').pack(anchor='w')
        self.type_var = tb.StringVar(value='Expense')
        tb.Radiobutton(left, text='Income', variable=self.type_var, value='Income').pack(anchor='w')
        tb.Radiobutton(left, text='Expense', variable=self.type_var, value='Expense').pack(anchor='w')

        tb.Label(left, text='Category').pack(anchor='w', pady=(8,0))
        self.category = tb.Entry(left)
        self.category.pack(fill='x')

        tb.Label(left, text='Amount').pack(anchor='w', pady=(8,0))
        self.amount = tb.Entry(left)
        self.amount.pack(fill='x')

        tb.Label(left, text='Date (YYYY-MM-DD)').pack(anchor='w', pady=(8,0))
        self.date = tb.Entry(left)
        self.date.insert(0, today_str())
        self.date.pack(fill='x')

        tb.Label(left, text='Note').pack(anchor='w', pady=(8,0))
        self.note = tb.Entry(left)
        self.note.pack(fill='x')

        tb.Button(left, text='Add Transaction', command=self.add_transaction).pack(pady=10)
        tb.Button(left, text='Refresh List', command=self.load_list).pack(pady=2)

        right = tb.Frame(frm)
        right.pack(side='left', fill='both', expand=True, padx=8)

        cols = ('id','date','type','category','amount','note')
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=100)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', self.on_edit)

        btns = tb.Frame(right, padding=6)
        btns.pack(fill='x')
        tb.Button(btns, text='Delete Selected', command=self.delete_selected).pack(side='left', padx=4)
        self.load_list()

    def add_transaction(self):
        ttype = self.type_var.get()
        category = self.category.get().strip().capitalize()
        amount = parse_float(self.amount.get().strip(), None)
        date = self.date.get().strip()
        note = self.note.get().strip()
        if not category or amount is None:
            messagebox.showwarning('Missing', 'Category and valid amount required')
            return
        self.db.add_transaction(self.user_id, ttype, category, amount, date, note)
        b = self.db.get_budget_for_category(self.user_id, category)
        if b and ttype.lower()=='expense':
            y,m,_ = date.split('-')
            summary = self.db.monthly_summary(self.user_id, int(y), int(m))
            total_for_cat = 0
            for row in summary:
                if row['category'].lower() == category.lower() and row['type'].lower()=='expense':
                    total_for_cat += row['total']
            if total_for_cat > b['monthly_limit']:
                messagebox.showwarning('Budget Exceeded', f'You exceeded budget for {category}. Limit: {b["monthly_limit"]}, Spent: {total_for_cat}')
        messagebox.showinfo('Added', 'Transaction added')
        self.load_list()
        if self.on_close:
            self.on_close()

    def load_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.db.get_transactions(self.user_id)
        for r in rows:
            self.tree.insert('', 'end', values=(r['id'], r['date'], r['type'], r['category'], r['amount'], r['note']))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for s in sel:
            vals = self.tree.item(s)['values']
            tid = vals[0]
            self.db.delete_transaction(tid, self.user_id)
        messagebox.showinfo('Deleted', 'Selected transactions deleted')
        self.load_list()
        if self.on_close:
            self.on_close()

    def on_edit(self, event):
        item = self.tree.selection()[0]
        vals = self.tree.item(item)['values']
        tid = vals[0]
        # Simple inline edit dialog
        from tkinter.simpledialog import askstring
        new_note = askstring('Edit Note', 'Note:', initialvalue=vals[5])
        if new_note is None:
            return
        self.db.update_transaction(tid, self.user_id, note=new_note)
        self.load_list()
        if self.on_close:
            self.on_close()
