"""Build full-coverage static Grid faces, leaving all historical binaries intact."""
from collections import defaultdict
from math import ceil, floor, isqrt
from pathlib import Path
from functools import lru_cache

from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from copy import deepcopy
from unicodedata import normalize

from midline_promotion import approved_outlines, marked_outline
from spacing_balance import balanced_outlines
from stroke_balance import equal_m, u_stem

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'
OUT = GRID / 'full-family/fonts'
MASTER = GRID / 'cyrillic/fonts/ConfiniumMono-Cyrillic.ttf'
STYLES = ('Grid', 'Open', 'Dense', 'Hollow')


class Flatten(BasePen):
    """Sample TrueType quadratics for the two-unit display-outline lattice."""
    def __init__(self):
        super().__init__(None)
        self.paths = []

    def _moveTo(self, p): self.paths.append([p])
    def _lineTo(self, p): self.paths[-1].append(p)
    def _qCurveToOne(self, b, c):
        a = self.paths[-1][-1]
        steps = max(2, ceil(max(abs(a[i]-2*b[i]+c[i]) for i in (0,1))**.5))
        for k in range(1, steps+1):
            t = k/steps
            self._lineTo(tuple((1-t)**2*a[i]+2*(1-t)*t*b[i]+t*t*c[i] for i in (0,1)))


def runs(bits):
    while bits:
        start = (bits & -bits).bit_length()-1
        end = start + ((bits >> start) ^ ((bits >> start)+1)).bit_length()-1
        yield start, end
        bits ^= ((1 << (end-start))-1) << start


def simplify(points):
    # Remove lattice stair steps to within 1.5 units (points are half-scale).
    if len(points)<3: return points
    (x,y),(u,v) = points[0],points[-1]
    dx,dy = u-x,v-y
    i=max(range(1,len(points)-1),key=lambda i:abs(dx*(points[i][1]-y)-dy*(points[i][0]-x)))
    if (dx*(points[i][1]-y)-dy*(points[i][0]-x))**2 <= .56*(dx*dx+dy*dy):
        return [points[0],points[-1]]
    return simplify(points[:i+1])[:-1]+simplify(points[i:])


def hollow(g, glyf):
    pen=Flatten(); g.draw(pen,glyf)
    dest=TTGlyphPen(None)
    if not pen.paths: return dest.glyph()
    origin=floor(g.xMin/2)-2
    events=defaultdict(list)
    for pts in pen.paths:
        for (x,y),(u,v) in zip(pts,pts[1:]+pts[:1]):
            for row in range(ceil((min(y,v)-1)/2),ceil((max(y,v)-1)/2)):
                crossing=x+(2*row+1-y)*(u-x)/(v-y)
                events[row].append((ceil((crossing-1)/2)-origin,1 if v>y else -1))
    # Nonzero scan conversion unions crossing strokes before the channel is cut.
    rows={}
    for y,edges in events.items():
        level=bits=last=0
        for x,delta in sorted(edges):
            if level: bits |= ((1<<(x-last))-1)<<last
            level+=delta; last=x
        rows[y]=bits
    radius=14  # 28 font units
    @lru_cache(None)
    def shrink(bits,r):
        return sum(((1<<(b-a-2*r))-1)<<(a+r) for a,b in runs(bits) if b-a>2*r)
    shell={}
    for y,bits in rows.items():
        inside=bits
        for d in range(-radius,radius+1):
            inside &= shrink(rows.get(y+d,0),isqrt(radius**2-d**2))
            if not inside: break
        shell[y]=bits ^ inside
    # Trace horizontal runs and their vertical ends, clockwise around solids.
    edges=defaultdict(list)
    for y,bits in shell.items():
        for a,b in runs(bits & ~shell.get(y-1,0)): edges[b,y].append((a,y))
        for a,b in runs(bits & ~shell.get(y+1,0)): edges[a,y+1].append((b,y+1))
        for a,b in runs(bits):
            edges[a,y].append((a,y+1)); edges[b,y+1].append((b,y))
    while edges:
        start=p=next(iter(edges)); path=[]
        while True:
            path.append(p); q=edges[p].pop()
            if not edges[p]: del edges[p]
            p=q
            if p==start: break
        if len(path)<3: continue
        mid=max(range(len(path)),key=lambda i:(path[i][0]-p[0])**2+(path[i][1]-p[1])**2)
        clean=simplify(path[:mid+1])[:-1]+simplify(path[mid:]+[p])[:-1]
        if len(clean)<3: continue
        points=[(2*(x+origin),2*y) for x,y in clean]
        dest.moveTo(points[0]);
        for point in points[1:]: dest.lineTo(point)
        dest.closePath()
    return dest.glyph()


def tune(g, delta, height):
    # Shift inner bar edges while preserving baseline, waist, x-height, cap,
    # descenders and above marks. Linear interpolation also moves curve controls.
    stops=[(0,0),(140,delta),(height//2-70,-delta/2),(height//2+70,delta/2),(height-140,-delta),(height,0)]
    for i,(x,y) in enumerate(g.coordinates):
        for (a,da),(b,db) in zip(stops,stops[1:]):
            if a<=y<=b:
                g.coordinates[i]=(x,round(y+da+(db-da)*(y-a)/(b-a))); break


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    for style in STYLES:
        path=(GRID/'hollow/ConfiniumMono-GridToken-Hollow.ttf' if style=='Hollow' else GRID/f'fonts/ConfiniumMono-GridToken-{style}.ttf')
        with TTFont(MASTER,recalcTimestamp=False) as f, TTFont(path) as archive:
            promoted=approved_outlines(f)
            promoted.update(balanced_outlines(f))
            base_m = f['glyf']['m']
            m = deepcopy(base_m)
            m.coordinates[:] = equal_m(m.coordinates, u_stem(f['glyf']['U'].coordinates))
            promoted['m'] = m
            for cp, name in f.getBestCmap().items():
                text = normalize('NFD', chr(cp))
                if len(text) == 2 and text[0] == 'm':
                    promoted[name] = marked_outline(m, base_m, f['glyf'][name])
            for g in promoted.values():
                g.recalcBounds(f['glyf'])
            archived=set(archive.getGlyphOrder())
            chars={n:chr(cp) for cp,n in f.getBestCmap().items()}
            for n in f.getGlyphOrder():
                g=promoted.get(n, f['glyf'][n])
                if n in archived and n not in promoted: g=archive['glyf'][n]
                elif style=='Hollow': g=hollow(g,f['glyf'])
                elif style!='Grid' and g.numberOfContours>0:
                    tune(g,-4 if style=='Open' else 4,560 if chars.get(n,'').islower() else 800)
                f['glyf'][n]=g
                if g.numberOfContours:
                    g.recalcBounds(f['glyf']); f['hmtx'][n]=(f['hmtx'][n][0],g.xMin)
            family='Confinium Mono Full '+style; ps='ConfiniumMono-Full'+style+'-Bold'
            for rec in f['name'].names:
                text={1:family,3:ps+'-Study',4:family+' Bold',6:ps,10:'Full-repertoire Grid family study: '+style,16:family}.get(rec.nameID)
                if text: rec.string=text.encode(rec.getEncoding())
            f.save(OUT/f'ConfiniumMono-Full{style}.ttf')


if __name__=='__main__': build()
