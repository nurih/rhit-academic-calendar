from time import time
from bs4 import BeautifulSoup
import urllib3

from datetime import date, datetime, time
from icalendar import Calendar, Event
import re
import requests

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA' 
url = 'https://www.rose-hulman.edu/campus-life/student-services/registrar/academic-calendars.html'



MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
          'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

DATE_RE = r"(?P<month>\w+)?\.?\s*(?P<day>\d+)"


def rebase_dates(items):
    result = []

    previous = items[0][0][-1]

    ref_year = date.today().year if date.today().month > 7 else date.today().year - 1

    for range, text in items:

        new_range = []

        for edge in range:
            if previous.month != 1 and edge.month == 1:
                ref_year = ref_year + 1
            previous = edge

            new_range.append(edge.replace(year=ref_year))

        result.append((new_range, text))

    return result


def scrape():
    http = urllib3.PoolManager()
    html = http.request('GET', url).data

    soup = BeautifulSoup(html, "html.parser")

    table_rows = soup.select(
        "#main > div > div.region.accordion-region > div > div > div.accordion-item > div.accordion-item-content > div > table > tbody > tr")

    result = []

    for tr in table_rows:
        tds = [c for c in tr.findChildren("p") if c]
        if len(tds) != 3:
            continue
        date_cell = tds[0].text
        description = tds[2].text
        parsed_range = parse_event_date_range(date_cell)
        result.append((parsed_range, description))

    return rebase_dates(result)


def parse_event_date_range(text):
    parts = [p.strip() for p in re.split(r'-|,', text)]
    range = []

    range.append(parse_event_date(parts[0]))

    if len(parts) == 2:
        range.append(parse_event_date(parts[1], range[0].month))

    return range


def decode_month(monthlike, default_month):
    if monthlike is None or monthlike.isnumeric():
        return default_month

    month_prefix = monthlike.lower()[:3]
    return MONTHS[month_prefix]


def parse_event_date(datelike, default_month=0):
    parts = datelike.split(' ')
    if parts[0].isnumeric():
        return date(date.today().year, default_month, int(parts[0]))

    return date(date.today().year, decode_month(parts[0], default_month), int(parts[1]))


def to_calendar(items):
    calendar = Calendar()

    for item in items:
        dtend = datetime.combine(item[0][-1], time(hour=23, minute=59))
        event = Event()
        text = re.sub(r'[^a-zA-Z0-9:,()/ .]+', '-', item[1])
        
        
        event.add('summary', text)
        event.add('dtstart', item[0][0])
        event.add('dtend', dtend)
        event.add('description', text)
        event.add('tzid', 'America/Indiana/Indianapolis')
        event.add('x-microsoft-cdo-busystatus', 'FREE')
        event.add('X-WR-CALNAME','Rose Hullman Academic Calendar')
        event.add('ORGANIZER;CN=RHIT','MAILTO:info@rose-hulman.edu')
        
        
        calendar.add_component(event)

    return calendar.to_ical()


if __name__ == '__main__':
    ics = to_calendar(scrape())
    with open('./rhit_calendar.ics', 'wb') as f:
        f.write(ics)
        f.close()
