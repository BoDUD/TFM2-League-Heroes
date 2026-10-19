from pathlib import Path
import json
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[1]
out=root
jobs=json.loads((root/'processing'/'jobs.json').read_text(encoding='utf-8'))
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
entries={e['id']:e for e in manifest['entries']}
checks=[]
for job in jobs:
    name=job['file']; w,h=job['cell_1x']; n=job['frames']
    result={'file':name,'expected_frames':n,'expected_cell_1x':[w,h]}
    try:
        entry=entries[job['id']]
        im=Image.open(out/'pixel_1x'/name).convert('RGBA')
        large=Image.open(out/name).convert('RGBA')
        a=np.array(im)
        assert im.size==(w*n,h),'1x dimensions'
        assert large.size==(w*n*8,h*8),'8x dimensions'
        assert entry['frames']==n and entry['cell_1x']==[w,h],'manifest geometry'
        assert set(np.unique(a[:,:,3])) <= {0,255},'alpha'
        assert np.array_equal(np.array(large),np.repeat(np.repeat(a,8,axis=0),8,axis=1)),'nearest 8x'
        colors={tuple(bytes.fromhex(x[1:])) for x in entry['palette']}
        actual={tuple(x[:3]) for x in a.reshape(-1,4) if x[3]}
        assert actual <= colors,'palette'
        for frame in range(n):
            f=a[:,frame*w:(frame+1)*w]
            assert np.array_equal(f,f[:,::-1]),f'frame{frame} symmetry'
            assert f[:,:,3].any(),f'frame{frame} empty'
            if job['id'] in {'w_cast','w_on'}:
                assert not f[h//2-5:h//2+5,w//2-5:w//2+5,3].any(),f'frame{frame} shield center filled'
        assert (out/'raw'/name).exists(),'missing raw'
        assert len({a[:,i*w:(i+1)*w].tobytes() for i in range(n)})>=2,'no animation'
        result.update(passed=True,alpha=[0,255],symmetry='exact per frame',palette_verified=True,nearest_8x_verified=True)
    except (AssertionError,KeyError,FileNotFoundError) as e:
        result.update(passed=False,error=str(e))
    checks.append(result)
report={'expected_sheets':13,'expected_total_frames':sum(j['frames'] for j in jobs),
    'passed_sheets':sum(c['passed'] for c in checks),'all_passed':all(c['passed'] for c in checks),'checks':checks}
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['all_passed'] else 1)
