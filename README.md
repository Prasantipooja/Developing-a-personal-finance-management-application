# Personal Finance Manager - GUI (Tkinter + ttkbootstrap + customtkinter)

This GUI version uses `customtkinter` and `ttkbootstrap` for a modern look and `matplotlib` for charts.
Run instructions (Windows / macOS / Linux):

1. Install Python 3.8+
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # macOS / Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```

Features:
- Login & Registration with hashed passwords (SQLite)
- Dashboard with Add/View Transactions, Reports, Budgets, Backup/Restore
- Modern themed UI using customtkinter & ttkbootstrap
- Matplotlib charts for monthly reports
- Data stored in `finance.db` in the project folder

Notes:
- Passwords are hashed using SHA-256. For production, consider `bcrypt`.
- The GUI aims to be lightweight for showcasing; you can extend it later.
