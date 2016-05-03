from termi import term_settings
from termi import renderer
import argparse
import sys
import json
from PIL import Image

def positive_int(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError('Only positive integers allowed')
    return x

def parse_args():
    parser = argparse.ArgumentParser(description='Convert images to ASCII')
    parser.add_argument(
        '--glyph-aspect-ratio', dest='glyph_ar', metavar='NUM',
        type=float, default=2, help='character aspect ratio (default: 2)')
    parser.add_argument(
        '--width', metavar='NUM', type=int, default=None,
        help='target image width (in characters)')
    parser.add_argument(
        '--height', metavar='NUM', type=int, default=None,
        help='target image height (in characters)')
    parser.add_argument(
        metavar='PATH', dest='input_path',
        help='where to get the input image from')
    parser.add_argument(
        '--palette', metavar='PATH', dest='palette_path',
        help='custom palette')
    return parser.parse_args()

def main():
    args = parse_args()
    size = [args.width, args.height]
    for i in range(2):
        if not size[i]:
            terminal_size = term_settings.get_term_size()
            target_size = (terminal_size[0] - 1, terminal_size[1] - 1)
            size[i] = target_size[i]
    if args.palette_path:
        with open(args.palette_path, 'r') as handle:
            palette = json.load(handle)
    else:
        palette = term_settings.DEFAULT_PALETTE
    image = Image.open(args.input_path)
    renderer.render_256(image, palette, size, args.glyph_ar)

if __name__ == '__main__':
    main()
