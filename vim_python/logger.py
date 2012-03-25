import os


HERE = os.path.dirname(__file__)
LOGFILE = os.path.join(HERE, '..', 'vim_python.log')
ENABLED = True


def log(msg):
    if ENABLED:
        logfile = open(LOGFILE, 'a')
        if not isinstance(msg, str):
            msg = repr(msg)
        logfile.write(msg + '\n')
        logfile.close()
