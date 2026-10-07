from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'outputs/kayle_ascend'
m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'));checks=[]
pal={tuple(int(c[j:j+2],16) for j in (1,3,5)) for c in m['palette']}
for r in m['assets']:
    im=Image.open(OUT/'pixel_1x'/r['file']).convert('RGBA');a=np.array(im);w,h=r['cell'];n=r['frames']
    assert im.size==(w*n,h)
    assert set(np.unique(a[:,:,3])) <= {0,255}
    assert {tuple(p[:3]) for p in a.reshape(-1,4) if p[3]}<=pal
    big=Image.open(OUT/r['file']).convert('RGBA')
    assert big.size==(w*n*16,h*16)
    assert big.tobytes()==im.resize(big.size,Image.Resampling.NEAREST).tobytes()
    hashes=[];bboxes=[]
    for i in range(n):
        f=a[:,i*w:(i+1)*w];sym=r['symmetry']
        if sym in ['left-right','both']:assert np.array_equal(f,f[:,::-1]),(r['name'],i,'lr')
        if sym in ['top-bottom','both']:assert np.array_equal(f,f[::-1]),(r['name'],i,'tb')
        if r['name'].startswith('wings'):
            start=10 if r['name']=='wings3' else 0
            assert not f[start:,w//2-6:w//2+6,3].any()
        if r['name']=='e_blast_x':assert not f[-4:,:,3].any()
        if r['symmetry']=='top-bottom':
            assert not f[:,-1,3].any()
            assert f[:,-2,3].any(),(r['name'],i,'leadingedge')
        hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
        bboxes.append(Image.fromarray(f).getchannel('A').getbbox())
    assert len(set(hashes))==n,(r['name'],'duplicate frames')
    checks.append({'name':r['name'],'frames':n,'distinct_frames':len(set(hashes)),'dimensions':True,'binary_alpha':True,'palette':True,'symmetry':True,'exact_16x':True,'bboxes':bboxes})
(OUT/'validation.json').write_text(json.dumps({'passed':True,'assets':11,'frames':53,'checks':checks},indent=2),encoding='utf-8')
print('PASS: 11 sheets / 53 unique per-animation frames; sizes, binary alpha, palette, symmetry, exact 16x, wing gaps, projectile leading edge, explosion floor margin')
