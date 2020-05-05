import re
import operator
import pytest  # type: ignore

import nad_receiver
from nad_receiver.nad_fake_transport import *

ON = "On"
OFF = "Off"


class Fake_NAD_Telnet(nad_receiver.NADReceiver):
    """NAD Receiver with fake transport for testing."""
    def __init__(self) -> None:
        self.transport = Fake_NAD_Telnet_Transport()


class Fake_NAD_C_356BE(nad_receiver.NADReceiver):
    """NAD Receiver with fake transport for testing."""
    def __init__(self) -> None:
        self.transport = Fake_NAD_C_356BE_Transport()


CommonTests = [
    ("receiver.main_power", "=", OFF, operator.eq),
    ("receiver.main_power", "?", OFF, operator.eq),
    ("receiver.main_power", "+", ON, operator.eq),
    ("receiver.main_power", "+", OFF, operator.eq),
    ("receiver.main_power", "?", OFF, operator.eq),
    ("receiver.main_mute", "?", None, operator.is_),

    ("receiver.main_power", "=", ON, operator.eq),
    ("receiver.main_power", "?", ON, operator.eq),

    ("receiver.main_mute", "=", OFF, operator.eq),
    ("receiver.main_mute", "?", OFF, operator.eq),

    # Not a feature for this amp
    ("receiver.main_dimmer", "?", None, operator.is_),

    # Stepper motor and this thing has no idea about the volume
    ("receiver.main_volume", "?", None, operator.is_),

    # No exception
    ("receiver.main_volume", "+", None, operator.is_),
    ("receiver.main_volume", "-", None, operator.is_),

    # Here the RS232 NAD manual seems to be slightly off / maybe the model is different
    # The manual claims:
    # CD Tuner Video Disc Ipod Tape2 Aux
    # My Amp:
    # CD Tuner Disc/MDC Aux Tape2 MP
    # Protocol V2 represents sources as strings, we should get these:
    ("receiver.main_source", "=", "AUX", operator.eq),
    ("receiver.main_source", "?", "AUX", operator.eq),
    ("receiver.main_source", "=", "CD", operator.eq),
    ("receiver.main_source", "?", "CD", operator.eq),
    ("receiver.main_source", "+", "TUNER", operator.eq),
    ("receiver.main_source", "-", "CD", operator.eq),
    ("receiver.main_source", "+", "TUNER", operator.eq),
    ("receiver.main_source", "+", "DISC/MDC", operator.eq),
    ("receiver.main_source", "+", "AUX", operator.eq),
    ("receiver.main_source", "+", "TAPE2", operator.eq),
    ("receiver.main_source", "+", "MP", operator.eq),
    ("receiver.main_source", "+", "CD", operator.eq),
    ("receiver.main_source", "-", "MP", operator.eq),

    # Tape monitor / tape 1 is independent of sources
    ("receiver.main_tape_monitor", "=", OFF, operator.eq),
    ("receiver.main_tape_monitor", "?", OFF, operator.eq),
    ("receiver.main_tape_monitor", "=", ON, operator.eq),
    ("receiver.main_tape_monitor", "+", OFF, operator.eq),

    ("receiver.main_speaker_a", "=", OFF, operator.eq),
    ("receiver.main_speaker_a", "?", OFF, operator.eq),
    ("receiver.main_speaker_a", "=", ON, operator.eq),
    ("receiver.main_speaker_a", "?", ON, operator.eq),
    ("receiver.main_speaker_a", "+", OFF, operator.eq),
    ("receiver.main_speaker_a", "+", ON, operator.eq),
    ("receiver.main_speaker_a", "-", OFF, operator.eq),
    ("receiver.main_speaker_a", "-", ON, operator.eq),

    ("receiver.main_speaker_b", "=", OFF, operator.eq),
    ("receiver.main_speaker_b", "?", OFF, operator.eq),

    ("receiver.main_power", "=", OFF, operator.eq),
]

SerialTests = [
    ("receiver.main_version", "?", "V1.02", operator.eq),
    ("receiver.main_model", "?", "C356BEE", operator.eq),
] + CommonTests

TelnetTests = [
    ("receiver.main_version", "?", "V2.10", operator.eq),
    ("receiver.main_model", "?", "T787", operator.eq),
] + CommonTests

# The NAD Units to test
NAD_Units = [
    (Fake_NAD_C_356BE(), SerialTests),
    (Fake_NAD_Telnet(), TelnetTests),
]


def _test_command(receiver, func, command, response, op) -> None:
    assert op(eval(func)(command, response), response)


def _test_commands(receiver, tests) -> None:
    for func, command, response, op in tests:
        _test_command(receiver, func, command, response, op)


def test_protocol() -> None:
    # This test can be run with the real amplifier, just instantiate
    # the real transport instead of the fake one
    for receiver, tests in NAD_Units:
        _test_commands(receiver, tests)
