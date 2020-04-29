#!/usr/bin/env python3

import gi
import sys
import PIL.Image
gi.require_version('Libinsane', '1.0')
from gi.repository import Libinsane
from gi.repository import GObject
from crop import split_images
from os import listdir, mkdir
from os.path import isfile, join


class Logger(GObject.GObject, Libinsane.Logger):
    def do_log(self, lvl, msg):
        if lvl <= Libinsane.LogLevel.WARNING:
            return
        print("{}: {}".format(lvl.value_nick, msg))


class Source():
    """
    Class to encapsulate source and device together
    """
    def __init__(self, dev, src):
        self.dev = dev
        self.src = src

    def get_source_name(self):
        """
        Returns a string composed of the sources device vendor, device model and source name
        :param dev: source object
        :return: string of the descriptive name
        """
        return self.dev.get_dev_vendor() + " " + self.dev.get_dev_model() + " " + self.src.get_name()


class Scanner():
    """
    Scanner class, contains all methods necessary to scan pictures
    """
    def __init__(self):
        # Set logger
        Libinsane.register_logger(Logger())
        # Init Libinsane API
        self.api = Libinsane.Api.new_safebet()
        self.picture_format = (6, 4, "inch")
        self.number_of_pictures = 3
        self.orientation = "landscape"
        self.album_directory = ""
        self.device_list = []
        self.source_list = []
        self.source_dict = dict() # TODO: we should only have the dict, not the list
        self.active_source = None
        self.resolution = 600

    def list_devices(self):
        """
        Lists available devices. The list is assigned to self.device_list
        """
        print("Looking for scan devices ...")
        self.device_list = self.api.list_devices(Libinsane.DeviceLocations.ANY)
        print("Found {} devices".format(len(self.device_list)))
        for dev in self.device_list:
            print(self.get_device_name(dev))

    def list_sources(self, auto_set=True):
        """
        Lists available sources for each device. The list is assigned to self.source_list
        :param auto_set: True to automatically set the active source to the first one of the list
        """
        print("Looking for scan sources ...")
        for device in self.device_list:
            sources = self.api.get_device(device.get_dev_id()).get_children()
            print("Available scan sources:")
            for src in sources:
                src = Source(device, src)
                name = src.get_source_name()
                self.source_dict[name] = src
                print("- {}".format(name))
                self.source_list.append(src)
        if auto_set and len(self.source_list) > 0:
            self.set_active_source(self.source_list[0])

    def list_all_scanners(self, auto_set=True):
        self.list_devices()
        self.list_sources(auto_set)

    def get_device_name(self, dev):
        """
        Returns a string composed of the devices vendor and model name
        :param dev: device object
        :return: string of the descriptive name
        """
        return dev.get_dev_vendor() + " " + dev.get_dev_model()

    def set_active_source(self, source):
        """
        Sets the active source
        :param source: source
        :return:
        """
        self.active_source = source
        print("Setting %s as the active source" % source.get_source_name())

    def set_picture_format(self, width, height, unit):
        """
        Set the picture format
        :param width: length of the long side of the picture
        :param height: length of the short side of the picture
        :param unit: length unit ("cm" or "inch")
        :return success
        """
        if not (width > 0 and height > 0 and (unit == "inch" or unit =="cm")):
            print("invalid format, reverting to previous format")
            return False
        else:
            self.picture_format = (width, height, unit)
            print("format %.2f %s x %.2f %s set" % (width, unit, height, unit))
            return True

    def set_number_of_pictures(self, num):
        if not(type(num) is int and num > 0 and num < 100):
            print("Invalid number of pictures, reverting to previous number")
        else:
            self.number_of_pictures = num
            print("Number of pictures set to %d" % num)

    def set_orientation(self, orientation):
        if orientation == "landscape" or orientation == "portrait":
            self.orientation = orientation
            print("Orientation set to %s" % orientation)
        else:
            print("Invalid orientation, reverting to previous orientation")

    def set_album_directory(self, directory):
        try:
            mkdir(directory)
        except FileExistsError:
            pass
        self.album_directory = directory
        print("Album directory set to %s" % directory)

    def set_resolution(self, res):
        if not (res > 0 and res < 2700):
            print("Invalid resolution, reverting to previous resolution")
        else:
            self.resolution = res

    def set_options(self):
        """
        Sets defined options to the active source
        """
        opts = self.active_source.src.get_options()
        opts = {opt.get_name(): opt for opt in opts}
        opts["resolution"].set_value(self.resolution)
        print("Resolution set to %d" % self.resolution)

    def scan(self, output_file):  # TODO: remove output_file
        """
        Scans image and saves to output_file
        :param output_file: name of the output file
        """
        # TODO: check if active source is valid before scanning
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
                        sub_images = split_images(img, (scan_params.get_width(), scan_params.get_height()), self.resolution, self.picture_format, self.orientation, self.number_of_pictures)
                        self.save_images(sub_images)
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

    def name_image(self):
        biggest_number = 0
        album_name = self.album_directory.split("\\")[-1]
        files = [f for f in listdir(self.album_directory) if isfile(join(self.album_directory, f))]
        for file in files:
            if file[:len(album_name)] == album_name:
                number = int(file[-8:-4])
                if number > biggest_number:
                    biggest_number = number
        return "%s_%04d" % (album_name, biggest_number+1)

    def save_images(self, images):
        for image in images:
            image.save("%s\\%s.jpg" % (self.album_directory, self.name_image()), format="JPEG")
        print("Images saved")


def raw_to_img(params, img_bytes):
    """
    Converts raw bytes to image object
    :param params: image parameters
    :param img_bytes: byte array
    :return: image object
    """
    fmt = params.get_format()
    assert (fmt == Libinsane.ImgFormat.RAW_RGB_24)
    (w, h) = (
        params.get_width(),
        int(len(img_bytes) / 3 / params.get_width())
    )
    print("Mode: RGB : Size: {}x{}".format(w, h))
    return PIL.Image.frombuffer("RGB", (w, h), img_bytes, "raw", "RGB", 0, 1)


# For testing
#if __name__ == "__main__":
#    scanner = Scanner()
#    scanner.list_all_scanners()
#    scanner.set_album_directory("test_album")
#    scanner.set_resolution(300)
#    scanner.scan("test3.jpg")
