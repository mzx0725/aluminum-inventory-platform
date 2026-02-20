from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_time():
    return datetime.now(BEIJING_TZ).replace(tzinfo=None)

def format_beijing_time(dt=None):
    if dt is None:
        dt = get_beijing_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')