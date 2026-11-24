"""Build an 800-unit variable face with Full Grid as its exact Bold master."""
from copy import deepcopy
from math import hypot
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.varLib.instancer import instantiateVariableFont

from k_steeper_study import REFERENCE as FORK_REFERENCE, apply_candidate as steeper_forks
from midline_promotion import REFERENCE_GRID, accented
from spacing_balance import I_CONTROL
from stroke_balance import equal_m, u_stem
from structural_capitals_study import REFERENCE as CAPITALS_REFERENCE, base_for as structural_base_for, thin_alternatives
from variable_diagonals import thin_master
from variable_extended import thin_extended
from variable_lowercase import thin_lowercase, thin_v
from unicodedata import normalize

SHARED_FIXES = {"uni0422": "T", "uni0425": "X", "uni0440": "p", "uni0430": "a", "uni0445": "x", "uni0443": "y", "uni0456": "i", "uni0131": "i", "uni0435": "e", "uni0421": "C", "uni041E": "O"}

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'fonts/ConfiniumMono[wght].ttf'
GRID = ROOT / 'studies/grid-token-bold/full-family/fonts/ConfiniumMono-FullGrid.ttf'
OUT = ROOT / 'studies/variable-repertoire'
BINARY = OUT / 'fonts/ConfiniumMono-VariableRepertoire[wght].ttf'


def inward_edges(points, ends):
    """Ink is on the right of directed TrueType contours. Limit each inset by
    the local stroke width so dots and fine marks survive at the light end."""
    edges = []
    contours = []
    first = 0
    for end in ends:
        for i in range(first, end+1):
            a, b = points[i], points[first if i == end else i+1]
            dx, dy = b[0]-a[0], b[1]-a[1]
            length = hypot(dx,dy) or 1
            contours.append(first)
            edges.append((a,b,dy/length,-dx/length))
        first=end+1
    offsets=[]
    for i,(a,b,nx,ny) in enumerate(edges):
        mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
        reach=130
        for j,(c,d,_,_) in enumerate(edges):
            dx,dy=d[0]-c[0],d[1]-c[1]
            if contours[i] != contours[j] and dx*dx+dy*dy:
                for px,py in (a,b):
                    k=max(0,min(1,((px-c[0])*dx+(py-c[1])*dy)/(dx*dx+dy*dy)))
                    reach=min(reach,hypot(px-c[0]-k*dx,py-c[1]-k*dy))
            det=nx*dy-ny*dx
            if abs(det)<1e-7: continue
            x,y=c[0]-mx,c[1]-my
            t,u=(x*dy-y*dx)/det,(x*ny-y*nx)/det
            if t>1e-5 and 0<=u<=1: reach=min(reach,t)
        offsets.append((nx,ny,min(50,reach*.38)))
    first=0; shifts=[]
    for end in ends:
        for i in range(first,end+1):
            ax,ay,r=offsets[end if i==first else i-1]; bx,by,s=offsets[i]
            # A bounded miter avoids spikes at acute diagonal joins.
            dot=ax*bx+ay*by; det=ax*by-ay*bx
            if abs(det)>.01:
                x,y=(r*by-s*ay)/det,(s*ax-r*bx)/det
            else: x,y=(ax*r+bx*s)/2,(ay*r+by*s)/2
            limit=min(1,1.45*min(r,s)/max(.001,hypot(x,y)))
            shifts.append((x*limit,y*limit))
        first=end+1
    return shifts


def masters(g, name=None, w_bold=None):
    bold=list(g.coordinates)
    light=thin_v(bold, w_bold) if name == 'v' else thin_master(name,bold)
    shared = SHARED_FIXES.get(name, name)
    if light is None:
        light=thin_lowercase(shared,bold)
    if light is None and shared is not None:
        char = chr(int(shared[3:], 16)) if shared.startswith("uni") else shared
        light=thin_extended(char,bold)
    if light is None:
        shifts=inward_edges(bold,g.endPtsOfContours)
        light=[(round(x+dx),round(y+dy)) for (x,y),(dx,dy) in zip(bold,shifts)]
        # Restore vertical alignment zones after thinning (including descenders).
        lo,hi=min(y for x,y in bold),max(y for x,y in bold)
        low,high=min(y for x,y in light),max(y for x,y in light)
        if high>low: light=[(x,round(lo+(y-low)*(hi-lo)/(high-low))) for x,y in light]
    book=[(round(.52*x+.48*u),round(.52*y+.48*v)) for (x,y),(u,v) in zip(light,bold)]
    return light,book,bold


def accent_prefix(base, name, glyph):
    dotless = base in ('i', 'j') and name != 'uni012F'
    count = glyph.endPtsOfContours[0] + 1 if dotless else len(glyph.coordinates)
    scale = .9 if name in ('uni1E03', 'uni0125') else 1
    return count, scale


def scaled_prefix(points, scale):
    return [(x, round(y * scale)) for x, y in points]


