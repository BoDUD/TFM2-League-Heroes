"""Native 24x40 sprite construction. No large-image sampling or shrinking."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json

HERE=Path(__file__).resolve().parent
OUT=HERE if (HERE/'palette.hex').exists() else HERE.parent/'outputs/vladimir-model-v2'
OUT.mkdir(parents=True,exist_ok=True)
COLORS=['1A0006','45020F','820116','BE0919','E8303A','B86870','F5906E','FDDCB8',
        '83536C','C69BA8','DFC7CD','F8E8DC','A898B0','E6D6DA','FAF4F2',
        '3A435E','556381','9AA6C0','EEF2F8','6F0115','E89AA8','930C21','FF1E1E','FFC8C8']
LETTERS='ABCDEFGHIJKLMNOPQRSTUVWX'
PALETTE=dict(zip(LETTERS,[tuple(bytes.fromhex(c))+(255,) for c in COLORS]))
PALETTE['.']=(0,0,0,0)
im=Image.new('L',(24,40),255)
d=ImageDraw.Draw(im)
def poly(points,c): d.polygon(points,fill=LETTERS.index(c))
def line(points,c): d.line(points,fill=LETTERS.index(c),width=1)
def rect(box,c): d.rectangle(box,fill=LETTERS.index(c))
def dot(x,y,c): im.putpixel((x,y),LETTERS.index(c))

# High collar: solid wing panels, peach rims. Paint behind the head.
poly([(2,8),(6,8),(9,10),(10,15),(6,13),(3,11)],'A')
poly([(3,9),(6,9),(8,11),(9,14),(6,12),(4,11)],'H')
poly([(4,10),(6,10),(7,11),(8,13),(6,12)],'C')
poly([(5,10),(6,11),(7,12)],'D')
poly([(18,9),(21,8),(23,10),(21,12),(18,15)],'A')
poly([(19,10),(21,9),(22,10),(20,12),(18,14)],'H')
poly([(20,10),(21,10),(20,11),(19,13)],'C')

# Coat silhouette and two connected flat wine-red regions.
poly([(9,14),(16,14),(18,16),(18,25),(20,33),(21,36),(18,37),
      (14,35),(10,36),(6,38),(3,36),(6,28),(8,24),(7,17)],'A')
poly([(9,15),(15,15),(17,17),(17,26),(19,34),(20,36),(18,36),
      (14,34),(10,35),(6,37),(4,36),(7,28),(9,24),(8,18)],'B')
poly([(9,15),(12,16),(12,25),(9,31),(6,36),(5,36),(7,29),(10,23)],'C')
poly([(14,16),(16,17),(16,26),(18,35),(16,34),(14,27)],'C')
line([(10,17),(11,20),(11,25),(8,31),(6,35)],'D')

# Arms angled outward, compact cuffs, clear shoulder spikes.
poly([(7,15),(9,17),(8,20),(6,22),(3,22),(4,19)],'A')
poly([(7,16),(8,17),(7,20),(5,21),(4,21),(5,19)],'C')
line([(7,17),(6,19),(5,20)],'D')
poly([(17,15),(19,17),(21,21),(20,23),(17,21),(16,17)],'A')
poly([(17,16),(18,17),(20,21),(18,21),(17,19)],'C')
line([(18,18),(19,20)],'D')

# Two steel wedge spikes on each shoulder.
line([(4,15),(7,15)],'A'); line([(5,15),(6,15)],'R')
line([(4,17),(7,16)],'A'); line([(5,17),(6,16)],'R')
line([(18,15),(21,16)],'A'); line([(19,15),(20,16)],'R')
line([(18,17),(21,18)],'A'); line([(19,17),(20,18)],'R')

# Peach lapels and continuous front trim, no extra inner black outlines.
line([(9,14),(10,16),(12,19)],'H')
line([(17,14),(16,17),(15,19)],'H')
line([(11,24),(10,27),(8,31),(6,35),(5,36)],'H')
line([(16,24),(17,28),(18,32),(19,35),(20,36)],'H')

# Three clean two-pixel-wide steel clasps on uniform crimson chest.
rect((12,16,15,24),'C')
for y in (17,20,23):
    dot(13,y,'R'); dot(14,y,'S')

# Large simple cuffs, each has two visible outside steel points.
poly([(3,20),(6,20),(7,22),(6,23),(2,23),(1,22)],'A')
rect((3,21,6,22),'C'); line([(2,22),(6,22)],'H')
dot(2,20,'R'); dot(1,21,'Q')
poly([(18,20),(21,20),(23,22),(22,23),(18,23)],'A')
rect((18,21,21,22),'C'); line([(18,22),(22,22)],'H')
dot(22,20,'R'); dot(23,21,'Q')

# Three separated claws per hand: two/three pixels long, lit steel tips.
for x,tipx,end in [(1,0,25),(3,2,26),(5,5,25)]:
    line([(x,23),(tipx,end)],'Q'); dot(tipx,end,'S')
for x,tipx,end in [(18,19,25),(20,21,26),(22,23,25)]:
    line([(x,23),(tipx,end)],'Q'); dot(tipx,end,'S')

# Pants are broad dark red panels with single-column stripes.
poly([(11,26),(16,26),(17,32),(16,37),(14,37),(13,31),(12,37),(9,37),(10,31)],'A')
poly([(11,27),(12,27),(12,31),(11,36),(10,36)],'T')
poly([(14,27),(15,27),(16,31),(16,36),(14,36)],'T')
line([(12,27),(11,32)],'U'); line([(15,27),(15,32)],'U')
line([(10,33),(12,33)],'G'); line([(14,33),(16,33)],'G')
rect((10,34,11,37),'C'); rect((14,34,15,37),'C')
line([(10,37),(12,37)],'R'); line([(14,37),(16,37)],'R')

# Broad connected coat-tail panels frame the pants rather than becoming specks.
poly([(8,27),(9,27),(8,31),(6,36),(4,36),(6,31)],'C')
line([(8,28),(7,31),(5,35)],'D')
line([(9,27),(8,30),(6,34),(5,36)],'H')
poly([(17,27),(18,30),(20,36),(18,36),(17,32)],'C')
line([(17,28),(18,32),(19,35)],'H')

# Shoes: exactly two rows. Both sole rows are at native y39.
rect((9,38,12,39),'A'); rect((14,38,18,39),'A')
line([(10,38),(12,38)],'V'); dot(11,38,'R')
line([(15,38),(17,38)],'V'); dot(17,38,'R')

# Hair is built directly as eight rows of two large locks and one highlight band.
poly([(12,0),(13,1),(15,2),(16,3),(17,5),(18,6),(18,9),(17,13),
      (17,14),(16,12),(16,8),(12,9),(9,10),(8,9),(7,7),(8,5),(10,4),(10,2),(11,2)],'A')
poly([(12,1),(13,2),(15,3),(16,5),(17,6),(17,9),(16,12),(16,8),(12,8),
      (9,9),(8,8),(8,6),(11,4),(11,2)],'J')
poly([(12,1),(12,3),(11,5),(9,6),(9,7),(12,6),(14,4),(14,3)],'L')
poly([(15,4),(16,6),(14,7),(12,8),(10,8),(13,6)],'K')

# Six-column pale face. Both eyes are level and equal (2 pixels each).
rect((11,8,16,11),'O')
line([(16,8),(16,11)],'N')
line([(11,9),(12,9)],'I'); line([(15,9),(16,9)],'I')
dot(11,10,'W'); dot(12,10,'X'); dot(15,10,'X'); dot(16,10,'W')
rect((12,12,15,12),'N'); dot(14,12,'I')
line([(13,13),(14,13)],'N')
# Narrow silver side-locks frame, rather than obscure, the eyes.
line([(10,8),(10,12),(11,14)],'L')
line([(17,8),(17,12),(16,14)],'K')

arr=np.array(im)
grid=[''.join('.' if v==255 else LETTERS[int(v)] for v in row) for row in arr]
# The shorter tip uses a new five-row hair cap; rows8-39 are identical.
arr2=arr.copy(); arr2[:8,:]=255
for dy,sy in [(3,0),(4,2),(5,4),(6,6),(7,7)]: arr2[dy]=arr[sy]

def rgba(a):
    out=np.zeros((*a.shape,4),dtype=np.uint8)
    for i,c in enumerate(LETTERS): out[a==i]=PALETTE[c]
    return Image.fromarray(out)

qa=[]
for i,a in enumerate((arr,arr2),1):
    rows=[''.join('.' if v==255 else LETTERS[int(v)] for v in row) for row in a]
    (OUT/f'vladimir_design_{i}_grid.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    sprite=rgba(a); sprite.save(OUT/f'vladimir_design_{i}_sprite.png')
    canvas=Image.new('RGBA',(128,128)); canvas.paste(sprite,(51,60))
    canvas.save(OUT/f'vladimir_design_{i}_1x.png')
    big=canvas.resize((1024,1024),Image.Resampling.NEAREST)
    big.save(OUT/f'vladimir_design_{i}.png')
    q=np.array(canvas); bbox=canvas.getbbox(); cols=np.unique(q[q[:,:,3]>0,:3],axis=0)
    assert bbox[3]-bbox[1]==(40 if i==1 else 37)
    assert bbox[3]==100 and not q[100:,:,3].any()
    assert len(cols)<=24 and set(np.unique(q[:,:,3]))=={0,255}
    assert np.array_equal(np.array(big),np.repeat(np.repeat(q,8,0),8,1))
    # Equal eyes at two two-pixel spans, with no eye colors elsewhere.
    em=np.all(q[:,:,:3]==[255,30,30],axis=2)|np.all(q[:,:,:3]==[255,200,200],axis=2)
    assert list(zip(*np.where(em)))==[(70,62),(70,63),(70,66),(70,67)]
    qa.append({'version':i,'height':bbox[3]-bbox[1],'width':bbox[2]-bbox[0],
               'bbox_1x':bbox,'colors':len(cols),'alpha':[0,255],'sole_row':99,
               'construction':'native grid; no large image resampling'})
assert np.array_equal(arr[8:],arr2[8:])
(OUT/'validation.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
(OUT/'palette.hex').write_text('\n'.join('#'+c for c in COLORS)+'\n',encoding='utf-8')
(OUT/'palette-letters.json').write_text(json.dumps({c:'#'+h for c,h in zip(LETTERS,COLORS)},indent=2),encoding='utf-8')

preview=Image.new('RGB',(800,440),'#1b2330'); pd=ImageDraw.Draw(preview)
for i,a in enumerate((arr,arr2)):
    x=85+i*380
    pd.text((x,16),f'V{i+1} | {40 if i==0 else 37}px | 8x',fill='#e8e4dd')
    sp=rgba(a); big=sp.resize((192,320),Image.Resampling.NEAREST)
    preview.paste(big,(x,48),big)
    pd.rectangle((x-20,380,x+210,435),fill='#716e64')
    preview.paste(sp,(x+80,390),sp)
    pd.text((x,398),'1x',fill='#ffffff')
preview.save(OUT/'vladimir_design_comparison.png')
print(json.dumps(qa))
