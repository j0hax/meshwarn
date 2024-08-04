from meshtastic.mesh_interface import MeshInterface
from time import sleep
import msgsplitter

import logging

logger = logging.getLogger(__name__)


class ChannelBroadcaster:
    """Broadcasts a message to differente channels"""

    def __init__(self, channel: str, device: MeshInterface):
        self._interface = device

        for k in self._interface._localChannels:
            if k.settings.name == channel:
                self._channelIndex = k.index
                break

        if not hasattr(self, "_channelIndex"):
            raise Exception(f"Could not find index for channel '{channel}'")

        logger.info(f"Channel index is {self._channelIndex}")

    def sendText(self, *messages):
        """Send messages to the target channels. If a message is too long, it will be split into multiple messages.

        Args:
            messages (str): Text Message to be sent
        """
        for message in messages:
            for chunk in msgsplitter.split(message, length_limit=200):
                pkt = self._interface.sendText(
                    text=chunk, wantAck=True, channelIndex=self._channelIndex
                )
                logger.info(
                    f"Sent packet ID {pkt.id} with contents '{pkt.decoded.payload.decode()}'"
                )
                sleep(10)
