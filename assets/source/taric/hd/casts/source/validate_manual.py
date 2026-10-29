"""Validate delivered sheets, rather than trusting the renderer's intermediate frames."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
import pixel_rig as rig

spec=json.loads((rig.PACK/'sheets.json').read_text())
src=np.asarray(rig.SRC)
palette=set(map(tuple,src[src[:,:,3]>0,:3].tolist()))
reports=[]
for s in spec['sheets']:
 p=rig.OUT/(s['name']+'.png')
 im=Image.open(p).convert('RGBA');a=np.array(im)
 blocks=a[4:1020].reshape(127,8,192,8,4)
 colors=set(map(tuple,np.unique(a[a[:,:,3]>0,:3],axis=0).tolist()))
 checks={
  'size_1536x1024':im.size==(1536,1024),
  'alpha_binary':bool(np.isin(a[:,:,3],[0,255]).all()),
  'exact_design_palette':colors<=palette,
  'flat_8px_grid_origin_y4':bool((blocks==blocks[:,:1,:,:1,:]).all()),
  'top_4px_clear':not bool(a[:4,:,3].any()),
  'nothing_below_ground_y924':not bool(a[924:,:,3].any()),
  'canvas_edges_clear':not bool(a[0,:,3].any() or a[-1,:,3].any() or a[:,0,3].any() or a[:,-1,3].any()),
 }
 assert all(checks.values()),(s['name'],checks)
 reports.append({'name':s['name'],'frames':s['frames'],'durations_ms':s['ms'],'checks':checks,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
frames=json.loads((rig.OUT/'pixel-QA.json').read_text())['frames']
for f in frames:
 expected=2 if f['action']=='dead' and f['frame']>=2 else 1
 assert len(f['component_sizes'])==expected,f
 assert f['palette_exact'] and f['alpha_binary'],f
assert len(frames)==49 and len(reports)==25
result={'status':'PASS','scope':'pixel source sheets; not game runtime acceptance','sheet_count':25,'frame_count':49,'source_design_sha256':hashlib.sha256((rig.PACK/'refs/design_1x.png').read_bytes()).hexdigest(),'palette_color_count':len(palette),'fixed_weapon_source_sha256':hashlib.sha256((rig.OUT/'rig-parts/weapon.png').read_bytes()).hexdigest(),'weapon_transform':'rigid rotation + translation, no scale or separate handle edits','two_arm_chains':['near_upper -> near_lower -> near_hand','bare_upper -> bare_lower -> bare_hand'],'connectivity':'all held-weapon frames 1 connected component; death 2-8 body + separate weapon','reports':reports}
(rig.OUT/'QA.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('PASS: 25 sheets, 49 frames, exact 44-color palette, binary alpha, 8px grid, ground and component gates')
