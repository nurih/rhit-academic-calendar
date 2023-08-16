import logging
from . import scraper
import azure.functions as func
import traceback


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Function invoked by HTTP trigger using a {req.method}")

    try:
        ical = scraper.to_calendar(scraper.scrape())
        return func.HttpResponse(ical, mimetype="text/calendar")
    except Exception:
        return func.HttpResponse(traceback.format_exc(), status_code=500)
