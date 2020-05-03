from nad_receiver.nad_transport import NadTransport
import re
from typing import Callable, Optional

class Fake_NAD_C_356BE_Transport(NadTransport):
    """A fake NAD C 356BE device.

    Behaves just like the real device (although faster).
    This is convenient for testing or when integrating this
    library into other applications, such as Home Assistant.
    """

    def __init__(self) -> None:
        self._toggle = {
            "Power": False,
            "Mute": False,
            "Tape1": False,
            "SpeakerA": True,
            "SpeakerB": False,
        }
        self._model = "C356BEE"
        self._version = "V1.02"
        self._sources = "CD TUNER DISC/MDC AUX TAPE2 MP".split()
        self._source = "CD"
        self._command_regex = re.compile(
            r"(?P<component>\w+)\.(?P<function>\w+)(?P<operator>[=\?\+\-])(?P<value>.*)"
        )

    def _toggle_property(self, property: str, operator: str, value: str) -> str:
        assert value in ["", "On", "Off"]
        val = self._toggle[property]
        if operator in ("+", "-"):
            val = not val
        if operator == "=":
            val = value == "On"
        self._toggle[property] = val
        return "On" if val else "Off"

    def communicate(self, command: str) -> str:
        match = self._command_regex.fullmatch(command)
        if not match or match.group("component") != "Main":
            return ""
        component = match.group("component")
        function = match.group("function")
        operator = match.group("operator")
        value = match.group("value")

        response: Callable[[Optional[str]], str] = lambda val: f"{component}.{function}{'=' + val if val else ''}"

        if function == "Version" and operator == "?":
            return response(self._version)
        if function == "Model" and operator == "?":
            return response(self._model)

        if function == "Power":
            return response(self._toggle_property(function, operator, value))

        if not self._toggle["Power"]:
            # Except for power, all other functions return "" when power is off.
            return ""

        if function in self._toggle.keys():
            return response(self._toggle_property(function, operator, value))

        if function == "Volume":
            # this thing doesn't report volume, but increase/decrease works and we do get the original command back
            if operator in ("+", "-"):
                return response(None) + operator

        if function == "Source":
            index = self._sources.index(self._source)
            assert index >= 0
            if operator == "+":
                index += 1
            if operator == "-":
                index -= 1
            if operator == "=":
                index = self._sources.index(value)
            if index < 0:
                index = len(self._sources) - 1
            if index == len(self._sources):
                index = 0
            self._source = self._sources[index]
            return response(self._source)

        return ""
