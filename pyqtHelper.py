import sys

def human_readable_size(bytes, suffix='B'):
    if bytes == 0:
        return '0 {}'.format(suffix)
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi']:
        if bytes < 1024.0:
            return '{0:.2f} {1}B'.format(bytes, unit)
        bytes /= 1024.0
    return '{0:.2f} {1}B'.format(bytes, 'Yi')