"""Offline, deterministic extraction. No model downloads or generated people."""
from pathlib import Path
import json
import hashlib
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = ROOT / 'assets/hero'
OUT = HERE / 'out'
CONFIG = json.loads((HERE / 'masks.json').read_text())
SOURCE = ROOT / 'Brand Assets/New v2.png'
src = np.array(Image.open(SOURCE).convert('RGB'))
H, W = src.shape[:2]
assert [W, H] == CONFIG['canvas'], 'Update source-coordinate masks for a new canvas size.'
BG = np.array([244, 244, 244], dtype=np.float32)
DEST.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
cv2.setRNGSeed(42)
cv2.setNumThreads(1)
ids = ['dome', 'building', 'plant', 'women', 'scientist', 'student']


def polygon(points):
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [np.array(points, np.int32)], 255)
    return mask


def refine(name):
    """GraphCut only in a narrow hand-traced band; interior source pixels stay intact."""
    mask = polygon(CONFIG['polygons'][name])
    for hole in CONFIG.get('holes', {}).get(name, []):
        mask[polygon(hole) > 0] = 0
    if name in ('dome', 'building'):
        return mask > 0
    if name == 'plant':
        hsv = cv2.cvtColor(src, cv2.COLOR_RGB2HSV)
        outer = cv2.dilate(mask, np.ones((13, 13), np.uint8)) > 0
        colored = outer & (hsv[:,:,0] >= 14) & (hsv[:,:,0] <= 95) & (hsv[:,:,1] > 85)
        closed = cv2.morphologyEx(colored.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(mask)
        cv2.drawContours(filled, [c for c in contours if cv2.contourArea(c)>5], -1, 255, cv2.FILLED)
        for points in CONFIG.get('plant_pale_regions', []):
            filled |= polygon(points)
        return (filled > 0) & outer
    band = 25 if name == 'women' else 9
    inner = cv2.erode(mask, np.ones((band, band), np.uint8))
    outer = cv2.dilate(mask, np.ones((13, 13), np.uint8))
    labels = np.where(mask > 0, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
    labels[outer == 0] = cv2.GC_BGD
    labels[inner > 0] = cv2.GC_FGD
    labels[np.max(np.abs(src.astype(float) - BG), axis=2) < 1] = cv2.GC_BGD
    cv2.grabCut(src, labels, None, np.zeros((1, 65)), np.zeros((1, 65)), 4, cv2.GC_INIT_WITH_MASK)
    result = (labels == cv2.GC_FGD) | (labels == cv2.GC_PR_FGD)
    result[CONFIG['baseline']:] = False
    return result


masks = {name: refine(name) for name in ids}
foreground = np.max(np.abs(src.astype(float) - BG), axis=2) > 0
yy, xx = np.mgrid[:H, :W]
sun = CONFIG['sun']
sun_area = (xx - sun['cx']) ** 2 + (yy - sun['cy']) ** 2 < (sun['r'] + 2) ** 2
colors = src.astype(np.int16)
front = masks['women'] | masks['scientist'] | masks['plant'] | masks['student']
yellow = (colors[:,:,0] >= 244) & (colors[:,:,1] >= 160) & (colors[:,:,1] <= 215) & (colors[:,:,2] < 90)
sun_visible = sun_area & (yellow | (~front & (colors[:,:,0] >= 244) & (colors[:,:,0] > colors[:,:,1]) & (colors[:,:,1] > colors[:,:,2] + 2)))
star_area = np.zeros((H, W), bool)
for cx, cy, r in CONFIG['sparkles']:
    star_area |= (abs(xx - cx) <= r + 3) & (abs(yy - cy) <= r + 3)

# One source-pixel owner. Never redraw, retouch or resample a person at 2x.
owner = np.zeros((H, W), np.uint8)
for i, name in enumerate(ids, 1):
    owner[masks[name] & foreground] = i
owner[sun_visible | star_area | ~foreground] = 0
# Capture tiny silhouette wisps outside the initial hand trace, including hair and cable.
unclaimed = foreground & ~sun_visible & ~star_area & (owner == 0)
distances = np.stack([cv2.distanceTransform((~masks[n]).astype(np.uint8), cv2.DIST_L2, 3) for n in ids])
nearest = distances.argmin(axis=0) + 1
owner[unclaimed] = nearest[unclaimed]
# Antialiased hand/basin edges inside the sun belong to the people, not the
# monument. Keep those wisps from appearing before the women are placed.
owner[(owner == 1) & sun_area] = 4
hsv = cv2.cvtColor(src, cv2.COLOR_RGB2HSV)
plant_wisps = ((xx > 1100) & (xx < 1485) & (yy > 285) & (yy < 827)
               & (hsv[:,:,0] >= 34) & (hsv[:,:,0] <= 85) & (hsv[:,:,1] > 30))
owner[(owner == 1) & plant_wisps] = 3
foot_flowers = ((xx > 805) & (xx < 885) & (yy > 750)
                & (hsv[:,:,0] >= 10) & (hsv[:,:,0] <= 60) & (hsv[:,:,1] > 85))
owner[(owner == 1) & foot_flowers] = 4
for i, name in enumerate(ids, 1):
    Image.fromarray((owner == i).astype(np.uint8) * 255).save(OUT / f'{name}-mask.png')


def architecture(name, i):
    """Fill occlusion with repeated source masonry, then Telea only at patch seams.

    Architecture is periodic. Same-row donor strips preserve courses, cornices and
    windows instead of smearing a 300px hole with diffusion alone. Source-visible
    pixels are restored verbatim after filling; synthesized pixels stay hidden at rest.
    """
    visible = owner == i
    silhouette = masks[name] & foreground & ~sun_visible & ~star_area
    silhouette[CONFIG['baseline']:] = False
    # The original sun overlaps the monument's left silhouette: preserve that contour.
    if name == 'dome':
        silhouette[sun_area & (yy < 530)] = False
    silhouette |= visible
    hidden = silhouette & ~visible
    # Inpaint a cropped architectural canvas with *all* other objects excluded.
    # Otherwise donors outside its silhouette can accidentally repeat a person.
    ys, xs = np.where(silhouette)
    x0,x1,y0,y1 = xs.min(),xs.max()+1,ys.min(),ys.max()+1
    base = src.copy()
    patch = src[y0:y1,x0:x1].copy()
    unknown = (~visible[y0:y1,x0:x1]).astype(np.uint8)*255
    patch[unknown > 0] = [145,145,145]
    base[y0:y1,x0:x1] = cv2.inpaint(patch, unknown, 5, cv2.INPAINT_TELEA)
    # Fixed clean donor bands keep vertical columns straight and avoid broad
    # diffusion smears. Narrow missing courses borrow another photographed course.
    if name == 'dome':
        bands = [(0,350,1085,1160,0),(350,430,1110,1170,0),
                 (430,510,1120,1195,0),(510,570,1100,1170,65),
                 (570,640,1100,1180,0),(640,710,1120,1300,70),
                 (710,H,1118,1302,0)]
        for low, high, left, right, dy in bands:
            use = hidden & (yy >= low) & (yy < high)
            sample_x = left + (xx - 600) % (right-left)
            sample_y = np.clip(yy + dy, 235, H-1)
            base[use] = src[sample_y[use],sample_x[use]]
    else:
        # Repeat the unobstructed front window bay behind the student. Mirroring
        # the receding right facade would reverse its perspective at the join.
        sample_x = 1638 + (xx - 1551) % 78
        sample_y = 475 + (yy - 475) % 120
        base[hidden] = src[sample_y[hidden], sample_x[hidden]]
    # Soften only a one-pixel join, never a visible source surface.
    seam = cv2.morphologyEx(hidden.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    smoothed = cv2.inpaint(base, seam * 255, 2, cv2.INPAINT_TELEA)
    base[hidden & (seam > 0)] = smoothed[hidden & (seam > 0)]
    base[visible] = src[visible]
    return base, silhouette


def cutout(rgb, mask):
    """Recover subpixel alpha against the known page matte, at most one pixel wide."""
    rgba = np.dstack([rgb, mask.astype(np.uint8) * 255])
    # Only outer edges touching the original page matte. Interior cut lines keep
    # all original RGB values; their underpainting is on the architectural layer.
    background = ~foreground
    edge = mask & (cv2.dilate(background.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    interior = cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    _, labels = cv2.distanceTransformWithLabels((~interior).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    palette = np.zeros((labels.max() + 1, 3), np.float32)
    palette[labels[interior]] = rgb[interior]
    estimate = palette[labels[edge]] - BG
    observed = rgb[edge].astype(float) - BG
    alpha = np.clip((observed * estimate).sum(axis=1) / np.maximum((estimate ** 2).sum(axis=1), 1), 0.03, 1)
    rgba[edge, :3] = np.clip(BG + observed / alpha[:, None], 0, 255).round().astype(np.uint8)
    rgba[edge, 3] = (alpha * 255).round().astype(np.uint8)
    rgba[rgba[:,:,3] == 0, :3] = 0
    return Image.fromarray(rgba)


def vector_images():
    # Match the source's understated yellow gradient; actual grain is photographic.
    cx, cy, r = sun['cx'], sun['cy'], sun['r']
    rgba = np.zeros((H, W, 4), np.uint8)
    stops = []
    for t in np.linspace(0, 1, 9):
        y = round(cy - r + 2 * r * t)
        band = sun_visible & (abs(yy - y) < 10)
        color = np.median(src[band], axis=0) if band.any() else (stops[-1][1] if stops else [254,185,45])
        stops.append((float(t), np.array(color).round().astype(int).tolist()))
    for c in range(3):
        rgba[:, :, c] = np.interp(np.clip((yy - cy + r) / (2 * r), 0, 1), [v[0] for v in stops], [v[1][c] for v in stops]).round().astype(np.uint8)
    # Supersampled coverage used both for the audit and the SVG circle geometry.
    scale = 4
    coverage = Image.new('L', (W * scale, H * scale))
    ImageDraw.Draw(coverage).ellipse(((cx-r)*scale, (cy-r)*scale, (cx+r)*scale-1, (cy+r)*scale-1), fill=255)
    rgba[:, :, 3] = np.array(coverage.resize((W, H), Image.Resampling.LANCZOS))
    yield 'sun', Image.fromarray(rgba), {'cx': cx, 'cy': cy, 'r': r, 'stops': stops}
    for j, (cx, cy, r) in enumerate(CONFIG['sparkles'], 1):
        img = Image.new('RGBA', (W * scale, H * scale))
        draw = ImageDraw.Draw(img)
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            end = r if angle % 90 == 0 else r * .66
            start = r * .36
            draw.line(((cx + math.cos(a)*start)*scale, (cy + math.sin(a)*start)*scale,
                       (cx + math.cos(a)*end)*scale, (cy + math.sin(a)*end)*scale), fill=(161,161,161,255), width=round(2*scale))
        yield f'sparkle-{j}', img.resize((W,H), Image.Resampling.LANCZOS), {'cx':cx,'cy':cy,'r':r,'color':'#a1a1a1'}


layers = {}
manifest = {'canvas': {'w': W, 'h': H}, 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'layers': []}
for name, im, geometry in vector_images():
    layers[name] = im
    x, y, x1, y1 = im.getbbox()
    manifest['layers'].append({'id':name,'z':1 if name == 'sun' else 8,'x':x-4,'y':y-4,'w':x1-x+8,'h':y1-y+8,'svg':geometry})

weights = {'desktop':0,'mobile':0}
for i, name in enumerate(ids, 1):
    rgb, mask = architecture(name, i) if name in ('dome','building') else (src.copy(), owner == i)
    im = cutout(rgb, mask)
    bbox = im.getbbox()
    x, y, x1, y1 = bbox
    box = (max(0,x-4), max(0,y-4), min(W,x1+4), min(H,y1+4))
    x,y,x1,y1 = box
    crop = im.crop(box)
    crop.save(DEST / f'{name}.webp', lossless=name in ('women','scientist','student'), quality=90, method=6, exact=True)
    small = crop.resize((round(crop.width/2),round(crop.height/2)), Image.Resampling.LANCZOS)
    small.save(DEST / f'{name}@1x.webp', quality=95, method=6, exact=True)
    # Audit the actual served WebPs, including compression and alpha quantisation.
    loaded = Image.new('RGBA', (W,H))
    loaded.paste(Image.open(DEST / f'{name}.webp'), (x,y))
    layers[name] = loaded
    loaded.save(OUT / f'{name}.png')
    weights['desktop'] += (DEST / f'{name}.webp').stat().st_size
    weights['mobile'] += (DEST / f'{name}@1x.webp').stat().st_size
    manifest['layers'].append({'id':name,'z':i+1,'x':x,'y':y,'w':x1-x,'h':y1-y,'bytes':(DEST/f'{name}.webp').stat().st_size,'bytes_1x':(DEST/f'{name}@1x.webp').stat().st_size})

manifest['layers'].sort(key=lambda l:l['z'])
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Image.fromarray(src).resize((1600,round(H*1600/W)),Image.Resampling.LANCZOS).save(DEST/'collage-flat.webp',quality=95,method=6)
composite = Image.new('RGBA',(W,H),(244,244,244,255))
for layer in manifest['layers']:
    composite = Image.alpha_composite(composite,layers[layer['id']])
composite.convert('RGB').save(OUT/'recomposite.png')
diff = np.abs(np.array(composite)[:,:,:3].astype(float)-src.astype(float))
Image.fromarray(np.clip(diff*8,0,255).astype(np.uint8)).save(OUT/'diff.png')
visible_diff = (diff.max(axis=2)>16).astype(np.uint8)
count, _, stats, _ = cv2.connectedComponentsWithStats(visible_diff)
large = [s.tolist() for s in stats[1:] if s[2]>4 and s[3]>4]
people_exact = True
for name in ['women', 'scientist', 'student']:
    exported = np.array(layers[name])
    opaque = (owner == ids.index(name)+1) & (exported[:,:,3] == 255)
    people_exact &= np.array_equal(exported[:,:,:3][opaque], src[opaque])
report = {
    'mae_rgb': diff.mean(axis=(0,1)).tolist(),
    'max_channel_error': float(diff.max()),
    'regions_over_4px_at_threshold_16': len(large),
    'largest_diff_regions': sorted(large,key=lambda s:s[4],reverse=True)[:10],
    'bytes': weights,
    'budget_bytes': {'desktop':600000,'mobile':250000},
    'people_interior_rgb_exact': people_exact,
}
(OUT/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

# Keep embedded percentages and SVG geometry in sync with regenerated crops.
from markup import sync
sync()
