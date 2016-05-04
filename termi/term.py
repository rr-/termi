def _format_sequence(seq, char):
    return '\033[{0}{1}'.format(';'.join(str(x) for x in seq), char)

def reset_attributes():
    return _format_sequence([0], 'm')

def mix_true_color(upper, lower):
    return _format_sequence([
        48, 2, upper[0], upper[1], upper[2],
        38, 2, lower[0], lower[1], lower[2],
    ], 'm')

def mix_256(upper, lower):
    return _format_sequence([48, 5, upper, 38, 5, lower], 'm')

def mix_16(upper, lower):
    return _format_sequence([
        (100 if upper >= 8 else 40) + (upper % 8),
        (90 if lower >= 8 else 30) + (lower % 8),
    ], 'm')

def move_cursor_up(how_many_lines):
    return _format_sequence([how_many_lines], 'A')

def clear_current_line():
    return _format_sequence([0], 'K')
