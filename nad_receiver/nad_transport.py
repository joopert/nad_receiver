import abc
import asyncio
import serialx  # type: ignore
import telnetlib3  # type: ignore

from typing import Optional

import logging

logging.basicConfig()
_LOGGER = logging.getLogger("nad_receiver.transport")


DEFAULT_TIMEOUT = 1


class NadTransport(abc.ABC):
    @abc.abstractmethod
    async def communicate(self, command: str) -> str:
        pass


class SerialPortTransport(NadTransport):
    """Transport for NAD protocol over RS-232."""

    def __init__(self, url: str) -> None:
        """Create RS232 connection."""
        self.ser = serialx.async_serial_for_url(
            url=url,
            baudrate=115200,
        )
        self.lock = asyncio.Lock()

    async def _open_connection(self) -> None:
        if not self.ser.is_open:
            await self.ser.open()
            _LOGGER.debug("serial open: %s", self.ser.is_open)

    async def communicate(self, command: str) -> str:
        async with self.lock:
            await self._open_connection()

            await self.ser.write(f"\r{command}\r".encode("utf-8"))
            # To get complete messages, always read until we get '\r'
            # Messages will be of the form '\rMESSAGE\r' which
            # serialx handles nicely
            msg = await asyncio.wait_for(self.ser.readuntil(serialx.CR), timeout=DEFAULT_TIMEOUT)
            if not msg.strip():  # discard '\r' if it was sent
                msg = await asyncio.wait_for(self.ser.readuntil(serialx.CR), timeout=DEFAULT_TIMEOUT)
            assert isinstance(msg, bytes)
            return msg.strip().decode()


# TelnetTransport wrapper
# A class to wrap the TelnetTransport in such
# a way that e.g. Home Assistant will not
# receive any exceptions
class TelnetTransportWrapper(NadTransport):
    def __init__(self, host: str, port: int, timeout: int) -> None:
        """Create NADTelnet."""
        self.nad_telnet = TelnetTransport(host, port, timeout)

    async def _pre_read(self) -> bool:
        # On initial connection
        # some firmwares sends nothing
        # some firmwares sends e.g. b'\rMain.Model=T787\r\n'
        # some firmwares sends multiple lines (BlueOS settings dump ?)
        #    including blank lines between data lines
        # At least clear the row "\rMain.Model=T787\r\n"
        try:
            await self.nad_telnet.read_until(b"\n")
            # Could raise eg. EOFError, UnicodeError
        except EOFError as cc:
            # Connection closed, no recovery
            _LOGGER.debug("Connection closed: %s", cc)
            self.nad_telnet.close_connection()
            return False
        except UnicodeError as ue:
            # Some unicode error, but connection is open
            _LOGGER.debug("Unicode error: %s", ue)
            return True

        return True

    async def _open_connection(self) -> bool:
        if self.nad_telnet.is_open():
            return True

        try:
            await self.nad_telnet.open_connection()
        except Exception as e:
            _LOGGER.debug("Connection failed to open: %s" % e)
            return False

        return await self._pre_read()

    async def communicate(self, cmd: str) -> str:
        rsp = ""
        if not await self._open_connection():
            return rsp

        try:
            rsp = await self.nad_telnet.communicate(cmd)
        except (EOFError, BrokenPipeError, ConnectionResetError) as cc:
            # Connection closed
            _LOGGER.debug("Connection closed: %s", cc)
            self.nad_telnet.close_connection()
        except UnicodeError as ue:
            # Some unicode error, but connection is open
            _LOGGER.debug("Unicode error: %s", ue)

        return rsp


class TelnetTransport(NadTransport):
    """
    Support NAD amplifiers that use telnet for communication.
    Supports all commands from the RS232 base class

    Known supported model: Nad T787.
    """

    def __init__(self, host: str, port: int, timeout: int) -> None:
        """Create NADTelnet."""
        self._reader: Optional[telnetlib3.TelnetReader] = None
        self._writer: Optional[telnetlib3.TelnetWriter] = None
        self.host = host
        self.port = port
        self.timeout = timeout

    def is_open(self) -> bool:
        return self._writer is not None and not self._writer.connection_closed

    async def open_connection(self) -> None:
        if self.is_open():
            raise Exception("Connection already open for host '%s:%s'" % (self.host, self.port))

        _LOGGER.debug("Open connection to: '%s:%s'" % (self.host, self.port))
        self._reader, self._writer = await asyncio.wait_for(
            telnetlib3.open_connection(
                self.host, self.port, encoding=False, connect_minwait=0.0
            ),
            timeout=self.timeout,
        )

    def close_connection(self) -> None:
        writer = self._writer
        self._reader = None
        self._writer = None
        if writer:
            _LOGGER.debug("Close connection to: '%s:%s'" % (self.host, self.port))
            writer.close()

    async def read_until(self, data: bytes) -> bytes:
        if not self._reader:
            raise Exception("Connection is closed")
        return await asyncio.wait_for(
            self._reader.readuntil(data), timeout=self.timeout
        )

    async def communicate(self, cmd: str) -> str:
        if not self._writer or not self._reader:
            raise Exception("Connection is closed")

        _LOGGER.debug("Sending command: '%s'", cmd)
        self._writer.write(f"\n{cmd}\r".encode())
        await self._writer.drain()

        # Notice NAD response to command ends with \r and starts with \n
        # E.g. b'\nMain.Power=On\r'
        rsp = await asyncio.wait_for(
            self._reader.readuntil(b"\r"), timeout=self.timeout
        )
        _LOGGER.debug("Read response: '%s'", str(rsp))
        return rsp.strip().decode()
