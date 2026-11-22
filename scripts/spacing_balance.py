"""Optical spacing for f–i in the full 800-unit family; no advance changes."""
from copy import deepcopy
from pathlib import Path
from unicodedata import normalize

from midline_promotion import marked_outline

I_CONTROL = (Path(__file__).resolve().parents[1] / 'studies/variable-repertoire'
             / 'i-width-study/reference/ConfiniumMono-FullGrid.ttf')


def wide_i(points, left, right):
    return [(left if k in (0, 5, 6, 9) else right if k in (3, 4) else x, y)
            for k, (x, y) in enumerate(points)]


def balance_i(points):
    # Move stem and dot together; extend the top flag towards f. Leave the
    # baseline foot (and the attachment for the ogonek) in place.
    return [(x - (32 if index in (1, 2, 7, 8, 10, 11, 12, 13) else
                  24 if index in (0, 9) else 0), y)
            for index, (x, y) in enumerate(points)]


def balance_f(points):
    # Shift the shaft and adjoining hook controls, not the bar or hook ends.
    moved = (0, 1, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17)
    return [(x + (56 if index in moved else 0), y)
            for index, (x, y) in enumerate(points)]


def balanced_outlines(font):
    glyf = font['glyf']
    f = deepcopy(glyf['f'])
    if tuple(f.coordinates[0]) != (232, 0) or f.endPtsOfContours != [17]:
        raise ValueError('Review f spacing after changing its construction')
    f.coordinates[:] = balance_f(f.coordinates)
    changes = {'f': f}
    for cp, name in font.getBestCmap().items():
        text = normalize('NFD', chr(cp))
        if len(text) == 2 and text[0] == 'f':
            changes[name] = marked_outline(f, glyf['f'], glyf[name])
        if text[0] != 'i' and chr(cp) not in 'ıі':
            continue
        target = deepcopy(glyf[name])
        base = glyf['i'].coordinates
        count = len(base) if target.coordinates[:len(base)] == base[:] else 10
        if target.coordinates[:count] != base[:count]:
            raise ValueError(f'Unexpected i base in {name}')
        target.coordinates[:count] = wide_i(balance_i(base[:count]), glyf['n'].xMin, glyf['n'].xMax)
        changes[name] = target
    return changes
