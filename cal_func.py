import datetime

from icalendar import Timezone, TimezoneStandard, TimezoneDaylight


def add_vtimezone(cal):
    tzc = Timezone()
    tzc.add('TZID', 'Europe/Copenhagen')
    tzc.add('X-LIC-LOCATION', 'Europe/Copenhagen')

    tzs = TimezoneStandard()
    tzs.add('TZNAME', 'CET')
    tzs.add('DTSTART', datetime.datetime(1970, 10, 25, 3, 0, 0))
    tzs.add('RRULE', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
    tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))

    tzd = TimezoneDaylight()
    tzd.add('TZNAME', 'CEST')
    tzd.add('DTSTART', datetime.datetime(1970, 3, 29, 2, 0, 0))
    tzs.add('RRULE', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
    tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

    tzc.add_component(tzs)
    tzc.add_component(tzd)
    cal.add_component(tzc)