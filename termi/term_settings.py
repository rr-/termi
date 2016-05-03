# Contains code from https://github.com/mkoskar/tcolors
import os
import sys
import re
import termios
import select
from contextlib import contextmanager

_poll = None
_TERM = os.environ.get('TERM')
if os.environ.get('TMUX'):
    _seqfmt = '\033Ptmux;\033{}\a\033\\'
elif _TERM and (_TERM == 'screen' or _TERM.startswith('screen-')):
    _seqfmt = '\033P{}\a\033\\'
else:
    _seqfmt = '{}\033\\'

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
        raise RuntimeError('<stdin> is not connected to a terminal')
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
    with get_term_colors():
        rgb = []
        for i in range(256):
            rgb.append(get_colorp(i))
        return rgb

def get_term_size():
    rows, columns = os.popen('stty size', 'r').read().split()
    return (int(columns), int(rows))
