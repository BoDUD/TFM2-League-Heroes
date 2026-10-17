from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import json, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/jayce-model'
RAW=OUT/'raw'
RAW.mkdir(parents=True,exist_ok=True)
P={
 'ink':'#15131d','hair0':'#28191a','hair1':'#42291f','hair2':'#65402a','hair3':'#8b5b38',
 'skin0':'#9f4d35','skin1':'#cd7851','skin2':'#e9a271','skin3':'#ffd093','white':'#fff2cb',
 'red0':'#590f22','red1':'#921b2b','red2':'#c33637','red3':'#e66748',
 'gold0':'#69502f','gold1':'#9b783e','gold2':'#cbab61','gold3':'#f5d98c','gold4':'#f5d98c',
 'leather0':'#30201e','leather1':'#543322','leather2':'#795037','leather3':'#aa7447',
 'navy0':'#171e32','navy1':'#28344c','navy2':'#3e4c67','navy3':'#60708a',
 'steel0':'#293c4c','steel1':'#4e6877','steel2':'#89a2a8','steel3':'#c9d8d0',
 'fur0':'#a89e86','fur1':'#d5ccb0','fur2':'#f2e7c9',
 'orange0':'#a83d13','orange1':'#ed7a19','orange2':'#ffb32c','yellow':'#ffe77c'}
RGBA={k:tuple(bytes.fromhex(v[1:]))+(255,) for k,v in P.items()}

class Canvas:
 def __init__(self,size):
  self.im=Image.new('RGBA',size,(0,0,0,0))
 def poly(self,pts,col): ImageDraw.Draw(self.im).polygon(pts,fill=RGBA[col])
 def rect(self,box,col): ImageDraw.Draw(self.im).rectangle(box,fill=RGBA[col])
 def line(self,pts,col,width=1): ImageDraw.Draw(self.im).line(pts,fill=RGBA[col],width=width)
 def ellipse(self,box,col): ImageDraw.Draw(self.im).ellipse(box,fill=RGBA[col])
 def part(self,pts,col,outline=1):
  mask=Image.new('L',self.im.size); ImageDraw.Draw(mask).polygon(pts,fill=255)
  if outline:
   edge=mask.filter(ImageFilter.MaxFilter(outline*2+1))
   self.im.paste(RGBA['ink'],(0,0),edge)
  self.im.paste(RGBA[col],(0,0),mask)
 def paste(self,other): self.im.alpha_composite(other.im if isinstance(other,Canvas) else other)

# Hand-authored face tiles. Every character below is one game pixel, never sampled
# from a resized source. Identical bytes are stamped in every body variant.
HEAD_ROWS=[
'.......XX........',
'....XXXaaXX......',
'..XXbbcccaaXX....',
'.XbbccddcbbaaX...',
'XabcccbbbbaaXaX..',
'XabbbaaaXXaXssX..',
'XaabaaXsttttttsX.',
'XaaassttttttttsX.',
'.XassXXttstXXtsX.',
'.XssstWItstWItsX.',
'.XsstttttsttttsX.',
'..XssttttsttutsX.',
'...XssttttstutsX.',
'....XsstttXXXtsX.',
'.....XssstttssX..',
'......XssssssX...',
'.......XXXXXX....',
]
HC={'X':'ink','a':'hair0','b':'hair1','c':'hair2','d':'hair3','s':'skin1','t':'skin2','u':'skin3','W':'white','I':'ink'}
HEAD=Image.new('RGBA',(17,17))
for yy,row in enumerate(HEAD_ROWS):
 for xx,v in enumerate(row):
  if v!='.': HEAD.putpixel((xx,yy),RGBA[HC[v]])
# Face finishing is also painted directly in cells: separate brows, two eyes,
# a short nose rather than a vertical stripe, and an upturned half smile.
hd=ImageDraw.Draw(HEAD)
hd.polygon([(7,6),(14,6),(15,8),(15,13),(13,15),(9,15),(6,12),(6,9)],fill=RGBA['skin2'])
hd.polygon([(6,9),(7,10),(7,12),(10,14),(13,15),(9,15),(6,12)],fill=RGBA['skin1'])
hd.line([(14,7),(15,9),(15,13),(13,15)],fill=RGBA['skin1'])
hd.line([(8,8),(10,8)],fill=RGBA['hair0']); hd.point((8,7),fill=RGBA['hair0'])
hd.line([(13,8),(14,8)],fill=RGBA['hair0']); hd.point((14,7),fill=RGBA['hair0'])
for xx in [8,13]:
 hd.point((xx,9),fill=RGBA['white']); hd.point((xx+1,9),fill=RGBA['ink'])
