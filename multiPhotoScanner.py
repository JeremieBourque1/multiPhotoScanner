#!/usr/bin/env python3

import gi
gi.require_version('Libinsane', '1.0')
from gi.repository import Libinsane
from gi.repository import GObject


class Logger(GObject.GObject, Libinsane.Logger):
    def do_log(self, lvl, msg):
        if lvl <= Libinsane.LogLevel.WARNING:
            return
        print("{}: {}".format(lvl.value_nick, msg))


class Scanner():
    def __init__(self):
        # Set logger
        Libinsane.register_logger(Logger())
        # Init Libinsane API
        self.api = Libinsane.Api.new_safebet()

    def list_devices(self):
        print("Looking for scan devices ...")
        devs = self.api.list_devices(Libinsane.DeviceLocations.ANY)
        print("Found {} devices".format(len(devs)))
        for dev in devs:
            print("[{}] : [{}]".format(dev.get_dev_id(), dev.to_string()))
        dev_id = devs[0].get_dev_id()


# For testing
if __name__ == "__main__":
    scanner = Scanner()
    scanner.list_devices()
