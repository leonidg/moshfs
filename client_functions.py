#!/usr/bin/python

from fuse import Fuse
from time import time

import errno
import fuse
import stat    # for file properties
import os      # for filesystem modes (O_RDONLY, etc)
import errno   # for error number codes (ENOENT, etc)
               # - note: these must be returned as negatives

fuse.fuse_python_api = fuse.FUSE_PYTHON_API_VERSION

class MyStat(fuse.Stat):
  def __init__(self, posix_st):
      self.st_mode = posix_st.st_mode
      self.st_ino = posix_st.st_ino
      self.st_dev = posix_st.st_dev
      self.st_nlink = posix_st.st_nlink
      self.st_uid = os.getuid() # posix_st.st_uid
      self.st_gid = os.getgid() # posix_st.st_gid
      self.st_size = posix_st.st_size
      self.st_atime = posix_st.st_atime
      self.st_mtime = posix_st.st_mtime
      self.st_ctime = posix_st.st_ctime

HANDLERS = None

class MoshFS(Fuse):
    def __init__(self, *args, **kwargs):
        if 'handlers' in kwargs:
            global HANDLERS
            self.handlers = kwargs['handlers']
            HANDLERS = self.handlers
        del kwargs['handlers']
        self.file_class = self.MoshFile
        Fuse.__init__(self, *args, **kwargs)

    def getattr(self, path):
        posix_st = self.handlers['getattr'](path)
        if posix_st == -errno.ENOENT:
            return posix_st
        fuse_st = MyStat(posix_st)
        return fuse_st

    def readdir(self, path, offset):
        for e in self.handlers['readdir'](path):
            yield fuse.Direntry(e)

    def unlink(self, path):
        self.handlers['unlink'](path)

    def rmdir(self, path):
        self.handlers['rmdir'](path)

    def mkdir(self, path, mode):
        self.handlers['mkdir'](path, mode)

    def readlink(self, path):
        return self.handlers['readlink'](path)

    def symlink(self, path, path1):
        self.handlers['symlink'](path, path1)

    def link(self, path, path1):
        self.handlers['link'](path, path1)

    def rename(self, path, path1):
        self.handlers['rename'](path, path1)

    def utime(self, path, times):
        self.handlers['utime'](path, times)

    class MoshFile(object):
        def __init__(self, path, flags, mode=0777):
            global HANDLERS
            self.handlers = HANDLERS
            self.file = self.handlers['open'](path, flags, mode)

        def read(self, length, offset):
            return self.handlers['read'](self.file, length, offset)

        def write(self, buf, offset):
            return self.handlers['write'](self.file, buf, offset)

        def release(self, flags):
            self.handlers['release'](self.file)

        def fsync(self, isfsyncfile):
            self.handlers['fsync'](self.file, isfsyncfile)

        def flush(self):
            self.handlers['flush'](self.file)

        def fgetattr(self):
            return self.handlers['fgetattr'](self.file)

        def ftruncate(self, len):
            self.handlers['ftruncate'](self.file)

    def main(self, *args, **kwargs):
        return Fuse.main(self, *args, **kwargs)
