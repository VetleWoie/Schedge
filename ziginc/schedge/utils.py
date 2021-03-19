from collections import namedtuple
from .models import PotentialTimeSlot, TimeSlot
import datetime as dt


def riise_hofsøy(event):
    def get_key(k):
        return k[0]

    time_slots = TimeSlot.objects.filter(event=event)
    PotentialTimeSlot.objects.filter(event=event).delete()
    timetuple = namedtuple("timetuple", ["dt", "state", "ts"])
    t_table = []
    for ts in time_slots:
        t_table.append(timetuple(dt.datetime.combine(ts.date, ts.start_time), +1, ts))
        t_table.append(timetuple(dt.datetime.combine(ts.date, ts.end_time), -1, ts))
    t_table.sort(key=get_key)

    S = []
    in_pts = []
    cnt = 0
    min_cnt = 2  # TODO replace with event.min_cnt or equivalent
    start = dt.datetime(1, 1, 1, 0, 0, 0)
    end = dt.datetime(1, 1, 1, 0, 0, 0)

    for i, t in enumerate(t_table):
        cnt += t.state
        if t.state == 1:  # step up
            S.append(t.ts)
            start = t.dt
            in_pts = S.copy()

            for sub_t in t_table[i:]:
                if sub_t.state == 1 or not sub_t.ts in in_pts:
                    continue
                end = sub_t.dt

                if len(in_pts) >= min_cnt and end - start >= event.duration:
                    # Only add/update pts if new one is valid
                    try:
                        pts = PotentialTimeSlot.objects.get(
                            event=event,
                            start_time=start.time(),
                            end_time=end.time(),
                            date=t.ts.date,
                        )
                    except PotentialTimeSlot.DoesNotExist:
                        pts = PotentialTimeSlot.objects.create(
                            event=event,
                            start_time=start.time(),
                            end_time=end.time(),
                            date=t.ts.date,
                        )
                        for ts in in_pts:
                            pts.participants.add(ts.creator)
                    else:  # no exception
                        pts.participants.add(t.ts.creator)

                if sub_t.ts == t.ts:
                    break
                in_pts.remove(sub_t.ts)
        else:  #  step down
            S.remove(t.ts)


# merges new timeslot to existing from same user if they overlap
def create_time_slot(event, user, timeslotdata):
    start = timeslotdata["start_time"]
    end = timeslotdata["end_time"]
    date = timeslotdata["date"]
    time_slots = TimeSlot.objects.filter(event=event, creator=user)
    for ts in time_slots:
        if (ts.start_time >= end or ts.end_time >= start) and date == ts.date:
            # Check if intersection exists
            ts_start = ts.start_time
            ts_end = ts.end_time
            ts.delete()
            return check_overlap_ts(
                event, user, min(start, ts_start), max(end, ts_end), date
            )
    # if recursive_call:
    TimeSlot.objects.create(
        event=event, start_time=start, end_time=end, date=date, creator=user
    )
    riise_hofsøy(event)
