"""Build an 800-unit variable face with Full Grid as its exact Bold master."""
from copy import deepcopy
from math import hypot
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

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


def masters(g):
    bold=list(g.coordinates)
    shifts=inward_edges(bold,g.endPtsOfContours)
    light=[(round(x+dx),round(y+dy)) for (x,y),(dx,dy) in zip(bold,shifts)]
    # Restore vertical alignment zones after thinning (including descenders).
    lo,hi=min(y for x,y in bold),max(y for x,y in bold)
    low,high=min(y for x,y in light),max(y for x,y in light)
    if high>low: light=[(x,round(lo+(y-low)*(hi-lo)/(high-low))) for x,y in light]
    book=[(round(.52*x+.48*u),round(.52*y+.48*v)) for (x,y),(u,v) in zip(light,bold)]
    return light,book,bold


def build():
    with TTFont(GRID,recalcTimestamp=False) as f, TTFont(PILOT) as pilot:
        # Reuse axis definitions and their localized names, not the pilot outlines.
        for tag in ('fvar','STAT','name'):
            f[tag]=deepcopy(pilot[tag])
        f['gvar']=newTable('gvar'); f['gvar'].variations={}
        glyf=f['glyf']; variations=f['gvar'].variations
        for n in f.getGlyphOrder():
            g=glyf[n]; width=f['hmtx'][n][0]
            if not g.numberOfContours:
                variations[n]=[]
                continue
            light,book,bold=masters(g)
            g.coordinates=GlyphCoordinates(book); g.recalcBounds(glyf)
            f['hmtx'][n]=(width,g.xMin)
            variations[n]=[TupleVariation({'wght':support},[(x-u,y-v) for (x,y),(u,v) in zip(coords,book)]+[(0,0)]*4)
                           for coords,support in [(light,(-1.,-1.,0.)),(bold,(0.,1.,1.))]]
        for rec in f['name'].names:
            text={1:'Confinium Mono Variable Repertoire',3:'ConfiniumMono-VariableRepertoire-Book',
                  4:'Confinium Mono Variable Repertoire Book',6:'ConfiniumMono-VariableRepertoire-Book',
                  10:'Variable study of the current Full Grid glyph library.',16:'Confinium Mono Variable Repertoire'}.get(rec.nameID)
            if text: rec.string=text.encode(rec.getEncoding())
        os2=f['OS/2']; os2.usWeightClass=400
        f['head'].macStyle=pilot['head'].macStyle; os2.fsSelection=pilot['OS/2'].fsSelection
        BINARY.parent.mkdir(parents=True,exist_ok=True); f.save(BINARY)


if __name__=='__main__': build()
