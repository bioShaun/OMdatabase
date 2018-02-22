from sys import stderr

class FastaIOError(IOError):
    pass

class ResNulError(Exception):
    pass

class TabformatErr(Exception):
    pass

class FastaErr(Exception):
    pass

class AnnotError(Exception):
    pass

class StatError(ArithmeticError):
    pass

def error(msg):
    err_msg  = '%s: %s\n' % (msg.__class__, msg)
    stderr.write(err_msg)