def build():
    with (TTFont(GRID,recalcTimestamp=False) as f, TTFont(PILOT) as pilot,
          TTFont(REFERENCE_GRID) as reference, TTFont(I_CONTROL) as spacing_control,
          TTFont(CAPITALS_REFERENCE) as capitals_reference, TTFont(FORK_REFERENCE) as fork_reference):
        # Reuse axis definitions and their localized names, not the pilot outlines.
        for tag in ('fvar','STAT','name'):
            f[tag]=deepcopy(pilot[tag])
        f['gvar']=newTable('gvar'); f['gvar'].variations={}
        glyf=f['glyf']; variations=f['gvar'].variations
        w_bold = list(glyf['w'].coordinates)
        base_for = accented(f)
        cmap = f.getBestCmap()
        for cp, name in cmap.items():
            text = normalize("NFD", chr(cp))
            if len(text) < 2 or ord(text[0]) not in cmap:
                continue
            base = cmap[ord(text[0])]
            # Derive only if the original Bold actually contains that base.
            # NFD alone is not enough: some glyphs are independently drawn.
            ref_base, ref_marked = reference['glyf'][base], reference['glyf'][name]
            count, scale = accent_prefix(base, name, ref_base)
            if (len(ref_marked.coordinates) > count
                    and count - 1 in ref_marked.endPtsOfContours
                    and list(ref_marked.coordinates[:count]) == scaled_prefix(ref_base.coordinates[:count], scale)):
                base_for[name] = base
        base_for["uni045E"] = "y"
        base_for["uni0451"] = "e"
        structural_thin = thin_alternatives(capitals_reference)
        structural_bold = {name: list(glyf[name].coordinates) for name in structural_thin}
        structural_bases = {name: structural_base_for(chr(cp)) for cp, name in cmap.items()
                            if structural_base_for(chr(cp)) in structural_thin}
        forks = [steeper_forks(instantiateVariableFont(fork_reference, {'wght': weight}), weight,
                               replace=False) for weight in (100, 400, 700)]
        base_masters = {base: masters(glyf[base], base, w_bold)
                        for base in set(base_for.values()) - {'m'} - structural_thin.keys() - forks[0].keys()}
        m_masters = [equal_m(m, u_stem(u)) for m, u in zip(
            masters(spacing_control['glyf']['m'], 'm'), masters(glyf['U'], 'U'))]
        if m_masters[-1] != list(glyf['m'].coordinates):
            raise ValueError('Promoted Bold m differs from Full Grid')
        base_masters['m'] = m_masters
        for n in f.getGlyphOrder():
            g=glyf[n]; width=f['hmtx'][n][0]
            if not g.numberOfContours:
                variations[n]=[]
                continue
            if n in forks[0]:
                light,book,bold = [list(fork[n].coordinates) for fork in forks]
                if bold != list(g.coordinates):
                    raise ValueError(f'Promoted Bold fork differs from Full Grid: {n}')
            elif n in structural_bases:
                base = structural_bases[n]
                control = capitals_reference['glyf']
                old_count = len(control[base].coordinates)
                count = len(structural_thin[base])
                bold = list(g.coordinates)
                light = structural_thin[base] + masters(control[n])[0][old_count:]
                book = [(round(.52*x+.48*u), round(.52*y+.48*v))
                        for (x,y),(u,v) in zip(light, bold)]
                if len(light) != len(bold) or bold[:count] != structural_bold[base]:
                    raise ValueError(f'Unexpected structural capital topology: {n}')
            elif n in base_for:
                base = base_for[n]
                ref_base, ref_marked = reference['glyf'][base], reference['glyf'][n]
                count, scale = accent_prefix(base, n, ref_base)
                expected = scaled_prefix(ref_base.coordinates[:count], scale)
                if list(ref_marked.coordinates[:count]) != expected:
                    raise ValueError(f'Unexpected accent base: {n}')
                marks = masters(ref_marked)
                cut = count if count < len(ref_base.coordinates) else None
                light,book,bold = [scaled_prefix(points[:cut], scale) + mark[count:]
                                   for points, mark in zip(base_masters[base], marks)]
                if bold != list(g.coordinates):
                    raise ValueError(f'Promoted Bold composition differs from Full Grid: {n}')
            elif n == 'm':
                light,book,bold=m_masters
            else:
                light,book,bold=masters(g,n,w_bold)
            g.coordinates=GlyphCoordinates(book); g.recalcBounds(glyf)
            f['hmtx'][n]=(width,g.xMin)
            variations[n]=[TupleVariation({'wght':support},[(x-u,y-v) for (x,y),(u,v) in zip(coords,book)]+[(0,0)]*4)
                           for coords,support in [(light,(-1.,-1.,0.)),(bold,(0.,1.,1.))]]
        names = f['name']
        unicode_names = {(r.nameID, r.toUnicode()) for r in names.names if r.isUnicode()}
        if any((r.nameID, r.toUnicode()) not in unicode_names
               for r in names.names if r.platformID == 1):
            raise ValueError('Cannot discard a unique Macintosh name')
        names.names = [r for r in names.names if r.platformID != 1]
        family, ps = 'Confinium Mono VF', 'ConfiniumMonoVF'
        values = {1: family, 3: ps+'-Regular', 4: family+' Regular',
                  5: f"Version {f['head'].fontRevision:.3f}", 6: ps+'-Regular',
                  10: 'Variable study of the current Full Grid glyph library.', 16: family}
        for rec in names.names:
            value = values.get(rec.nameID)
            if rec.toUnicode() == 'Book':
                value = 'Regular'
            if value:
                rec.string = value.encode(rec.getEncoding())
        for instance in f['fvar'].instances:
            style = names.getDebugName(instance.subfamilyNameID)
            instance.postscriptNameID = names.addName(ps+'-'+style, platforms=((3, 1, 0x409),))
        os2=f['OS/2']; os2.usWeightClass=400
        f['head'].macStyle=pilot['head'].macStyle; os2.fsSelection=pilot['OS/2'].fsSelection
        BINARY.parent.mkdir(parents=True,exist_ok=True); f.save(BINARY)


if __name__=='__main__': build()
