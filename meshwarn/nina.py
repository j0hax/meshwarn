import requests
from collections import deque

import logging
logger = logging.getLogger(__name__)

class MessageChecker:
    def __init__(self, buffer_size=1024) -> None:
        # Create a large circular buffer to ensure the last values are known
        self._known = deque([], maxlen=buffer_size)

    def usable(self, id) -> bool:
        if id in self._known:
            return False
        else:
            self._known.append(id)
            logger.info(f"Added ID '{id}' to record")
            return True

ninaBaseUrl = "https://warnung.bund.de/api31"
checker = MessageChecker()

def get_details(id):
    url = f"{ninaBaseUrl}/warnings/{id}.json"
    warningDetails = requests.get(url).json()
    headline = warningDetails["info"][0]["headline"]
    description = warningDetails["info"][0]["description"]
    return f"{headline}: {description}"


def get_warnings(code):
    url = f"{ninaBaseUrl}/dashboard/{code}.json"
    response = requests.get(url)
    warnungen = response.json()
    for warnung in warnungen:
        
        id = warnung["payload"]["id"]
        if checker.usable(id):
            yield get_details(id)
