import signal, sys, threading
from . import _maix

force_exit_timeout = 2

def force_exit():
    print("Force exit now")
    _maix.util.do_exit_function()
    sys.exit(1)

def signal_handle(signum, frame):
    _maix.app.set_exit_flag(True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # set exit flag and wait force_exit_timeout seconds, then force exit
    t = threading.Timer(force_exit_timeout, force_exit)
    t.daemon = True
    t.start()


def register_signal_handle():
    signal.signal(signal.SIGINT, signal_handle)