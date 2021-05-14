from collections import namedtuple
from .models import PotentialTimeSlot, TimeSlot
import datetime as dt

def riise_hofsøy(event):
    """Finds the potential time slots

    Called after a time slot has been altered. Deletes the previous
    potential time slots from the database and creates new ones.

    Parameters
    ----------
    event : event object
        The event that the algorithm is computing potential
        time slots for.
    """
    
    def get_key(k):
        """ Returns the first element in the touple """
        return k[0]

    time_slots = TimeSlot.objects.filter(event=event) # get all timeslots for this event
    PotentialTimeSlot.objects.filter(event=event).delete() # Delete pre-existing potential time slots
    TimeTuple = namedtuple("TimeTuple", ["dt", "state", "ts"])
    t_table = []

    for ts in time_slots:
        # add start time to time table
        t_table.append(TimeTuple(dt.datetime.combine(ts.date, ts.start_time), +1, ts)) 
        if ts.start_time > ts.end_time: # time slot is a rollover to next day so store it as ending next day
            t_table.append(TimeTuple(dt.datetime.combine(ts.date + dt.timedelta(1), ts.end_time), -1, ts))
        else: # store end of time slot in time table
            t_table.append(TimeTuple(dt.datetime.combine(ts.date, ts.end_time), -1, ts))
    # sort the tuples
    t_table.sort(key=get_key)

    S = []
    in_potential_time_slot = [] #current active potential time slots
    count = 0
    min_count = 2  # TODO replace with event.min_count or equivalent
    start = dt.datetime(1, 1, 1, 0, 0, 0)
    end = dt.datetime(1, 1, 1, 0, 0, 0)

    for i, t in enumerate(t_table):
        count += t.state # Keep track of overlapping time slots
        if t.state == 1:  # step up
            S.append(t.ts)
            start = t.dt
            in_potential_time_slot = S.copy()

            # check for sub time slots
            # only interested in the ones that has already started, but not finished 
            for sub_t in t_table[i:]:
                if sub_t.state == 1 or not sub_t.ts in in_potential_time_slot:
                    continue
                end = sub_t.dt

                if len(in_potential_time_slot) >= min_count and end - start >= event.duration:
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
                        for ts in in_potential_time_slot:
                            pts.participants.add(ts.creator)
                    else:  # no exception
                        pts.participants.add(t.ts.creator)
                # breaks when all sub time slots has been found
                if sub_t.ts == t.ts:
                    break
                in_potential_time_slot.remove(sub_t.ts)
        else:  #  step down
            S.remove(t.ts)

# merges new timeslot to existing from same user if they overlap
def create_time_slot(event, user, timeslotdata):
    """Creates a new time slot.

    Parameters
    ----------
    event : event object
        The event the time slot belongs to.
    user : user object
        The user that created the time slot
    timeslotdata : dict
        The rest of the data needed to create a time slot
    """
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
            return create_time_slot(
                event, user, {"start_time":min(start, ts_start), "end_time": max(end, ts_end), "date": date}
            )
    TimeSlot.objects.create(
        event=event, start_time=start, end_time=end, date=date, creator=user
    )
    riise_hofsøy(event)