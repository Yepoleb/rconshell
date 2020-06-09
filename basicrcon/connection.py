import socket
import random

from basicrcon import byteio
from basicrcon.exceptions import BrokenMessageError, AuthenticationError

SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0

class RconConnection:
    def __init__(self, address, timeout=3):
        self.sock = socket.create_connection(address, timeout)
        self.sockf = self.sock.makefile("rwb") # Create buffered file object
        self.sockr = byteio.ByteReader(self.sockf, endian="<")
        self.sockw = byteio.ByteWriter(self.sockf, endian="<")

    def close(self):
        self.sockf = None
        self.sock.close()

    def send_packet(self, kind, body):
        msgid = random.getrandbits(31)
        body_enc = body.encode("utf-8")
        size = len(body_enc) + 10
        self.sockw.write_int32(size)
        self.sockw.write_int32(msgid)
        self.sockw.write_int32(kind)
        self.sockw.write(body_enc)
        self.sockw.write(b"\x00\x00")
        self.sockf.flush()
        return msgid

    def recv_packet(self):
        size = self.sockr.read_int32()
        msgid = self.sockr.read_int32()
        kind = self.sockr.read_int32()
        body_size = size - 10
        body_enc = self.sockr.read(body_size)
        self.sockr.read(2) # terminators
        body = body_enc.decode("utf-8")
        return msgid, kind, body

    def authenticate(self, password):
        sendid = self.send_packet(SERVERDATA_AUTH, password)
        recvid, kind, body = self.recv_packet()
        if kind != SERVERDATA_AUTH_RESPONSE:
            recvid, kind, body = self.recv_packet()
        if kind != SERVERDATA_AUTH_RESPONSE:
            raise BrokenMessage("Broken auth flow")
        if recvid != sendid:
            raise AuthenticationError("Server did not accept password")

    def execute(self, cmd):
        self.send_packet(SERVERDATA_EXECCOMMAND, cmd)

    def response(self):
        msgid, kind, body = self.recv_packet()
        return body
