import customtkinter as ctk
from tkinter import messagebox
import ttkbootstrap as tb
from database import Database
from getpass import getpass

class AuthWindow:
    def __init__(self, master, on_login):
        self.master = master
        self.on_login = on_login
        self.db = Database()
        self.window = tb.Toplevel(master)
        self.window.title('Login - Personal Finance')
        self.window.geometry('360x260')
        self.window.resizable(False, False)
        self._build()

    def _build(self):
        frm = tb.Frame(self.window, padding=20)
        frm.pack(fill='both', expand=True)

        tb.Label(frm, text='Username').pack(anchor='w')
        self.username = tb.Entry(frm)
        self.username.pack(fill='x', pady=5)

        tb.Label(frm, text='Password').pack(anchor='w')
        self.password = tb.Entry(frm, show='*')
        self.password.pack(fill='x', pady=5)

        btn_frame = tb.Frame(frm)
        btn_frame.pack(fill='x', pady=10)
        tb.Button(btn_frame, text='Login', command=self.login).pack(side='left', expand=True, padx=5)
        tb.Button(btn_frame, text='Register', command=self.register).pack(side='left', expand=True, padx=5)

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if not user or not pwd:
            messagebox.showwarning('Missing', 'Enter username and password')
            return
        uid = self.db.login_user(user, pwd)
        if uid:
            messagebox.showinfo('Success', f'Welcome {user}')
            self.window.destroy()
            self.on_login(uid, user)
        else:
            messagebox.showerror('Failed', 'Login failed. Check credentials.')

    def register(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if not user or not pwd:
            messagebox.showwarning('Missing', 'Enter username and password')
            return
        ok = self.db.register_user(user, pwd)
        if ok:
            messagebox.showinfo('Registered', 'Registration successful. You can login now.')
        else:
            messagebox.showerror('Exists', 'Username already exists. Choose another.')
