import logging
import requests
from lxml import html
from datetime import datetime
import pytz
from icalendar import Calendar, Event
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

base_url = r'https://huset-kbh.dk/'
params = {'taxonomyId':'274', 'page_nr':'10'}
out_ics_file = '/Users/csjunker/PycharmProjects/huset-Bio-iCal/Huset-Bio.ics'

rex = re.compile(r'^(\d{2})\.(\d{2}).*?(\d{1,2}).(\d{2}).*')

headers = {
    'User-Agent': 'Mozilla/5.0'
}

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

def my_handler(event, context):
    logger.info('got event{}'.format(event))
    r = requests.get(base_url, params=params, headers=headers)
    tree = html.fromstring(r.text)
    results = tree.cssselect('#widgets-wrapper')[0].getchildren()

    cal = Calendar()
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
            uid=component.get('uid')
            seq=component.get('sequence')
            idict[uid] = seq

    count = 0
    last_date = 'NO_LAST*DATE'
    for movie in results:
        event_genre = get_element_value(movie, '.event-genre')
        if not event_genre in ['Familie/Børn, Samlingspunkt Indre By', 'Samlingspunkt Indre By']:
            count += 1
            movie_id = movie.get('data-id')
            movie_time = get_element_value(movie, '.event-time')

            event_name = get_element_value(movie, '.event-name')

            event_url = get_element(movie, '.event-desc-text a').get('href')
            elem_description = get_element_value(movie, '.event-desc-text p')
            event_picture_url = get_element(movie, '.img-responsive').get('src')

            logger.info ('ID', movie_id)
            logger.info ('TIME', movie_time)
            last_date = movie_time
            da, md, hh, mm = parsetime(movie_time)

            logger.info('GENRE', event_genre)
            logger.info('NAME', event_name)
            logger.info ('DESC', elem_description)

            logger.info ('IMG', event_picture_url)
            logger.info ('URL', event_url)

            event = Event()
            uid = 'Husets-Bio-' + movie_id
            seq = 0
            if uid in idict:
                seq = idict[uid]
                seq = seq + 1
            event.add ('UID', uid)
            event.add ('SEQUENCE', seq)
            logger.info('UID', uid)
            logger.info('SEQUENCE', seq)

            event.add('LOCATION', 'Husets-Biograf; Rådhusstræde 13, 1466 København K')
            year = int(datetime.now().strftime("%Y"))
            currentmonth = int(datetime.now().strftime("%m"))
            if (currentmonth - 2) > md:
                year = year + 1
            event.add('dtstart', datetime(year, md, da, hh, mm, 0, tzinfo=local_tz))
            event.add('dtstamp', datetime.now(local_tz))
            event.add('LAST-MODIFIED', datetime.now(pytz.utc))
            event.add ('CATEGORIES', event_genre)

            event.add ('DESICRIPTION', elem_description)
            event.add ('URL', event_url)
            event.add ('SUMMARY', event_name)


            cal.add_component(event)


    logger.info ()
    logger.info ('##################')
    logger.info ('COUNT', count)
    logger.info ('last_date', last_date)
    logger.info ('DATETIME', datetime.now())
    istr = cal.to_ical()
    logger.info (istr)

    t = local_tz.localize(datetime.now())
    t_utc = t.astimezone(pytz.UTC)
    logger.info ('t:', t)
    logger.info ('t_utc:', t_utc)

    text_file = open(out_ics_file, 'wb')
    text_file.write(istr)
    text_file.close()

    logger.info()
    logger.info('aws s3 cp Huset-Bio.ics s3://husets-bio/Huset-Bio.ics --acl public-read')


    #message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])
    return {
        'message' : istr
    }