hd.line([(13,10),(13,11)],fill=RGBA['skin1']); hd.point((14,11),fill=RGBA['skin3'])
hd.point((13,12),fill=RGBA['skin0'])
hd.line([(10,13),(13,13),(14,12)],fill=RGBA['hair0'])
hd.line([(10,14),(12,14)],fill=RGBA['skin3'])

def translate(points,dx,dy): return [(x+dx,y+dy) for x,y in points]

def legs(c,variant,dy):
 dst=c
 c=Canvas(dst.im.size)
 # Layered coat, turned pelvis and boots are separately painted at native scale.
 def pts(q): return translate(q,0,dy)
 if variant=='front':
  c.part(pts([(46,76),(56,76),(61,87),(60,95),(64,97),(65,100),(56,100),(55,94),(54,87),(49,84)]),'navy0',2)
  c.poly(pts([(53,78),(56,78),(59,87),(57,90),(54,84)]),'navy1')
  c.poly(pts([(55,86),(61,86),(61,90),(58,93),(55,91)]),'gold0')
  c.poly(pts([(55,86),(59,86),(59,89),(57,91),(55,89)]),'gold2')
  c.poly(pts([(55,91),(58,92),(58,96),(62,97),(63,99),(57,99),(55,96)]),'leather1')
  c.poly(pts([(60,97),(62,97),(63,99),(60,99)]),'gold1')
  dst.paste(c); c=Canvas(dst.im.size)
  c.part(pts([(41,76),(50,77),(45,85),(40,90),(38,97),(37,100),(30,100),(31,97),(34,95),(34,88)]),'navy2',2)
  c.poly(pts([(42,78),(46,78),(42,85),(37,88),(36,85)]),'navy3')
  c.poly(pts([(34,86),(40,85),(43,88),(41,92),(37,93),(34,90)]),'gold1')
  c.poly(pts([(35,86),(38,86),(40,88),(38,91),(35,90)]),'gold3')
  c.poly(pts([(38,86),(39,87),(39,89),(38,89)]),'red2')
  c.poly(pts([(35,92),(38,93),(37,97),(35,98),(32,98),(33,96)]),'leather2')
  c.rect((31,98+dy,37,100+dy),'leather1'); c.rect((31,99+dy,34,100+dy),'gold2')
  dst.im.alpha_composite(c.im,(2,0))
 else:
  # Both boots face right, with level soles and a clear forward/back stagger.
  c.part(pts([(42,76),(49,77),(47,86),(43,92),(43,97),(47,98),(48,100),(37,100),(37,97),(38,90),(40,85)]),'navy0',2)
  c.poly(pts([(41,85),(46,86),(44,91),(40,93),(39,90)]),'gold0')
  c.poly(pts([(40,87),(43,87),(42,91),(40,91)]),'gold1')
  c.poly(pts([(39,93),(42,93),(41,97),(46,98),(47,100),(38,100)]),'leather1')
  c.rect((44,99+dy,47,100+dy),'gold1')
  dst.im.alpha_composite(c.im,(-2,0)); c=Canvas(dst.im.size)
  c.part(pts([(48,77),(55,77),(57,85),(55,92),(55,96),(60,98),(61,100),(50,100),(49,96),(50,88),(47,85)]),'navy2',2)
  c.poly(pts([(50,79),(53,80),(55,84),(53,88),(50,87)]),'navy3')
  c.poly(pts([(50,86),(56,85),(58,88),(55,92),(51,92),(49,89)]),'gold1')
  c.poly(pts([(50,86),(54,86),(55,88),(52,91),(50,89)]),'gold3')
  c.rect((53,86+dy,54,88+dy),'red2')
  c.poly(pts([(51,93),(55,93),(54,97),(59,98),(60,100),(50,100)]),'leather2')
  c.poly(pts([(55,98),(58,98),(60,100),(54,100)]),'gold2')
  dst.paste(c)

