"""Compile the editable UFO masters; does not regenerate drawings."""
from pathlib import Path
import subprocess
import sys
import os

ROOT = Path(__file__).resolve().parents[1]

def main():
    os.environ.setdefault('SOURCE_DATE_EPOCH','1795132800')  # 2026-11-20 UTC
    (ROOT/'fonts').mkdir(exist_ok=True)
    common=[sys.executable,'-m','fontmake','-m',str(ROOT/'sources/ConfiniumMono.designspace')]
    subprocess.run(common+['-o','variable','--output-path',str(ROOT/'fonts/ConfiniumMono[wght].ttf')],check=True,cwd=ROOT)
    # Derive statics from the same variable outlines to guarantee matching designs.
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    from draw import WEIGHTS
    from fontTools.otlLib.builder import buildStatTable
    variable=TTFont(ROOT/'fonts/ConfiniumMono[wght].ttf',recalcTimestamp=False)
    buildStatTable(variable,[{'tag':'wght','name':'Weight','values':[
        {'value':weight,'name':style,**({'flags':2} if weight==400 else {})}
        for weight,style in WEIGHTS.items()]}])
    variable.save(ROOT/'fonts/ConfiniumMono[wght].ttf')
    for weight,style in WEIGHTS.items():
        font=TTFont(ROOT/'fonts/ConfiniumMono[wght].ttf',recalcTimestamp=False)
        font=instantiateVariableFont(font,{'wght':weight},inplace=True,updateFontNames=True)
        font['OS/2'].usWeightClass=weight
        font.save(ROOT/f'fonts/ConfiniumMono-{style}.ttf')
    print('Built variable font and seven static review fonts.')

if __name__=='__main__': main()
