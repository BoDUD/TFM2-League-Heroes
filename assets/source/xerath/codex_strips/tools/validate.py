from pathlib import Path
from PIL import Image
import json, hashlib
from collections import Counter
base=Path(__file__).resolve().parents[1]
source=base/"source"
m=json.loads((base/"manifest.json").read_text(encoding="utf-8-sig"))
cells=json.loads((base/"xerath_cells.json").read_text())
d=Image.open(base/"source"/"xerath_design_1x.png").convert("RGBA")
h=Image.open(base/"source"/"xerath_head_1x.png").convert("RGBA")
palette={p for p in d.getdata() if p[3]}
energy={(int(s[:2],16),int(s[2:4],16),int(s[4:],16),255) for s in ["000A6E","003C59","0090F9","016FA8","019CEF","01B3FB","01D8FA","01F8FC","023439","FBFCFC"]}
headpts=[(x,y,h.getpixel((x,y))) for y in range(128) for x in range(128) if h.getpixel((x,y))[3]]
bodypts=[(x,y,d.getpixel((x,y))) for y in range(128) for x in range(128) if d.getpixel((x,y))[3] and not h.getpixel((x,y))[3] and not(75<=y<=85 and(x<=55 or x>=72))]
head_box=h.getbbox()
report={"passed":[],"limitations":["Fixed short source arms do not reach above the hood. Raised arms use exact quarter turns and have a limited pose range.","Body leans are whole-figure translations, not a rotation or redraw.","Run is a subtle glide made of original parts, not a newly painted flowing-leg cycle.","Death late-frame eyes are dark: explicit exception to unchanged head colors.","GIF playback rounds durations to10ms; PNG/manifest timing is authoritative."]}
def require(ok,label):
    if not ok: raise AssertionError(label)
    report["passed"].append(label)
require((base/"xerath_idle.png").read_bytes()==(source/"xerath_idle.png").read_bytes(),"supplied idle PNG byte-identical")
require((base/"xerath_cells.json").read_bytes()==(source/"xerath_cells.json").read_bytes(),"source timing/pivots JSON byte-identical")
frames_total=0
for tag,a in m["animations"].items():
    require(len(a["frames"])==len(cells["tags"][tag]),tag+" frame count")
    im=Image.open(base/a["file"]).convert("RGBA")
    sm=Image.open(base/a["file_1x"]).convert("RGBA")
    require(im.size==tuple(a["size_8x"]),tag+" sheet dimensions")
    # Transparent RGB payload is immaterial; compare alpha and all opaque pixels.
    up=sm.resize(im.size,Image.Resampling.NEAREST)
    require(im.getchannel("A").tobytes()==up.getchannel("A").tobytes(),tag+" strict8x alpha")
    visible=im.getbbox()
    p=im.load(); q=up.load()
    require(all(p[x,y]==q[x,y] for y in range(visible[1],visible[3]) for x in range(visible[0],visible[2]) if p[x,y][3]),tag+" strict8x opaque grid")
    require({p[3] for p in sm.getdata()}<={0,255},tag+" binary alpha")
    require({p for p in sm.getdata() if p[3]}<=palette,tag+" approved23color palette")
    offsets=[]; poses=[]; preview=[]
    for f,original in zip(a["frames"],cells["tags"][tag]):
        i=f["frame_index"];frames_total+=1
        require(f["duration_ms"]==original["ms"] and f["pivot_1x"]==original["pivot"],f"{tag}:{i} duration and pivot")
        frame=Image.open(base/"preview"/f"{tag}_{i:02}_1x.png").convert("RGBA")
        require(frame.getbbox()==tuple(f["bbox_local_1x"]),f"{tag}:{i} bbox")
        require(frame.crop((0,82,128,96)).getbbox() is None,f"{tag}:{i} healthbar exclusion")
        dx,dy=f["head_translation_from_design"]
        dark=f["head_dark_death_exception"]
        require(all(frame.getpixel((x+dx,y+dy))==((4,2,8,255) if dark and c in energy else c) for x,y,c in headpts),f"{tag}:{i} exact source head")
        f["head_bbox_local_1x"]=[head_box[0]+dx,head_box[1]+dy,head_box[2]+dx,head_box[3]+dy]
        if tag not in ("run","dead"):
            require(all(frame.getpixel((x+dx,y+dy))==c for x,y,c in bodypts),f"{tag}:{i} exact body shoulder chain seal legs")
        if tag=="run":
            legshift=[-1,-1,-2,-2,-1,0,0,-1][i]
            require(all(frame.getpixel((x+dx+(legshift if y>=86 else 0),y+dy))==c for x,y,c in bodypts),f"{tag}:{i} exact translated glide parts")
        if f["release_frame"]:
            claw=f["front_claw_centroid_1x"]
            require(claw is not None and claw[0]>f["pivot_1x"][0],f"{tag}:{i} release claw points right")
            f["front_claw_centroid_local_8x"]=[round(claw[0]*8+4,2),round(claw[1]*8+4,2)]
            f["front_claw_centroid_sheet_8x"]=[f["cell_rect_8x"][0]+f["front_claw_centroid_local_8x"][0],f["cell_rect_8x"][1]+f["front_claw_centroid_local_8x"][1]]
            f["release_tick"]={"attack":10,"skill":54,"skill_quick":22,"skill2":10,"ult_shot":0}[tag]
        offsets.append([dx-f["pivot_1x"][0],dy])
        poses.append(frame.tobytes())
        preview.append(Image.open(base/"preview"/f"{tag}_{i:02}_8x.png").convert("RGB"))
    # Unused frame cells remain empty.
    cols,rows=a["grid"]
    for i in range(len(a["frames"]),cols*rows):
        x=(i%cols)*128;y=(i//cols)*96
        require(sm.crop((x,y,x+128,y+96)).getbbox() is None,tag+" unused cell empty")
    if tag=="run":
        require(len({o[0] for o in offsets})==1,"run fixed head X relative pivot")
        require(max(o[1] for o in offsets)-min(o[1] for o in offsets)<=1,"run bob<=1pixel")
        require(poses[0]==poses[-1],"run seamless first/last cell")
        require(len(set(poses))>=3,"run meaningful distinct phases")
    if tag=="dead": require(poses[-1]==poses[-2],"death final hold identical")
    # Encoding-only preview; artwork in every image was already generated by the part rig.
    preview[0].save(base/"preview"/f"{tag}.gif",save_all=True,append_images=preview[1:],duration=[f["duration_ms"] for f in a["frames"]],loop=0,disposal=2,optimize=False)
    for p in preview: p.close()
m["frame_count_total"]=frames_total
m["bbox_convention"]="exclusive right/bottom; sheet rect [x,y,width,height]; all claw positions are local unless sheet suffix"
m["source_design_sha256"]=hashlib.sha256((base/"source"/"xerath_design_1x.png").read_bytes()).hexdigest()
m["artist_qa_status"]="reviewable part-rig draft; technical invariants passed, motion fidelity limitations documented"
(base/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
report["frame_count_total"]=frames_total
report["status"]="technical_pass_with_artistic_limitations"
(base/"qa-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"status":report["status"],"frames":frames_total,"checks":len(report["passed"])}))


