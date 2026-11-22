"""Thin construction zones for lowercase shoulders, bowls and apertures."""
from math import hypot

from spacing_balance import balance_i, wide_i

# Map each shared stem wall, bar and tangent control consistently. A
# horizontal/vertical land remains straight, including across curve joins.
WALLS = {
    'n': ((80, 132), (240, 188), (560, 612), (720, 668)),
    'm': ((80, 120), (208, 168), (336, 376), (464, 424), (592, 632), (720, 680)),
    'p': ((80, 132), (240, 188), (560, 612), (720, 668)),
    'q': ((80, 132), (240, 188), (560, 612), (720, 668)),
    'r': ((112, 164), (272, 220), (528, 580), (688, 636)),
    'u': ((80, 132), (240, 188), (560, 612), (720, 668)),
}
ZONES = ((-200, -200), (0, 0), (140, 54), (420, 506), (560, 560))


def remap(value, anchors):
    for (a, x), (b, y) in zip(anchors, anchors[1:]):
        if a <= value <= b:
            return round(x + (value - a) * (y - x) / (b - a))
    raise ValueError(f'Point {value} outside calibrated zones')


def thin_v(bold, w_bold):
    """Build v's parallel shoulders around the actual Thin w valley."""
    target = thin_lowercase('w', w_bold)[3][1]
    slope = (bold[9][0] - bold[10][0]) / 280
    outer, wall = 124, 180
    inner = 400 - slope * (280 - target)
    knee = 280 + (inner - wall) / slope
    foot = outer + slope * 280
    return [(round(x), round(y)) for x, y in [(outer, 560), (wall, 560), (wall, knee),
            (400, target), (800-wall, knee), (800-wall, 560), (800-outer, 560),
            (800-outer, 280), (800-foot, 0), (foot, 0), (outer, 280)]]


def thin_lowercase(name, bold):
    if name == 'i':
        # Same stem, dot and top-bar weight as j. The dotless form uses
        # the same first contour; all terminals are cut on the grid.
        thin = [(200, 560), (468, 560), (468, 54), (632, 54), (632, 0),
                (184, 0), (184, 54), (412, 54), (412, 506), (200, 506),
                (412, 744), (412, 800), (468, 800), (468, 744)]
        return wide_i(balance_i(thin[:len(bold)]), WALLS['n'][0][1], WALLS['n'][-1][1])
    if name == 'e':
        xs = ((80, 132), (240, 188), (560, 612), (680, 632), (720, 668))
        ys = ((0, 0), (136, 52), (226, 254), (348, 306), (428, 508), (560, 560))
        return [(remap(x, xs), remap(y, ys)) for x, y in bold]
    if name == 's':
        # Rotationally balanced lobes. Match the 52-unit upper, middle
        # and lower bars, and pair the straight stem walls around y=420.
        upper = [(650, 560), (650, 508), (256, 508), (188, 508),
                 (188, 425), (188, 399), (188, 306), (256, 306),
                 (544, 306), (664, 306), (664, 173), (664, 140),
                 (664, 0), (540, 0)]
        return upper + [(800-x, 560-y) for x,y in upper]
    if name == 'y':
        # Parallel arm edges, followed by a tangent hook with flat lands
        # 52 units apart. The bend softens toward the descender, not the tip.
        left_slope, right_slope = .49, .46
        left = 137
        right = 665
        il = left + 54*hypot(1, left_slope)
        ir = right - 54*hypot(1, right_slope)
        cleft = (ir-il)/(left_slope+right_slope)
        join = (ir-left)/(left_slope+right_slope)
        outer_turn = right - right_slope*665
        inner_turn = ir - right_slope*665
        points = [(left, 560), (il, 560), (il + left_slope*cleft, 560-cleft), (ir, 560),
                  (right, 560), (outer_turn, -105), (outer_turn-right_slope*95, -200), (255, -200),
                  (162, -200), (162, -148), (255, -148), (inner_turn-right_slope*43, -148),
                  (inner_turn, -105), (left+left_slope*join, 560-join)]
        return [(round(x), round(y)) for x,y in points]
    if name == 'h':
        # Same shoulder and stem walls as n, with the left stem extended.
        return [(remap(x, WALLS['n']), remap(y, ZONES + ((800, 800),))) for x, y in bold]
    if name in ('a', 'b', 'd', 'g', 'j', 'z'):
        return thin_bowls_and_hooks(name, bold)
    if name in WALLS:
        return [(remap(x, WALLS[name]), remap(y, ZONES)) for x, y in bold]
    if name == 'x':
        # Two equal-width strokes crossing at the centre of the x-height.
        slope = 222 / 278
        half = 54 * hypot(1, slope) / 2
        inset = 280 * slope
        lo, hi = 400 - inset - half, 400 - inset + half
        notch = half / slope
        return [(round(x), round(y)) for x, y in [(lo, 560), (hi, 560),
                (400, 280+notch), (800-hi, 560), (800-lo, 560), (400+half, 280),
                (800-lo, 0), (800-hi, 0), (400, 280-notch), (hi, 0), (lo, 0), (400-half, 280)]]
    if name == 'k':
        # ±45° arms, both ~54 units normal to the stroke. Solve the join
        # between their parallel edges before cutting the ends on the grid.
        x, y, half = 350, 290, 54 * hypot(1, 1) / 2
        wall = 188
        upper = y - x
        lower = y + x
        return [(round(a), round(b)) for a, b in [(132, 0), (132, 800), (wall, 800),
                (wall, wall+upper+half), (560-upper-half, 560), (560-upper+half, 560),
                (x+half, y), (lower+half, 0), (lower-half, 0), (x, y-half),
                (wall, wall+upper-half), (wall, 0)]]
    if name == 'X':
        if bold != [(80, 0), (316, 400), (80, 800), (248, 800), (400, 542), (552, 800),
                    (720, 800), (484, 400), (720, 0), (552, 0), (400, 258), (248, 0)]:
            raise ValueError('X: review Thin master after changing the Bold contour')
        slope = .59
        half = 54 * hypot(1, slope) / 2
        left, right = 400 - 400*slope - half, 400 - 400*slope + half
        notch = half/slope
        return [(round(x), round(y)) for x, y in [(left, 0), (400-half, 400), (left, 800), (right, 800),
                (400, 400+notch), (800-right, 800), (800-left, 800), (400+half, 400),
                (800-left, 0), (800-right, 0), (400, 400-notch), (right, 0)]]
    if name == 'w':
        if bold != [(80, 560), (224, 560), (224, 308), (276, 177), (344, 420), (456, 420),
                    (524, 177), (576, 308), (576, 560), (720, 560), (720, 280), (608, 0),
                    (441, 0), (400, 145), (359, 0), (192, 0), (80, 280)]:
            raise ValueError('w: review Thin master after changing the Bold contour')
        # Two complete 48-unit diagonal strokes per half. Their inner
        # intersections find the valleys rather than inheriting tapered miters.
        a, b = .4, .28
        outer, inner = 256 - 24*hypot(1, a), 256 + 24*hypot(1, a)
        ridge, cleft = 280 - 24*hypot(1, b), 280 + 24*hypot(1, b)
        y = (inner-ridge)/(a+b)
        x = ridge+b*y
        shoulder = ridge+b*408
        j = (inner-173)/a
        k = (outer-125)/a
        return [(round(x), round(y)) for x, y in [(125, 560), (173, 560), (173, j), (x, y),
                (shoulder, 408), (800-shoulder, 408), (800-x, y), (627, j), (627, 560),
                (675, 560), (675, k), (800-outer, 0), (800-cleft, 0), (400, (400-cleft)/b),
                (cleft, 0), (outer, 0), (125, k)]]
    return None


