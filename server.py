#!/usr/bin/python

import sys

from rpc import dual_socket
from rpc.rpc import RPC

import rpc

import server_functions
from server_functions import getattr, readdir, unlink, mkdir, rmdir,\
    readlink, symlink, link, rename, utime, \
    open, read, write, release, fsync, flush, fgetattr, ftruncate

rpc.dual_socket.LOGFILE['value'] = "/tmp/moshfslog.server"

def reset_communicator(communicator, hellomsg):
    hello_msg, sending_port = hellomsg.split(" ")
    if hello_msg != "HELLO":
        print "Invalid HELLO message. Exiting."
        sys.exit(1)
    communicator.sending_socket.set_host_port(sending_port)
    communicator.listening_socket.set_client_port(sending_port)
    helloack = "HELLOACK"
    communicator.sending_socket.send_data(helloack)

def init():
    listening_socket = dual_socket.ListeningSocket()
    sending_socket = dual_socket.SendingSocket(None, None)
    listening_port = listening_socket.get_port()
    print "Bound to port %d" % (listening_port,)
    communicator = dual_socket.DualSocketCommunicator(listening_socket, sending_socket)
    hellomsg = listening_socket.recv_data()
    sending_socket.set_host_addr(listening_socket.client_addr)
    reset_communicator(communicator, hellomsg)
    return communicator

def main():
    communicator = init()
    rpc = RPC(communicator)
    rpc.register_rpc_handler('getattr', getattr)
    rpc.register_rpc_handler('readdir', readdir)
    rpc.register_rpc_handler('unlink', unlink)
    rpc.register_rpc_handler('mkdir', mkdir)
    rpc.register_rpc_handler('rmdir', rmdir)
    rpc.register_rpc_handler('readlink', readlink)
    rpc.register_rpc_handler('symlink', symlink)
    rpc.register_rpc_handler('link', link)
    rpc.register_rpc_handler('rename', rename)
    rpc.register_rpc_handler('utime', utime)
    rpc.register_rpc_handler('open', open)
    rpc.register_rpc_handler('read', read)
    rpc.register_rpc_handler('write', write)
    rpc.register_rpc_handler('release', release)
    rpc.register_rpc_handler('fsync', fsync)
    rpc.register_rpc_handler('flush', flush)
    rpc.register_rpc_handler('fgetattr', fgetattr)
    rpc.register_rpc_handler('ftruncate', ftruncate)

    while True:
        rpc_call = communicator.recv()
        if rpc_call.startswith("HELLO"):
            reset_communicator(communicator, rpc_call)
            continue
        rpc.call_handler(rpc_call)

if __name__ == "__main__":
    main()
