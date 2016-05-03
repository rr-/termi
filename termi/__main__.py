from termi import term_settings
from termi import renderer
import argparse
import sys
import json

def positive_int(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError('Only positive integers allowed')
    return x

def parse_args():
    parser = argparse.ArgumentParser(description='Convert images to ASCII')
    subparsers = parser.add_subparsers()

    main_parser = subparsers.add_parser('show', help='convert image to ASCII')
    main_parser.add_argument(
        '--glyph-aspect-ratio', dest='glyph_ar', metavar='NUM', type=float, default=1.9,
        help='character aspect ratio (default: 1.9)')
    main_parser.add_argument(
        '--width', metavar='NUM', type=int, default=None,
        help='target image width (in characters)')
    main_parser.add_argument(
        '--height', metavar='NUM', type=int, default=None,
        help='target image height (in characters)')
    main_parser.add_argument(
        metavar='PATH', dest='input_path',
        help='where to get the input image from')
    main_parser.add_argument(
        '--palette', metavar='PATH', dest='palette_path',
        help='custom palette')
    main_parser.add_argument(
        '--quality', metavar='NUM', dest='quality', default=5, type=positive_int,
        help='quality (the higher the better)')
    main_parser.set_defaults(func=cmd_render_image)

    dump_parser = subparsers.add_parser(
        'dump-palette',
        help='guess palette from terminal settings and dump it to stdout')
    dump_parser.set_defaults(func=cmd_dump_palette)

    args = parser.parse_args()
    if not hasattr(args, 'func') or not args.func:
        parser.print_help()
        sys.exit(1)
    return args

def cmd_render_image(args):
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
        palette = term_settings.get_term_palette()
    output = renderer.prepare_image(
        palette, args.input_path, size, args.glyph_ar, args.quality)
    renderer.print_output(*output)

def cmd_dump_palette(args):
    palette = term_settings.get_term_palette()
    print(json.dumps(palette))

def main():
    args = parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
