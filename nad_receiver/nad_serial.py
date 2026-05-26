"""NADReceiver classes for serial/RS232 and Telnet communication."""

from typing import Optional, Union

from nad_receiver.nad_commands import CMDS
from nad_receiver.nad_transport import (NadTransport, SerialPortTransport,
                                        TelnetTransportWrapper, DEFAULT_TIMEOUT)

import logging

_LOGGER = logging.getLogger("nad_receiver")


class NADReceiver:
    """NAD receiver."""
    transport: NadTransport

    def __init__(self, serial_port: str) -> None:
        """Create RS232 connection."""
        self.transport = SerialPortTransport(serial_port)

    def exec_command(self, domain: str, function: str, operator: str, value: Optional[str] = None) -> Optional[str]:
        """
        Write a command to the receiver and read the value it returns.

        The receiver will always return a value, also when setting a value.
        """
        if operator in CMDS[domain][function]['supported_operators']:
            if operator == '=' and value is None:
                raise ValueError('No value provided')

            cmd = ''.join([CMDS[domain][function]['cmd'], operator])  # type: ignore
            assert isinstance(cmd, str)
            if value:
                cmd = cmd + value
        else:
            raise ValueError('Invalid operator provided %s' % operator)

        try:
            msg = self.transport.communicate(cmd)
            _LOGGER.debug(f"sent: '{cmd}' reply: '{msg}'")
            return msg.split('=')[1]
        except IndexError:
            pass
        return None

    def main_dimmer(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Dimmer."""
        return self.exec_command('main', 'dimmer', operator, value)

    def main_mute(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Mute."""
        return self.exec_command('main', 'mute', operator, value)

    def main_power(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Power."""
        return self.exec_command('main', 'power', operator, value)

    def main_volume(self, operator: str, value: Optional[str] = None) -> Optional[float]:
        """
        Execute Main.Volume.

        Returns float
        """
        if value is not None:
            volume = self.exec_command('main', 'volume', operator, str(value))
        else:
            volume = self.exec_command('main', 'volume', operator)

        if volume is None:
            return None
        try:
            return float(volume)
        except ValueError:
            pass
        return None

    def main_ir(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.IR."""
        return self.exec_command('main', 'ir', operator, value)

    def main_listeningmode(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.ListeningMode."""
        return self.exec_command('main', 'listeningmode', operator, value)

    def main_sleep(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Sleep."""
        return self.exec_command('main', 'sleep', operator, value)

    def main_tape_monitor(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Tape1."""
        return self.exec_command('main', 'tape_monitor', operator, value)

    def main_speaker_a(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.SpeakerA."""
        return self.exec_command('main', 'speaker_a', operator, value)

    def main_speaker_b(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.SpeakerB."""
        return self.exec_command('main', 'speaker_b', operator, value)

    def main_source(self, operator: str, value: Optional[str] = None) -> Optional[Union[int, str]]:
        """
        Execute Main.Source.

        Returns int
        """
        if value is not None:
            source = self.exec_command('main', 'source', operator, str(value))
        else:
            source = self.exec_command('main', 'source', operator)

        if source is None:
            return None
        try:
            return int(source)
        except ValueError:
            return source

    def main_version(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Version."""
        return self.exec_command('main', 'version', operator, value)

    def main_model(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Main.Model."""
        return self.exec_command('main', 'model', operator, value)

    def tuner_am_frequency(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Tuner.AM.Frequence."""
        return self.exec_command('tuner', 'am_frequency', operator, value)

    def tuner_am_preset(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Tuner.AM.Preset."""
        return self.exec_command('tuner', 'am_preset', operator, value)

    def tuner_band(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Tuner.Band."""
        return self.exec_command('tuner', 'band', operator, value)

    def tuner_fm_frequency(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Tuner.FM.Frequence."""
        return self.exec_command('tuner', 'fm_frequency', operator, value)

    def tuner_fm_mute(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Tuner.FM.Mute."""
        return self.exec_command('tuner', 'fm_mute', operator, value)

    def tuner_fm_preset(self, operator: str, value: Optional[str] = None) -> Optional[str]:
        """Execute Tuner.FM.Preset."""
        return self.exec_command('tuner', 'fm_preset', operator, value)


class NADReceiverTelnet(NADReceiver):
    """
    Support NAD amplifiers that use telnet for communication.
    Supports all commands from the RS232 base class

    Known supported model: Nad T787.
    """

    def __init__(self, host: str, port: int = 23, timeout: int = DEFAULT_TIMEOUT):
        """Create NADTelnet."""
        self.transport = TelnetTransportWrapper(host, port, timeout)
