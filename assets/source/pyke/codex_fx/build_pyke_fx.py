from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,re,shutil,html
OUT=Path('outputs/pyke-fx');SPECS=json.loads(Path('work/fx_specs.json').read_text(encoding='utf-8'))
for d in ['native','previews','prompts']: (OUT/d).mkdir(exist_ok=True)
LR={'q_charge','w_cast','e_left','e_stun','q_slow','r_mark','r_strike','r_reset','p_heal'}
TB={'q_hook','q_stab_hit','e_phantom','r_mark'}
records=[];overview=Image.new('RGB',(1200,1600),'#111923');draw=ImageDraw.Draw(overview)
for k,s in enumerate(SPECS):
 name=s['file'][8:-4];raw=Image.open(OUT/'raw'/s['file']).convert('RGBA');ra=np.array(raw)
 mask=ra[:,:,3]>=128;ys,xs=np.where(mask)
 # One shared vertical crop per action preserves relative vertical motion.
 top=max(0,int(ys.min())-10);bottom=min(raw.height,int(ys.max())+11)
 n=s['frames'];cw=s['width']//n//16;ch=s['height']//16
 colors=list(dict.fromkeys(re.findall(r'#[A-Fa-f0-9]{6}',s['prompt'])))
 rgb=np.array([tuple(bytes.fromhex(c[1:])) for c in colors],dtype=np.int32)
 final=[];stats=[]
 for i in range(n):
  crop=raw.crop((round(i*raw.width/n),top,round((i+1)*raw.width/n),bottom))
  # Area coverage eliminates soft edge debris; palette selection uses area-averaged visible RGB.
  rgba=np.array(crop,dtype=np.float32);alpha=rgba[:,:,3]/255
  render_h={'e_left':15,'r_strike':28,'p_heal':33}.get(name,ch)
  coverage=np.array(Image.fromarray(alpha,mode='F').resize((cw,render_h),Image.Resampling.BOX))
  avg=[]
  for j in range(3):
   weighted=np.array(Image.fromarray(rgba[:,:,j]*alpha,mode='F').resize((cw,render_h),Image.Resampling.BOX))
   avg.append(weighted/np.maximum(coverage,0.001))
  means=np.stack(avg,2);indices=np.argmin(((means[:,:,None,:]-rgb[None,None,:,:])**2).sum(3),2)
  a=np.zeros((ch,cw,4),np.uint8);a[:render_h,:,:3]=rgb[indices];a[:render_h,:,3]=np.where(coverage>=(0.30 if name=='q_hook' else 0.16),255,0)
  if name in LR:
   for x in range(cw//2):a[:,cw-1-x]=a[:,x]
  if name in TB:
   for y in range(ch//2):a[ch-1-y]=a[y]
  if name=='p_heal':a[:,cw//2-5:cw//2+5]=0
  # Remove darkest continuous rims from light/water; harpoon is a physical object.
  if name!='q_hook':
   opaque=a[:,:,3]>0;p=np.pad(opaque,1)
   boundary=opaque & ~(p[1:-1,:-2]&p[1:-1,2:]&p[:-2,1:-1]&p[2:,1:-1])
   for dark,light in [('0B5466','16929E'),('4A0612','8A0A1C')]:
    dc=np.array(tuple(bytes.fromhex(dark)));lc=np.array(tuple(bytes.fromhex(light)))
    a[boundary & np.all(a[:,:,:3]==dc,2),:3]=lc
  a[a[:,:,3]==0]=0
  fr=Image.fromarray(a);final.append(fr)
  visible=a[a[:,:,3]>0,:3];lum=visible @ np.array([.2126,.7152,.0722]);lum.sort()
  stats.append(dict(frame=i+1,bbox=fr.getbbox(),opaque_pixels=len(visible),mean_luminance=round(float(lum.mean()),2),brightest_10pct_luminance=round(float(lum[-max(1,len(lum)//10):].mean()),2),lr_symmetric=np.array_equal(a,a[:,::-1]),tb_symmetric=np.array_equal(a,a[::-1])))
 native=Image.new('RGBA',(cw*n,ch))
 for i,fr in enumerate(final):native.alpha_composite(fr,(i*cw,0))
 native.save(OUT/'native'/s['file']);native.resize((s['width'],s['height']),Image.Resampling.NEAREST).save(OUT/s['file'])
 previews=[]
 for fr in final:
  bg=Image.new('RGBA',fr.size,'#111923');bg.alpha_composite(fr);previews.append(bg.resize((cw*8,ch*8),Image.Resampling.NEAREST).convert('RGB'))
 previews[0].save(OUT/'previews'/f'{name}.gif',save_all=True,append_images=previews[1:],duration=100,loop=0,disposal=2)
 # Show representative first, peak and final stages without adding labels to delivered art.
 tile=Image.new('RGBA',(600,156),'#111923')
 for col,idx in enumerate([0,n//2,n-1]):
  fr=final[idx];scale=min(180//cw,130//ch);scale=max(scale,1);zoom=fr.resize((cw*scale,ch*scale),Image.Resampling.NEAREST)
  tile.alpha_composite(zoom,(col*200+(200-zoom.width)//2,(156-zoom.height)//2))
 px=(k%2)*600;py=(k//2)*200;overview.paste(tile.convert('RGB'),(px,py+32));draw.text((px+15,py+10),f'{k+1:02}  {name} / {n} frames',fill='white')
 rec=dict(number=s['number'],file=s['file'],frames=n,size=[s['width'],s['height']],cell_native=[cw,ch],raw_size=list(raw.size),raw_y_crop=[top,bottom],symmetry=('LR' if name in LR else '')+('TB' if name in TB else ''),frames_stats=stats,unique_frames=len({f.tobytes() for f in final}),source='ImageGen',preview_frame_ms=100)
 records.append(rec);(OUT/'prompts'/f'{name}.txt').write_text(s['prompt'],encoding='utf-8')
 assert rec['unique_frames']>=2,(name,'static animation')
 for fr in final:
  a=np.array(fr);assert set(np.unique(a[:,:,3]))<={0,255};assert {tuple(c) for c in a[a[:,:,3]>0,:3]}<={tuple(c) for c in rgb}
  if name in LR:assert np.array_equal(a,a[:,::-1])
  if name in TB:assert np.array_equal(a,a[::-1])
overview.save(OUT/'overview.png')
(OUT/'validation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2('work/pyke_fx_pack/pyke_fx_pack/fx_list.json',OUT/'fx_list.json')
shutil.copy2('work/pyke_fx_pack/pyke_fx_pack/PROMPTS.md',OUT/'PROMPTS_source.md')
shutil.copy2('work/fx_specs.json',OUT/'specs.json')
shutil.copy2(__file__,OUT/'build_pyke_fx.py')
cards=''.join(f'<article><h3>{html.escape(r["file"])} ({r["frames"]} 帧)</h3><img src="previews/{r["file"][8:-4]}.gif"><p>{r["size"][0]}×{r["size"][1]} · {r["symmetry"]}</p></article>' for r in records)
(OUT/'preview.html').write_text('<!doctype html><meta charset="utf-8"><title>派克特效</title><style>body{background:#111923;color:#eee;font:16px system-ui;padding:30px}main{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}article{background:#202c3b;padding:15px}img{image-rendering:pixelated;max-width:100%}</style><h1>派克：16 张特效预览</h1><p>100 毫秒/帧仅供预览，正式时长由技能动画决定。</p><main>'+cards+'</main>',encoding='utf-8')
print(json.dumps([dict(name=r['file'],frames=r['frames'],unique=r['unique_frames']) for r in records]))
