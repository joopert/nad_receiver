import re
import pytest  # type: ignore

import nad_receiver
from nad_receiver.nad_fake_transport import Fake_NAD_C_356BE_Transport

ON = "On"
OFF = "Off"


class Fake_NAD_C_356BE(nad_receiver.NADReceiver):
    """NAD Receiver with fake transport for testing."""
    def __init__(self):
        self.transport = Fake_NAD_C_356BE_Transport()


def test_NAD_C_356BE_old_api():
    # This test can be run with the real amplifier, just instantiate
    # the real transport instead of the fake one
    receiver = Fake_NAD_C_356BE()
    assert receiver.main_power("?") in (ON, OFF)

    # switch off
    assert receiver.main_power("=", OFF) == OFF
    assert receiver.main_power("?") == OFF
    assert receiver.main_power("+") == ON
    assert receiver.main_power("+") == OFF
    assert receiver.main_power("?") == OFF

    # C 356BE does not reply for commands other than power when off
    assert receiver.main_mute("?") is None

    assert receiver.main_power("=", ON) == ON
    assert receiver.main_power("?") == ON

    assert receiver.main_mute("=", OFF) == OFF
    assert receiver.main_mute("?") == OFF

    # Not a feature for this amp
    assert receiver.main_dimmer("?") is None

    # Stepper motor and this thing has no idea about the volume
    assert receiver.main_volume("?") is None

    # No exception
    assert receiver.main_volume("+") is None
    assert receiver.main_volume("-") is None

    assert receiver.main_version("?") == "V1.02"
    assert receiver.main_model("?") == "C356BEE"

    # Here the RS232 NAD manual seems to be slightly off / maybe the model is different
    # The manual claims:
    # CD Tuner Video Disc Ipod Tape2 Aux
    # My Amp:
    # CD Tuner Disc/MDC Aux Tape2 MP
    ### FIXME: Protocol V2 represents sources as strings, we should get these:
    # assert receiver.main_source("=", "AUX") == "AUX"
    # assert receiver.main_source("?") == "AUX"
    # assert receiver.main_source("=", "CD") == "CD"
    # assert receiver.main_source("?") == "CD"
    # assert receiver.main_source("+") == "TUNER"
    # assert receiver.main_source("-") == "CD"
    # assert receiver.main_source("+") == "TUNER"
    # assert receiver.main_source("+") == "DISC/MDC"
    # assert receiver.main_source("+") == "AUX"
    # assert receiver.main_source("+") == "TAPE2"
    # assert receiver.main_source("+") == "MP"
    # assert receiver.main_source("+") == "CD"
    # assert receiver.main_source("-") == "MP"

    # Tape monitor / tape 1 is independent of sources
    assert receiver.main_tape_monitor("=", OFF) == OFF
    assert receiver.main_tape_monitor("?") == OFF
    assert receiver.main_tape_monitor("=", ON) == ON
    assert receiver.main_tape_monitor("+") == OFF

    assert receiver.main_speaker_a("=", OFF) == OFF
    assert receiver.main_speaker_a("?") == OFF
    assert receiver.main_speaker_a("=", ON) == ON
    assert receiver.main_speaker_a("?") == ON
    assert receiver.main_speaker_a("+") == OFF
    assert receiver.main_speaker_a("+") == ON
    assert receiver.main_speaker_a("-") == OFF
    assert receiver.main_speaker_a("-") == ON

    assert receiver.main_speaker_b("=", OFF) == OFF
    assert receiver.main_speaker_b("?") == OFF

    assert receiver.main_power("=", OFF) == OFF


