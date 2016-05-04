def _format_sequence(attrs, char):
    return '\033[{0}{1}'.format(';'.join(str(x) for x in attrs), char)

def reset_attributes():
    return _format_sequence([0], 'm')

def mix_true_color(bg, fg):
    return _format_sequence([
        48, 2, bg[0], bg[1], bg[2],
        38, 2, fg[0], fg[1], fg[2],
    ], 'm')

def mix_256(bg, fg):
    return _format_sequence([48, 5, bg, 38, 5, fg], 'm')

def mix_16(bg, fg):
    return _format_sequence([
        (100 if bg >= 8 else 40) + (bg % 8),
        (90 if fg >= 8 else 30) + (fg % 8),
    ], 'm')

def set_cursor_pos(x, y):
    return _format_sequence([0, 0], 'f')