def body(form='hammer',variant='front'):
 # Cannon logical origin is +6 columns, -27 rows, with three fewer leg rows.
 cannon=form=='cannon'; dx=6 if cannon else 0; top=17 if cannon else 44
 c=Canvas((85,128))
 # Source body uses the hammer coordinate system. Cannon compresses ONLY the
 # hand-authored lower-body row plan by three omitted rows, never image scaling.
 short=-3 if cannon else 0
 # Tails behind legs.
 if variant=='front':
  c.part([(43,71),(56,72),(56,90+short),(49,94+short),(45,89+short),(44,81)],'navy0',2)
  c.poly([(47,76),(51,76),(52,89+short),(49,92+short),(47,89+short)],'navy1')
  c.line([(46,86+short),(48,91+short),(50,92+short),(53,88+short)],'gold1',2)
 else:
  c.part([(40,70),(49,72),(48,86+short),(42,92+short),(33,90+short),(37,84),(38,76)],'navy0',2)
  c.poly([(40,75),(44,76),(42,86+short),(35,89+short),(39,82)],'navy2')
  c.line([(34,90+short),(41,91+short),(46,87+short)],'gold1',2)
 # Lower legs are native pixel shapes with the upper joints relocated for bent stance.
 legs(c,variant,short)
 # Coat torso broad and sturdy.
 if variant=='front':
  c.part([(42,59),(52,58),(60,63),(58,75),(54,80),(42,79),(39,73),(39,65)],'leather1',2)
  c.poly([(43,62),(47,63),(46,72),(43,76),(41,72)],'leather2')
  c.poly([(51,64),(55,63),(57,67),(54,74),(48,75),(48,70)],'leather0')
  c.part([(45,62),(52,62),(56,66),(53,71),(46,70),(43,66)],'gold1')
  c.poly([(46,62),(50,62),(53,65),(51,68),(45,66)],'gold3')
  c.poly([(46,64),(51,64),(52,66),(49,69),(46,67)],'red1')
  c.ellipse((47,64,53,70),'gold3'); c.ellipse((48,65,52,69),'red1')
  c.rect((49,65,50,68),'gold4'); c.rect((48,66,51,67),'gold4')
  # Far arm supports the raised grip, elbow tucked forward.
  if cannon:
   c.part([(37,61),(42,62),(43,68),(48,70),(46,75),(39,72),(34,68)],'leather1',2)
   c.poly([(36,62),(39,62),(40,66),(37,68),(35,67)],'gold2')
  else:
   c.part([(37,59),(41,59),(42,65),(38,70),(33,71),(32,67),(35,63)],'leather1',2)
   c.poly([(36,60),(39,60),(38,64),(34,68),(33,67)],'leather3')
  # Big asymmetrical shoulder plate, curved lower fork.
  c.part([(56,58),(61,57),(67,55),(66,60),(64,63),(64,66),(68,67),(62,68),(56,66),(54,62)],'gold1',2)
  c.poly([(56,59),(62,58),(66,56),(64,60),(59,62),(55,61)],'gold4')
  c.poly([(58,62),(63,60),(62,65),(65,66),(60,66),(57,64)],'gold2')
  c.poly([(59,62),(62,61),(61,65),(59,65)],'red1')
  c.rect((57,63,58,65),'gold3')
  c.part([(58,69),(63,69),(64,74),(61,79),(58,79),(55,75)],'leather1')
  c.poly([(58,69),(62,69),(63,73),(60,76),(56,74)],'gold2')
  c.poly([(59,70),(61,70),(61,73),(59,74)],'red2')
 else:
  wide=3 if variant=='B' else 1
  c.part([(42-wide,59),(50,58),(57,63),(56,73),(53,80),(42-wide,79),(39-wide,73),(40-wide,65)],'leather1',2)
  c.poly([(41-wide,62),(45,62),(45,73),(41-wide,76),(40-wide,70)],'leather2')
  c.poly([(48,64),(53,63),(55,67),(51,75),(47,76)],'leather0')
  if variant=='B':
   c.part([(41,63),(47,62),(52,65),(51,70),(45,73),(40,68)],'gold1')
   c.poly([(42,63),(46,63),(49,65),(46,69),(42,67)],'gold3')
   c.ellipse((43,64,50,71),'gold3'); c.ellipse((44,65,49,70),'red1')
   c.rect((46,65,47,69),'gold4'); c.rect((44,67,49,68),'gold4')
  else:
   c.poly([(47,63),(50,64),(51,68),(49,71),(47,69)],'gold2')
   c.rect((48,65,49,68),'red1')
  # Far arm, body-facing right.
  c.part([(48,64),(52,64),(54,69),(60,69),(62,73),(58,75),(51,73),(47,69)],'leather0')
  c.poly([(50,65),(52,66),(53,70),(58,71),(58,73),(52,72)],'leather2')
  c.part([(50,58),(55,58),(59,60),(60,65),(57,68),(52,66),(49,63)],'gold1',2)
  c.poly([(51,59),(55,59),(58,61),(57,63),(51,62)],'gold4')
  c.poly([(53,63),(57,62),(58,65),(55,66),(52,65)],'red1')
  c.rect((50,61,51,64),'gold2')
  # Near arm projects toward the weapon; distinct profile elbow silhouette.
  if cannon:
   c.part([(54,67),(58,68),(59,72),(64,72),(65,76),(59,77),(54,74),(51,70)],'leather2',2)
   c.poly([(55,68),(58,69),(58,72),(62,73),(61,75),(56,73)],'gold2')
  else:
   c.part([(54,67),(58,67),(59,71),(64,65),(67,67),(64,73),(58,77),(54,75),(51,71)],'leather2',2)
   c.poly([(54,68),(57,68),(58,72),(55,74),(52,71)],'gold2')
   c.poly([(55,69),(57,69),(57,72),(55,72)],'red2')
 # Belt across waist, following orientation.
 c.poly([(42,75),(49,76),(55,74),(56,77),(49,79),(41,78)],'leather0')
 c.line([(42,76),(48,77),(54,76)],'leather3',1)
 bx=47 if variant=='front' else 51
 c.rect((bx,75,bx+3,78),'gold2'); c.rect((bx+1,76,bx+2,77),'leather0')
 # Cream fur collar, red scarf, then the exact shared face.
 c.part([(40,56),(43,56),(47,60),(51,58),(54,56),(57,60),(54,64),(49,63),(44,64),(39,60)],'fur0')
 c.poly([(41,57),(43,57),(46,61),(43,62),(40,60)],'fur2')
 c.poly([(52,59),(54,57),(56,60),(53,62),(50,62)],'fur2')
 c.part([(43,58),(48,60),(53,60),(55,63),(51,64),(46,62),(43,61)],'red0',1)
 c.line([(44,59),(48,61),(53,62)],'red2',1)
 if variant=='front' or variant=='B':
  c.poly([(46,63),(49,64),(50,68),(47,67)],'red1')
 # Face uses identical coordinates and no rotation.
 c.im.alpha_composite(HEAD,(40,44))
 # Cannon authored row map: keep head, neck and torso unchanged; bend knees by
 # shortening the lower-body section. Legs already ended on row97.
 if cannon:
  # All coordinates above use hammer origin, including head. Translate to target.
  target=Canvas((128,85)); target.im.alpha_composite(c.im,(dx,-27)); c=target
 return c

