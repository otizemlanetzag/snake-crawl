from api.security import valid_session
from Advanced_crawl.advanced_crawl import handler

def main(request):
    if not valid_session(request):
        return {"statusCode":401,"headers":{"Content-Type":"application/json","Cache-Control":"no-store"},"body":"{\"error\":\"Authentication required\"}"}
    return handler(request)
