#!/usr/bin/env python3

import argparse
from meshtastic.serial_interface import SerialInterface
from meshwarn.devicehandler import ChannelBroadcaster
from meshwarn.nina import MessageChecker
from apscheduler import Scheduler
from apscheduler.triggers.cron import CronTrigger

import logging

logger = logging.getLogger(__name__)


def main(serial, channel, ars):
    logging.basicConfig(level=logging.INFO)
    logger.info("Started")

    interface = SerialInterface(serial)

    newsChannel = ChannelBroadcaster(channel, interface)
    checker = MessageChecker(ars, newsChannel)

    warnTrigger = CronTrigger(minute="*/5")

    with Scheduler() as scheduler:
        # Add schedules, configure tasks here
        scheduler.add_schedule(checker.sendNina, trigger=warnTrigger)
        scheduler.run_until_stopped()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="meshwarn",
        description="Periodically send German federal warnings over the Meshtastic network",
        epilog="ALPHA VERSION",
    )

    parser.add_argument(
        "-s",
        "--serial",
        "--port",
        help="The port of the device to connect to using serial, e.g. /dev/ttyUSB0. (defaults to trying to detect a port)",
    )
    parser.add_argument(
        "-c", "--channel", default="Warn", help="Channel to broadcast messages to"
    )
    parser.add_argument(
        "--ars", default="032410000000", help="Amtlicher Regionalschlüssel"
    )
    args = parser.parse_args()

    main(**vars(args))