def hammer_weapon(side=False):
 c=Canvas((85,128))
 if not side:
  # Continuous straight shaft raster, then collars/grips along the SAME axis.
  p0=(32,45); p1=(65,90)
  c.line([p0,p1],'ink',7); c.line([p0,p1],'steel1',3)
  c.line([(31,46),(64,91)],'steel3',1)
  for a,b in [((39,55),(43,61)),((56,78),(59,82))]:
   c.line([a,b],'ink',6); c.line([a,b],'red1',4); c.line([(a[0]-1,a[1]),(b[0]-1,b[1])],'red2',1)
  for a,b in [((35,49),(37,52)),((46,65),(47,67)),((61,84),(63,86))]:
   c.line([a,b],'steel0',6); c.line([a,b],'steel2',4); c.line([(a[0]-1,a[1]),(b[0]-1,b[1])],'steel3',1)
  c.part([(61,85),(66,86),(68,91),(69,94),(65,92),(62,90)],'steel1')
  c.poly([(63,86),(65,87),(68,92),(65,90)],'steel3')
  # Two chamfered cubic hammer faces, mirror-like gold bands and red grooves.
  c.part([(18,41),(23,37),(28,40),(29,45),(30,48),(26,53),(23,51),(21,46)],'gold1',2)
  c.poly([(19,41),(23,38),(26,40),(23,43)],'gold4')
  c.poly([(21,43),(25,42),(27,45),(26,49),(24,49)],'gold2')
  c.poly([(21,44),(25,44),(25,46),(22,46)],'red2')
  c.poly([(24,48),(27,47),(27,50),(26,52),(24,50)],'orange1')
  c.part([(33,34),(37,30),(41,35),(41,39),(44,41),(41,45),(37,44),(35,40)],'gold1',2)
  c.poly([(34,34),(37,31),(40,35),(38,38)],'gold4')
  c.poly([(38,39),(41,37),(43,41),(40,44),(38,42)],'gold2')
  c.poly([(37,37),(39,36),(39,39),(38,40),(36,39)],'red2')
  c.part([(27,39),(31,37),(35,39),(37,44),(34,48),(30,48),(27,45)],'steel1')
  c.ellipse((28,39,35,47),'gold1'); c.ellipse((29,40,34,46),'orange1')
  c.ellipse((30,41,34,45),'orange2'); c.ellipse((30,41,33,45),'ink')
  c.rect((31,42,32,44),'orange1'); c.rect((31,42,32,43),'yellow')
  c.poly([(27,39),(29,38),(31,38),(30,40),(28,41)],'steel3')
 else:
  # Exactly vertical pole, invariant x coordinate throughout.
  c.rect((64,45,70,96),'ink'); c.rect((66,46,68,94),'steel1'); c.rect((66,46,66,93),'steel3')
  c.rect((65,61,69,69),'red0'); c.rect((66,61,68,69),'red1'); c.rect((66,61,66,69),'red2')
  c.rect((65,77,69,81),'red1'); c.rect((66,77,66,81),'red2')
  for y in [50,58,71,85]:
   c.rect((64,y,70,y+2),'steel0'); c.rect((65,y,69,y+1),'steel2'); c.rect((65,y,66,y+1),'steel3')
  c.part([(64,89),(70,89),(70,93),(67,97),(64,93)],'steel1')
  c.poly([(65,90),(67,90),(67,95),(65,92)],'steel3')
  c.part([(58,34),(64,32),(64,49),(58,47)],'gold1',2)
  c.poly([(58,34),(63,33),(63,36),(59,37)],'gold4')
  c.rect((59,37,61,44),'gold2'); c.rect((59,40,62,42),'red1')
  c.poly([(59,46),(63,46),(63,49),(59,47)],'gold3')
  c.part([(72,31),(78,33),(79,47),(73,49)],'gold1',2)
  c.poly([(73,32),(77,34),(77,37),(73,35)],'gold4')
  c.poly([(74,37),(78,38),(78,44),(74,45)],'gold2')
  c.rect((74,40,78,42),'red2'); c.poly([(74,47),(78,45),(78,47),(74,49)],'gold3')
  c.part([(64,36),(70,35),(73,38),(73,45),(69,48),(64,46)],'steel1')
  c.ellipse((63,36,73,47),'gold2'); c.ellipse((65,38,71,45),'orange1')
  c.ellipse((66,39,70,44),'ink'); c.rect((67,40,69,43),'orange2'); c.rect((67,40,68,41),'yellow')
 return c

