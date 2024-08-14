
import argparse

__version__ = "0.0.1"

parser = argparse.ArgumentParser(description='maixhub python toolkit')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
parser.add_argument('cmd', help='command', choices=["ui"])

def main():
    args = parser.parse_args()
    print("== welcome to maixhub python utils ==")
    if args.cmd == "ui":
        from . import ui
        ui.main()
