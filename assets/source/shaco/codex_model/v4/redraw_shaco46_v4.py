from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'shaco-native46-v4'
OUT.mkdir(parents=True, exist_ok=True)
INPUT = ROOT / 'work' / 'shaco-model4-input' / 'shaco_model_pack4'
P = {'O':'#0F0419', 'n':'#1D264A', 'b':'#334782', 'h':'#475C75',
     'r':'#9C0D29', 'c':'#B3112D', 's':'#FC2D3F',
     'g':'#8A5D25', 'y':'#F3BF27', 'l':'#FFF2A3',
     'w':'#F7F7F8', 'v':'#D1CBDE', 't':'#AAA3BE', 'k':'#2F2E40',
     'a':'#8AAAC2', 'e':'#03A7E9', 'i':'#B8FAFF'}
C = {k:tuple(bytes.fromhex(v[1:]))+(255,) for k,v in P.items()}

def draw(version):
    art = np.zeros((46,43,4),np.uint8)
    tags = np.full((46,43),'',object)
    active = ''
    def p(x,y,k):
        art[y,x]=C[k]; tags[y,x]=active
    def span(y,x0,x1,k):
        for x in range(x0,x1+1): p(x,y,k)
    def rows(y,ss,k):
        for dy,(l,r) in enumerate(ss): span(y+dy,l,r,k)
    def stamp(x,y,text):
        for dy,row in enumerate(text.strip('\n').splitlines()):
            for dx,k in enumerate(row):
                if k != '.':p(x+dx,y+dy,k)

    # Long trousers are authored as two curved silhouettes with 2x2 tiles.
    # Neither the target image nor its 46-row cut is sampled into this sprite.
    active='pants'
    near=[(19,23),(18,23),(17,23),(16,23),(16,23),(16,23),(17,23),(17,22),(18,22)]
    far =[(24,27),(24,28),(24,29),(24,30),(24,31),(24,31),(24,31),(25,30),(25,30)]
    for side,ss in enumerate((near,far)):
        origin=16 if side==0 else 24
        for dy,(l,r) in enumerate(ss):
            for x in range(l,r+1):
                tile=((x-origin)//2+dy//2)%2
                p(x,28+dy,'k' if tile==0 else ('v' if side==0 else 't'))
    # Continuous dark inside seam separates the legs from the hips down.
    for y in range(30,37): p(24,y,'O')

    active='boots'
    stamp(17,38,'''
..nnb.
..nbb.
.nnbh.
.nbbh.
nnnb..
''')
    stamp(25,38,'''
.nnnb.
..nnb.
..nbb.
..nbbh
.nbbh.
''')
    active='boot_rims'
    stamp(17,37,'''
yyy.yy
.yyy..
''')
    stamp(25,37,'''
yyy.yy
.yyy..
''')
    active='boot_spikes'
    stamp(21,38,'''
.w
vt
''')
    stamp(30,38,'''
.w
vt
''')
    active='shoes'
    # Near boot has a flared gold ankle and a short red toe.
    stamp(15,42,'''
..nnn..
.csscc.
.ssscr.
''')
    # A longer far toe rises two rows above the shared soles.
    stamp(27,41,'''
........s.
...cc..ss.
..csscssc.
.cssssscr.
''')
    active='boot_rims'
    span(41,17,20,'y');p(19,42,'y');p(20,41,'l')
    span(41,29,31,'y');p(28,42,'y')

    # Narrow oblique torso, with the red plane to the viewer's left.
    active='jacket'
    rows(18,[(20,26),(20,26),(19,26),(19,26),(19,26),(20,26),(20,26),(20,26),(19,26),(19,26)],'c')
    rows(19,[(21,22),(20,22),(20,22),(20,23),(21,23),(21,23),(22,23),(22,23)],'s')
    rows(19,[(24,27),(24,27),(24,27),(25,27),(25,27),(25,27),(25,27),(25,27),(25,28)],'n')
    span(24,25,25,'b');span(25,25,25,'b');span(26,25,26,'b')
    active='coat_tails'
    rows(28,[(18,23),(17,22),(16,21),(15,20),(15,18),(14,16)],'c')
    rows(28,[(20,22),(19,21),(18,20),(17,19),(16,17)],'s')
    p(14,33,'r');span(28,26,28,'n');span(29,27,29,'n')

    active='arms'
    stamp(14,19,'''
..nbb
.nbbh
.nbbh
nnnb.
''')
    stamp(30,22,'''
nbb..
nbbh.
.nbbh
..nnn
''')
    active='near_cuff'
    stamp(12,22,'''
..cc..
.cssc.
cssssc
cssscr
.ccrr.
''')
    active='far_cuff'
    stamp(32,25,'''
.cc...
csssc.
cssssc
rcsscr
.rrcc.
''')
    active='hands'
    stamp(12,27,'''
.aa
aah
ahh
''')
    stamp(36,30,'''
aa.
aah
.hh
''')
    active='near_dagger'
    stamp(5,27,'''
..w.w.
.wwwvv
wvvttt
.tkt..
''')
    span(28,11,11,'y');span(29,11,11,'y');p(11,27,'y');p(11,30,'g')
    p(12,29,'n')
    active='far_dagger'
    span(32,36,38,'y')
    stamp(37,33,'''
wv.
wv.
.wv
.wv
..w
''')

    active='near_shoulder'
    stamp(15,13,'''
.w....
.ww...
.vwv..
tvvtt.
ttvttt
.tttnt
''')
    active='shoulder_rims'
    stamp(14,17,'''
.yy...
..yyy.
....yy
.....y
''')
    active='far_shoulder'
    stamp(30,17,'''
....w
...vw
.vvtv
tvttt
nttt.
''')
    active='shoulder_rims'
    span(22,30,33,'y');p(34,21,'y');p(30,21,'g')
    active='collar'
    stamp(21,17,'''
ly...y
yy.yyy
.yy.y.
..y...
''')
    active='buttons'
    for yy in (23,26):
        p(24,yy-1,'l');span(yy,23,25,'y');p(24,yy+1,'g')
    active='belt'
    span(27,19,23,'y');span(27,25,28,'g')

    active='red_hat'
    stamp(25,1,'''
...ss...
..csss..
.cssssc.
csssscc.
ccsscccc
.rccr.cc
..rr...c
..rc.cc.
...ccc..
''')
    span(10,30,31,'c');p(31,11,'r');p(31,12,'r')
    active='navy_hat'
    stamp(13,1,'''
....bbbbb........
..bbbbhbbbb......
.bbbhhbbbbnb.....
.bbhnnnnbbbb.....
bbhnn...nnbbb....
bhnn.....nnbbb...
nnn.......nbbbb..
...........nbbbb.
............nbbb.
.............nnb.
''')
    active='bells'
    stamp(12,7,'ly\nyg')
    stamp(33,7,'yl\ngy')

    # Porcelain mask turns diagonally down/right. Its far socket is separated
    # from the near one by two porcelain cells and one dark rim on each side.
    # B deepens the jaw into the ruff; the boot/trouser coordinates stay fixed.
    active='mask'
    rows(9,[(23,28),(22,29),(21,30),(20,30),(21,30),(22,30),(23,31),(25,29),(27,28)],'w')
    for y,x in [(10,29),(11,30),(12,30),(13,30),(14,30),(15,31),(16,29),(17,28)]:p(x,y,'v')
    if version=='B':
        rows(14,[(22,30),(23,31),(23,31),(25,29),(26,29),(28,28)],'w')
        for y,x in [(14,30),(15,31),(16,31),(17,29),(18,29)]:p(x,y,'v')
    active='sockets'
    ey=11 if version=='A' else 12
    for yy in (ey-1,ey,ey+1):
        span(yy,22,25,'n');span(yy,27,30,'n');p(26,yy,'w')
    span(9,23,25,'w');span(9,26,28,'n');p(29,9,'c')
    if version=='B':span(10,23,25,'w');p(28,10,'w');p(29,10,'w')
    p(27,ey-1,'n')
    active='eyes'
    for xx in (23,28):
        span(ey,xx,xx+1,'e');span(ey+1,xx,xx+1,'e');p(xx+1,ey+1,'i')
        active='sockets';p(xx,ey,'n');active='eyes'
    active='grin'
    gy=14 if version=='A' else 16
    span(gy-1,22,24,'O');span(gy,23,27,'O');span(gy+1,25,28,'O')
    for xx,yy in [(23,gy),(25,gy),(26,gy+1),(28,gy+1)]:p(xx,yy,'w')
    active='nose'
    ny=12 if version=='A' else 13
    span(ny,25,26,'w');span(ny+1,26,27,'w');span(ny+2,28,29,'w');span(ny+3,30,31,'w')
    active='chin'
    cy=16 if version=='A' else 18
    span(cy,25,28,'w');p(28,cy,'v');p(28,cy+1,'w')

    occupied=art[:,:,3]>0
    adjacent=np.zeros_like(occupied)
    adjacent[1:]|=occupied[:-1];adjacent[:-1]|=occupied[1:]
    adjacent[:,1:]|=occupied[:,:-1];adjacent[:,:-1]|=occupied[:,1:]
    outline=adjacent&~occupied
    art[outline]=C['O'];tags[outline]='outline'
    return art,tags

reports={}
for version in ('A','B'):
    a,tags=draw(version)
    yy,xx=np.where(a[:,:,3]>0)
    assert yy.min()==0 and yy.max()==45
    canvas=np.zeros((128,128,4),np.uint8)
    canvas[54:100,43:86]=a
    im=Image.fromarray(canvas)
    im.save(OUT/f'shaco_native46_{version}_1x.png')
    enlarged=im.resize((1024,1024),Image.Resampling.NEAREST)
    enlarged.save(OUT/f'shaco_native46_{version}.png')
    Image.fromarray(a).resize((430,460),Image.Resampling.NEAREST).save(ROOT/'work'/f'shaco46_v4_{version}_preview.png')
    colors=set(map(tuple,a[a[:,:,3]>0,:3].tolist()))
    assert len(colors)<=22
    assert set(np.unique(canvas[:,:,3]))=={0,255}
    assert not canvas[100:,:,3].any()
    assert np.array_equal(np.asarray(enlarged),np.repeat(np.repeat(canvas,8,axis=0),8,axis=1))
    eye=(tags=='eyes')
    ey=11 if version=='A' else 12
    for x in (23,28):
        assert eye[ey:ey+2,x:x+2].sum()==3
        assert (np.all(a[ey:ey+2,x:x+2]==C['i'],axis=2)).sum()==1
    assert eye.sum()==6
    golden=np.zeros_like(eye)
    for k in ('g','y','l'):golden|=np.all(a==C[k],axis=2)
    allowed=np.isin(tags,['bells','collar','buttons','belt','shoulder_rims','boot_rims','near_dagger','far_dagger'])
    assert not (golden&~allowed).any()
    reports[version]={'height':46,'occupied_bounds_1x':[int(xx.min()+43),54,int(xx.max()+44),100],
       'last_occupied_row':99,'pixels_below_feet':0,'opaque_colors':len(colors),
       'alpha_values':[0,255],'strict_8x8':True,'mask_height':9 if version=='A' else 11,
       'eyes':{'size':[2,2],'same_rows':[54+ey,55+ey],'white_bridge_cells':1,'dark_rim_cells_between':2,'cyan_pixels_each':3,'dark_upper_left_corner':True,'bright_core_each':1},
       'pants_rows_local':[28,36],'boots_rows_local':[37,45],
       'authoring':'direct colored cell placement; no source image resampling'}

(OUT/'validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'palette.json').write_text(json.dumps(P,indent=2),encoding='utf-8')
print(json.dumps(reports,indent=2))
