"""Approved Midline Knees sources and the full-family glyphs that inherit them."""
from copy import deepcopy
from pathlib import Path
from unicodedata import normalize

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

STUDY = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold/av-knees'
REFERENCE_GRID = STUDY / 'reference/ConfiniumMono-FullGrid.ttf'
REFERENCE_VARIABLE = STUDY / 'reference/ConfiniumMono-VariableRepertoire[wght].ttf'
UPPER = STUDY / 'ConfiniumMono-GridToken-AVKnees152StraightAVW.ttf'
LOWER = STUDY / 'ConfiniumMono-GridToken-LowercaseVWKnees144W.ttf'
BASES = 'AVWvw'
SHARED = {'А': 'A'}  # The Cyrillic build derives this outline directly from Latin A.


def accented(font):
    result = {}
    for cp, name in font.getBestCmap().items():
        text = normalize('NFD', chr(cp))
        if len(text) == 2 and text[0] in BASES:
            result[name] = text[0]
    return result


def marked_outline(base, reference_base, reference_marked):
    """Swap the flattened base but keep every mark contour and its position."""
    n = len(reference_base.coordinates)
    k = reference_base.numberOfContours
    if (reference_marked.coordinates[:n] != reference_base.coordinates[:]
            or reference_marked.endPtsOfContours[:k] != reference_base.endPtsOfContours):
        raise ValueError('Expected accented outline to start with the reference base')
    delta = len(base.coordinates) - n
    marked = deepcopy(reference_marked)
    marked.coordinates = GlyphCoordinates(list(base.coordinates) + list(reference_marked.coordinates[n:]))
    marked.flags = base.flags + reference_marked.flags[n:]
    marked.endPtsOfContours = base.endPtsOfContours + [e + delta for e in reference_marked.endPtsOfContours[k:]]
    marked.numberOfContours = len(marked.endPtsOfContours)
    return marked


def approved_outlines(font):
    with TTFont(UPPER) as upper, TTFont(LOWER) as lower, TTFont(REFERENCE_GRID) as reference:
        changes = {n: deepcopy(upper['glyf'][n]) for n in 'AVW'}
        changes.update({n: deepcopy(lower['glyf'][n]) for n in 'vw'})
        # Keep v's outside silhouette. Move its two parallel inner edges
        # together so the cleft lands on w's upper-valley height.
        v, w = changes['v'].coordinates, changes['w'].coordinates
        target = w[3][1]
        if v[3][0] != 400 or w[6][1] != target:
            raise ValueError('Review v/w cleft point order before changing the outlines')
        rise = target - v[3][1]
        for i in (2, 3, 4):
            x, y = v[i]
            v[i] = (x, y + rise)
        cmap = font.getBestCmap()
        for char, base in SHARED.items():
            changes[cmap[ord(char)]] = deepcopy(changes[base])
        for name, base in accented(font).items():
            changes[name] = marked_outline(changes[base], reference['glyf'][base], reference['glyf'][name])
        return changes
