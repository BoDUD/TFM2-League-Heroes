import json
from PIL import Image,ImageDraw
import pixel_rig as rig

spec=json.loads((rig.PACK/'sheets.json').read_text())
timelines={}
for s in spec['sheets']:
 for f,ms in zip(s['frames'],s['ms']):
  im,_=rig.render(s['tag'],f-1)
  timelines.setdefault(s['tag'],[]).append((im,ms))
tags=['run','attack','attack_p','skill','skill2','ult','hit','dead']
all_frames=[]
for t in range(0,2400,40):
 panel=Image.new('RGB',(960,560),(118,125,112))
 dr=ImageDraw.Draw(panel)
 for idx,tag in enumerate(tags):
  seq=timelines[tag];phase=t%sum(ms for im,ms in seq)
  current=seq[-1][0]
  for im,ms in seq:
   if phase<ms:current=im;break
   phase-=ms
  tile=current.crop((8,32,88,116)).resize((240,252),Image.Resampling.NEAREST)
  x=(idx%4)*240;y=(idx//4)*280
  panel.paste(tile,(x,y+24),tile)
  dr.text((x+8,y+6),tag,fill='white')
 all_frames.append(panel)
all_frames[0].save(rig.OUT/'taric_actions_preview.gif',save_all=True,append_images=all_frames[1:],duration=40,loop=0,disposal=2)
all_frames[0].save(rig.OUT/'taric_actions_preview.png')
print('Saved 8-action animated preview')