def cannon_weapon():
 c=Canvas((128,85))
 # Exact horizontal common axis y=46. No rotations or deformations.
 c.part([(13,46),(19,42),(24,42),(27,45),(31,45),(31,48),(24,50),(19,50)],'steel0',1)
 c.poly([(14,46),(20,43),(20,46)],'steel3'); c.poly([(15,47),(20,47),(20,49)],'steel1')
 c.rect((21,42,25,50),'gold1'); c.rect((21,42,24,43),'gold3'); c.rect((21,44,22,48),'gold2')
 c.rect((24,44,26,48),'steel2'); c.rect((26,44,66,49),'ink')
 c.rect((27,45,66,48),'steel0'); c.rect((28,45,66,45),'steel2')
 c.rect((33,45,40,48),'red1'); c.rect((33,45,40,45),'red2')
 for x in [30,42,50,60,68]:
  c.rect((x,44,x+2,49),'steel1'); c.rect((x,44,x+1,45),'steel3')
 # Folded hammer faces and their two gold rails.
 c.part([(54,38),(66,38),(69,40),(69,44),(56,44),(54,42)],'gold1',2)
 c.rect((55,38,65,39),'gold4'); c.rect((56,40,60,43),'gold2'); c.rect((62,40,66,43),'gold3')
 c.rect((60,39,61,43),'gold0')
 c.part([(54,50),(68,50),(69,53),(66,55),(55,55),(53,53)],'gold1',2)
 c.rect((55,50,67,51),'gold3'); c.rect((55,52,59,54),'gold2'); c.rect((62,52,66,54),'gold2')
 c.rect((60,52,61,55),'gold0')
 # Core remains visible between front and rear folded plates.
 c.part([(72,41),(76,40),(80,43),(80,50),(77,53),(73,52),(70,49),(70,44)],'gold1')
 c.ellipse((71,41,80,52),'orange1'); c.ellipse((72,42,79,51),'orange2')
 c.ellipse((73,43,78,50),'steel0'); c.rect((74,44,77,49),'steel1')
 c.rect((75,44,76,47),'yellow'); c.rect((73,43,74,44),'steel3')
 c.part([(80,39),(86,39),(90,41),(90,44),(82,43),(79,42)],'gold1',1)
 c.rect((81,39,85,40),'gold4'); c.rect((82,41,87,42),'gold2')
 c.part([(80,51),(89,50),(90,53),(86,55),(80,55),(78,53)],'gold1',1)
 c.rect((81,51,87,52),'gold3'); c.rect((81,53,85,54),'gold2')
 # Open barrel mouth, silver ring, black interior and little outer teeth.
 c.part([(87,42),(90,43),(92,45),(92,49),(90,51),(87,52),(85,50),(85,44)],'steel1',1)
 c.poly([(87,42),(90,43),(91,45),(89,45),(88,44),(86,45)],'steel3')
 c.poly([(86,48),(88,50),(90,49),(91,48),(91,50),(88,52),(86,50)],'steel2')
 c.poly([(88,44),(90,45),(91,46),(91,49),(88,50),(87,48),(87,46)],'ink')
 c.rect((89,46,90,48),'navy0')
 return c

