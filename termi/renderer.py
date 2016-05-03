from PIL import Image
import numpy
import itertools
import sys

class Output(object):
    def __init__(self, size, sequences):
        self.size = size
        self.sequences = sequences

def _from_rgb(color):
    return numpy.array([color[0], color[1], color[2]], numpy.float)

def _fit_rectangle(source_rectangle, target_rectangle):
    source_ar = source_rectangle[0] / source_rectangle[1]
    target_ar = target_rectangle[0] / target_rectangle[1]
    if target_ar < source_ar:
        scale_ratio = target_rectangle[0] / source_rectangle[0]
    else:
        scale_ratio = target_rectangle[1] / source_rectangle[1]
    output_rectangle = (
        int(source_rectangle[0] * scale_ratio),
        int(source_rectangle[1] * scale_ratio))
    output_pos = (
        (output_rectangle[0] - source_rectangle[0]) / 2,
        (output_rectangle[1] - source_rectangle[1]) / 2)
    assert output_rectangle[0] <= target_rectangle[0] + 1
    assert output_rectangle[1] <= target_rectangle[1] + 1
    return output_pos, output_rectangle

def _dither(pix, size, x, y, quant_error):
    width, height = size
    if x + 1 < width:
        pix[x+1, y] += quant_error * 7/16
    if y + 1 < height:
        if x > 0:
            pix[x-1, y+1] += quant_error * 3/16
        pix[x, y+1] += quant_error * 5/16
        if x + 1 < width:
            pix[x+1, y+1] += quant_error / 16

def _get_pixels(image):
    real_pix = image.convert('RGB').load()
    pix = {}
    for y in range(image.height):
        for x in range(image.width):
            pix[x, y] = _from_rgb(real_pix[x, y])
    return pix

def render_256(image, palette, container_size, glyph_ar):
    pos, final_size = _fit_rectangle(
        (image.width, int(image.height * 2 / glyph_ar)),
        (container_size[0], container_size[1] * 2))
    image = image.resize(final_size, resample=Image.LANCZOS)
    pix = _get_pixels(image)

    all_colors = numpy.array([_from_rgb(color) for color in palette])
    colors = {}
    for x in range(image.width):
        for y in range(image.height):
            old_pixel = pix[x, y]
            index = numpy.linalg.norm(all_colors - old_pixel, axis=1).argmin()
            colors[x, y] = index
            new_pixel = all_colors[index]
            _dither(pix, final_size, x, y, old_pixel - new_pixel)

    output = {}
    for x in range(image.width):
        for y in range(0, image.height, 2):
            color_a = colors[x, y]
            color_b = colors[x, y + 1]
            output[x, y // 2] = (color_a, color_b, '▄')

    for y in range(image.height // 2):
        for x in range(image.width):
            bg, fg, char = output[x, y]
            sys.stdout.write('\033[48;5;{0}m'.format(bg))
            sys.stdout.write('\033[38;5;{0}m'.format(fg))
            sys.stdout.write(char)
        sys.stdout.write('\033[0m\n')
