"""NADReceiverTCP class for TCP communication."""

import codecs
import socket
from time import sleep
from typing import Any, Dict, Iterable, Optional


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
    SOURCES_REVERSED = {value: key for key, value in SOURCES.items()}

    PORT = 50001
    BUFFERSIZE = 1024

    def __init__(self, host: str) -> None:
        """Setup globals."""
        self._host = host

    def _send(self, message: str, read_reply: bool = False) -> Optional[str]:
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
            self._send(self.CMD_POWERSAVE + self.CMD_OFF)

    def power_on(self) -> None:
        """Power the device on."""
        status = self.status()
        if not status:
            return None
        if not status['power']:
            self._send(self.CMD_ON, read_reply=True)
            sleep(0.5)

    def set_volume(self, volume: int) -> None:
        """Set volume level of the device. Accepts integer values 0-200."""
        if 0 <= volume <= 200:
            volume_hex = format(volume, "02x")
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
        if status['power']:
            if status['source'] != source:
                if source in self.SOURCES:
                    self._send(self.CMD_SOURCE + self.SOURCES[source],
                               read_reply=True)

    def available_sources(self) -> Iterable[str]:
        """Return a list of available sources."""
        return list(self.SOURCES.keys())
