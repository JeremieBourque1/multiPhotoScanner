import PIL.Image


def split_images(source_image, scan_dimensions, resolution, picture_format, orientation, number_of_pictures=3):
    """
    Splits full image into cropped individual images
    :param source_image: full image
    :param resolution: dpi resolution of the image
    :param picture_format: format of the pictures (width, height, unit)
    :param number_of_pictures: number of pictures scanned at the same time
    :param orientation: "landscape" or "portrait"
    :return list of images
    """
    valid = False
    image_formats = []
    images = [None] * number_of_pictures
    w, h = length_to_pixels(resolution, picture_format)
    scan_width = scan_dimensions[0]
    scan_height = scan_dimensions[1]
    if number_of_pictures == 3:
        # ((left, top, right, bottom), rotate)
        image_formats = [((0, 0, h, w), True), ((scan_width-h, 0, scan_width, w), True), ((0, scan_height-h, w, scan_height), False)]
        valid = True
    if valid:
        for i in range(number_of_pictures):
            sub_image = source_image.crop(image_formats[i][0])
            if image_formats[i][1] and orientation == "landscape":
                sub_image = sub_image.rotate(90, expand=True)
            images[i] = sub_image
    return images


def length_to_pixels(resolution, picture_format):
    width_accuracy = 0.98  # width dimension accuracy coefficient
    height_accuracy = 0.99  # height dimension accuracy coefficient
    width = picture_format[0] * resolution * width_accuracy
    height = picture_format[1] * resolution * height_accuracy
    if picture_format[2] == "inch":
        return width, height
    elif picture_format[2] == "cm":
        return width*0.393701, height*0.393701


if __name__ == "__main__":
    im = PIL.Image.open("test2.jpg")
    split_images(im, 600, (6,4,"inch"))