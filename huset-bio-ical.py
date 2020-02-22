import datetime
import pytz
from icalendar import Calendar, Event
import re
import os.path
import subprocess

from huset_parse import getBioEvents

__version__ = '2.1'

from cal_func import add_vtimezone

ics_filename = 'Huset-Bio.ics'

rex = re.compile(r'^(\d{2})\.(\d{2}).*?(?:Kl\.|At).*?(\d{1,2}).(\d{2}).*')

def parsetime(timestr):
    print ('PT[{}]'.format(timestr))
    m = rex.match(timestr)
    print ('mm:', m)
    print ('groups:', m.lastindex, ':', m.groups())
    return (int(x) for x in m.groups())

def get_element(movie, cssselector):
    return movie.cssselect(cssselector)[0]

def get_element_value(movie, cssselector):
    return get_element(movie, cssselector).text_content().strip()

def set_movie_status(movie, event):
    event_status = movie.cssselect('.ticket-replace-status')
    if type(event_status) == list and len(event_status) > 0:
        event_status = get_element_value(movie, '.ticket-replace-status')
        if event_status == None:
            return None
        elif event_status == 'Aflyst' or event_status == 'Cancelled':
            eventupdate(event, 'SUMMARY', '(CANCELLED) ' + event.get('SUMMARY'))
        elif event_status == 'Få billetter' or event_status == 'Limited Tickets':
            eventupdate(event, 'SUMMARY', event.get('SUMMARY') + ' (Limited Tickets)')
        elif event_status == 'Ny dato' or event_status == 'New date':
            None
        elif event_status == 'Ny scene' or event_status == 'New stage':
            None
        elif event_status == 'Udsolgt' or event_status == 'Sold out':
            eventupdate(event, 'SUMMARY', '(SOLD OUT) ' + event.get('SUMMARY'))

    return None

def eventupdate(event, key, value):
    event[key] = value


cal = Calendar()
calName = 'Husets-Bio All Shows'
calTimezone = 'Europe/Copenhagen'


cal.add('PRODID', '-//HUSETS-BIOGRAF//NOSGML V' + __version__ + '//EN')
cal.add('VERSION', '2.0') #ical version not calendar version
cal.add('CLASS', 'PUBLIC')
cal.add('URL', 'https://services.husets-biograf.dk/calendar/all-shows')
cal.add('NAME', calName)
cal.add('X-WR-CALNAME', calName)
cal.add('TIMEZONE-ID', calTimezone)
cal.add('X-WR-TIMEZONE', calTimezone)
cal.add('REFRESH-INTERVAL;VALUE=DURATION', 'PT2H')
cal.add('X-PUBLISHED-TTL', 'PT2H')
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
            uid=component.get('UID')
            seq=component.get('SEQUENCE')
            idict[uid] = seq

count = 0
last_date = 'NO_LAST*DATE'

for movie in getBioEvents():
    event_genre = get_element_value(movie, '.event-genre')

    count += 1
    movie_id = movie.get('data-id')
    movie_time = get_element_value(movie, '.event-time')

    event_name = get_element_value(movie, '.event-name')

    event_url = get_element(movie, '.event-desc-text a').get('href')
    elem_description = get_element_value(movie, '.event-desc-text p')
    event_picture_url = get_element(movie, '.img-responsive').get('src')
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
    event.add('DTSTART', datetime.datetime(year, md, da, hh, mm, 0, tzinfo=local_tz))
    event.add('DTSTAMP', datetime.datetime.now(local_tz))
    event.add('LAST-MODIFIED', datetime.datetime.now(pytz.utc))
    event.add ('CATEGORIES', event_genre)

    event.add ('DESCRIPTION', elem_description)
    event.add ('URL', event_url)
    event.add ('SUMMARY', event_name)

    event_status = set_movie_status(movie, event)
    print('STATUS', event_status)

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
