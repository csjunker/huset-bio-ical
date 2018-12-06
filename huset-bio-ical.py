import requests
from lxml import html
from datetime import datetime
import pytz
from icalendar import Calendar, Event
import re


base_url = r'https://huset-kbh.dk/'
params = {'taxonomyId':'274', 'page_nr':'10'}

##search_url = base_url
##oversigt = html.parse(search_url)

rex = re.compile(r'^(\d{2})\.(\d{2}).*?(\d{1,2}).(\d{2}).*')
#rex = re.compile(r'^TIME\ (\d{2})(.*)')

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
cal.add('prodid', 'Husets Biograf')
cal.add('varsion', '0.1')

local_tz = pytz.timezone('Europe/Copenhagen')

text_file = open('/Users/csjunker/PycharmProjects/huset-Bio-iCal/Huset-Bio.ics', 'r')
istr = text_file.read()
text_file.close()

idict = {}

gcal = Calendar.from_ical(istr)
for component in gcal.walk():
    if component.name == "VEVENT":
        #print(component.get('summary'))
        uid=component.get('uid')
        seq=component.get('sequence')
        idict[uid] = seq
        #seq = seq + 1
        #print(uid)
        #print(seq)
        #print(component.get('dtstamp'))

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
        event.add ('UID', uid)
        event.add ('SEQUENCE', seq)
        print('UID', uid)
        print('SEQUENCE', seq)

        event.add('LOCATION', 'Husets-Biograf; Rådhusstræde 13, 1466 København K')
        year = int(datetime.now().strftime("%Y"))
        currentmonth = int(datetime.now().strftime("%m"))
        if (currentmonth - 2) > md:
            year = year + 1
        event.add('dtstart', datetime(year, md, da, hh, mm, 0, tzinfo=local_tz))
        #event.add('dtend', datetime(2018, 4, 4, 10, 0, 0, tzinfo=local_tz))
        event.add('dtstamp', datetime.now(local_tz))
        event.add('LAST-MODIFIED', datetime.now(pytz.utc))
        event.add ('CATEGORIES', event_genre)

        #event.add('COMMENT' 'Kommentar')
        event.add ('DESICRIPTION', elem_description)
        event.add ('URL', event_url)
        event.add ('SUMMARY', event_name)


        cal.add_component(event)



print ()
print ('##################')
print ('COUNT', count)
print ('last_date', last_date)
print ('DATETIME', datetime.now())
istr = cal.to_ical()
print (istr)

t = local_tz.localize(datetime.now())
t_utc = t.astimezone(pytz.UTC)
print ('t:', t)
print ('t_utc:', t_utc)

text_file = open('/Users/csjunker/PycharmProjects/huset-Bio-iCal/Huset-Bio.ics', 'wb')
text_file.write(istr)
text_file.close()

