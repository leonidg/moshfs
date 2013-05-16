#!/usr/bin/python

import sys

from client_functions import MoshFS

from rpc import dual_socket
from rpc.rpc import RPC

import rpc

rpc.dual_socket.LOGFILE['value'] = "/tmp/moshfslog.client"

def init(sending_hostname, sending_port):
    listening_socket = dual_socket.ListeningSocket()
    listening_port = listening_socket.get_port()
    sending_socket = dual_socket.SendingSocket(sending_hostname, sending_port)
    sending_socket.send_data("HELLO %d" % (listening_port,))
    hello_ack = listening_socket.recv_data()
    if hello_ack != "HELLOACK":
        print "Invalid HELLOACK. Exiting."
        sys.exit(1)
    communicator = dual_socket.DualSocketCommunicator(listening_socket, sending_socket)
    return communicator

def main(sending_hostname, sending_port):
    communicator = init(sending_hostname, sending_port)
    rpc = RPC(communicator)

    moshfs_getattr = rpc.make_rpc_stub('getattr')
    moshfs_readdir = rpc.make_rpc_stub('readdir')
    moshfs_unlink = rpc.make_rpc_stub('unlink')
    moshfs_mkdir = rpc.make_rpc_stub('mkdir')
    moshfs_rmdir = rpc.make_rpc_stub('rmdir')
    moshfs_readlink = rpc.make_rpc_stub('readlink')
    moshfs_symlink = rpc.make_rpc_stub('symlink')
    moshfs_link = rpc.make_rpc_stub('link')
    moshfs_rename = rpc.make_rpc_stub('rename')
    moshfs_utime = rpc.make_rpc_stub('utime')
    moshfs_open = rpc.make_rpc_stub('open')
    moshfs_read = rpc.make_rpc_stub('read')
    moshfs_write = rpc.make_rpc_stub('write')
    moshfs_release = rpc.make_rpc_stub('release')
    moshfs_fsync = rpc.make_rpc_stub('fsync')
    moshfs_flush = rpc.make_rpc_stub('flush')
    moshfs_fgetattr = rpc.make_rpc_stub('fgetattr')
    moshfs_ftruncate = rpc.make_rpc_stub('ftruncate')

    fs = MoshFS(handlers={
            'getattr': moshfs_getattr,
            'readdir': moshfs_readdir,
            'unlink': moshfs_unlink,
            'mkdir': moshfs_mkdir,
            'rmdir': moshfs_rmdir,
            'readlink': moshfs_readlink,
            'symlink': moshfs_symlink,
            'link': moshfs_link,
            'rename': moshfs_rename,
            'utime': moshfs_utime,
            'open': moshfs_open,
            'read': moshfs_read,
            'write': moshfs_write,
            'release': moshfs_release,
            'fsync': moshfs_fsync,
            'flush': moshfs_flush,
            'fgetattr': moshfs_fgetattr,
            'ftruncate': moshfs_ftruncate
            })
    fs.parse(errex=1)
    fs.main()

if __name__ == "__main__":
    # stupid hack to get around FUSE command-line parsing
    hostname = sys.argv[2]
    port = sys.argv[3]
    sys.argv = [sys.argv[0], sys.argv[1]]
    main(hostname, port)
