import math
import itertools
import sys
from PIL import Image

class Output(object):
    def __init__(self, size, sequences):
        self.size = size
        self.sequences = sequences

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

def _quantize(source_image, palette):
    try:
        import numpy
    except ImportError:
        return source_image.quantize(palette=palette, method=1)

    def _from_rgb(color):
        return numpy.array([color[0], color[1], color[2]], numpy.float)

    # Floyd-Steinberg
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

    target_image = Image.new(mode='P', size=source_image.size)
    source_pixels = source_image.load()
    target_pixels = target_image.load()

    source_pixels_copy = {}
    for x in range(source_image.width):
        for y in range(source_image.height):
            source_pixels_copy[x, y] = _from_rgb(source_pixels[x, y])

    palette_colors = numpy.array(list(zip(*(iter(palette.getpalette()),) * 3)))
    for x in range(source_image.width):
        for y in range(source_image.height):
            source_pixel = source_pixels_copy[x, y]
            index = numpy.linalg.norm(palette_colors - source_pixel, axis=1).argmin()
            target_pixels[x, y] = (index,)
            target_pixel = palette_colors[index]
            _dither(
                source_pixels_copy,
                source_image.size,
                x, y,
                source_pixel - target_pixel)
    return target_image

def _write_sequence(attrs):
    _write_str('\033[{0}m'.format(';'.join(str(x) for x in attrs)))

def _write_str(str):
    sys.stdout.write(str)

def _create_palette_image(palette):
    palette_image = Image.new(mode='P', size=(1, len(palette)))
    while len(palette) < 256:
        palette += [palette[0]]
    palette_image.putpalette([comp for color in palette for comp in color])
    return palette_image

def _get_output(image, container_size, glyph_ar, palette=None):
    pos, final_size = _fit_rectangle(
        (image.width, int(image.height * 2 / glyph_ar)),
        (container_size[0], container_size[1] * 2))
    image = image.convert('RGB')
    image = image.resize(final_size, resample=Image.LANCZOS)
    if palette:
        palette_image = _create_palette_image(palette)
        image = _quantize(image, palette=palette_image)
    pixels = image.load()
    output = {}
    for x in range(image.width):
        for y in range(0, image.height, 2):
            try:
                color_a = pixels[x, y]
                color_b = pixels[x, y + 1]
                output[x, y // 2] = (color_a, color_b, '▄')
            except IndexError:
                pass
    return (final_size[0], final_size[1] // 2), output

def render_true_color(image, container_size, glyph_ar):
    size, output = _get_output(image, container_size, glyph_ar)
    width, height = size
    for y in range(height):
        for x in range(width):
            try:
                bg, fg, char = output[x, y]
                _write_sequence([48, 2, bg[0], bg[1], bg[2]])
                _write_sequence([38, 2, fg[0], fg[1], fg[2]])
                _write_str(char)
            except IndexError:
                print(' ')
        _write_sequence([0])
        _write_str('\n')

def render_256(image, palette, container_size, glyph_ar):
    size, output = _get_output(image, container_size, glyph_ar, palette)
    width, height = size
    for y in range(height):
        for x in range(width):
            try:
                bg, fg, char = output[x, y]
                _write_sequence([48, 5, bg])
                _write_sequence([38, 5, fg])
                _write_str(char)
            except IndexError:
                print(' ')
        _write_sequence([0])
        _write_str('\n')

def render_16(image, palette, container_size, glyph_ar):
    size, output = _get_output(image, container_size, glyph_ar, palette)
    width, height = size
    for y in range(height):
        for x in range(width):
            try:
                bg, fg, char = output[x, y]
                _write_sequence([(100 if bg >= 8 else 40) + (bg % 8)])
                _write_sequence([(90 if fg >= 8 else 30) + (fg % 8)])
                _write_str(char)
            except IndexError:
                print(' ')
        _write_sequence([0])
        _write_str('\n')
