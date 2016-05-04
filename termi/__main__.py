import argparse
import json
import sys
import time
from termi import term
from termi import term_settings
from termi import renderer
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
        type=int, default=8, choices=(4, 8, 24), help='color bit resolution')
    parser.add_argument(
        '--animate', action='store_true', help='animate GIF images')
    parser.add_argument(
        '--loop', action='store_true', help='loop animation until ^C')
    args = parser.parse_args()
    if args.loop:
        args.animate = True
    return args

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
    else:
        palette = None
    if args.palette_path:
        if args.depth == 24:
            raise RuntimeError('Palette doesn\'t make sense with --depth=24')
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
    if palette:
        palette_image = renderer.create_palette_image(palette)
    else:
        palette_image = None

    if args.depth == 24:
        output_strategy = term.mix_true_color
    elif args.depth == 8:
        output_strategy = term.mix_256
    elif args.depth == 4:
        output_strategy = term.mix_16

    if args.animate and getattr(image, 'is_animated', False):
        frames = []
        while image.tell() + 1 < image.n_frames:
            print('decoding frame {0} / {1}'.format(
                image.tell(), image.n_frames), file=sys.stderr, end='\r')
            frame = renderer.render_image(
                image, size, args.glyph_ar, palette_image, output_strategy)
            frames.append(frame)
            image.seek(image.tell() + 1)

        stop = False
        while True:
            for frame in frames:
                try:
                    print(term.set_cursor_pos(0, 0) + frame, end='')
                    time.sleep(image.info['duration'] / 1000)
                except (KeyboardInterrupt, SystemExit):
                    return
            if not args.loop:
                return
    else:
        print(
            renderer.render_image(
                image, size, args.glyph_ar, palette_image, output_strategy),
            end='')


if __name__ == '__main__':
    main()
