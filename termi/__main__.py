import argparse
import json
import sys
import time
from PIL import Image
from termi import term
from termi import term_settings
from termi import renderer

def positive_int(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError('Only positive integers allowed')
    return value

def parse_args():
    parser = argparse.ArgumentParser(
        prog='termi', description='Convert images to ASCII')
    parser.add_argument(
        '--glyph-ar', dest='glyph_ar', metavar='NUM',
        type=float, default=2, help='character aspect ratio (default: 2)')
    parser.add_argument(
        '--width', metavar='NUM', type=int, default=None,
        help='target width in characters (default: terminal width)')
    parser.add_argument(
        '--height', metavar='NUM', type=int, default=None,
        help='target height in characters (default: terminal height)')
    parser.add_argument(
        metavar='PATH', dest='input_path',
        help='where to get the input image from')
    parser.add_argument(
        '--depth', metavar='NUM', dest='depth',
        type=int, default=8, choices=(4, 8, 24),
        help='color bit resolution (default: 8)')
    parser.add_argument(
        '--palette', metavar='PATH', dest='palette_path',
        help='custom palette (JSON); for --depth=4 can be also "dark" or "light"')
    parser.add_argument(
        '--scale', default='lanczos',
        choices=('lanczos', 'bicubic', 'nearest'),
        help='how to scale the image')
    parser.add_argument(
        '--animate', action='store_true', help='animate GIF images')
    parser.add_argument(
        '--loop', action='store_true', help='loop the animation until ^C')
    args = parser.parse_args()
    if args.loop:
        args.animate = True
    return args

def _get_palette(depth, path):
    if depth == 4:
        return term_settings.PALETTE_16_DARK
    if depth == 8:
        return term_settings.PALETTE_256
    if path:
        if depth == 24:
            raise RuntimeError('Palette doesn\'t make sense with --depth=24')
        if path == 'dark':
            if depth != 4:
                raise RuntimeError('Dark palette can be only used with --depth=4')
            return term_settings.PALETTE_16_DARK
        if path == 'light':
            if depth != 4:
                raise RuntimeError('Light palette can be only used with --depth=4')
            return term_settings.PALETTE_16_LIGHT
        with open(path, 'r') as handle:
            return json.load(handle)
    return None

def main():
    args = parse_args()
    target_size = [args.width, args.height]
    for i in range(2):
        if not target_size[i]:
            terminal_size = term_settings.get_term_size()
            target_size[i] = terminal_size[i] - 1

    palette = _get_palette(args.depth, args.palette_path)

    image = Image.open(args.input_path)
    if palette:
        palette_image = renderer.create_palette_image(palette)
    else:
        palette_image = None

    output_strategy = {
        24: term.mix_true_color,
        8: term.mix_256,
        4: term.mix_16,
    }[args.depth]

    scale_strategy = {
        'lanczos': Image.LANCZOS,
        'bicubic': Image.BICUBIC,
        'nearest': Image.NEAREST,
    }[args.scale]

    frame = renderer.render_image(
        image, target_size, args.glyph_ar, palette_image,
        output_strategy, scale_strategy)
    print(frame, end='')
    height = frame.count('\n')

    if args.animate and getattr(image, 'is_animated', False):
        frames = []
        while image.tell() + 1 < image.n_frames:
            print(
                'decoding frame {0} / {1}'.format(image.tell(), image.n_frames),
                file=sys.stderr,
                end='\r')
            frame = renderer.render_image(
                image, target_size, args.glyph_ar, palette_image,
                output_strategy, scale_strategy)
            frames.append(frame)
            image.seek(image.tell() + 1)

        print(term.clear_current_line(), end='')

        while True:
            for frame in frames:
                try:
                    print(term.move_cursor_up(height) + frame, end='')
                    time.sleep(image.info['duration'] / 1000)
                except (KeyboardInterrupt, SystemExit):
                    return
            if not args.loop:
                return


if __name__ == '__main__':
    main()
