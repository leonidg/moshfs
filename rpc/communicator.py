import socket

class Communicator(object):
    def recv(self):
        raise NotImplementedError()

    def send(self, msg):
        raise NotImplementedError()
        
