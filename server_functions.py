import os.path
import errno

MOUNTED_DIRECTORY = "/tmp/moshfs"
FH_TABLE = {}

def fixpath(path):
    if path.startswith("/"):
        path = path[1:]
    return os.path.join(MOUNTED_DIRECTORY, path)

def getattr(path):
    try:
        return os.lstat(fixpath(path))
    except OSError:
        return -errno.ENOENT

def readdir(path):
    return os.listdir(fixpath(path))

def unlink(path):
    os.unlink(fixpath(path))

def mkdir(path, mode):
    os.mkdir(fixpath(path), mode)

def rmdir(path):
    os.rmdir(fixpath(path))

def readlink(path):
    return os.readlink(fixpath(path))

def symlink(path, path1):
    os.symlink(fixpath(path), fixpath(path1))

def link(path, path1):
    os.link(fixpath(path), fixpath(path1))

def rename(path, path1):
    os.rename(fixpath(path), fixpath(path1))

def utime(path, times):
    os.utime(fixpath(path), times)

def flag2mode(flags):
    md = {os.O_RDONLY: 'r', os.O_WRONLY: 'w', os.O_RDWR: 'w+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags & os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m

def open(path, flags, mode):
    fh = os.fdopen(os.open(fixpath(path), flags, mode),
                   flag2mode(flags))
    fd = fh.fileno()
    FH_TABLE[fd] = fh
    return fd

# these are relative a fileno

def read(fd, length, offset):
    fh = FH_TABLE[fd]
    fh.seek(offset)
    return fh.read(length)

def write(fd, buf, offset):
    fh = FH_TABLE[fd]
    fh.seek(offset)
    fh.write(buf)
    return len(buf)

def release(fd):
    fh = FH_TABLE[fd]
    fh.close()
    del FH_TABLE[fd]

def _fflush(fh):
    if 'w' in fh.mode or 'a' in fh.mode:
        fh.flush()

def fsync(fd, isfsyncfile):
    fh = FH_TABLE[fd]
    _fflush(fh)
    if isfsyncfile and hasattr(os, 'fdatasync'):
        os.fdatasync(fh.fileno())
    else:
        os.fsync(fh.fileno())

def flush(fd):
    fh = FH_TABLE[fd]
    _fflush(fh)
    os.close(os.dup(fh.fileno()))

def fgetattr(fd):
    fh = FH_TABLE[fd]
    return os.fstat(fh.fileno())

def ftruncate(fd, len):
    fh = FH_TABLE[fd]
    fh.truncate(len)
