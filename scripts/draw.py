"""Original Confinium Mono pilot drawings; no imported outlines.

Run explicitly to regenerate UFOs. For manual editing, edit the UFOs and run
build.py without this script. Coordinates are design units, y upwards.
"""
from pathlib import Path
from font_license import apply_ufo_license
from datetime import date
import json
import math
from fontTools.svgLib.path import parse_path
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from ufoLib2 import Font

ROOT = Path(__file__).resolve().parents[1]
FAMILY = "Confinium Mono"
WEIGHTS = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Book", 500: "Medium", 600: "SemiBold", 700: "Bold"}


def polygon(points):
    return "M " + " L ".join(f"{x:g},{y:g}" for x, y in points) + " Z"


def rounded(x, y, w, h, r):
    # Clockwise outer contour, smoothly eased quarter-circle corners.
    k = 0.55228475
    return (f"M {x+r},{y} L {x+w-r},{y} "
            f"C {x+w-r+r*k},{y} {x+w},{y+r-r*k} {x+w},{y+r} "
            f"L {x+w},{y+h-r} C {x+w},{y+h-r+r*k} {x+w-r+r*k},{y+h} {x+w-r},{y+h} "
            f"L {x+r},{y+h} C {x+r-r*k},{y+h} {x},{y+h-r+r*k} {x},{y+h-r} "
            f"L {x},{y+r} C {x},{y+r-r*k} {x+r-r*k},{y} {x+r},{y} Z")


def reverse_path(path):
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.reverseContourPen import ReverseContourPen
    from fontTools.pens.svgPathPen import SVGPathPen
    rec = RecordingPen()
    parse_path(path, rec)
    pen = SVGPathPen(None)
    rec.replay(ReverseContourPen(pen))
    return pen.getCommands()


def bowl(x, y, w, h, r, t):
    return rounded(x, y, w, h, r) + " " + reverse_path(rounded(x+t, y+t, w-2*t, h-2*t, max(18, r-t*.65)))


def polar(cx, cy, radius, angle):
    angle = math.radians(angle)
    return f'{cx + radius * math.cos(angle)},{cy + radius * math.sin(angle)}'


def arc(cx, cy, radius, start, end, pieces=1):
    """Circular cubic approximation with analytic tangent handles.

    Paired radii share centres and angles. Fixed piece counts preserve master
    correspondence; each piece is at most 90 degrees. No freehand handles.
    """
    delta = math.radians((end-start)/pieces)
    assert abs(delta) <= math.pi/2 + 1e-9
    k = 4/3 * math.tan(delta/4)
    commands = []
    for i in range(pieces):
        a = math.radians(start) + i*delta; b = a+delta
        x0 = cx+radius*math.cos(a); y0 = cy+radius*math.sin(a)
        x3 = cx+radius*math.cos(b); y3 = cy+radius*math.sin(b)
        commands.append(f'C {x0-k*radius*math.sin(a)},{y0+k*radius*math.cos(a)} '
                        f'{x3+k*radius*math.sin(b)},{y3-k*radius*math.cos(b)} {x3},{y3}')
    return ' '.join(commands)+' '


