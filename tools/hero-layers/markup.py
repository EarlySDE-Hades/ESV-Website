"""Embed offline manifest positions; no JSON request is needed by the website."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = '        <!-- Generated hero layers: tools/hero-layers/markup.py -->'
END = '        <!-- End generated hero layers -->'


def render():
    manifest = json.loads((ROOT/'assets/hero/manifest.json').read_text())
    lines = [START, '        <div class="collage" data-collage role="img"',
             '             aria-label="Collage of India\'s builders: a scientist at a microscope, two women carrying produce, a student with a folder, a historic domed monument, a modern building and a flowering plant, under a rising yellow sun.">']
    for layer in manifest['layers']:
        name,x,y,w,h,z = [layer[k] for k in ['id','x','y','w','h','z']]
        style = f'left:{x/2114*100:.8f}%;top:{y/846*100:.8f}%;width:{w/2114*100:.8f}%;height:{h/846*100:.8f}%;z-index:{z}'
        lines.append(f'          <span class="collage__layer" data-layer="{name}" style="{style}" aria-hidden="true">')
        if 'svg' in layer:
            g=layer['svg']
            lines.append(f'            <svg class="collage__piece" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}" aria-hidden="true" focusable="false">')
            if name == 'sun':
                lines.append('              <defs><linearGradient id="collage-sun" x1="0" y1="0" x2="0" y2="1">')
                for t,c in g['stops']:
                    color='#'+''.join(f'{v:02x}' for v in c)
                    lines.append(f'                <stop offset="{t*100:g}%" stop-color="{color}" />')
                lines.append('              </linearGradient></defs>')
                lines.append(f'              <circle cx="{g["cx"]}" cy="{g["cy"]}" r="{g["r"]}" fill="url(#collage-sun)" />')
            else:
                segments=[]
                for angle in range(0,360,45):
                    a=math.radians(angle)
                    start=g['r']*.36
                    end=g['r'] if angle%90==0 else g['r']*.66
                    segments.append(f'M{g["cx"]+math.cos(a)*start:.3f} {g["cy"]+math.sin(a)*start:.3f}L{g["cx"]+math.cos(a)*end:.3f} {g["cy"]+math.sin(a)*end:.3f}')
                lines.append(f'              <path d="{" ".join(segments)}" fill="none" stroke="{g["color"]}" stroke-width="2" stroke-linecap="round" />')
            lines.append('            </svg>')
        else:
            # Descriptors represent the common source canvas, so sizes represents
            # the canvas too. CSS and intrinsic dimensions preserve each crop.
            lines.append(f'            <img class="collage__piece" src="assets/hero/{name}.webp"')
            lines.append(f'                 srcset="assets/hero/{name}@1x.webp 1057w, assets/hero/{name}.webp 2114w"')
            lines.append(f'                 sizes="(max-width: 720px) 100vw, (max-width: 1224px) calc(100vw - 64px), 1160px"')
            lines.append(f'                 width="{w}" height="{h}" decoding="async" alt="" draggable="false" />')
        lines.append('          </span>')
    lines.extend(['        </div>',END])
    return '\n'.join(lines)


def sync():
    path=ROOT/'index.html'
    html=path.read_text(encoding='utf-8')
    if START in html:
        a=html.index(START)
        b=html.index(END,a)+len(END)
    else:
        raise ValueError('Generated hero layer markers are missing from index.html')
    path.write_text(html[:a]+render()+html[b:],encoding='utf-8')


if __name__ == '__main__':
    sync()
