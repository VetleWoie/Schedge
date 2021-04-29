import datetime as dt

def time_add(time, delta):
    """adds a timedelta to a time object"""
    return (dt.datetime.combine(dt.date.today(), time) + delta).time()

def time_diff(x, y):
    dt1 = dt.datetime.combine(dt.date.today(), x)
    if x < y:
        dt2 = dt.datetime.combine(dt.date.today(), y)
    else:
        dt2 = dt.datetime.combine(dt.date.today() + dt.timedelta(days=1), y)

    return dt2 - dt1