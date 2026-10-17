from pathlib import Path
import re,json,hashlib
from PIL import Image,ImageDraw
import numpy as np
O=Path(__file__).resolve().parent;specs=json.loads((O/'generation-prompts.json').read_text(encoding='utf-8'))
bindings={v['file']:v for v in json.loads((O/'fx_list.json').read_text(encoding='utf-8'))}
colors=['FFFFFF','FFFFC8','F4FF50','C4F024','72CC14','D8FFFF','7CF0FF','24BCF0','1270B8','FF8CF0','B080FF','FFB040']
pal=np.array([list(bytes.fromhex(c)) for c in colors],np.int32)
wide={'w_laser','w_wall','a_burst','e_shot','w_pulse','r_shot','p_slow','p_haste','w_slow'}
tb={'a_burst','p_spark','w_pulse','w_laser','w_wall','e_shot','r_shot'}
auras={'p_ready','p_shv','w_cast','e_on','r_on','r_st2'}
clear={'p_ready','w_cast','e_on','r_on','r_st2'}

def mirror(a,axis):
    b=np.flip(a,axis).copy()
    # Keep the brighter sampled member of each symmetric pair, then mirror it.
    weights=a[...,:3].astype(np.int32).sum(2)+(a[...,3]>0)*1000
    wb=b[...,:3].astype(np.int32).sum(2)+(b[...,3]>0)*1000
    return np.where((wb>weights)[...,None],b,a)

