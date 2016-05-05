from PIL import Image
from termi import term

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

def create_palette_image(palette):
    palette_image = Image.new(mode='P', size=(1, len(palette)))
    while len(palette) < 256:
        palette += [palette[0]]
    palette_image.putpalette([comp for color in palette for comp in color])
    return palette_image

def resize_image(image, container_size, glyph_ar, scale_strategy):
    _, final_size = _fit_rectangle(
        (image.width, int(image.height * 2 / glyph_ar)),
        (container_size[0], container_size[1] * 2))
    image = image.convert('RGB')
    return image.resize(final_size, resample=scale_strategy)

def render_image(image, target_size, glyph_ar, palette_image,
                 output_strategy, scale_strategy):
    image = resize_image(image, target_size, glyph_ar, scale_strategy)
    if palette_image:
        image = image.quantize(palette=palette_image)
    pixels = image.load()
    output = ''
    for pos_y in range(0, image.height, 2):
        for pos_x in range(image.width):
            color_a = pixels[pos_x, pos_y]
            if pos_y + 1 < image.height:
                color_b = pixels[pos_x, pos_y + 1]
            else:
                color_b = color_a
            output += output_strategy(color_a, color_b)
            output += '▄'
        output += term.reset_attributes()
        output += '\n'
    return output