def test_NAD_C_356BE_new_api():
    # This test can be run with the real amplifier, just instantiate
    # the real transport instead of the fake one
    receiver = Fake_NAD_C_356BE()
    assert receiver.main.power.get() in (ON, OFF)

    # switch off
    assert receiver.main.power.set(OFF) == OFF
    assert receiver.main.power.get() == OFF
    assert receiver.main.power.increase() == ON
    assert receiver.main.power.increase() == OFF
    assert receiver.main.power.get() == OFF

    # C 356BE does not reply for commands other than power when off
    with pytest.raises(ValueError):
        receiver.main.mute.get()

    assert receiver.main.power.set(ON) == ON
    assert receiver.main.power.get() == ON

    assert receiver.main.mute.set(OFF) == OFF
    assert receiver.main.mute.get() == OFF

    # Not a feature for this amp
    with pytest.raises(ValueError):
        receiver.main.dimmer.get()

    # Stepper motor and this thing has no idea about the volume
    with pytest.raises(ValueError):
        receiver.main.volume.get()

    # No exception
    assert receiver.main.volume.increase() is None
    assert receiver.main.volume.decrease() is None

    assert receiver.main.version.get() == "V1.02"
    assert receiver.main.model.get() == "C356BEE"

    # Here the RS232 NAD manual seems to be slightly off / maybe the model is different
    # The manual claims:
    # CD Tuner Video Disc Ipod Tape2 Aux
    # My Amp:
    # CD Tuner Disc/MDC Aux Tape2 MP
    assert receiver.main.source.set("AUX") == "AUX"
    assert receiver.main.source.get() == "AUX"
    assert receiver.main.source.set("CD") == "CD"
    assert receiver.main.source.get() == "CD"
    assert receiver.main.source.increase() == "TUNER"
    assert receiver.main.source.decrease() == "CD"
    assert receiver.main.source.increase() == "TUNER"
    assert receiver.main.source.increase() == "DISC/MDC"
    assert receiver.main.source.increase() == "AUX"
    assert receiver.main.source.increase() == "TAPE2"
    assert receiver.main.source.increase() == "MP"
    assert receiver.main.source.increase() == "CD"
    assert receiver.main.source.decrease() == "MP"

    # Tape monitor / tape 1 is independent of sources
    assert receiver.main.tape_monitor.set(OFF) == OFF
    assert receiver.main.tape_monitor.get() == OFF
    assert receiver.main.tape_monitor.set(ON) == ON
    assert receiver.main.tape_monitor.increase() == OFF

    assert receiver.main.speaker_a.set(OFF) == OFF
    assert receiver.main.speaker_a.get() == OFF
    assert receiver.main.speaker_a.set(ON) == ON
    assert receiver.main.speaker_a.get() == ON
    assert receiver.main.speaker_a.increase() == OFF
    assert receiver.main.speaker_a.increase() == ON
    assert receiver.main.speaker_a.decrease() == OFF
    assert receiver.main.speaker_a.decrease() == ON

    assert receiver.main.speaker_b.set(OFF) == OFF
    assert receiver.main.speaker_b.get() == OFF

    assert receiver.main.power.set(OFF) == OFF


def test_dynamic_api():
    receiver = Fake_NAD_C_356BE()
    assert receiver.main.power.get() in (ON, OFF)

    # invalid attributes result in attribute error
    with pytest.raises(AttributeError):
        receiver.foo
    with pytest.raises(AttributeError):
        receiver.foo.bar

    # valid attributes work and have a good __repr__
    assert str(receiver.main) == "NADReceiver.main"
    assert str(receiver.main.power) == "NADReceiver.main.power"
    assert str(receiver.main.power.get) == "NADReceiver.main.power.get"
    assert str(receiver.main.power.increase) == "NADReceiver.main.power.increase"
    assert str(receiver.main.power.decrease) == "NADReceiver.main.power.decrease"
    assert str(receiver.main.power.set) == "NADReceiver.main.power.set"

    # functions on dynamic objects can be called
    assert callable(receiver.main.power.get)
    assert callable(receiver.main.power.set)
    assert callable(receiver.main.power.increase)
    assert callable(receiver.main.power.decrease)

    # attributes can not be called
    with pytest.raises(TypeError, match="object is not callable"):
        receiver.main()
    with pytest.raises(TypeError, match="object is not callable"):
        receiver.main.power()

    # invalid properties are AttributeErrors
    with pytest.raises(AttributeError):
        receiver.main.power.invalid
    with pytest.raises(AttributeError):
        receiver.main.power.invalid()
    with pytest.raises(AttributeError):
        receiver.main.power.get.invalid_too
