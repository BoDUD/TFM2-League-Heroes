from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
O=Path(__file__).resolve().parent
# User-supplied GRID_PROMPTS explicitly requests nearest-neighbor readback.
palette=['#0b0716','#183544','#005b73','#008eaa','#35bdca','#3b326b','#a1c41a','#d5ef32','#f0ff75','#a45b3d','#ee925e','#ffc58a','#f5eadb','#a5a5b6','#525369','#5b203c','#8e315b','#b75845','#733c38','#d8414c','#f7c315','#f28d15','#4f7911','#bd703f']
pal=np.array([tuple(bytes.fromhex(c[1:])) for c in palette],dtype=np.int32)
qa=[]
for take in 'ABC':
    im=Image.open(O/'raw'/f'generated-{take}.png').convert('RGBA')
    a=np.array(im);mask=a[...,3]>=254;ys,xs=np.nonzero(mask)
    bbox=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
    small=np.array(im.crop(bbox).resize((24,40),Image.Resampling.NEAREST))
    opaque=small[...,3]>=240
    colors=small[opaque,:3].astype(np.int32)
    d=((colors[:,None,:]-pal[None,:,:])**2).sum(2)
    small[opaque,:3]=pal[d.argmin(1)].astype(np.uint8)
    small[...,3]=np.where(opaque,255,0);small[~opaque]=0
    canvas=np.zeros((59,39,4),dtype=np.uint8);canvas[12:52,8:32]=small
    Image.fromarray(canvas).save(O/f'zeri-grid-{take}_1x.png')
    big=np.zeros((1536,1024,4),dtype=np.uint8)
    big[:1534,:1014]=np.repeat(np.repeat(canvas,26,0),26,1)
    Image.fromarray(big).save(O/f'zeri-grid-{take}.png')
    Image.fromarray(canvas).resize((312,472),Image.Resampling.NEAREST).save(O/f'zeri-grid-{take}_8x.png')
    ys,xs=np.nonzero(canvas[...,3]);used=set(map(tuple,canvas[canvas[...,3]>0,:3]))
    assert ys.min()==12 and ys.max()==51
    assert len(used)<=24 and set(np.unique(canvas[...,3]))<={0,255}
    assert np.array_equal(big[:1534,:1014].reshape(59,26,39,26,4),np.broadcast_to(canvas[:,None,:,None,:],(59,26,39,26,4)))
    qa.append(dict(take=take,height=40,width=int(xs.max()-xs.min()+1),bbox=[int(xs.min()),12,int(xs.max()+1),52],colors=len(used),alpha_binary=True,grid26_exact=True,raw_bbox=bbox,method='AI redraw, transparent silhouette crop, nearest-neighbor 24x40 readback, fixed shared 24-color palette'))
sheet=Image.new('RGB',(1248,800),'#e8eaef');dr=ImageDraw.Draw(sheet)
for i,take in enumerate('ABC'):
    im=Image.open(O/f'zeri-grid-{take}_8x.png');sheet.paste(im,(i*312,30),im);dr.text((i*312+130,8),take,fill='#182030')
current=Image.open(O/'raw/references/current_1x.png').convert('RGBA').resize((312,472),Image.Resampling.NEAREST)
sheet.paste(current,(936,30),current);dr.text((1035,8),'Previous',fill='#182030')
for i,take in enumerate('ABC'):
    im=Image.open(O/f'zeri-grid-{take}_1x.png').crop((13,20,27,30)).resize((224,160),Image.Resampling.NEAREST)
    sheet.paste(im,(i*312+44,550),im)
    dr.text((i*312+105,730),f'{take} face 16x',fill='#182030')
face=Image.open(O/'raw/references/3_league_face.png').crop((1065,0,1674,520)).convert('RGB')
face.thumbnail((280,220));sheet.paste(face,(952,540));dr.text((1015,775),'Face reference',fill='#182030')
sheet.save(O/'zeri-grid-compare.png')
p=Image.new('RGB',(24*36,64),'white');dp=ImageDraw.Draw(p)
for i,c in enumerate(palette):dp.rectangle((i*36,0,i*36+35,35),fill=c)
p.save(O/'zeri-palette.png')
(O/'palette.json').write_text(json.dumps(palette,indent=2),encoding='utf-8')
(O/'qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(qa))
