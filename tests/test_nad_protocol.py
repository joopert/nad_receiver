import re
import pytest  # type: ignore
import pytest_asyncio  # type: ignore

import nad_receiver
from nad_receiver.nad_fake_transport import Fake_NAD_C_356BE_Transport

ON = "On"
OFF = "Off"


class Fake_NAD_C_356BE(nad_receiver.NADReceiver):
    """NAD Receiver with fake transport for testing."""
    def __init__(self) -> None:
        self.transport = Fake_NAD_C_356BE_Transport()


@pytest.mark.asyncio
async def test_NAD_C_356BE() -> None:
    # This test can be run with the real amplifier, just instantiate
    # the real transport instead of the fake one
    receiver = Fake_NAD_C_356BE()
    assert await receiver.main_power("?") in (ON, OFF)

    # switch off
    assert await receiver.main_power("=", OFF) == OFF
    assert await receiver.main_power("?") == OFF
    assert await receiver.main_power("+") == ON
    assert await receiver.main_power("+") == OFF
    assert await receiver.main_power("?") == OFF

    # C 356BE does not reply for commands other than power when off
    assert await receiver.main_mute("?") is None

    assert await receiver.main_power("=", ON) == ON
    assert await receiver.main_power("?") == ON

    assert await receiver.main_mute("=", OFF) == OFF
    assert await receiver.main_mute("?") == OFF

    # Not a feature for this amp
    assert await receiver.main_dimmer("?") is None

    # Stepper motor and this thing has no idea about the volume
    assert await receiver.main_volume("?") is None

    # No exception
    assert await receiver.main_volume("+") is None
    assert await receiver.main_volume("-") is None

    assert await receiver.main_version("?") == "V1.02"
    assert await receiver.main_model("?") == "C356BEE"

    # Here the RS232 NAD manual seems to be slightly off / maybe the model is different
    # The manual claims:
    # CD Tuner Video Disc Ipod Tape2 Aux
    # My Amp:
    # CD Tuner Disc/MDC Aux Tape2 MP
    # Protocol V2 represents sources as strings, we should get these:
    assert await receiver.main_source("=", "AUX") == "AUX"
    assert await receiver.main_source("?") == "AUX"
    assert await receiver.main_source("=", "CD") == "CD"
    assert await receiver.main_source("?") == "CD"
    assert await receiver.main_source("+") == "TUNER"
    assert await receiver.main_source("-") == "CD"
    assert await receiver.main_source("+") == "TUNER"
    assert await receiver.main_source("+") == "DISC/MDC"
    assert await receiver.main_source("+") == "AUX"
    assert await receiver.main_source("+") == "TAPE2"
    assert await receiver.main_source("+") == "MP"
    assert await receiver.main_source("+") == "CD"
    assert await receiver.main_source("-") == "MP"

    # Tape monitor / tape 1 is independent of sources
    assert await receiver.main_tape_monitor("=", OFF) == OFF
    assert await receiver.main_tape_monitor("?") == OFF
    assert await receiver.main_tape_monitor("=", ON) == ON
    assert await receiver.main_tape_monitor("+") == OFF

    assert await receiver.main_speaker_a("=", OFF) == OFF
    assert await receiver.main_speaker_a("?") == OFF
    assert await receiver.main_speaker_a("=", ON) == ON
    assert await receiver.main_speaker_a("?") == ON
    assert await receiver.main_speaker_a("+") == OFF
    assert await receiver.main_speaker_a("+") == ON
    assert await receiver.main_speaker_a("-") == OFF
    assert await receiver.main_speaker_a("-") == ON

    assert await receiver.main_speaker_b("=", OFF) == OFF
    assert await receiver.main_speaker_b("?") == OFF

    assert await receiver.main_power("=", OFF) == OFF
