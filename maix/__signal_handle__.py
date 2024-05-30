import signal
import sys

def signal_handle(signum, frame):
    # _maix.app.set_exit_flag(True)
    # signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(0)

def register_signal_handle():
    signal.signal(signal.SIGINT, signal_handle)