"""Match m's three stems to capital U without moving its outside walls."""
from pathlib import Path

from variable_lowercase import remap

M_CONTROL = (Path(__file__).resolve().parents[1] / 'studies/variable-repertoire'
             / 'm-stroke-study/reference/ConfiniumMono-VariableRepertoire[wght].ttf')


def stem_positions(points):
    return [round(points[i][0]) for i in (0, 30, 23, 22, 15, 14)]


def u_stem(points):
    return round(points[2][0] - points[1][0])


def equal_m(points, stem):
    positions = stem_positions(points)
    left, _, mid_left, mid_right, _, right = positions
    center_left = (mid_left + mid_right - stem) // 2
    target = [left, left + stem, center_left, center_left + stem, right - stem, right]
    if not all(a < b for a, b in zip(target, target[1:])):
        raise ValueError('Equal-width m would close its counters')
    anchors = tuple(zip(positions, target))
    return [(remap(round(x), anchors), round(y)) for x, y in points]
