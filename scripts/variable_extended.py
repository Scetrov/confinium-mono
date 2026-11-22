"""Compatible Thin masters for selected European Latin and Cyrillic letters."""
from math import hypot

from spacing_balance import balance_f
from variable_diagonals import thin_master
from variable_lowercase import thin_lowercase


def zones(points, x, y):
    """Move shared walls, tangencies and control points as a group."""
    return [(x[a], y[b]) for a, b in points]


def slash(x0, x1, y0, y1, width):
    """A parallel-sided stroke with upright end cuts, in contour order."""
    half = width * hypot(x1-x0, y1-y0) / (2 * (x1-x0))
    return [(x0, y0+half), (x1, y1+half), (x1, y1-half), (x0, y0-half)]


def round_zones(xs=(129, 191, 609, 671)):
    """Shared walls and nested rounded corners for Ø, Ю and Э."""
    l, li, ri, r = xs
    x = {80:l, 123:l+43, 196:l+116, 240:l+160,
         560:r-160, 604:r-116, 677:r-43, 720:r}
    xi = {240:li, 259:li+41, 272:li+106, 528:ri-106, 541:ri-41, 560:ri}
    y = {v:v for v in (0, 43, 116, 160, 640, 684, 757, 800)}
    yi = {140:54, 159:95, 172:160, 628:640, 641:705, 660:746}
    return x, y, xi, yi


def round_bowl(points, xs=(129, 191, 609, 671)):
    x, y, xi, yi = round_zones(xs)
    return zones(points[:20], x, y) + zones(points[20:36], xi, yi)


def unscale(values, scale, shift=0):
    """Recover parent coordinate zones from a scaled Full Grid part."""
    result = {round(scale*v+shift): v for v in values}
    if len(result) != len(set(values)):
        raise ValueError('Scaled coordinate zones are ambiguous')
    return result


def open_round(c, p):
    x, y, xi, yi = round_zones()
    if c in 'UC':
        # Open the lower counter with an elliptical bend. Both edges leave
        # the stems at y=190 and land almost directly above one another.
        # Tangent controls approximate 30° outer and 45° inner arc sections
        # in the existing three- and two-quadratic point orders.
        outer_x = {**x, 123:184, 196:278, 240:333, 560:467, 604:522, 677:616}
        inner_x = {**xi, 259:277, 272:337, 528:463, 541:523}
        outer_y = {**y, 43:51, 116:139, 160:190}
        inner_y = {**yi, 159:134, 172:190, 800:800}

        def outer(points):
            return [(outer_x[a], outer_y[b]) if b <= 160 else (x[a], y[b])
                    for a, b in points]

        def inner(points):
            return [(inner_x[a], inner_y[b]) if b <= 172 else (xi[a], inner_y[b])
                    for a, b in points]

        if c == 'U':
            return outer(p[:2]) + inner(p[2:12]) + outer(p[12:])
        # Leave the upper C intact; the terminal faces stay square.
        y.update({220:220, 580:580})
        inner_y.update({220:220, 580:580})
        return outer(p[:1]) + inner(p[1:19]) + outer(p[19:40])
    return zones(p[:22], x, {**y, 220:220, 580:580}) + zones(p[22:40], xi, {**yi, 220:220, 580:580})


def lower_bowl(points, height=560, xs=(132, 188, 612, 668)):
    l, li, ri, r = xs
    x = {80:l, 240:li, 272:li+62, 528:ri-62, 560:ri, 720:r}
    y = {0:0, 160:112, 400:height-112, 560:height}
    yi = {140:54, 172:116, 388:height-116, 420:height-54}
    if height == 510:
        y = {0:0, 146:112, 364:height-112, 510:height}
        yi = {127:54, 157:116, 353:height-116, 382:height-54}
    # The outside has a tight square shoulder (as in the Bold o).
    # Keep the inside similarly squared; these controls retain tangency.
    return (zones(points[:12], {**x,240:l+112,560:r-112}, y)
            + zones(points[12:24], x, yi))


# The explicit point lists match the on/off-curve order of the Full Grid glyphs.
T = [(369,0), (369,746), (129,746), (129,800),
     (671,800), (671,746), (431,746), (431,0)]
