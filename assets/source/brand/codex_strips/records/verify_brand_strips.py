from pathlib import Path
from PIL import Image
import json, hashlib, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/brand-strips'
SRC=ROOT/'work/brand_strips_pack/brand_strips_pack'
m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
pal={tuple(bytes.fromhex(h[1:])) for h in m['palette']}
report={'passed':True,'idle_sha256_unchanged':hashlib.sha256((OUT/'brand_idle.png').read_bytes()).digest()==hashlib.sha256((SRC/'brand_idle.png').read_bytes()).digest(),'animations':{}}
for tag,a in m['animations'].items():
    im=Image.open(OUT/a['file']).convert('RGBA');arr=np.array(im)
    native=np.array(Image.open(OUT/'1x'/f'brand_{tag}_1x.png').convert('RGBA'))
    assert list(im.size)==a['size']
    assert np.array_equal(arr,native.repeat(8,0).repeat(8,1))
    assert set(np.unique(arr[:,:,3])).issubset({0,255})
    assert {tuple(p[:3]) for p in native.reshape(-1,4) if p[3]}.issubset(pal)
    diagnostics=[]
    for f in a['frames']:
        x0,y0,x1,y1=f['cell_rect'];sub=native[y0:y1,x0:x1];mask=sub[:,:,3]>0
        assert not mask[82:].any()
        assert f['pivot']==json.loads((SRC/'brand_cells.json').read_text())['tags'][tag][f['frame']-1]['pivot']
        if tag not in ['idle','dead']:assert f['head_exact'] is True
        if 'release' in f:
            for x,y in f['release']['positions']:assert sub[y,x,3]==255 and sub[y,x,0]>160
        visited=set();sizes=[]
        for y,x in zip(*np.where(mask)):
            if (y,x) in visited:continue
            stack=[(y,x)];visited.add((y,x));n=0
            while stack:
                cy,cx=stack.pop();n+=1
                for dy in [-1,0,1]:
                    for dx in [-1,0,1]:
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<96 and 0<=nx<128 and mask[ny,nx] and (ny,nx) not in visited:visited.add((ny,nx));stack.append((ny,nx))
            sizes.append(n)
        diagnostics.append({'frame':f['frame'],'components_8_connected':sorted(sizes,reverse=True)})
        assert len(sizes)==1,(tag,f['frame'],'disconnected silhouette',sizes)
    report['animations'][tag]={'frames':len(a['frames']),'size':im.size,'grid_alpha_palette_baseline':'passed','head':'exact translated design' if tag not in ['idle','dead'] else 'supplied idle' if tag=='idle' else 'rigid body rotation, death exception','component_diagnostics':diagnostics}
    if tag=='ult':
        assert [81-(f['bbox'][3]-1) for f in a['frames'][1:5]]==[3,4,4,2]
    if tag=='dead':
        f6=a['frames'][6]['cell_rect'];f7=a['frames'][7]['cell_rect'];assert np.array_equal(native[f6[1]:f6[3],f6[0]:f6[2]],native[f7[1]:f7[3],f7[0]:f7[2]])
assert report['idle_sha256_unchanged']
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({t:[f['components_8_connected'] for f in a['component_diagnostics']] for t,a in report['animations'].items()}))
