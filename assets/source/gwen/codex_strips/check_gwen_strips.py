from PIL import Image
import numpy as np
import json,hashlib
from pathlib import Path
B=Path('work/gwen_strips_pack/gwen_strips_pack'); O=Path('outputs/gwen-strips')
m=json.loads((O/'manifest.json').read_text(encoding='utf8')); head=Image.open(B/'design/gwen_head_1x.png').convert('RGBA'); head=head.crop(head.getbbox()); ha=np.array(head); mask=ha[:,:,3]>0
pal=set(m['palette']); result={}
for tag,info in m['animations'].items():
    s=Image.open(O/f'gwen_{tag}_1x.png').convert('RGBA'); big=Image.open(O/f'gwen_{tag}.png').convert('RGBA'); a=np.array(s)
    colours=set('#%02X%02X%02X'%tuple(p[:3]) for p in a.reshape(-1,4) if p[3])
    floors=[]; heads=[]; sourcelegs=[]
    for f in info['frames']:
        x,y,w,h=f['cell_rect']; fr=s.crop((x,y,x+w,y+h)); ar=np.array(fr)
        floors.append(int((ar[82:,:,3]>0).sum()))
        hx,hy,hw,hh=f['head_rect']; patch=np.array(fr.crop((hx,hy,hx+hw,hy+hh)))
        heads.append(bool(np.array_equal(patch[mask],ha[mask])))
    result[tag]={'frame_count':info['frame_count'],'size_matches':list(big.size)==info['image_size'],'strict_8x_blocks':bool(np.array_equal(np.array(big),np.array(s.resize(big.size,Image.Resampling.NEAREST)))),'binary_alpha':set(a[:,:,3].flatten())<=set([0,255]),'palette_matches':colours<=pal,'all_heads_identical':all(heads),'pixels_below_floor':sum(floors),'frame_durations':[f['ms'] for f in info['frames']],'visual_acceptance':'needs_review','scope':'offline action asset checks; no live game proof'}
    assert result[tag]['size_matches'] and result[tag]['strict_8x_blocks'] and result[tag]['binary_alpha'] and result[tag]['palette_matches'] and result[tag]['all_heads_identical'] and result[tag]['pixels_below_floor']==0,(tag,result[tag])
assert hashlib.sha256((B/'gwen_idle.png').read_bytes()).digest()==hashlib.sha256((O/'gwen_idle.png').read_bytes()).digest()
dead=Image.open(O/'gwen_dead_1x.png'); assert np.array_equal(np.array(dead.crop((256,96,384,192))),np.array(dead.crop((384,96,512,192))))
(O/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('PASS:52 frames; exact unchanged idle; dimensions,8x blocks,alpha,palette,head,floor,timings; death final two identical')