F = [(281,0), (281,479), (145,479), (145,531), (281,531), (281,674),
     (281,800), (392,800), (639,800), (639,746), (424,746), (343,746),
     (343,660), (343,531), (591,531), (591,479), (343,479), (343,0)]


def soft_sign(l, r):
    li, ri = l+60, r-60
    return [(l,0), (l,800), (li,800), (li,451), (r-172,451), (r,451),
            (r,299), (r,152), (r,0), (r-172,0),
            (li,54), (ri-85,54), (ri,54), (ri,139), (ri,312),
            (ri,397), (ri-85,397), (li,397)]


def eth_hook():
    # Offset the endpoints along their normals and blend the control offset
    # to keep the middle of the quadratic at comparable weight.
    a, b, c = (287, 783), (633, 600), (640, 355)
    def normal(v, w):
        dx, dy = w[0]-v[0], w[1]-v[1]
        return -dy/hypot(dx,dy), dx/hypot(dx,dy)
    n, m = normal(a,b), normal(b,c)
    def edge(sign):
        def shift(p, u, v):
            return (p[0]+sign*28*u, p[1]+sign*28*v)
        return [shift(a,*n), shift(b, .55*(n[0]+m[0]), .55*(n[1]+m[1])), shift(c,*m)]
    return edge(-1)[::-1] + edge(1)


def ligature_e(points):
    ex = {349:366, 444:422, 462:464, 614:597, 632:639, 703:657, 727:695}
    ey = {0:0, 136:52, 160:106, 168:124, 226:254, 348:306,
          396:427, 400:437, 428:508, 560:560}
    return zones(points, ex, ey)


TARGETS = 'ØÆÞæðøþŁłŊИифЮюЭЬЫЪTfUCODÐŒœ'


