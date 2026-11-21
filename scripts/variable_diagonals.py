"""Optical Thin masters for joined straight strokes in M, N, and W.

The coordinates follow the approved Bold point order, but are constructed
from parallel edges and exact intersections, not independent vertex insets.
"""
from math import hypot


# Fail clearly if the upstream Bold topology (including its point order) changes.
BOLD = {
    'M': [(80, 0), (80, 800), (240, 800), (240, 779), (400, 339), (560, 779),
          (560, 800), (720, 800), (720, 0), (560, 0), (560, 381), (472, 140),
          (328, 140), (240, 381), (240, 0)],
    'N': [(80, 0), (80, 800), (253, 800), (560, 266), (560, 800), (720, 800),
          (720, 0), (547, 0), (240, 534), (240, 0)],
    'W': [(80, 800), (208, 800), (208, 419), (259, 250), (336, 560), (464, 560),
          (541, 250), (592, 419), (592, 800), (720, 800), (720, 400), (600, 0),
          (472, 0), (400, 288), (328, 0), (200, 0), (80, 400)],
}


def thin_master(name, bold):
    name = 'M' if name == 'uni041C' else name
    if name not in BOLD:
        return None
    if bold != BOLD[name]:
        raise ValueError(f'{name}: review Thin master after changing the Bold contour')
    if name == 'N':
        # Constant x separation between two lines of the same slope.
        slope = (547 - 240) / 534
        half = 54 * hypot(1, slope) / 2
        left, right = 400 + 400*slope - half, 400 + 400*slope + half
        points = [(129, 0), (129, 800), (right-800*slope, 800),
                  (609, (right-609)/slope), (609, 800), (671, 800),
                  (671, 0), (left, 0), (191, (left-191)/slope), (191, 0)]
    elif name == 'M':
        slope = 160 / 440
        half = 54 * hypot(1, slope) / 2
        lower, upper = 451 - half, 451 + half
        top_join = (upper - 191) / slope
        lower_join = (lower - 191) / slope
        chin = lower - slope*155
        points = [(129, 0), (129, 800), (191, 800), (191, top_join),
                  (400, (upper-400)/slope), (609, top_join), (609, 800), (671, 800),
                  (671, 0), (609, 0), (609, lower_join), (800-chin, 155), (chin, 155),
                  (191, lower_join), (191, 0)]
    else:
        outer_slope, centre_slope = .30, .25
        outer_half = 44 * hypot(1, outer_slope) / 2
        centre_half = 44 * hypot(1, centre_slope) / 2
        outside, inside = 267 - outer_half, 267 + outer_half
        ridge_side, cleft_side = 262 - centre_half, 262 + centre_half
        valley_y = (inside - ridge_side) / (outer_slope + centre_slope)
        valley_x = ridge_side + centre_slope * valley_y
        ridge_x = ridge_side + centre_slope * 540
        inner_join = (inside - 168) / outer_slope
        outer_join = (outside - 120) / outer_slope
        points = [(120, 800), (168, 800), (168, inner_join), (valley_x, valley_y),
                  (ridge_x, 540), (800-ridge_x, 540), (800-valley_x, valley_y),
                  (632, inner_join), (632, 800), (680, 800), (680, outer_join),
                  (800-outside, 0), (800-cleft_side, 0), (400, (400-cleft_side)/centre_slope),
                  (cleft_side, 0), (outside, 0), (120, outer_join)]
    return [(round(x), round(y)) for x, y in points]
