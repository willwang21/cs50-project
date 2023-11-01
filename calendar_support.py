import copy
import datetime as dt
import icalevents.icaldownload as icd
import icalevents.icalparser as icp


def import_calendar(path):
    """
    Takes a file path to an ics file and returns a list of icalevents
    events occurring in the next 4 weeks within that file.
    """
    es = icp.parse_events(
        icd.ICalDownload().data_from_file(path),
        default_span=dt.timedelta(weeks=4)
    )
    return es


def find_closest_15min(dt1, when='before'):
    """
    Given a datetime, finds the quarter-hour mark immediately before or after it.

    ex. if when == 'after', 2021-12-01 01:37:08 yields 2021-12-01 01:45:00.
    """
    dt_hour = dt.datetime.combine(dt1.date(), dt.time(hour=dt1.hour, tzinfo=dt1.tzinfo))
    td = dt.timedelta(minutes=15)
    if when == 'before':
        for i in range(3, -1, -1):
            dt_rounded = dt_hour + i * td
            if dt_rounded <= dt1:
                break
    elif when == 'after':
        for i in range(1, 5):
            dt_rounded = dt_hour + i * td
            if dt_rounded >= dt1:
                break
    return dt_rounded


class AvailableTimes():
    """
    A flipped representation of a calendar, containing times that are not occupied.
    """
    def __init__(self, es: list[icp.Event], today: dt.datetime):
        tz = today.tzinfo
        today_midnight = dt.datetime.combine(today.date(), dt.time(tzinfo=tz))
        fifteen_td = dt.timedelta(minutes=15)

        # There are 4 * 7 * 24 * 4 = 2688 15-minute periods in 4 weeks
        slots = {today_midnight + i * fifteen_td for i in range(2688)}
        # Discard the timeslots taken up by calendar events
        for e in es:
            counter = find_closest_15min(e.start, when='before')
            end = find_closest_15min(e.end, when='after')
            while counter < end:
                slots.discard(counter)
                counter += fifteen_td

        self.times = slots
        self.today = today
        self.tz = tz

    def intersect(self, at2: 'AvailableTimes'):
        """Returns a new AvailableTimes instance where both parents are free."""
        new = copy.copy(self)
        new.times = self.times & at2.times
        return new

    def restrict(self, wanted_times: dict[dt.datetime]):
        """Returns a new AvailableTimes instance with datetimes only within the bounds given."""
        new = copy.copy(self)
        new.times = {dtm for dtm in self.times if dtm.time() >= wanted_times['start']
                                                  and dtm.time() <= wanted_times['end']}
        return new


def find_meeting_time(path1, path2, meet_type: str, meet_length: int) -> list[dt.datetime]:
    """
    Given two paths to calendars, finds at most 3 times where both calendars are free.

    Meeting lengths are multiples of 15 minutes. Note: the two calendars must be in 
    the same time zone.
    """
    es1 = import_calendar(path1)
    es2 = import_calendar(path2)
    tz = dt.timezone(es1[0].start.utcoffset())
    today = dt.datetime.now(tz=tz)

    at1 = AvailableTimes(es1, today)
    at2 = AvailableTimes(es2, today)
    total_at = at1.intersect(at2)

    # Setting magic times for different meeting types
    if meet_type == 'morning':
        wanted_times = {'start': dt.time(9), 'end': dt.time(11, 30)}
    elif meet_type == 'lunch':
        wanted_times = {'start': dt.time(11, 30), 'end': dt.time(13, 30)}
    elif meet_type == 'afternoon':
        wanted_times = {'start': dt.time(13), 'end': dt.time(17)}
    elif meet_type == 'dinner':
        wanted_times = {'start': dt.time(17), 'end': dt.time(19, 30)}
    elif meet_type == 'evening':
        wanted_times = {'start': dt.time(18, 30), 'end': dt.time(21)}
    possible_times = sorted(total_at.restrict(wanted_times).times)

    # Try to find a block of time big enough to fit the meeting
    fifteen_td = dt.timedelta(minutes=15)
    meet_times = []
    periods = meet_length // 15
    counter = 0
    day = possible_times[0] - dt.timedelta(days=1)
    for i in range(1, len(possible_times)):
        guess = possible_times[i]
        if guess - fifteen_td == possible_times[i-1] and guess.day != day:
            counter += 1
        else:
            counter = 0
        if counter == periods:
            meet_times.append(possible_times[i-periods])
            day = guess.day
            counter = 0
    return meet_times[:3]
