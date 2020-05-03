"""
NAD has an RS232 interface to control the receiver.

Not all receivers have all functions.
Functions can be found on the NAD website: http://nadelectronics.com/software
"""

import codecs
import socket
from time import sleep
from typing import Any, Dict, Iterable, Optional, Union
from nad_receiver.nad_commands import CMDS
from nad_receiver.nad_transport import (NadTransport, SerialPortTransport, TelnetTransport,
                                        DEFAULT_TIMEOUT)

import logging


logging.basicConfig()
_LOGGER = logging.getLogger("nad_receiver")
# Uncomment this line to see all communication with the device:
# _LOGGER.setLevel(logging.DEBUG)


class NADReceiver:
    """NAD receiver."""
    transport: NadTransport

    def __init__(self, serial_port: str) -> None:
        """Create RS232 connection."""
        self.transport = SerialPortTransport(serial_port)

    def exec_command(self, domain: str, function: str, operator: str, value: Optional[str] =None) -> Optional[str]:
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

    def main_dimmer(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Dimmer."""
        return self.exec_command('main', 'dimmer', operator, value)

    def main_mute(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Mute."""
        return self.exec_command('main', 'mute', operator, value)

    def main_power(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Power."""
        return self.exec_command('main', 'power', operator, value)

    def main_volume(self, operator: str, value: Optional[str] =None) -> Optional[float]:
        """
        Execute Main.Volume.

        Returns float
        """
        volume = self.exec_command('main', 'volume', operator, value)
        if volume is None:
            return None
        try:
            res = float(volume)
            return res
        except (ValueError):
            pass

        return None

    def main_ir(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.IR."""
        return self.exec_command('main', 'ir', operator, value)

    def main_listeningmode(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.ListeningMode."""
        return self.exec_command('main', 'listeningmode', operator, value)

    def main_sleep(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Sleep."""
        return self.exec_command('main', 'sleep', operator, value)

    def main_tape_monitor(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Tape1."""
        return self.exec_command('main', 'tape_monitor', operator, value)

    def main_speaker_a(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.SpeakerA."""
        return self.exec_command('main', 'speaker_a', operator, value)

    def main_speaker_b(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.SpeakerB."""
        return self.exec_command('main', 'speaker_b', operator, value)

    def main_source(self, operator: str, value: Optional[str]=None) -> Optional[Union[int, str]]:
        """
        Execute Main.Source.

        Returns int
        """
        source = self.exec_command('main', 'source', operator, value)
        if source is None:
            return None
        try:
            # try to return as integer, some receivers return numbers
            return int(source)
        except ValueError:
            # return source as string
            return source
        return None

    def main_version(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Version."""
        return self.exec_command('main', 'version', operator, value)

    def main_model(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Main.Model."""
        return self.exec_command('main', 'model', operator, value)

    def tuner_am_frequency(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Tuner.AM.Frequence."""
        return self.exec_command('tuner', 'am_frequency', operator, value)

    def tuner_am_preset(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Tuner.AM.Preset."""
        return self.exec_command('tuner', 'am_preset', operator, value)

    def tuner_band(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Tuner.Band."""
        return self.exec_command('tuner', 'band', operator, value)

    def tuner_fm_frequency(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Tuner.FM.Frequence."""
        return self.exec_command('tuner', 'fm_frequency', operator, value)

    def tuner_fm_mute(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Tuner.FM.Mute."""
        return self.exec_command('tuner', 'fm_mute', operator, value)

    def tuner_fm_preset(self, operator: str, value: Optional[str] =None) -> Optional[str]:
        """Execute Tuner.FM.Preset."""
        return self.exec_command('tuner', 'fm_preset', operator, value)


class NADReceiverTelnet(NADReceiver):
    """
    Support NAD amplifiers that use telnet for communication.
    Supports all commands from the RS232 base class

    Known supported model: Nad T787.
    """

    def __init__(self, host: str, port: int =23, timeout: int =DEFAULT_TIMEOUT):
        """Create NADTelnet."""
        self.transport = TelnetTransport(host, port, timeout)


class NADReceiverTCP:
    """
    Support NAD amplifiers that use tcp for communication.

    Known supported model: Nad D 7050.
    """

    POLL_VOLUME = "0001020204"
    POLL_POWER = "0001020209"
    POLL_MUTED = "000102020a"
    POLL_SOURCE = "0001020203"

    CMD_POWERSAVE = "00010207000001020207"
    CMD_OFF = "0001020900"
    CMD_ON = "0001020901"
    CMD_VOLUME = "00010204"
    CMD_MUTE = "0001020a01"
    CMD_UNMUTE = "0001020a00"
    CMD_SOURCE = "00010203"

    SOURCES = {'Coaxial 1': '00', 'Coaxial 2': '01', 'Optical 1': '02',
               'Optical 2': '03', 'Computer': '04', 'Airplay': '05',
               'Dock': '06', 'Bluetooth': '07'}
    SOURCES_REVERSED = {value: key for key, value in
                        SOURCES.items()}

    PORT = 50001
    BUFFERSIZE = 1024

    def __init__(self, host: str) -> None:
        """Setup globals."""
        self._host = host

    def _send(self, message: str, read_reply: bool =False) -> Optional[str]:
        """Send a command string to the amplifier."""
        sock: socket.socket
        for tries in range(0, 3):
            try:
                sock = socket.create_connection((self._host, self.PORT),
                                                timeout=5)
                break
            except socket.timeout:
                print("Socket connection timed out.")
                return None
            except (ConnectionError, BrokenPipeError):
                if tries == 2:
                    print("socket connect failed.")
                    return None
                sleep(0.1)
        if not sock:
            return None
        with sock:
            sock.send(codecs.decode(message.encode(), encoding='hex_codec'))
            if read_reply:
                sleep(0.1)
                reply = ''
                tries = 0
                max_tries = 20
                while len(reply) < len(message) and tries < max_tries:
                    try:
                        reply += codecs.encode(sock.recv(self.BUFFERSIZE), 'hex')\
                            .decode("utf-8")
                        return reply
                    except (ConnectionError, BrokenPipeError):
                        pass
                    tries += 1
        return None

    def status(self) -> Optional[Dict[str, Any]]:
        """
        Return the status of the device.

        Returns a dictionary with keys 'volume' (int 0-200) , 'power' (bool),
         'muted' (bool) and 'source' (str).
        """
        nad_reply = self._send(self.POLL_VOLUME +
                               self.POLL_POWER +
                               self.POLL_MUTED +
                               self.POLL_SOURCE, read_reply=True)
        if nad_reply is None:
            return None

        # split reply into parts of 10 characters
        num_chars = 10
        nad_status = [nad_reply[i:i + num_chars]
                      for i in range(0, len(nad_reply), num_chars)]

        return {'volume': int(nad_status[0][-2:], 16),
                'power': nad_status[1][-2:] == '01',
                'muted': nad_status[2][-2:] == '01',
                'source': self.SOURCES_REVERSED[nad_status[3][-2:]]}

    def power_off(self) -> None:
        """Power the device off."""
        status = self.status()
        if not status:
            return None
        if status['power']:
            #  Setting power off when it is already off can cause hangs
            self._send(self.CMD_POWERSAVE + self.CMD_OFF)

    def power_on(self) -> None:
        """Power the device on."""
        status = self.status()
        if not status:
            return None
        if not status['power']:
            self._send(self.CMD_ON, read_reply=True)
            sleep(0.5)  # Give NAD7050 some time before next command

    def set_volume(self, volume: int) -> None:
        """Set volume level of the device. Accepts integer values 0-200."""
        if 0 <= volume <= 200:
            volume_hex = format(volume, "02x")  # Convert to hex
            self._send(self.CMD_VOLUME + volume_hex)

    def mute(self) -> None:
        """Mute the device."""
        self._send(self.CMD_MUTE, read_reply=True)

    def unmute(self) -> None:
        """Unmute the device."""
        self._send(self.CMD_UNMUTE)

    def select_source(self, source: str) -> None:
        """Select a source from the list of sources."""
        status = self.status()
        if not status:
            return None
        if status['power']:  # Changing source when off may hang NAD7050
            # Setting the source to the current source will hang the NAD7050
            if status['source'] != source:
                if source in self.SOURCES:
                    self._send(self.CMD_SOURCE + self.SOURCES[source],
                               read_reply=True)

    def available_sources(self) -> Iterable[str]:
        """Return a list of available sources."""
        return list(self.SOURCES.keys())
