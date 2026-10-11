from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
SRC=Path('work/zeri_face_pack/zeri');OUT=Path('outputs/zeri-face')
OUT.mkdir(parents=True,exist_ok=True);(OUT/'raw').mkdir(exist_ok=True)
a=np.array(Image.open(SRC/'design_1x.png').convert('RGBA'))
old=sorted({tuple(map(int,c)) for c in a[a[:,:,3]>0,:3]})
letters='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lut={letters[i]:c for i,c in enumerate(old)}
lut.update(H=(154,200,80),d=(49,143,10),m=(161,70,51),v=(140,32,32),w=(67,32,28))
# Hand-authored 8x8 pixel faces: no resizing or resampling of the face.
maps={
'A':['3JJJPP2J','JJPPPPPJ','J222PP22','E2OHPOD2','E2PdPLP2','E2OPmm2J','JJ2PP2EJ','0J2L2EJ2'],
'B':['3JJJPP2J','JJPPPPPJ','J22PPP22','E2OHPOd2','E2PdPLP2','E2OPmv2J','JJ2PP2EJ','0J2L2EJ2'],
'C':['3JJJPP2J','JJPPPPPJ','J222PP22','E2OdPOd2','E2PPPLP2','E2OPvm2J','JJ2PP2EJ','0J2L2EJ2'],
'D':['3JJJPP2J','JJPPPPPJ','J22PPP22','E2OHP2d2','E2PdPLP2','E2OPvm2J','JJ2PL2EJ','0J2L2EJ2']}
# D in A's far eye uses green iris, not the original boot brown D.
maps['A'][3]='E2OHPOd2'
mask=np.zeros((128,128),bool);mask[68:76,60:68]=True
stats=[];compare=Image.new('RGB',(1200,620),'#EEEEF0');draw=ImageDraw.Draw(compare)
for i,(name,rows) in enumerate(maps.items()):
    assert len(rows)==8 and all(len(r)==8 for r in rows)
    b=a.copy()
    for y,r in enumerate(rows):
        for x,k in enumerate(r): b[68+y,60+x]=(*lut[k],255)
    assert np.array_equal(a[~mask],b[~mask])
    assert set(np.unique(b[:,:,3]))=={0,255}
    ys,xs=np.nonzero(b[:,:,3]);assert ys.max()==99
    Image.fromarray(b).save(OUT/f'zeri_face_{name}_1x.png')
    zoom=np.repeat(np.repeat(b,8,0),8,1)
    Image.fromarray(zoom).save(OUT/f'zeri_face_{name}.png')
    changes=[]
    for y,x in zip(*np.nonzero((a!=b).any(2))):
        changes.append(dict(canvas=[int(x),int(y)],figure=[int(x-53),int(y-60)],before=list(map(int,a[y,x])),after=list(map(int,b[y,x]))))
    stats.append(dict(variant=name,changed_pixels=len(changes),outside_box_identical=True,edit_box=[60,68,8,8],colors=len(set(tuple(c) for c in b[b[:,:,3]>0,:3])),changes=changes,rows=rows))
    # Show face with original unchanged hair at 12x and tight whole sprite at 2x.
    head=Image.fromarray(b[60:79,53:77]).resize((288,228),Image.Resampling.NEAREST)
    compare.paste(head,(i*300+6,36),head)
    whole=Image.fromarray(b).resize((256,256),Image.Resampling.NEAREST)
    compare.paste(whole,(i*300+22,274),whole)
    small=Image.fromarray(b[60:100,53:77]).resize((48,80),Image.Resampling.NEAREST)
    compare.paste(small,(i*300+126,515),small)
    draw.text((i*300+138,12),name,fill='#222222')
    draw.text((i*300+90,601),'native sprite at 2x',fill='#222222')
compare.save(OUT/'zeri_face_compare.png')
reference=Image.open(SRC/'5_liked_faces.png').convert('RGB')
ref=reference.resize((600,reference.height*600//reference.width),Image.Resampling.NEAREST)
board=Image.new('RGB',(1200,620+ref.height+36),'#EEEEF0');board.paste(compare,(0,0));board.paste(ref,(300,646))
ImageDraw.Draw(board).text((480,626),'User-liked face references',fill='#222222')
board.save(OUT/'zeri_face_compare_with_reference.png')
best=Image.fromarray(np.array(Image.open(OUT/'zeri_face_A_1x.png'))[60:100,53:77])
best.resize((192,320),Image.Resampling.NEAREST).save(OUT/'zeri_face_A_detail.png')
(OUT/'pixel-changes.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
Image.open(SRC/'design_1x.png').save(OUT/'raw/approved_design_1x.png')
(OUT/'raw/pixel-maps.json').write_text(json.dumps(maps,indent=2))
print(json.dumps([{k:v for k,v in s.items() if k not in ['changes','rows']} for s in stats]))
