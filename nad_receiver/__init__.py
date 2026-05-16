"""
NAD has an RS232 interface to control the receiver.

Not all receivers have all functions.
Functions can be found on the NAD website: http://nadelectronics.com/software
"""

import logging

from nad_receiver.nad_serial import NADReceiver, NADReceiverTelnet
from nad_receiver.nad_tcp import NADReceiverTCP

logging.basicConfig()

__all__ = ["NADReceiver", "NADReceiverTelnet", "NADReceiverTCP"]
