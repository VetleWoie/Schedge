from django import template

register = template.Library()

@register.filter()
def nicedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = int(timedeltaobj.total_seconds())
    timetot = ""
    if secs > 86400: # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} day{}".format(days, "s" if days > 1 else "")
        secs = secs - days*86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hour{}".format(hrs, "s" if hrs > 1 else "")
        secs = secs - hrs*3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} minute{}".format(mins, "s" if mins > 1 else "")
        secs = secs - mins*60

    if secs > 0:
        timetot += " {} second{}".format(secs, "s" if secs > 1 else "")
    return timetot