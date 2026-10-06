from pathlib import Path
import json, hashlib, shutil
import numpy as np
from PIL import Image, ImageDraw

out=Path('outputs/khazix-strips')
src=Path('work/khazix_strips_pack/khazix_strips_pack')
m=json.loads((out/'manifest.json').read_text())
contract=json.loads((src/'khazix_cells.json').read_text())
head=np.array(Image.open(src/'design/khazix_head_1x.png'))[66:82,69:78]
palette={tuple(bytes.fromhex(c[1:])) for c in m['palette']}
report={'checks':{},'frame_count':0,'new_frames':40,'palette_count':len(palette)}
frames={}
for tag,act in m['actions'].items():
    a=np.array(Image.open(out/act['file']).convert('RGBA'))
    b=np.array(Image.open(out/f'khazix_{tag}_1x.png').convert('RGBA'))
    assert list(Image.open(out/act['file']).size)==act['size_8x']
    assert np.array_equal(a,np.repeat(np.repeat(b,8,axis=0),8,axis=1)),tag
    assert set(np.unique(a[:,:,3]))<={0,255}
    assert {tuple(p[:3]) for p in b[b[:,:,3]>0]}<=palette
    assert len(act['frames'])==len(contract['tags'][tag])
    frames[tag]=[]
    for e,c in zip(act['frames'],contract['tags'][tag]):
        x,y,w,h=e['cell_rect_1x'];cell=b[y:y+h,x:x+w]
        assert e['pivot']==c['pivot'] and e['ms']==c['ms']
        assert not cell[82:,:,3].any()
        assert hashlib.sha256(cell.tobytes()).hexdigest()==e['pixel_hash']
        assert list(Image.fromarray(cell).getbbox())==e['bbox']
        rotated=e['head_rotation']==90
        expected=np.rot90(head) if rotated else head
        joint=(9.5,4.5) if rotated else (4.5,9.5)
        hx,hy=e['head_joint'];left=int(np.floor(hx-joint[0]));top=int(np.floor(hy-joint[1]))
        hh,ww=expected.shape[:2];patch=cell[top:top+hh,left:left+ww]
        mask=expected[:,:,3]>0
        assert np.array_equal(patch[mask],expected[mask]),(tag,e['frame'],'head mismatch')
        assert mask.sum()==e['head_mask_pixels']
        if 'release' in e:
            tip=e['release']['claw_tip_1x'];assert cell[tip[1],tip[0],3]==255
        frames[tag].append(cell)
        report['frame_count']+=1
    for j in range(len(act['frames']),act['grid'][0]*act['grid'][1]):
        x=j%act['grid'][0]*128;y=j//act['grid'][0]*96
        assert not b[y:y+96,x:x+128,3].any()
    assert Image.open(out/act['file']).size==Image.open(src/f'now/khazix_now_{tag}.png').size
assert (out/'khazix_idle.png').read_bytes()==(src/'khazix_idle.png').read_bytes()
run=m['actions']['run']['frames']
assert len({e['head_joint'][0]-e['pivot'][0] for e in run})==1
assert max(e['head_joint'][1]-e['pivot'][1] for e in run)-min(e['head_joint'][1]-e['pivot'][1] for e in run)==1
def normalized(tag,i):
    im=Image.fromarray(frames[tag][i]);return np.array(im.crop(im.getbbox()))
assert np.array_equal(normalized('dead',5),normalized('dead',6))
assert np.array_equal(normalized('dead',5),normalized('dead',7))
report['checks']={k:True for k in ['sheet_dimensions_match_input','strict_8x8_blocks','binary_alpha','approved_palette_only','head_opaque_pixels_exact_all_46_frames','pivot_and_durations_match_input','no_pixels_below_row_81','blank_cells_transparent','idle_byte_identical','run_head_horizontal_stable','run_head_bob_one_row','death_last_three_poses_identical','release_tips_opaque']}
(out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for name in ['khazix_design_1x.png','khazix_head_1x.png','khazix_palette.png']:
    shutil.copy2(src/'design'/name,out/'raw'/name)
shutil.copy2('work/build_khazix_strips.py',out/'raw/build_khazix_strips.py')
shutil.copy2(__file__,out/'raw/verify_khazix_strips.py')
tags=list(frames);pics=[]
for time in range(0,2400,10):
    canvas=Image.new('RGB',(1024,440),(245,245,245));draw=ImageDraw.Draw(canvas)
    for j,tag in enumerate(tags):
        times=[e['ms'] for e in m['actions'][tag]['frames']]
        t=min(time,sum(times)-1) if tag=='dead' else time%sum(times)
        i=0
        while t>=times[i]:t-=times[i];i+=1
        im=Image.fromarray(frames[tag][i]).resize((256,192),Image.Resampling.NEAREST)
        x=j%4*256;y=j//4*220
        canvas.paste(im,(x,y+24),im)
        draw.text((x+12,y+7),f'{tag}  {i+1}/{len(times)}',fill=(30,30,30))
    pics.append(canvas)
pics[0].save(out/'previews/all_actions.gif',save_all=True,append_images=pics[1:],duration=10,loop=0,disposal=2)
print(json.dumps(report,indent=2))
