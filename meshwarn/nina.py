import requests
from collections import deque
from meshwarn.devicehandler import ChannelBroadcaster
import logging

logger = logging.getLogger(__name__)

ninaBaseUrl = "https://warnung.bund.de/api31"


def get_details(id: str) -> tuple[str, str]:
    """Get headline and description of a NINA warning

    Args:
        id (str): ID of a specific NINA warning

    Returns:
        tuple[str, str]: Headline and description
    """
    url = f"{ninaBaseUrl}/warnings/{id}.json"
    warningDetails = requests.get(url).json()
    headline = warningDetails["info"][0]["headline"]
    description = warningDetails["info"][0]["description"]
    return headline, description


class MessageChecker:
    def __init__(self, ars: str, cb: ChannelBroadcaster, buffer_size=1024) -> None:
        """Manager for fetching and sending NINA warnings

        Args:
            ars (str): Amtlicher Regionalschlüssel
            cb (ChannelBroadcaster): Meshtastic channel to broadcast to
            buffer_size (int, optional): History of events to remember. Defaults to 1024.
        """
        self.ars = ars
        self.cb = cb
        self._known = deque([], maxlen=buffer_size)

    def known(self, id: str, add=True) -> bool:
        """Check if a NINA Warning is already known (sent).
        This prevents us from sending the same event every x minutes when checking.

        Args:
            id (str): Specific event ID
            add (bool, optional): Record the event ID to the buffer. Defaults to True.

        Returns:
            bool: Boolean if the event is known to the
        """
        if id in self._known:
            logger.info(f"Warning with ID '{id}' is already known")
            return True
        else:
            if add:
                self._known.append(id)
                logger.info(f"Added ID '{id}' to list of known warnings")
            return False

    def get_warnings(self):
        """Gets warnings for the

        Yields:
            _type_: _description_
        """
        url = f"{ninaBaseUrl}/dashboard/{self.ars}.json"
        response = requests.get(url)
        warnungen = response.json()
        for warnung in warnungen:
            id = warnung["payload"]["id"]
            if not self.known(id):
                yield get_details(id)

    def sendNina(self):
        """Poll the Bundesamt für Bevölkerungsschutz NINA API.
        If there are new warnings, these are broadcasted to a Meshtastic channel.

        Args:
            cb (ChannelBroadcaster): The Channel to broadcast to.
        """
        for headline, description in self.get_warnings():
            self.cb.sendText(f"{headline}: {description}")
