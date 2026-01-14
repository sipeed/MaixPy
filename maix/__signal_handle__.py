import signal, sys, threading
from . import _maix

# force_exit_timeout = 2

# def force_exit():
#     print("Force exit now")
#     sys.exit(1)

def signal_handle(signum, frame):
    _maix.app.set_exit_flag(True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGILL, signal.SIG_DFL)
    signal.signal(signal.SIGABRT, signal.SIG_DFL)

    device_name = _maix.sys.device_name().lower()
    if device_name == 'maixcam' or device_name == 'maixcam-pro': # MaixCAM must exit at here, otherwise it can not release hardware resources
        _maix.util.do_exit_function()
        sys.exit(0)
    else:
        _maix.util.do_exit_function()
        sys.exit(0)
        # # set exit flag and wait force_exit_timeout seconds, then force exit
        # t = threading.Timer(force_exit_timeout, force_exit)
        # t.daemon = True
        # t.start()
def register_signal_handle():
    signal.signal(signal.SIGINT, signal_handle)
    signal.signal(signal.SIGILL, signal_handle)
    signal.signal(signal.SIGABRT, signal_handle)