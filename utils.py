from datetime import datetime

def today_str():
    return datetime.now().strftime('%Y-%m-%d')

def parse_float(s, default=0.0):
    try:
        return float(s)
    except Exception:
        return default
