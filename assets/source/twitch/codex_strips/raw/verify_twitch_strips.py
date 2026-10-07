from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[1]/'outputs/twitch-strips'
m=json.loads((root/'manifest.json').read_text());c=json.loads((root/'twitch_cells.json').read_text())
design=np.array(Image.open(root/'source/twitch_design_1x.png').convert('RGBA'))
head=np.array(Image.open(root/'source/twitch_head_1x.png').convert('RGBA'))
palette={tuple(v) for v in design[design[:,:,3]>0,:3]}
head_pixels=[(int(x-59),int(y-66),head[y,x].copy()) for y,x in zip(*np.nonzero(head[:,:,3]))]
count=0; release=[]
for tag,info in m['tags'].items():
    im=Image.open(root/info['file']);a=np.array(im)
    assert list(im.size)==info['size']
    assert set(np.unique(a[:,:,3]))<= {0,255}
    grid=a[::8,::8];assert np.array_equal(a,np.repeat(np.repeat(grid,8,0),8,1))
    assert {tuple(p) for p in a[a[:,:,3]>0,:3]}<=palette
    used=np.zeros(grid.shape[:2],bool)
    for entry,contract in zip(info['frames'],c['tags'][tag]):
        x,y,w,h=entry['rect'];f=grid[y:y+h,x:x+w];used[y:y+h,x:x+w]=True
        assert entry['ms']==contract['ms'] and entry['pivot']==contract['pivot']
        yy,xx=np.nonzero(f[:,:,3]);assert entry['bbox']==[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
        assert not f[82:,:,3].any()
        if entry['head_rotation']==0:
            hx,hy=entry['head_bbox_origin']
            assert all(np.array_equal(f[hy+dy,hx+dx],color) for dx,dy,color in head_pixels),(tag,entry['index'])
        if 'release' in entry:
            r=entry['release'];release.append(dict(tag=tag,index=entry['index'],**r))
            for name in ['bow_tip','near_hand','far_hand']:
                px,py=r[name];assert f[py,px,3]==255,(tag,name,r[name])
        count+=1
    assert not grid[~used,3].any()
run=m['tags']['run']['frames']
assert len({r['stride']['head_relative_x'] for r in run})==1
assert max(r['stride']['bob'] for r in run)-min(r['stride']['bob'] for r in run)<=1
assert run[0]['stride']['near_foot'][0]>run[0]['stride']['far_foot'][0]
assert run[4]['stride']['near_foot'][0]<run[4]['stride']['far_foot'][0]
assert run[2]['stride']['near_lift']==2 and run[6]['stride']['far_lift']==2
assert count==44
summary=dict(frames=count,grid=True,palette_size=len(palette),hard_alpha=True,empty_unused_cells=True,frame_contract=True,head_exact_translation=True,run_stride_proof=True,release_points_on_opaque_pixels=True,release=release)
(root/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