def thin_extended(c, p):
    if c not in TARGETS:
        return None
    if c in 'UCЭ':
        q = open_round(c, p)
        if c == 'Э':
            q += [(376,373),(376,427),(637,427),(637,373)]
    elif c in 'OØ':
        q = round_bowl(p)
        if c == 'Ø':
            half = 27 * hypot(1, 554/800)
            q += [(123-half,0), (677-half,800), (677+half,800), (123+half,0)]
    elif c in 'DÐ':
        x, y, xi, yi = round_zones()
        q = zones(p[:12], x, y) + zones(p[12:22], xi, yi)
        if c == 'Ð':
            q += [(88,386),(88,438),(304,438),(304,386)]
    elif c in 'Œœ':
        # After narrowing the ligature components, use one coincident wall
        # between them so overlapping solids don't make a darker seam.
        x, _, xi, _ = round_zones()
        original_x = unscale((*x, *xi), .61, 30)
        original_x.update({149:196, 399:604})  # UFO controls are rounded after scaling.
        if c == 'Œ':
            q = round_bowl([(original_x[a], b) for a,b in p[:36]], (108,168,370,430))
            ex = {349:370, 444:430, 727:679}
            ey = {0:0, 140:54, 330:373, 470:427, 660:746, 800:800}
            q += zones(p[36:], ex, ey)
        else:
            q = lower_bowl([(original_x[x],y) for x,y in p[:24]], xs=(107,163,366,422))
            q += ligature_e(p[24:])
    elif c == 'ø':
        half = 27 * hypot(1, 554/560)
        q = lower_bowl(p) + [(123-half,0), (677-half,560), (677+half,560), (123+half,0)]
    elif c in 'Łł':
        stem = ([(129,0),(129,800),(191,800),(191,54),(671,54),(671,0)]
                if c == 'Ł' else
                [(193,800),(415,800),(415,147),(415,54),(508,54),(623,54),
                 (623,0),(456,0),(353,0),(353,160),(353,748),(193,748)])
        q = stem + slash(84, 524, 215, 475, 52)
    elif c == 'Þ':
        q = [(132,124),(132,615),(519,615),(559,615),(626,590),(668,550),
             (668,519),(668,486),(668,455),(626,415),(559,390),(519,390),
             (188,390),(188,124),(188,443),(540,443),(580,443),(612,468),
             (612,490),(612,515),(612,537),(580,562),(540,562),(188,562),
             (132,0),(132,800),(188,800),(188,0)]
    elif c == 'þ':
        q = thin_lowercase('p', p[:26]) + [(132,0),(132,800),(188,800),(188,0)]
    elif c == 'ð':
        q = lower_bowl(p, 510) + eth_hook() + slash(327, 617, 563, 751, 50)
    elif c == 'Æ':
        # Replace the doubled right leg with a common vertical stem. The left
        # diagonal has 56 normal units, measured away from the bar and apex.
        slope = .29
        left = 105
        inner = left + 56*hypot(1,slope)
        q = [(left,0),(left+800*slope,800),(430,800),(430,0),
             (370,0),(370,242),(inner+242*slope,242),(inner,0),
             (inner+296*slope,296),(370,296),(370,(370-inner)/slope),
             (370,0),(370,800),(679,800),(679,746),(430,746),(430,427),
             (679,427),(679,373),(430,373),(430,54),(679,54),(679,0)]
        # The A counter is triangular in Bold. Keep it open against the shared
        # stem: its left edge lies on the same sloping wall as the lower leg.
        # Don't fill the A counter with the E's stem: it ends at x=370.
        # The lower portion of the A leg and the E share x=370..430.
    elif c == 'æ':
        # The two parts share a single 56-unit stem instead of stacking walls.
        ax = {98:126, 372:366, 469:422, 347:333, 303:275, 167:162,
              79:107, 352:324, 191:204, 342:303, 174:163}
        ay = {0:0, 44:18, 128:52, 144:89, 156:116, 176:162, 184:180,
              200:217, 212:244, 336:296, 388:474, 400:456, 420:506, 560:560}
        q = zones(p[:30], ax, ay) + ligature_e(p[30:])
    elif c == 'Ŋ':
        q = thin_master('N', p[:10]) + [(609,40),(671,40),(671,-40),
             (671,-200),(511,-200),(401,-200),(401,-146),(507,-146),(609,-146),(609,-44)]
    elif c in 'Ии':
        h = 800 if c == 'И' else 560
        slope = (560-232)/508 if h == 800 else (560-232)/356
        half = 27*hypot(1,slope)
        lo, hi = 400-slope*h/2-half, 400-slope*h/2+half
        q = [(125,0),(125,h),(187,h),(187,(187-lo)/slope),(lo+slope*h,h),
             (675,h),(675,0),(613,0),(613,(613-hi)/slope),(hi,0)]
    elif c == 'ф':
        q = lower_bowl(p) + [(370,-200),(370,800),(430,800),(430,-200)]
    elif c in 'Юю':
        # Restore the original O zones before drawing the narrowed bowl.
        x, y, xi, yi = round_zones((275,335,635,695))
        original_x = unscale((*x, *xi), .73, 193)
        if c == 'Ю':
            q = round_bowl([(original_x[x],y) for x,y in p[:36]], (275,335,635,695))
            h, low, high = 800, 373, 427
        else:
            # Scale the bend depth, not the thickness of the horizontal bars.
            outer = {round(.70*v):round(.70*v) for v in y}
            inner = {round(.70*k):round(.70*(v - 54))+54 if k < 400
                     else 560-(round(.70*(746-v))+54) for k,v in yi.items()}
            q = zones(p[:20], {k:x[v] for k,v in original_x.items() if v in x}, outer)
            q += zones(p[20:36], {k:xi[v] for k,v in original_x.items() if v in xi}, inner)
            h, low, high = 560, 254, 306
        q += [(121,0),(121,h),(181,h),(181,high),(308,high),(308,low),(181,low),(181,0)]
    elif c == 'Ь':
        q = soft_sign(130, 670)
    elif c == 'Ы':
        q = soft_sign(107, 515) + [(612,0),(612,800),(672,800),(672,0)]
    elif c == 'Ъ':
        q = soft_sign(229, 682) + [(116,746),(116,800),(289,800),(289,746)]
    elif c == 'T':
        q = T
    else:
        q = balance_f(F)
    if len(q) != len(p):
        raise ValueError(f'{c}: review Thin master after changing Full Grid topology')
    return [(round(x),round(y)) for x,y in q]