def thin_bowls_and_hooks(name, bold):
    if name == 'z':
        # Same diagonal direction on both edges, clipped to equal flat bars.
        slope = 364 / 298
        half = 52 * hypot(1, slope) / 2
        def left(y):
            return 400 + slope * (y - 280) - half
        def right(y):
            return 400 + slope * (y - 280) + half
        end = 680
        knee = 280 + (end - 400 - half) / slope
        return [(round(x), round(y)) for x, y in [(120, 560), (end, 560), (end, knee),
                (right(54), 54), (end, 54), (end, 0), (120, 0), (120, 560-knee),
                (left(506), 506), (120, 506)]]
    if name == 'a':
        xs = ((80, 132), (112, 150), (236, 188), (560, 612), (720, 668))
        ys = ((0, 0), (128, 52), (212, 244), (336, 296), (420, 506), (560, 560))
        # The narrow channel above the lower bowl stays open; top and bottom
        # of its cutout more closely match the adjacent horizontal bars.
        return [(remap(x, xs), remap(y, ys)) if i not in (15, 16, 17, 18, 19)
                else (remap(x, xs), remap(y, ((336, 296), (388, 474), (420, 506))))
                for i, (x, y) in enumerate(bold)]
    if name in 'bd':
        xs = WALLS['n']
        ys = ZONES + ((800, 800),)
        return [(remap(x, xs), remap(y, ys)) for x, y in bold]

    # Hooks: keep the baseline and descender zone fixed. Match the two
    # curved wall tangents by sharing the vertical turn height, and keep
    # the terminal horizontal lands 52 units apart.
    if name == 'g':
        xs = WALLS['n']
        ys = ((-200, -200), (-60, -148), (0, 0), *ZONES[2:])
        turns = {1: -108, 8: -108}
    else:
        xs = ((96, 128), (176, 200), (360, 412), (520, 468))
        ys = ((-200, -200), (-60, -148), (420, 506), (560, 560), (640, 744), (800, 800))
        turns = {2: -108, 9: -108}
    return [(remap(x, xs), turns[i] if i in turns else remap(y, ys)) for i, (x, y) in enumerate(bold)]
