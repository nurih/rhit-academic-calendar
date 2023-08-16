import logging
import azure.functions as func
import traceback


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Alive invoked with {req.method}")

    try:        
        return func.HttpResponse('Yes.', mimetype="text/plain")
    except Exception:
        return func.HttpResponse(traceback.format_exc(), status_code=500)