def curved_glyphs(t):
    """Concentric bowls and tangent-connected s; cuts slope +0.15."""
    cut = math.degrees(math.atan(.15))
    radius = 168; inner = radius-t
    # Shared outside of c/e, from the top-right wall to the lower terminal.
    outside = (arc(430,340,radius,0,90) + 'L 264,508 '
               + arc(264,340,radius,90,180) + 'L 96,160 '
               + arc(264,160,radius,180,270) + 'L 430,-8 '
               + arc(430,160,radius,270,360+cut,2))
    lower_inside = (f'L {polar(430,160,inner,cut)} '
                    + arc(430,160,inner,360+cut,270,2)
                    + f'L 264,{-8+t} ' + arc(264,160,inner,270,180))
    c = ('M 598,340 '+outside+lower_inside+f'L {96+t},340 '
         + arc(264,340,inner,180,90)+f'L 430,{508-t} '
         + arc(430,340,inner,90,0)+'Z')
    e = (f'M {96+t},230 L 598,230 L 598,340 '+outside+lower_inside+'Z ')
    eye = (f'M {96+t},{230+t} L {598-t},{230+t} L {598-t},340 '
           + arc(430,340,inner,0,90)+f'L 264,{508-t} '
           + arc(264,340,inner,90,180)+'Z')
    e += reverse_path(eye)

    # s: common internal tangent of two equal centreline circles. Both sides
    # of the diagonal use the same tangent; no kink or mass change at a join.
    # Keep the tangent angle fixed across masters. Solve the radius/centre
    # separation instead, so all points are affine in t and interpolation
    # preserves exact tangency (varying the angle caused midpoint kinks).
    theta = 255
    nx, ny = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    r = (157*nx - 516*ny + t)/(2*(1-ny)); ri = r-t
    upper_y, lower_y = 508-r, -8+r
    s = (f'M {polar(430,340,radius,45)} '+arc(430,340,radius,45,90)
         + 'L 270,508 '+arc(270,upper_y,r,90,theta,2)
         + f'L {polar(427,lower_y,ri,theta-180)} '+arc(427,lower_y,ri,theta-180,-90,2)
         + f'L 300,{-8+t} '+arc(300,lower_y,ri,270,180+cut)
         + f'L {polar(300,lower_y,r,180+cut)} '+arc(300,lower_y,r,180+cut,270)
         + 'L 427,-8 '+arc(427,lower_y,r,270,theta+180,2)
         + f'L {polar(270,upper_y,ri,theta)} '+arc(270,upper_y,ri,theta,90,2)
         + f'L 430,{508-t} '+arc(430,340,inner,90,45)+'Z')

    # g: true concentric bowl corners, with a same-winding overlapping hook.
    # The hook touches only the right wall, never the counter. Its two radii
    # also share a centre, preserving stroke thickness around the return.
    g = rounded(102,-8,482,516,139)+' '+reverse_path(rounded(102+t,-8+t,482-2*t,516-2*t,139-t))
    hook = ('M 241,-222 L 451,-222 '+arc(451,-89,133,270,360)
            + f'L 584,131 L {584-t},131 L {584-t},-89 '
            + arc(451,-89,133-t,0,-90)+f'L 241,{-222+t} Z')
    return {'c':c, 'e':e, 's':s, 'g':g+' '+hook}


def drawings(t):
    paths = {}
    paths['H'] = polygon([(92,0),(92,700),(92+t,700),(92+t,365+t/2),(605-t,365+t/2),(605-t,700),(605,700),(605,0),(605-t,0),(605-t,365-t/2),(92+t,365-t/2),(92+t,0)])
    paths['O'] = bowl(83,-8,531,716,160,t)
    # Short, eased diagonal facets belong to both outer and inner boundaries.
    def zero(x,y,w,h,r,f):
        return (f'M {x+r},{y} L {x+w-r},{y} Q {x+w},{y} {x+w},{y+r} '
                f'L {x+w},{y+h-f-12} Q {x+w},{y+h-f} {x+w-9},{y+h-f+9} '
                f'L {x+w-f+9},{y+h-9} Q {x+w-f},{y+h} {x+w-f-12},{y+h} '
                f'L {x+r},{y+h} Q {x},{y+h} {x},{y+h-r} '
                f'L {x},{y+f+12} Q {x},{y+f} {x+9},{y+f-9} '
                f'L {x+f-9},{y+9} Q {x+f},{y} {x+f+12},{y} Z')
    paths['zero'] = zero(139,-8,419,716,111,95) + ' ' + reverse_path(zero(139+t,-8+t,419-2*t,716-2*t,max(24,111-t*.6),max(40,95-t*.35)))
    paths['Q'] = paths['O'] + ' ' + reverse_path(polygon([(510,52),(510+t*.76,52+t*.22),(576+t*.35,-115),(647,-115),(647,-115-t),(551,-115-t)]))
    # Two arms, one continuous straight right-arm descender, level end cut.
    paths['y'] = polygon([(76,500),(76+t*1.48,500),(421.125-t*.54,185+t*1.34),(548-t*1.08,500),(548,500),(258,-220),(258-t*1.08,-220),(421.125-t*1.08,185)])
    paths.update(curved_glyphs(t))
    paths['.notdef'] = bowl(130,0,437,700,12,min(t,50))
    return paths


