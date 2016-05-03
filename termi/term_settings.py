# Contains code from https://github.com/mkoskar/tcolors
import os
import sys
import re
import termios
import select
from contextlib import contextmanager

DEFAULT_PALETTE = [(int(x[0:2], 16), int(x[2:4], 16),int(x[4:6], 16)) for x in [
    '2B2B2B', '870000', '3F573F', '875F00', '005FAF', '3F3F67', '004747', '818181',
    '414141', 'D70000', '6FA76F', 'D7AF00', '00AFFF', '7F7FB7', '00B7B7', 'CECECE',
    '000000', '00005F', '000087', '0000AF', '0000D7', '0000FF', '005F00', '005F5F',
    '005F87', '005FAF', '005FD7', '005FFF', '008700', '00875F', '008787', '0087AF',
    '0087D7', '0087FF', '00AF00', '00AF5F', '00AF87', '00AFAF', '00AFD7', '00AFFF',
    '00D700', '00D75F', '00D787', '00D7AF', '00D7D7', '00D7FF', '00FF00', '00FF5F',
    '00FF87', '00FFAF', '00FFD7', '00FFFF', '5F0000', '5F005F', '5F0087', '5F00AF',
    '5F00D7', '5F00FF', '5F5F00', '5F5F5F', '5F5F87', '5F5FAF', '5F5FD7', '5F5FFF',
    '5F8700', '5F875F', '5F8787', '5F87AF', '5F87D7', '5F87FF', '5FAF00', '5FAF5F',
    '5FAF87', '5FAFAF', '5FAFD7', '5FAFFF', '5FD700', '5FD75F', '5FD787', '5FD7AF',
    '5FD7D7', '5FD7FF', '5FFF00', '5FFF5F', '5FFF87', '5FFFAF', '5FFFD7', '5FFFFF',
    '870000', '87005F', '870087', '8700AF', '8700D7', '8700FF', '875F00', '875F5F',
    '875F87', '875FAF', '875FD7', '875FFF', '878700', '87875F', '878787', '8787AF',
    '8787D7', '8787FF', '87AF00', '87AF5F', '87AF87', '87AFAF', '87AFD7', '87AFFF',
    '87D700', '87D75F', '87D787', '87D7AF', '87D7D7', '87D7FF', '87FF00', '87FF5F',
    '87FF87', '87FFAF', '87FFD7', '87FFFF', 'AF0000', 'AF005F', 'AF0087', 'AF00AF',
    'AF00D7', 'AF00FF', 'AF5F00', 'AF5F5F', 'AF5F87', 'AF5FAF', 'AF5FD7', 'AF5FFF',
    'AF8700', 'AF875F', 'AF8787', 'AF87AF', 'AF87D7', 'AF87FF', 'AFAF00', 'AFAF5F',
    'AFAF87', 'AFAFAF', 'AFAFD7', 'AFAFFF', 'AFD700', 'AFD75F', 'AFD787', 'AFD7AF',
    'AFD7D7', 'AFD7FF', 'AFFF00', 'AFFF5F', 'AFFF87', 'AFFFAF', 'AFFFD7', 'AFFFFF',
    'D70000', 'D7005F', 'D70087', 'D700AF', 'D700D7', 'D700FF', 'D75F00', 'D75F5F',
    'D75F87', 'D75FAF', 'D75FD7', 'D75FFF', 'D78700', 'D7875F', 'D78787', 'D787AF',
    'D787D7', 'D787FF', 'D7AF00', 'D7AF5F', 'D7AF87', 'D7AFAF', 'D7AFD7', 'D7AFFF',
    'D7D700', 'D7D75F', 'D7D787', 'D7D7AF', 'D7D7D7', 'D7D7FF', 'D7FF00', 'D7FF5F',
    'D7FF87', 'D7FFAF', 'D7FFD7', 'D7FFFF', 'FF0000', 'FF005F', 'FF0087', 'FF00AF',
    'FF00D7', 'FF00FF', 'FF5F00', 'FF5F5F', 'FF5F87', 'FF5FAF', 'FF5FD7', 'FF5FFF',
    'FF8700', 'FF875F', 'FF8787', 'FF87AF', 'FF87D7', 'FF87FF', 'FFAF00', 'FFAF5F',
    'FFAF87', 'FFAFAF', 'FFAFD7', 'FFAFFF', 'FFD700', 'FFD75F', 'FFD787', 'FFD7AF',
    'FFD7D7', 'FFD7FF', 'FFFF00', 'FFFF5F', 'FFFF87', 'FFFFAF', 'FFFFD7', 'FFFFFF',
    '080808', '121212', '1C1C1C', '262626', '303030', '3A3A3A', '444444', '4E4E4E',
    '585858', '626262', '6C6C6C', '767676', '808080', '8A8A8A', '949494', '9E9E9E',
    'A8A8A8', 'B2B2B2', 'BCBCBC', 'C6C6C6', 'D0D0D0', 'DADADA', 'E4E4E4', 'EEEEEE',
]]

_poll = None
_TERM = os.environ.get('TERM')
if os.environ.get('TMUX'):
    _seqfmt = '\033Ptmux;\033{}\a\033\\'
elif _TERM and (_TERM == 'screen' or _TERM.startswith('screen-')):
    _seqfmt = '\033P{}\a\033\\'
else:
    _seqfmt = '{}\033\\'

class TerminalSettingsError(RuntimeError):
    pass

def get_colorp(n):
    return get_term_color([4, n])

def get_colorfg():
    return get_term_color([10])

def get_colorbg():
    return get_term_color([11])

def get_colorcur():
    return get_term_color([12])

def get_term_color(ansi, timeout=1000, retries=5):
    global _poll
    if not _poll:
        _poll = select.poll()
        _poll.register(sys.stdin.fileno(), select.POLLIN)
    while _poll.poll(0):
        sys.stdin.read()
    query = '\033]' + ';'.join([str(a) for a in ansi]) + ';?' + '\007'
    os.write(0, _seqfmt.format(query).encode())
    regex = re.compile(
        '\033\\](\d+;)+rgba?:(([0-9a-f]+)/)?([0-9a-f]+)/([0-9a-f]+)/([0-9a-f]+)\007',
        re.IGNORECASE)
    match = None
    output = ''
    while not match:
        if retries < 1 or not _poll.poll(timeout):
            return None
        retries -= 1
        output += sys.stdin.read()
        match = regex.search(output)
    return [int(match.group(i)[:2], 16) for i in (4, 5, 6)]

@contextmanager
def get_term_colors():
    if not sys.stdin.isatty():
        raise TerminalSettingsError('<stdin> is not connected to a terminal')
    tc_save = None
    try:
        tc_save = termios.tcgetattr(sys.stdin.fileno())
        tc = termios.tcgetattr(sys.stdin.fileno())
        tc[3] &= ~termios.ECHO
        tc[3] &= ~termios.ICANON
        tc[6][termios.VMIN] = 0
        tc[6][termios.VTIME] = 0
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, tc)
        yield
    finally:
        if tc_save:
            termios.tcsetattr(
                sys.stdin.fileno(),
                termios.TCSANOW,
                tc_save)

def get_term_palette():
    try:
        with get_term_colors():
            rgb = []
            for i in range(256):
                rgb.append(get_colorp(i))
            return rgb
    except TerminalSettingsError:
        return DEFAULT_PALETTE

def get_term_size():
    output = os.popen('stty size', 'r').read().split()
    if len(output) == 0:
        return (80, 25)
    rows, columns = output
    return (int(columns), int(rows))