def hands(form,variant):
 c=Canvas((85,128))
 if variant=='front':
  centers=[(40,59),(58,77)] if form=='hammer' else [(43,72),(59,73)]
 else: centers=[(65,65),(65,76)] if form=='hammer' else [(57,73),(65,73)]
 for x,y in centers:
  c.part([(x-2,y-2),(x+1,y-2),(x+3,y),(x+2,y+3),(x-1,y+3),(x-3,y+1)],'leather1',1)
  c.rect((x-1,y-1,x+1,y),'leather3'); c.rect((x,y+1,x+2,y+1),'leather2')
 if form=='cannon':
  t=Canvas((128,85)); t.im.alpha_composite(c.im,(6,-27)); return t
 return c

def render(im,kind):
 # Paint final output cell-by-cell; there is no resize/resample operation.
 size=(1024,1536) if kind=='hammer' else (1536,1024)
 out=Image.new('RGBA',size,(0,0,0,0)); d=ImageDraw.Draw(out)
 for y in range(im.height):
  for x in range(im.width):
   q=im.getpixel((x,y))
   if q[3]: d.rectangle((x*12,y*12,x*12+11,y*12+11),fill=q)
 return out

def save_asset(name,im,kind):
 render(im,kind).save(OUT/(name+'.png'))
 im.save(RAW/(name+'-cells.png'))
 # Original native-grid drawing and final-size source are preserved unchanged.
 render(im,kind).save(RAW/(name+'.png'))

def make(form,variant):
 b=body(form,variant); w=hammer_weapon(variant!='front') if form=='hammer' else cannon_weapon()
 h=hands(form,variant); full=Canvas(b.im.size); full.paste(b); full.paste(w); full.paste(h)
 b.paste(h)
 # Foreground grips may approach the collar, but never repaint the shared head.
 hx,hy=(40,44) if form=='hammer' else (46,17)
 for item in [b,full]: item.im.alpha_composite(HEAD,(hx,hy))
 # The specified lowest boot row includes its outline; no pixel may cross it.
 limit=100 if form=='hammer' else 70
 for item in [b,w,h,full]:
  ImageDraw.Draw(item.im).rectangle((0,limit+1,item.im.width-1,item.im.height-1),fill=(0,0,0,0))
 # Sole pixels define the requested standing anchor exactly, including outline.
 sole_gap=(42 if variant=='front' else 48)+(6 if form=='cannon' else 0)
 for item in [b,full]: item.im.putpixel((sole_gap,limit),(0,0,0,0))
 name=f'jayce-{form}-'+('front' if variant=='front' else 'side-'+variant)
 save_asset(name,full.im,form)
 if variant=='front':
  save_asset(name+'-body',b.im,form); save_asset(name+'-weapon',w.im,form)
  h.im.save(RAW/(name+'-foreground-hands-cells.png'))
 return full.im

if __name__=='__main__':
 # Requested order: front hammer -> front cannon -> side hammer A/B -> side cannon A/B.
 for form,variant in [('hammer','front'),('cannon','front'),('hammer','A'),('hammer','B'),('cannon','A'),('cannon','B')]:
  make(form,variant)
 HEAD.save(RAW/'shared-head-cells.png')
 (RAW/'palette.json').write_text(json.dumps(P,indent=2),encoding='utf-8')
 print('Saved ten final PNGs and native-grid sources.')
