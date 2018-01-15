"""
NAD has an RS232 interface to control the receiver.

Not all receivers have all functions.
Functions can be found on the NAD website: http://nadelectronics.com/software
"""

import codecs
import socket
from time import sleep
from nad_receiver.nad_commands import CMDS
import serial  # pylint: disable=import-error
import threading
import telnetlib

DEFAULT_TIMEOUT = 1
DEFAULT_WRITE_TIMEOUT = 1


class NADReceiver(object):
    """NAD receiver."""

    def __init__(self, serial_port, timeout=DEFAULT_TIMEOUT,
                 write_timeout=DEFAULT_WRITE_TIMEOUT):
        """Create RS232 connection."""
        self.ser = serial.Serial(serial_port, baudrate=115200, timeout=timeout,
                                 write_timeout=write_timeout)
        self.lock = threading.Lock()

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

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.lock.acquire()

        self.ser.write(''.join(['\r', cmd, '\r']).encode('utf-8'))

        self.ser.read(1)  # NAD uses the prefix and suffix \r.
        # With this we read the first \r and skip it
        msg = self.ser.read_until(bytes('\r'.encode()))
        self.lock.release()

        return msg.decode().strip().split('=')[1]
        # b'Main.Volume=-12\r will return -12

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


class NADReceiverTCP(object):
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

    def __init__(self, host):
        """Setup globals."""
        self._host = host

    def _send(self, message, read_reply=False):
        """Send a command string to the amplifier."""
        sock = None
        for tries in range(0, 3):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self._host, self.PORT))
                break
            except (ConnectionError, BrokenPipeError):
                if tries == 3:
                    print("socket connect failed.")
                    return
                sleep(0.1)
        sock.send(codecs.decode(message, 'hex_codec'))
        if read_reply:
            sleep(0.1)
            reply = ''
            tries = 0
            max_tries = 20
            while len(reply) < len(message) and tries < max_tries:
                try:
                    reply += codecs.encode(sock.recv(self.BUFFERSIZE), 'hex')\
                        .decode("utf-8")
                except (ConnectionError, BrokenPipeError):
                    pass
                tries += 1
            sock.close()
            if tries >= max_tries:
                return
            return reply
        sock.close()

    def status(self):
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
            return

        # split reply into parts of 10 characters
        num_chars = 10
        nad_status = [nad_reply[i:i + num_chars]
                      for i in range(0, len(nad_reply), num_chars)]

        return {'volume': int(nad_status[0][-2:], 16),
                'power': nad_status[1][-2:] == '01',
                'muted': nad_status[2][-2:] == '01',
                'source': self.SOURCES_REVERSED[nad_status[3][-2:]]}

    def power_off(self):
        """Power the device off."""
        status = self.status()
        if status['power']:  # Setting power off when it is already off can cause hangs
            self._send(self.CMD_POWERSAVE + self.CMD_OFF)

    def power_on(self):
        """Power the device on."""
        status = self.status()
        if not status['power']:
            self._send(self.CMD_ON, read_reply=True)
            sleep(0.5)  # Give NAD7050 some time before next command

    def set_volume(self, volume):
        """Set volume level of the device. Accepts integer values 0-200."""
        if 0 <= volume <= 200:
            volume = format(volume, "02x")  # Convert to hex
            self._send(self.CMD_VOLUME + volume)

    def mute(self):
        """Mute the device."""
        self._send(self.CMD_MUTE, read_reply=True)

    def unmute(self):
        """Unmute the device."""
        self._send(self.CMD_UNMUTE)
 
    def select_source(self, source):
        """Select a source from the list of sources."""
        status = self.status()
        if status['power']:  # Changing source when off may hang NAD7050
            if status['source'] != source:  # Setting the source to the current source will hang the NAD7050
                if source in self.SOURCES:
                    self._send(self.CMD_SOURCE + self.SOURCES[source], read_reply=True)

    def available_sources(self):
        """Return a list of available sources."""
        return list(self.SOURCES.keys())


class NADReceiverTelnet(NADReceiver):
    """
    Support NAD amplifiers that use telnet for communication.
    Supports all commands from the RS232 base class

    Known supported model: Nad T787.
    """
    def __init__(self, host, port=23, timeout=DEFAULT_TIMEOUT):
        """Create Telnet connection."""
        self.telnet = telnetlib.Telnet(host, port, 5)
        self.timeout = timeout
        # Some versions of the firmware report Main.Model=T787.
        # some versions do not, we want to clear that line
        msg = self.telnet.read_until('\n'.encode(), self.timeout)
        #msg.decode().strip().split('=')[1]

    def __del__(self):
        """
        Close any telnet session
        """
        self.telnet.close()

    def exec_command(self, domain, function, operator, value=None):
        """
        Write a command to the receiver and read the value it returns.
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

        # Not possible to test for open Telnet connection
        # let is raise if any issues
        # For telnet the first \r / \n is recommended only
        self.telnet.write((''.join(['\r', cmd, '\n']).encode()))

        found = False
        while not found:
            msg = self.telnet.read_until('\n'.encode(), self.timeout)
            msg = msg.decode().strip('\r\n')
            #print("NAD reponded with '%s'" % msg)
            # Wait for the response that equals the requested domain.function
            if msg.strip().split('=')[0].lower() == '.'.join([domain, function]).lower():
                found = True

        return msg.strip().split('=')[1]
        # b'Main.Volume=-12\r will return -12
