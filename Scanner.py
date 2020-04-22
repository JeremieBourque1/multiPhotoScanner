#!/usr/bin/env python3

import gi
import sys
import PIL.Image

gi.require_version('Libinsane', '1.0')
from gi.repository import Libinsane
from gi.repository import GObject


class Logger(GObject.GObject, Libinsane.Logger):
    def do_log(self, lvl, msg):
        if lvl <= Libinsane.LogLevel.WARNING:
            return
        print("{}: {}".format(lvl.value_nick, msg))


class Source():
    def __init__(self, dev, src):
        self.dev = dev
        self.src = src


class Scanner():
    def __init__(self):
        # Set logger
        Libinsane.register_logger(Logger())
        # Init Libinsane API
        self.api = Libinsane.Api.new_safebet()
        self.device_list = []
        self.source_list = []
        self.active_source = None
        self.resolution = 600

    def list_devices(self):
        """
        Lists available devices
        """
        print("Looking for scan devices ...")
        self.device_list = self.api.list_devices(Libinsane.DeviceLocations.ANY)
        print("Found {} devices".format(len(self.device_list)))
        for dev in self.device_list:
            print(self.get_device_name(dev))

    def list_sources(self, auto_set=True):
        """
        Lists available sources for each device
        :param auto_set: True to automatically set the active source to the first one of the list
        :return:
        """
        print("Looking for scan sources ...")
        for device in self.device_list:
            sources = self.api.get_device(device.get_dev_id()).get_children()
            print("Available scan sources:")
            for src in sources:
                print("- {}".format(src.get_name()))
                self.source_list.append(Source(device, src))
        if auto_set and len(self.source_list) > 0:
            self.set_active_source(self.source_list[0])

    def get_device_name(self, dev):
        """
        Returns a string composed of the devices vendor and model name
        :param dev: device
        :return: descriptive name
        """
        return dev.get_dev_vendor() + " " + dev.get_dev_model()

    def get_source_name(self, source):
        return source.dev.get_dev_vendor() + " " + source.dev.get_dev_model() + " " + source.src.get_name()

    def set_active_source(self, source):
        """
        Sets the active source
        :param source: source
        :return:
        """
        self.active_source = source
        print("Setting %s as the active source" % self.get_source_name(source))

    def set_options(self):
        opts = self.active_source.src.get_options()
        opts = {opt.get_name(): opt for opt in opts}
        set_flags = opts["resolution"].set_value(self.resolution)
        print("Resolution set to %d" % self.resolution)

    def scan(self, output_file):
        self.set_options()
        print("Starting scan")
        session = self.active_source.src.scan_start()
        try:
            page_nb = 0
            while not session.end_of_feed() and page_nb < 20:
                # Do not assume that all the pages will have the same size !
                scan_params = session.get_scan_parameters()
                print("Expected scan parameters: {} ; {}x{} = {} bytes".format(
                    scan_params.get_format(),
                    scan_params.get_width(), scan_params.get_height(),
                    scan_params.get_image_size()))
                total = scan_params.get_image_size()
                img = []
                r = 0
                if output_file is not None:
                    out = output_file.format(page_nb)
                else:
                    out = None
                print("Scanning page {} --> {}".format(page_nb, out))
                while not session.end_of_page():
                    data = session.read_bytes(128 * 1024)
                    data = data.get_data()
                    img.append(data)
                    r += len(data)
                    progress = int(r/total*100)
                    print("Scan progress: %d%%" % progress)
                img = b"".join(img)
                print("Got {} bytes".format(len(img)))
                if out is not None:
                    print("Saving page as {} ...".format(out))
                    if scan_params.get_format() == Libinsane.ImgFormat.RAW_RGB_24:
                        img = raw_to_img(scan_params, img)
                        img.save(out, format="JPEG")
                        print("Full image saved")
                        split_images(img)
                    else:
                        print("Warning: output format is {}".format(
                            scan_params.get_format()
                        ))
                        with open(out, 'wb') as fd:
                            fd.write(img)
                page_nb += 1
                print("Page {} scanned".format(page_nb))
            if page_nb == 0:
                print("No page in feeder ?")
        finally:
            print("Scanning complete")
            session.cancel()


def raw_to_img(params, img_bytes):
    fmt = params.get_format()
    assert (fmt == Libinsane.ImgFormat.RAW_RGB_24)
    (w, h) = (
        params.get_width(),
        int(len(img_bytes) / 3 / params.get_width())
    )
    print("Mode: RGB : Size: {}x{}".format(w, h))
    return PIL.Image.frombuffer("RGB", (w, h), img_bytes, "raw", "RGB", 0, 1)


def split_images(source_image):
    image1 = source_image.crop((0, 0, 2377, 3529)).rotate(90, expand=True)
    image1.save("splitTest1.jpg", format="JPEG")
    print("Image 1 saved")
    image2 = source_image.crop((2377, 0, 4771, 3529)).rotate(90, expand=True)
    image2.save("splitTest2.jpg", format="JPEG")
    print("Image 2 saved")
    image3 = source_image.crop((0, 3529, 3546, 5921))
    image3.save("splitTest3.jpg", format="JPEG")
    print("Image 3 saved")

# For testing
if __name__ == "__main__":
    scanner = Scanner()
    scanner.list_devices()
    scanner.list_sources()
    scanner.scan("test2.jpg")