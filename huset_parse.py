import requests
from lxml import html
import EventData

base_url = r'https://huset-kbh.dk/'
params = {'taxonomyId':'274', 'page_nr':'10', 'lang':'da'}
headers = {
    'User-Agent': 'Mozilla/5.0'
}

def get_element(movie, cssselector):
    return movie.cssselect(cssselector)[0]

def get_element_value(movie, cssselector):
    return get_element(movie, cssselector).text_content().strip()



def fetchHusetHtml():
    r = requests.get(base_url, params=params, headers=headers)
    tree = html.fromstring(r.text)
    return tree

def getBioEvents():
    tree = fetchHusetHtml()
    results = tree.cssselect('#widgets-wrapper')[0].getchildren()

    events = []
    for movie in results:
        event_genre = get_element_value(movie, '.event-genre')
        if not event_genre in ['Familie/Børn, Samlingspunkt Indre By', 'Samlingspunkt Indre By']:
            events.append(movie)

    return events
