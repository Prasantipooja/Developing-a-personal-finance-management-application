import ttkbootstrap as tb
from tkinter import ttk, messagebox
from database import Database
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportsWindow:
    def __init__(self, master, user_id):
        self.master = master
        self.user_id = user_id
        self.db = Database()
        self.window = tb.Toplevel(master)
        self.window.title('Reports')
        self.window.geometry('800x520')
        self._build()

    def _build(self):
        frm = tb.Frame(self.window, padding=10)
        frm.pack(fill='both', expand=True)
        control = tb.Frame(frm)
        control.pack(fill='x')
        tb.Label(control, text='Year (YYYY)').pack(side='left')
        self.year_entry = tb.Entry(control, width=8)
        self.year_entry.pack(side='left', padx=6)
        tb.Label(control, text='Month (1-12)').pack(side='left')
        self.month_entry = tb.Entry(control, width=4)
        self.month_entry.pack(side='left', padx=6)
        tb.Button(control, text='Show Monthly Chart', command=self.show_monthly).pack(side='left', padx=6)
        tb.Button(control, text='Show Yearly Summary', command=self.show_yearly).pack(side='left', padx=6)

        self.canvas_frame = tb.Frame(frm)
        self.canvas_frame.pack(fill='both', expand=True, pady=8)

    def show_monthly(self):
        try:
            year = int(self.year_entry.get().strip())
            month = int(self.month_entry.get().strip())
        except Exception:
            messagebox.showwarning('Invalid', 'Enter valid year and month')
            return
        rows = self.db.monthly_summary(self.user_id, year, month)
        categories = [r['category'] for r in rows if r['type'].lower()=='expense']
        totals = [r['total'] for r in rows if r['type'].lower()=='expense']
        if not categories:
            messagebox.showinfo('No Data', 'No expense data for that month')
            return
        # Create a bar chart (matplotlib). Follow instructions: single plot, no specific colors
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(categories, totals)
        ax.set_title(f'Expenses by Category - {year}-{month:02d}')
        ax.set_ylabel('Amount')
        # embed in Tk
        for w in self.canvas_frame.winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_yearly(self):
        try:
            year = int(self.year_entry.get().strip())
        except Exception:
            messagebox.showwarning('Invalid', 'Enter valid year')
            return
        rows = self.db.yearly_summary(self.user_id, year)
        # display simple table
        for w in self.canvas_frame.winfo_children():
            w.destroy()
        tree = ttk.Treeview(self.canvas_frame, columns=('type','category','total'), show='headings')
        for c in ('type','category','total'):
            tree.heading(c, text=c.title())
        tree.pack(fill='both', expand=True)
        total_income = 0
        total_expense = 0
        for r in rows:
            tree.insert('', 'end', values=(r['type'], r['category'], r['total']))
            if r['type'].lower()=='income':
                total_income += r['total']
            else:
                total_expense += r['total']
        lbl = tb.Label(self.canvas_frame, text=f'Total Income: {total_income}  Total Expense: {total_expense}  Savings: {total_income-total_expense}')
        lbl.pack(pady=6)
