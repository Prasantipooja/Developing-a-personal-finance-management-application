import customtkinter as ctk
import ttkbootstrap as tb
from auth_gui import AuthWindow
from dashboard import Dashboard

def start_app():
    root = tb.Window(themename='darkly')  # use ttkbootstrap theme
    root.title('Personal Finance Manager')
    root.geometry('400x200')
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))

    def on_login(user_id, username):
        Dashboard(root, user_id, username)

    tb.Label(root, text='Welcome to Personal Finance Manager', font=('Helvetica', 14)).pack(pady=20)
    tb.Button(root, text='Login / Register', command=lambda: AuthWindow(root, on_login)).pack(pady=8)
    root.mainloop()

if __name__ == '__main__':
    start_app()
