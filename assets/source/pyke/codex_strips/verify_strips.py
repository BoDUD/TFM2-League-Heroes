from PIL import Image
from pathlib import Path
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parent/'source';OUT=Path(__file__).resolve().parent
m=json.loads((OUT/'manifest.json').read_text());src=json.loads((ROOT/'pyke_cells.json').read_text())
design=np.array(Image.open(ROOT/'design/pyke_design_1x.png').convert('RGBA'))
palette={tuple(p[:3]) for p in design.reshape(-1,4) if p[3]}
h=Image.open(ROOT/'design/pyke_head_1x.png').convert('RGBA').crop((68,59,81,73));ha=np.array(h);hm=ha[:,:,3]>0
checks=[]
for tag,info in m['tags'].items():
    big=np.array(Image.open(OUT/f'pyke_{tag}.png').convert('RGBA'));small=np.array(Image.open(OUT/f'pyke_{tag}_1x.png').convert('RGBA'))
    assert np.array_equal(big,np.repeat(np.repeat(small,8,axis=0),8,axis=1)),tag+' grid'
    assert [big.shape[1],big.shape[0]]==info['image_size']
    assert set(np.unique(big[:,:,3])).issubset({0,255})
    used={tuple(p[:3]) for p in small.reshape(-1,4) if p[3]};assert used<=palette,tag+' palette'
    assert len(info['frames'])==len(src['tags'][tag])
    heads=0;areas=[]
    for i,r in enumerate(info['frames']):
        assert r['ms']==src['tags'][tag][i]['ms'] and r['pivot']==src['tags'][tag][i]['pivot']
        a=np.array(Image.open(OUT/'frames'/f'{tag}_{i+1:02d}_1x.png').convert('RGBA'))
        assert not a[82:,:,3].any(),(tag,i,'feet')
        if r['head_origin']:
            x,y=r['head_origin'];b=a[y:y+14,x:x+13]
            assert b.shape==ha.shape and np.array_equal(b[hm],ha[hm]),(tag,i,'head mismatch')
            heads+=1
        elif r['head_rotation']==90:
            rh=np.array(h.rotate(90,expand=True));rm=rh[:,:,3]>0;found=False
            for sy in range(96-rh.shape[0]+1):
                for sx in range(128-rh.shape[1]+1):
                    sample=a[sy:sy+rh.shape[0],sx:sx+rh.shape[1]]
                    if np.array_equal(sample[rm],rh[rm]):found=True;break
                if found:break
            assert found,(tag,i,'rotated head mismatch')
        if r['release'] and tag in ['attack','skill_stab']:
            assert r['harpoon_tip'][0]>r['hand'][0],(tag,i,'rightward strike')
        if tag=='skill' and i>=4:assert not r['harpoon_held'] and r['harpoon_tip'] is None
        areas.append(int((a[:,:,3]>0).sum()))
    if tag=='skill_stab':assert not small[96:192,256:384,3].any()
    if tag=='run':
        relative=[r['head_origin'][0]-r['pivot'][0] for r in info['frames']]
        assert len(set(relative))==1
        yy=[r['head_origin'][1]-r['pivot'][1] for r in info['frames']];assert max(yy)-min(yy)<=1
    checks.append({'tag':tag,'frames':len(info['frames']),'palette_colors':len(used),'head_exact_frames':heads,'alpha':'0/255','grid':'exact 8x8','below_feet':0,'areas':areas,'unique_frames':len({hashlib.sha256(np.array(f).tobytes()).hexdigest() for f in [Image.open(OUT/'frames'/f'{tag}_{j+1:02d}_1x.png') for j in range(len(info['frames']))]})})
assert (OUT/'pyke_idle.png').read_bytes()==(ROOT/'pyke_idle.png').read_bytes()
(OUT/'validation.json').write_text(json.dumps({'checks':checks,'original_idle_unchanged':True,'head_template_exact_upright_frames':sum(c['head_exact_frames'] for c in checks),'limitations':['rigid-part pose approximation','45-degree pixel rotations may produce alias stair steps','prone legs retain bent design geometry','GIF duration precision is 10 milliseconds; use manifest exact timing','no in-game validation']},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS:',sum(c['frames'] for c in checks),'frames;',sum(c['head_exact_frames'] for c in checks),'upright heads exact; native palette, 8x8 grid, alpha and feet verified.')
