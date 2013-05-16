import socket
import threading
import time

from communicator import Communicator

CHUNK_SIZE = 1024

LOGFILE = dict(value='log')
def addToLog(msg):
    return False
    fh = open(LOGFILE['value'], "a")
    if not msg.endswith("\n"):
        msg += "\n"
    fh.write(msg)
    fh.close()


class ListeningSocket(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.bind(("", 0))
        self.set_client_addr(None)
        self.set_client_port(None)
        self.lock = threading.Lock()

    def get_port(self):
        return int(self.sock.getsockname()[1])

    def recv_data(self, amnt=CHUNK_SIZE):
        msg, client = self.sock.recvfrom(amnt)
        self.set_client_addr(client[0])
        self.set_client_port(client[1])
        return msg

    def set_client_addr(self, client_addr):
        self.client_addr = client_addr

    def set_client_port(self, client_port):
        if client_port is not None:
            self.client_port = int(client_port)
        else:
            self.client_port = None

    def close(self):
        self.sock.close()


class SendingSocket(object):
    def __init__(self, host_addr, host_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.set_host_addr(host_addr)
        self.set_host_port(host_port)
        self.lock = threading.Lock()

    def send_data(self, data):
        return self.sock.sendto(data, (self.host_addr, self.host_port))

    def set_host_addr(self, host_addr):
        self.host_addr = host_addr

    def set_host_port(self, host_port):
        if host_port is not None:
            self.host_port = int(host_port)
        else:
            self.host_port = None

    def close(self):
        self.sock.close()


class DualSocketCommunicator(Communicator):
    def __init__(self, listening_socket, sending_socket):
        self.listening_socket = listening_socket
        self.sending_socket = sending_socket
        self.messages_sent = 0
        self.messages_received = 0
        self._lock = threading.Lock()

    def recv(self):
        self._lock.acquire()
        msg = ""
        done = False
        while not done:
            chunk = self.listening_socket.recv_data()
            self.sending_socket.send_data("ACK")
            if chunk == '$$$$$$$$$$':
                done = True
                continue
            else:
                msg += chunk
        self._lock.release()
        return msg

    def send(self, msg):
        self._lock.acquire()
        message_id = self.messages_sent
        while len(msg) > 0:
            addToLog("sending message %s" % msg[:1024])
            amnt_sent = self.sending_socket.send_data(msg[:1024])
            msg = msg[amnt_sent:]
            ack = self.listening_socket.recv_data(3)
            addToLog("got ack %s" % ack)
        self.sending_socket.send_data('$$$$$$$$$$')
        ack = self.listening_socket.recv_data(3)
        self.messages_sent += 1
        self._lock.release()

    def cleanup(self):
        self.listening_socket.close()
        self.sending_socket.close()
