from pathlib import Path
from PIL import Image
import json,numpy as np,hashlib,re,shutil
out=Path('outputs/khazix-fx');m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
fx=json.loads((out/'fx_list.json').read_text(encoding='utf-8'))
assert len(m['effects'])==16 and {e['file'] for e in m['effects']}=={e['file'] for e in fx}
results=[]
for e in m['effects']:
    big=np.array(Image.open(out/e['file']).convert('RGBA'))
    small=np.array(Image.open(out/'pixel_1x'/e['file']).convert('RGBA'))
    assert list(Image.open(out/e['file']).size)==e['size']
    assert np.array_equal(big,np.repeat(np.repeat(small,16,0),16,1))
    assert set(np.unique(big[:,:,3]))=={0,255}
    palette={tuple(bytes.fromhex(x[1:])) for x in e['palette']}
    assert {tuple(x[:3]) for x in small[small[:,:,3]>0]}<=palette
    cw,ch=e['cell_game_pixels'];hashes=[]
    for i,f in enumerate(e['frame_data']):
        cell=small[:,i*cw:(i+1)*cw];mask=cell[:,:,3]>0
        assert mask.any() and int(mask.sum())==f['opaque_pixels']
        h=hashlib.sha256(cell.tobytes()).hexdigest();assert h==f['pixel_sha256'];hashes.append(h)
        assert list(Image.fromarray(cell).getbbox())==f['bbox_1x']
        if e['symmetry_x']:assert np.array_equal(cell,cell[:,::-1])
        if e['symmetry_y']:assert np.array_equal(cell,cell[::-1])
        hole=e['central_empty_width']
        if hole and not(e['tag']=='evo' and i==5):assert not cell[:,(cw-hole)//2:(cw+hole)//2,3].any()
        if e['tag']!='w_spike':
            p=np.pad(mask,1);edge=mask&(~p[:-2,1:-1]|~p[2:,1:-1]|~p[1:-1,:-2]|~p[1:-1,2:])
            for c in ['3A0E6A','4A3CB0','2E7A28']:assert not (edge&np.all(cell[:,:,:3]==tuple(bytes.fromhex(c)),axis=2)).any()
    raw=out/e['raw'];assert raw.exists()
    results.append({'tag':e['tag'],'frames':e['frames'],'unique_frames':len(set(hashes)),'sha256':hashlib.sha256((out/e['file']).read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'mean_luminance':round(float(np.mean([f['mean_luminance'] for f in e['frame_data']])),2),'brightest_decile_mean':round(float(np.mean([f['brightest_decile_mean'] for f in e['frame_data']])),2)})
report={'effect_count':16,'frame_count':sum(e['frames'] for e in m['effects']),'checks':{k:True for k in ['all_expected_files_present','specified_dimensions','exact_16x16_blocks','binary_transparency','per_effect_palette','all_frames_nonempty','required_symmetries','central_actor_clearance','deepest_ramp_not_rimming_lights','raw_sources_retained']},'runtime_qa':False,'timings_configured':False,'results':results}
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(__file__,out/'raw/verify_khazix_fx.py')
print(json.dumps(report,ensure_ascii=False,indent=2))
