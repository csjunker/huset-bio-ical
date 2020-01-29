import requests
from lxml import html
import datetime
import pytz
from icalendar import Calendar, Event, Timezone, TimezoneDaylight, TimezoneStandard
import re
import os.path
import subprocess

def add_vtimezone(cal):
    tzc = Timezone()
    tzc.add('tzid', 'Europe/Copenhagen')
    tzc.add('x-lic-location', 'Europe/Copenhagen')

    tzs = TimezoneStandard()
    tzs.add('tzname', 'CET')
    tzs.add('dtstart', datetime.datetime(1970, 10, 25, 3, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
    tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))

    tzd = TimezoneDaylight()
    tzd.add('tzname', 'CEST')
    tzd.add('dtstart', datetime.datetime(1970, 3, 29, 2, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
    tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

    tzc.add_component(tzs)
    tzc.add_component(tzd)
    cal.add_component(tzc)

base_url = r'https://huset-kbh.dk/'
params = {'taxonomyId':'274', 'page_nr':'10'}
ics_filename = 'Huset-Bio.ics'

##search_url = base_url
##oversigt = html.parse(search_url)

rex = re.compile(r'^(\d{2})\.(\d{2}).*?Kl\..*?(\d{1,2}).(\d{2}).*')

def parsetime(timestr):
    print ('PT[{}]'.format(timestr))
    m = rex.match(timestr)
    print ('mm:', m)
    print ('groups:', m.lastindex, ':', m.groups())
    return (int(x) for x in m.groups())

headers = {
    'User-Agent': 'Mozilla/5.0'
}

r = requests.get(base_url, params=params, headers=headers)

def get_element(movie, cssselector):
    return movie.cssselect(cssselector)[0]

def get_element_value(movie, cssselector):
    return get_element(movie, cssselector).text_content().strip()

tree = html.fromstring(r.text)

#results = tree.xpath(xpath)
results = tree.cssselect('#widgets-wrapper')[0].getchildren()
#print ('hugo HUGO', len(results))


cal = Calendar()
#cal = new CalendCalendarar(None)
calName = 'Husets-Bio All Shows'
calTimezone = 'Europe/Copenhagen'
cal.add('prodid', '7703f8e4-7a23-402f-bd1d-047656ee3cc7')
cal.add('version', '2.0')
cal.add('url', 'https://services.husets-biograf.dk/calendar/all-shows')
cal.add('name', calName)
cal.add('X-WR-CALNAME', calName)
#DESCRIPTION:A description of my calendar
#X-WR-CALDESC:A description of my calendar
cal.add('TIMEZONE-ID', calTimezone)
cal.add('X-WR-TIMEZONE', calTimezone)
cal.add('REFRESH-INTERVAL;VALUE=DURATION', 'PT2H')
cal.add('X-PUBLISHED-TTL', 'PT2H')
#COLOR:34:50:105
cal.add('CALSCALE', 'GREGORIAN')
##cal.add('METHOD', 'PUBLISH')

local_tz = pytz.timezone(calTimezone)


calSequence = 0
updateSeq = False
idict = {}
if os.path.isfile(ics_filename):
    text_file = open(ics_filename, 'r')
    istr = text_file.read()
    text_file.close()

    gcal = Calendar.from_ical(istr)
    tmpseq = gcal.get('SEQUENCE')
    if not tmpseq is None:
        calSequence =  tmpseq;
    print ('exist SEQ', tmpseq)

    for component in gcal.walk():
        if component.name == "VEVENT":
            uid=component.get('uid')
            seq=component.get('sequence')
            idict[uid] = seq

count = 0
last_date = 'NO_LAST*DATE'
for movie in results:
#movie = results[1]
    event_genre = get_element_value(movie, '.event-genre')
    if not event_genre in ['Familie/Børn, Samlingspunkt Indre By', 'Samlingspunkt Indre By']:

        #print(html.tostring(movie))
        print ()

        count += 1
        movie_id = movie.get('data-id')
        movie_time = get_element_value(movie, '.event-time')

        event_name = get_element_value(movie, '.event-name')

        event_url = get_element(movie, '.event-desc-text a').get('href')
        elem_description = get_element_value(movie, '.event-desc-text p')
        event_picture_url = get_element(movie, '.img-responsive').get('src')
        #aa = get_element_value (movie, '')
        #.img-responsive
        #.event-desc-text
        #.ticket-price
        #.ticket-status

        print ('ID', movie_id)
        print ('TIME', movie_time)
        last_date = movie_time
        da, md, hh, mm = parsetime(movie_time)

        print('GENRE', event_genre)
        print('NAME', event_name)
        print ('DESC', elem_description)

        print ('IMG', event_picture_url)
        print ('URL', event_url)

        event = Event()
        uid = 'Husets-Bio-' + movie_id
        seq = 0
        if uid in idict:
            seq = idict[uid]
            seq = seq + 1
            updateSeq = True
        event.add ('UID', uid)
        event.add ('SEQUENCE', seq)
        print('UID', uid)
        print('SEQUENCE', seq)

        event.add('LOCATION', 'Husets-Biograf; Rådhusstræde 13, 1466 København K')
        year = int(datetime.datetime.now().strftime("%Y"))
        currentmonth = int(datetime.datetime.now().strftime("%m"))
        if (currentmonth - 2) > md:
            year = year + 1
        event.add('dtstart', datetime.datetime(year, md, da, hh, mm, 0, tzinfo=local_tz))
        #event.add('dtend', datetime.datetime(2018, 4, 4, 10, 0, 0, tzinfo=local_tz))
        event.add('dtstamp', datetime.datetime.now(local_tz))
        event.add('LAST-MODIFIED', datetime.datetime.now(pytz.utc))
        event.add ('CATEGORIES', event_genre)

        #event.add('COMMENT' 'Kommentar')
        event.add ('DESCRIPTION', elem_description)
        event.add ('URL', event_url)
        event.add ('SUMMARY', event_name)


        cal.add_component(event)

add_vtimezone(cal)
if updateSeq == True:
    calSequence = calSequence + 1
#cal.add('sequence', calSequence)


print ()
print ('##################')
print ('COUNT', count)
print ('last_date', last_date)
print ('DATETIME', datetime.datetime.now())
istr = cal.to_ical()
#print (istr)

t = local_tz.localize(datetime.datetime.now())
t_utc = t.astimezone(pytz.UTC)
print ('t:', t)
print ('t_utc:', t_utc)

text_file = open(ics_filename, 'wb')
text_file.write(istr)
text_file.close()

print()
print('aws s3 cp Huset-Bio.ics s3://husets-bio/Huset-Bio.ics --acl public-read')
rc = subprocess.run(['aws', 's3', 'cp', 'Huset-Bio.ics', 's3://husets-bio/Huset-Bio.ics', '--acl', 'public-read'])
print('rc', rc)

print('validate', 'https://icalendar.org/validator.html?url=https://services.husets-biograf.dk/calendar/all-shows')
