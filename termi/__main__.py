from termi import term_settings
from termi import renderer
import argparse
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
    parser.add_argument(
        '--depth', metavar='NUM', dest='depth',
        type=int, default=8, choices=(4, 8), help='color bit resolution')
    return parser.parse_args()

def main():
    args = parse_args()
    size = [args.width, args.height]
    for i in range(2):
        if not size[i]:
            terminal_size = term_settings.get_term_size()
            target_size = (terminal_size[0] - 1, terminal_size[1] - 1)
            size[i] = target_size[i]

    if args.depth == 4:
        palette = term_settings.PALETTE_16_DARK
    elif args.depth == 8:
        palette = term_settings.PALETTE_256
    if args.palette_path:
        if args.palette_path == 'dark':
            if args.depth != 4:
                raise RuntimeError('Dark palette can be only used with --depth=4')
            palette = term_settings.PALETTE_16_DARK
        elif args.palette_path == 'light':
            if args.depth != 4:
                raise RuntimeError('Light palette can be only used with --depth=4')
            palette = term_settings.PALETTE_16_LIGHT
        else:
            with open(args.palette_path, 'r') as handle:
                palette = json.load(handle)

    image = Image.open(args.input_path)

    if args.depth == 8:
        renderer.render_256(image, palette, size, args.glyph_ar)
    elif args.depth == 4:
        renderer.render_16(image, palette, size, args.glyph_ar)

if __name__ == '__main__':
    main()