def main():
    source = ROOT/'sources'; source.mkdir(exist_ok=True)
    ds = DesignSpaceDocument()
    axis = AxisDescriptor(); axis.name='Weight'; axis.tag='wght'; axis.minimum=100; axis.default=400; axis.maximum=700
    ds.addAxis(axis)
    master_specs = [(100,24),(400,66),(700,108)]
    snapshots=[]
    codepoints = {ord(c): c for c in 'HOQgyces'} | {48:'zero',32:'space',160:'nbspace'}
    for weight,t in master_specs:
        style=WEIGHTS[weight]; f=Font(); info=f.info
        info.familyName=FAMILY; info.styleName=style; info.unitsPerEm=1000
        info.ascender=885; info.descender=-242; info.capHeight=700; info.xHeight=500
        info.versionMajor=0; info.versionMinor=1
        info.openTypeOS2WeightClass=weight; info.openTypeOS2WidthClass=5
        info.openTypeOS2TypoAscender=885; info.openTypeOS2TypoDescender=-242; info.openTypeOS2TypoLineGap=0
        info.openTypeHheaAscender=885; info.openTypeHheaDescender=-242; info.openTypeHheaLineGap=0
        info.openTypeOS2WinAscent=885; info.openTypeOS2WinDescent=242
        info.openTypeOS2Selection=[7]; info.postscriptIsFixedPitch=True
        info.openTypeNameDescription='Original nine-glyph review pilot. Not a complete family.'
        paths=drawings(t)
        for name in ['.notdef','space','nbspace','H','O','zero','Q','g','y','c','e','s']:
            glyph=f.newGlyph(name); glyph.width=697
            glyph.unicodes=[cp for cp,n in codepoints.items() if n==name]
            if name in paths: parse_path(paths[name],glyph.getPen())
        f.glyphOrder=list(f.keys())
        apply_ufo_license(info)
        filename=f'ConfiniumMono-{style}.ufo'; f.save(source/filename,overwrite=True)
        desc=SourceDescriptor(); desc.path=str(source/filename); desc.name=style; desc.familyName=FAMILY; desc.styleName=style; desc.location={'Weight':weight}
        if weight==400: desc.copyInfo=True; desc.copyLib=True; desc.copyFeatures=True
        ds.addSource(desc)
        row=[]
        for i,name in enumerate(['H','O','zero','Q','g','y','c','e','s']):
            row.append(f'<g transform="translate({i*697},0)"><path d="{paths[name]}"/></g>')
        snapshots.append(f'<g transform="translate(0,{885+(weight-100)/300*1127}) scale(1,-1)">'+''.join(row)+'</g>')
    for weight,style in WEIGHTS.items():
        inst=InstanceDescriptor(); inst.familyName=FAMILY; inst.styleName=style; inst.name=f'{FAMILY} {style}'
        inst.location={'Weight':weight}; ds.addInstance(inst)
    ds.write(source/'ConfiniumMono.designspace')
    sketches=ROOT/'sketches'; sketches.mkdir(exist_ok=True)
    (sketches/f'{date.today()}-nine-glyphs.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -50 6373 3481"><title>Confinium Mono — Thin, Book, Bold original outline sketch</title><rect x="-50" y="-50" width="6373" height="3481" fill="#faf8f2"/><g fill="#172426">'+''.join(snapshots)+'</g></svg>')
    (source/'coverage.json').write_text(json.dumps({'family':FAMILY,'stage':'nine-glyph pilot','glyphs':[{'name':name,'codepoints':[f'U+{cp:04X}' for cp,n in codepoints.items() if n==name],'spacing':'single-cell','advance':697} for name in ['.notdef','space','nbspace','H','O','zero','Q','g','y','c','e','s']]},indent=2)+'\n')
    print('Wrote three original UFO masters, designspace, coverage manifest and dated sketch.')

if __name__=='__main__': main()
