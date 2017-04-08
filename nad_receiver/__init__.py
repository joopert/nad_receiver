"""
NAD has an RS232 interface to control the receiver.

Not all receivers have all functions.
Functions can be found on the NAD website: http://nadelectronics.com/software
"""

import codecs
import socket
from nad_receiver.nad_commands import CMDS
import serial  # pylint: disable=import-error

DEFAULT_TIMEOUT = 1
DEFAULT_WRITE_TIMEOUT = 1


class NADReceiver(object):
    """NAD receiver."""

    def __init__(self, serial_port, timeout=DEFAULT_TIMEOUT,
                 write_timeout=DEFAULT_WRITE_TIMEOUT):
        """Create RS232 connection."""
        self.ser = serial.Serial(serial_port, baudrate=115200, timeout=timeout,
                                 write_timeout=write_timeout)

    def exec_command(self, domain, function, operator, value=None):
        """
        Write a command to the receiver and read the value it returns.

        The receiver will always return a value, also when setting a value.
        """
        if operator in CMDS[domain][function]['supported_operators']:
            if operator is '=' and value is None:
                raise ValueError('No value provided')

            if value is None:
                cmd = ''.join([CMDS[domain][function]['cmd'], operator])
            else:
                cmd = ''.join(
                    [CMDS[domain][function]['cmd'], operator, str(value)])
        else:
            raise ValueError('Invalid operator provided %s' % operator)

        if not self.ser.is_open:
            self.ser.open()

        self.ser.write(''.join(['\r', cmd, '\r']).encode('utf-8'))

        self.ser.read(1)  # NAD uses the prefix and suffix \r.
        # With this we read the first \r and skip it
        msg = self.ser.read_until(bytes('\r'.encode()))

        return msg.decode().strip().split('=')[
            1]  # b'Main.Volume=-12\r will return -12

    def main_dimmer(self, operator, value=None):
        """Execute Main.Dimmer."""
        return self.exec_command('main', 'dimmer', operator, value)

    def main_mute(self, operator, value=None):
        """Execute Main.Mute."""
        return self.exec_command('main', 'mute', operator, value)

    def main_power(self, operator, value=None):
        """Execute Main.Power."""
        return self.exec_command('main', 'power', operator, value)

    def main_volume(self, operator, value=None):
        """
        Execute Main.Volume.

        Returns int
        """
        return int(self.exec_command('main', 'volume', operator, value))

    def main_ir(self, operator, value=None):
        """Execute Main.IR."""
        return self.exec_command('main', 'ir', operator, value)

    def main_listeningmode(self, operator, value=None):
        """Execute Main.ListeningMode."""
        return self.exec_command('main', 'listeningmode', operator, value)

    def main_sleep(self, operator, value=None):
        """Execute Main.Sleep."""
        return self.exec_command('main', 'sleep', operator, value)

    def main_source(self, operator, value=None):
        """
        Execute Main.Source.

        Returns int
        """
        return int(self.exec_command('main', 'source', operator, value))

    def main_version(self, operator, value=None):
        """Execute Main.Version."""
        return self.exec_command('main', 'version', operator, value)

    def tuner_am_frequency(self, operator, value=None):
        """Execute Tuner.AM.Frequence."""
        return self.exec_command('tuner', 'am_frequency', operator, value)

    def tuner_am_preset(self, operator, value=None):
        """Execute Tuner.AM.Preset."""
        return self.exec_command('tuner', 'am_preset', operator, value)

    def tuner_band(self, operator, value=None):
        """Execute Tuner.Band."""
        return self.exec_command('tuner', 'band', operator, value)

    def tuner_fm_frequency(self, operator, value=None):
        """Execute Tuner.FM.Frequence."""
        return self.exec_command('tuner', 'fm_frequency', operator, value)

    def tuner_fm_mute(self, operator, value=None):
        """Execute Tuner.FM.Mute."""
        return self.exec_command('tuner', 'fm_mute', operator, value)

    def tuner_fm_preset(self, operator, value=None):
        """Execute Tuner.FM.Preset."""
        return self.exec_command('tuner', 'fm_preset', operator, value)

class NADtcp(object):

    def __init__(self, host):
        self._host = host

    def send(self, message, read_reply=False):
        """Send a command string to the amplifier."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._host, self._port))
        except Exception:
            return
        message = codecs.decode(message, 'hex_codec')
        sock.send(message)
        sleep(0.5)
        if read_reply:
            reply = sock.recv(self._buffersize)
            sock.close()
            return reply
        sock.close()
        sleep(1)

    def status(self):
        query_all = \
            "000102020400010202060001020207000102020800010202050001020209" \
            "000102020a000102020c0001020203000102020d00010207000001020800"

        nad_reply = self.send(query_all, read_reply=True)
        if nad_reply is None:
            return
        nad_reply = codecs.encode(nad_reply, 'hex').decode("utf-8")

        # split reply into parts of 10 characters
        num_chars = 10
        nad_status = [nad_reply[i:i + num_chars]
                      for i in range(0, len(nad_reply), num_chars)]
        return nad_status
