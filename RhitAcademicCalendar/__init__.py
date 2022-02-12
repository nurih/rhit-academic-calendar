import logging
from . import scraper
import traceback
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Got invoked')

    try:
        ical = scraper.to_calendar(scraper.scrape())
        return func.HttpResponse(ical, mimetype='text/calendar')
    except Exception:
        return func.HttpResponse(traceback.format_exc(), status_code=500)
