from pathlib import Path
import sys,json
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
REPO=Path('D:/TFM2-Workshop/repo/.claude/worktrees/nervous-austin-5d9567')
sys.path.insert(0,str(REPO/'tools/art'))
from design_riven import to_lab,keep_axis
OUT=Path('outputs/zeri-refine')
raw=np.asarray(Image.open('work/zeri_refine_readback.png').convert('RGBA'))
hexes=['100C14','7A9A08','B4E01E','E8FA5A','0E3E66','1670A0','22A0C8','F6C21E','E0287A','6AD02A','A8261E','3E1838','6A2A5A','5A2E1E','8A4A30','F6A418','C8784A','F2B47E','C8CCD6','F2F4F8']
pal=np.array([list(bytes.fromhex(c)) for c in hexes],np.uint8)
op=raw[...,3]>0
idx=np.full(op.shape,-1,int)
idx[op]=((to_lab(raw[op,:3])[:,None]-to_lab(pal)[None])**2).sum(-1).argmin(1)
# Hair buns 0-4; head 5-14; body 15-35. Remove only redundant full rows.
rows=[r for r in range(19) if r not in [3,6,9,10]]
tail=keep_axis([idx[y] for y in range(19,42)],21,range(10,13))
rows += [r+19 for r in tail]
if 41 not in rows:
    rows[-1]=41
cols=keep_axis([idx[rows][:,x] for x in range(idx.shape[1])],28,range(10,18))
sub=idx[np.ix_(rows,cols)]
face=np.zeros(sub.shape,bool)
face[5:15,:]=False
for y,r in enumerate(rows):
    for x,c in enumerate(cols):
        if 8<=r<=17 and 10<=c<=17: face[y,x]=True
families={1:1,2:1,3:1,4:2,5:2,6:2,7:3,8:4,9:4,10:5,11:6,12:6,13:7,14:7,15:8,16:9,17:9,18:10,19:10}
changed=Counter()
for _ in range(3):
    prev=sub.copy()
    for y in range(sub.shape[0]):
        for x in range(sub.shape[1]):
            cur=prev[y,x]
            if cur<0 or face[y,x]:continue
            ns=[prev[yy,xx] for yy in range(max(0,y-1),min(sub.shape[0],y+2)) for xx in range(max(0,x-1),min(sub.shape[1],x+2)) if (yy,xx)!=(y,x)]
            opaque=[v for v in ns if v>=0]
            if cur==0 and len(opaque)==len(ns) and len(ns)==8:
                colors=[v for v in opaque if v>0]
                if colors:
                    fam=Counter(families[v] for v in colors).most_common(1)[0][0]
                    sub[y,x]={1:1,2:4,3:7,4:8,5:10,6:11,7:13,8:15,9:16,10:18}[fam]
                    changed['internal_black']+=1
            elif y<15 and cur in [4,5,6] and sum(v in [1,2,3] for v in opaque)>=5:
                sub[y,x]=1;changed['hair_teal_speck']+=1
            elif cur in [1,2,3,4,5,6,11,12,13,14] and cur not in ns:
                same=[v for v in opaque if v>0 and families.get(v)==families[cur]]
                if len(same)>=4:
                    sub[y,x]=Counter(same).most_common(1)[0][0];changed['shade_speck']+=1
fig=np.zeros(sub.shape+(4,),np.uint8); mask=sub>=0
fig[mask,:3]=pal[sub[mask]];fig[mask,3]=255
feet=np.where((fig[-2:,:,3]>0).any(0))[0]
mid=(feet.min()+feet.max())/2
x0=int(round(64-mid));y0=64
can=np.zeros((128,128,4),np.uint8);can[y0:y0+36,x0:x0+28]=fig
Image.fromarray(can).save(OUT/'zeri_refine_1x.png')
zoom=np.repeat(np.repeat(can,8,0),8,1)
Image.fromarray(zoom).save(OUT/'zeri_refine.png')
used=sorted({tuple(map(int,p)) for p in can[can[...,3]>0,:3]})
(OUT/'palette.hex').write_text('\n'.join('#%02X%02X%02X'%p for p in used)+'\n')
swatch=Image.new('RGB',(320,64),'white');d=ImageDraw.Draw(swatch)
for i,c in enumerate(used):d.rectangle((i%10*32,i//10*32,i%10*32+31,i//10*32+31),fill=c)
swatch.save(OUT/'palette.png')
preview=Image.new('RGBA',(600,360),'#EEEEF0');d=ImageDraw.Draw(preview)
# Guide pixels removed by sampling only original block centers within its sprite box.
target=Image.open('work/zeri_pack1b/zeri/1_target.png').convert('RGBA')
t=np.array(target)[4::8,4::8]
t[(t[:,:,:3]==255).all(2)]=0
crop=t[64:100,51:79]
for i,c in enumerate([crop,fig]):
    im=Image.fromarray(c).resize((c.shape[1]*8,c.shape[0]*8),Image.Resampling.NEAREST)
    preview.alpha_composite(im,(i*300+38,24))
d.text((90,325),'target 28x36',fill='#222222');d.text((390,325),'refine 28x36',fill='#222222')
preview.convert('RGB').save(OUT/'zeri_refine_comparison.png')
Image.fromarray(fig).resize((224,288),Image.Resampling.NEAREST).save(OUT/'zeri_refine_detail.png')
ys,xs=np.nonzero(can[...,3]); assert ys.max()==99 and ys.max()-ys.min()+1==36 and xs.max()-xs.min()+1<=28
assert len(used)<=20 and set(np.unique(can[...,3]))=={0,255} and not can[100:,:,3].any()
qa=dict(height=36,width=28,colors=len(used),top_row=64,sole_row=99,left_col=x0,foot_mid_col=x0+mid,source_readback=[31,42],rows_kept=rows,columns_kept=cols,face_original_rows_kept=[r for r in rows if 8<=r<=17],alpha_values=[0,255],pixel_grid=8,cleanup_counts=dict(changed),isolated_feature_policy='Preserve intentional eyes, plaster, lightning and hardware; remove unsupported shade specks.')
(OUT/'image-qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(qa))
