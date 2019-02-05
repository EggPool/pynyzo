"""
Nyzo connection layer.
Raw bytes over sockets, with 4 bytes len prefix.
Adapted from eggpool's bismuth code
"""

import socket
import struct
from time import time
import threading

from pynyzo.helpers import base_app_log
from pynyzo.message import Message
from pynyzo.messagetype import MessageType
from pynyzo.messageobject import MessageObject, EmptyMessageObject

# Logical timeout
LTIMEOUT = 45

__version__ = '0.1.0'


class Connection(object):
    """Connection to a Nyzo Node. Handles auto reconnect when needed"""

    __slots__ = ('app_log', 'ip', 'port', 'verbose', 'sdef', 'stats', 'last_activity', 'command_lock', 'raw')

    def __init__(self, ip: str, port: int=9444, verbose: bool=False, app_log: object=None):
        self.app_log = base_app_log(app_log)
        self.ip = ip
        self.port = port
        self.verbose = verbose
        self.sdef = None
        self.last_activity = 0
        self.command_lock = threading.Lock()
        self.check_connection()

    def check_connection(self):
        """Check connection state and reconnect if needed."""
        if not self.sdef:
            try:
                if self.verbose:
                    self.app_log.info(f"Connecting to {self.ip}:{self.port}")
                self.sdef = socket.socket()
                self.sdef.connect((self.ip, self.port))
                self.last_activity = time()
            except Exception as e:
                self.sdef = None
                raise RuntimeError(f"Connections: {e}")

    def send(self, data, retry=True):
        """Sends data buffer to the peer, appends the len header"""
        self.check_connection()
        try:
            self.sdef.settimeout(LTIMEOUT)
            # Header is len of full message, including header
            header = struct.pack(">I", len(data) + 4)
            # Send buffer in one packet - Do not make 2 calls.
            res = self.sdef.sendall(header + data)
            self.last_activity = time()
            # res is always 0 on linux
            if self.verbose:
                self.app_log.info(f"Sent {len(data) + 4} bytes: {(header + data).hex()}")
            return True
        except Exception as e:
            # send failed, try to reconnect
            # TODO: handle tries #
            self.sdef = None
            if retry:
                if self.verbose:
                    self.app_log.warning(f"Send failed ({e}), trying to reconnect")
                self.check_connection()
            else:
                if self.verbose:
                    self.app_log.warning(f"Send failed ({e}), trying to reconnect")
                return False
            try:
                self.sdef.settimeout(LTIMEOUT)
                # Make sure the packet is sent in one call
                res = self.sdef.sendall(header + data)
                return True
            except Exception as e:
                self.sdef = None
                raise RuntimeError(f"Connections: {e}")

    def receive(self):
        """Wait for an answer, for LTIMEOUT sec."""
        self.check_connection()
        self.sdef.settimeout(LTIMEOUT)
        try:
            # Get header
            data = self.sdef.recv(4)
            if not data:
                raise RuntimeError("Socket EOF")
            length = struct.unpack('>I', data)[0] - 4
            if self.verbose:
                self.app_log.info(f"Receiving {length} announced bytes")
        except socket.timeout as e:
            self.sdef = None
            return ""
        try:
            chunks = []
            bytes_recd = 0
            while bytes_recd < length:
                chunk = self.sdef.recv(min(length - bytes_recd, 2048))
                if not chunk:
                    raise RuntimeError("Socket EOF2")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            self.last_activity = time()
            buffer = b''.join(chunks)
            return buffer
        except Exception as e:
            """
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            """
            self.sdef = None
            raise RuntimeError("Connections: {}".format(e))

    def command(self, command, options=None):
        """
        Sends a command and return it's raw result. - left over from bis, do not use
        """
        with self.command_lock:
            try:
                self.send(command)
                ret = self.receive()
                return ret
            except Exception as e:
                """
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                """
                # TODO : better handling of tries and delay between
                if self.verbose:
                    print("Error <{}> sending command, trying to reconnect.".format(e))
                self.check_connection()
                self.send(command)
                ret = self.receive()
                return ret

    def close(self):
        """Close the socket"""
        try:
            self.sdef.close()
        except Exception as e:
            pass
        finally:
            self.sdef = None

    def fetch_buffer(self, message: Message, identifier: bytes=b'') -> bytes:
        """From Message - fetch bin buffer"""
        # TODO
        # identifier = NodeManager.identifierForIpAddress(self.ip);
        self.send(message.get_bytes_for_transmission())
        response = self.receive()
        return response

    def fetch(self, message: Message, identifier: bytes=b'') -> MessageObject:
        """Fetch then decode"""
        buffer = self.fetch_buffer(message, identifier)
        return Message.from_bytes(buffer, b'').get_content()  # self.ip, but convert or use str for ips?


if __name__ == "__main__":
    print("I'm a module, can't run!")
