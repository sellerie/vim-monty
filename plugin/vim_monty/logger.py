import os


HERE = os.path.dirname(__file__)
LOGFILE = os.path.join(HERE, '..', '..', 'vim_monty.log')
ENABLED = False


def log(msg):
    if ENABLED:
        logfile = open(LOGFILE, 'a')
        if not isinstance(msg, str):
            msg = repr(msg)
        logfile.write(msg + '\n')
        logfile.close()