def readback(raw,w,h,bounds=None,rainbow=False):
    # Quantize raw pixels before each cell's majority-color readback; transparent
    # samples are a real class. No procedural bolt/ring drawing is used.
    a=np.array(raw.convert('RGBA'))
    active=(a[...,3]>=150)&(a[...,:3].max(2)>=140)
    ys,xs=np.nonzero(active)
    if not len(xs):raise ValueError('Empty generated frame')
    bx0,by0,bx1,by1=bounds or (xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    a=a[by0:by1,bx0:bx1];active=active[by0:by1,bx0:bx1]
    rgb=a[...,:3].astype(np.int32);ids=np.zeros(active.shape,np.uint8)
    for y in range(len(ids)):
        ds=((rgb[y,:,None,:]-pal[None,:,:])**2).sum(2)
        if not rainbow:ds[:,9:]=1000000000
        ids[y]=ds.argmin(1)+1
    ids[~active]=0
    out=np.zeros((h,w,4),np.uint8)
    for yy in range(h):
        y0=int(yy*len(ids)/h);y1=max(y0+1,int((yy+1)*len(ids)/h))
        for xx in range(w):
            x0=int(xx*ids.shape[1]/w);x1=max(x0+1,int((xx+1)*ids.shape[1]/w))
            votes=np.bincount(ids[y0:y1,x0:x1].ravel(),minlength=len(pal)+1)
            j=int(votes.argmax())
            # Preserve thin generated sparks whose cell has sufficient coverage.
            if j==0 and votes[1:].sum()>=votes.sum()*0.15:j=int(votes[1:].argmax())+1
            if j:out[yy,xx]=[*pal[j-1],255]
    return out

manifest={'scale':16,'timing_note':'No engine frame durations were supplied. GIFs use 80ms per frame for visual review only.','palette':['#'+c for c in colors],'effects':{}}
sheet=Image.new('RGB',(1200,6*210),'#101827');draw=ImageDraw.Draw(sheet)
for index,s in enumerate(specs):
    name=s['name'];f=O/'raw'/f'zeri_fx_{name}.png'
    if not f.exists():continue
    n=int(re.search(r'(\d+) frames',s['prompt']).group(1))
    ww,hh=map(int,re.search(r'each cell (\d+)x(\d+)',s['prompt']).groups());cw,ch=ww//16,hh//16
    cols=1 if name in wide else (2 if n==4 else 3);rows=(n+cols-1)//cols
    im=Image.open(f).convert('RGBA');rw,rh=im.size;frames=[];records=[]
    dims=list(map(int,re.findall(r'\d+',bindings[f.name]['size'])))
    ew,eh=(dims*2)[:2] if len(dims)==1 else dims
    crops=[];bounds=[]
    for i in range(n):
        raw=im.crop((round(i%cols*rw/cols),round(i//cols*rh/rows),round((i%cols+1)*rw/cols),round((i//cols+1)*rh/rows)))
        ar=np.array(raw);mask=(ar[...,3]>=150)&(ar[...,:3].max(2)>=140);yy,xx=np.nonzero(mask)
        if not len(xx):raise ValueError((name,i,'blank raw cell'))
        crops.append(raw);bounds.append([int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)])
    union=(min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds))
    for i in range(n):
        x0=round(i%cols*rw/cols);x1=round((i%cols+1)*rw/cols)
        y0=round(i//cols*rh/rows);y1=round((i//cols+1)*rh/rows)
        raw=crops[i]
        if name=='w_laser':
            # Layout allocates 204 columns; the actual beam spans 100 to right.
            ew2=100;eh2=13
            a=readback(raw,ew2,eh2,union);cell=np.zeros((ch,cw,4),np.uint8)
            cell[(ch-eh2)//2:(ch-eh2)//2+eh2,cw//2:cw//2+ew2]=a
        else:
            fw,fh=min(ew,cw-2),min(eh,ch-2)
            a=readback(raw,fw,fh,union,name in {'r_nova','r_on','r_hit'});cell=np.zeros((ch,cw,4),np.uint8)
            ox=(cw-fw)//2;oy=(ch-fh)//2
            if name in tb:ox=cw-1-fw
            if name in auras:oy=ch-1-fh
            cell[oy:oy+fh,ox:ox+fw]=a
        cell=mirror(cell,0 if name in tb else 1)
        if name=='r_nova':cell=mirror(cell,0)
        if name in clear:
            cell[ch-36:,(cw-14)//2:(cw+14)//2]=0
        if name=='p_shv':
            gy,gx=np.indices((ch,cw));inside=((gx-(cw-1)/2)/9)**2+((gy-(ch-1)/2)/17)**2<1
            cell[inside]=0
        if name in {'r_nova','r_on','r_hit'}:
            fringe=np.zeros((ch,cw),bool)
            for color in pal[9:]:fringe|=(cell[...,:3]==color).all(2)&(cell[...,3]>0)
            # Keep rainbow on a thin exterior fringe, recolor interior using
            # the approved light ramps without adding new source shapes.
            gy,gx=np.indices((ch,cw));radius=((gx-(cw-1)/2)/cw)**2+((gy-(ch-1)/2)/ch)**2
            candidates=sorted(set(radius[fringe].tolist()),reverse=True)
            keep=np.zeros_like(fringe);budget=max(1,int((cell[...,3]>0).sum()*0.08))
            for r in candidates:
                same=fringe&(radius==r)
                if keep.sum()+same.sum()<=budget:keep|=same
            change=fringe&~keep;rgb=cell[change,:3].astype(np.int32)
            if len(rgb):cell[change,:3]=pal[:9][((rgb[:,None]-pal[None,:9])**2).sum(2).argmin(1)]
        if name=='w_laser':cell[:,:cw//2]=0
        axis=0 if name in tb else 1
        assert np.array_equal(cell,np.flip(cell,axis)),name
        if name=='r_nova':assert np.array_equal(cell,cell[::-1]),name
        assert set(np.unique(cell[...,3]))<={0,255}
        assert cell[...,3].any(),(name,i,'readback blank')
        ys,xs=np.nonzero(cell[...,3])
        records.append({'frame':i+1,'rect':[i*cw,0,cw,ch],'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'pixels':len(xs)})
        frames.append(cell)
    strip=np.concatenate(frames,axis=1)
    Image.fromarray(strip).save(O/'pixel_1x'/f.name)
    enlarged=np.repeat(np.repeat(strip,16,0),16,1);Image.fromarray(enlarged).save(O/f.name)
    assert enlarged.shape[1]==ww*n and enlarged.shape[0]==hh
    gifs=[]
    for a in frames:
        frame=Image.fromarray(a).resize((cw*4,ch*4),Image.Resampling.NEAREST)
        bg=Image.new('RGBA',frame.size,'#101827');bg.alpha_composite(frame);gifs.append(bg.convert('RGB'))
    gifs[0].save(O/'previews'/f'{name}.gif',save_all=True,append_images=gifs[1:],duration=80,loop=0,disposal=2)
    pick=Image.fromarray(frames[min(2,n-1)]);scale=min(280/cw,165/ch,8)
    pick=pick.resize((round(cw*scale),round(ch*scale)),Image.Resampling.NEAREST)
    sx=index%4*300;sy=index//4*210;sheet.paste(pick,(sx+(300-pick.width)//2,sy+15+(165-pick.height)//2),pick)
    draw.text((sx+12,sy+184),f'{name} | {n} frames | {cw}x{ch}',fill='#E5F0FF')
    manifest['effects'][name]={'file':f.name,'native_size':[cw*n,ch],'cell':[cw,ch],'frames':records,'binding':bindings[f.name]['binding'],'symmetry':'xy' if name=='r_nova' else ('y' if name in tb else 'x'),'center_clear':[14,36] if name in clear else None,'raw_grid':[cols,rows],'sha256':hashlib.sha256((O/f.name).read_bytes()).hexdigest()}
sheet.save(O/'zeri_fx_contact.png')
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Normalized',len(manifest['effects']),'of24; frames',sum(len(e['frames']) for e in manifest['effects'].values()))
