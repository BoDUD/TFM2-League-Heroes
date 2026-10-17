#!/usr/bin/env python3
"""Miss Fortune's model fix (2026-10-04): her body traced from League at game size, square by square.

    python tools/art/fix_missfortune_model.py            # apply to assets/source/native/missfortune_<tag>.png
    python tools/art/fix_missfortune_model.py --check    # only report what would change and the frame checks

Why. The user saw her in-game idle at 3x and said 「女枪模型也有点怪异的地方」. Measured against League's model
rendered at the sprite's size (tools/lol/native_pose.py with assets/source/missfortune/poses.json, the same cells and
pivots as these strips), Codex's step-2 strips had:
  - a flat white "T" on the belly (skin highlight FBDAC2 with a gold line through it) instead of a bare, shaded midriff;
  - a flat white 3x4 block for the far arm, no forearm, and the far gun held up beside the hair (it read as floating)
    while League holds it low, the bell toward the viewer by the knee;
  - the near gun held at the chin/chest with a one-square hand and no arm (idle, run 1-8, attack 1-3, skill 2-3,
    skill2 1, ult 1/3/4/5/7, dead 1); League holds it at the hip/waist, forward or down;
  - every arm a flat FBDAC2 slab (skill2 3-6 white columns framing the face), sticks of 1-2 squares through the hat
    brim and hair for raised arms (attack 5, skill 4/5, ult 6), skill 6's far gun up by the hair;
  - a bodice that did not read (navy/teal bits and a vertical gold line from chin to belt) and brown shorts running
    into brown legs, where League has a teal crop bodice, a bare midriff, a gold belt line and teal shorts;
  - enclosed 1-6 square holes (run chin/gun pockets, between legs and guns) and a loose dropped gun in dead 2.

How (the trace, 描原版). Each frame was compared with League's same frame (render + part map, joints from
tools/lol/pose_joints.py); League's places were mapped onto the sprite (+1 row: the sprite's torso sits a row under
League's at the same pivot) and drawn in MF's own 25 palette squares:
  - one torso, traced from League idle 1 and voted into the palette (neck oWs, chest TsWsT, bodice tTTTtn/ntntnn,
    midriff osWso/sWWso/oWsso shaded CF876F with an FBDAC2 middle and D7674B sides, belt GgyyGG, shorts nttTtn/ntTttn)
    is stamped under the neck of every upright frame (casting body = idle body; frames whose head sits a row lower use
    it with one midriff row less so the legs keep their length);
  - sleeves are the skin-highlight white with the grey 565360 on the underside (the strip palette has no cloth white:
    option (a) of the audit), forearms CF876F with a D7674B shade side, 2x2 hands W s / s o; raised arms are a bell
    sleeve at the elbow, a 2-square forearm and a fist on the grip, drawn beside the hat brim, not through it;
  - the guns are one gold blunderbuss drawn at League's angles (E, ESE, SE, SSE, S, N, NE, ENE; mirrored for the far
    side), placed with the grip in the hand at League's hand/grip position; Codex's own far guns stay where they already
    hang low;
  - arms whose silhouette was already right (skill2, hit, dead, ult's raised far arm) are only re-shaded along the arm
    (sleeve near the shoulder, forearm, hand); the hat brim and hair behind removed sticks come back from the next frame
    of the same head (attack 6 for attack 5, skill 6 for skill 5) or by hand (ult 6);
  - the face, the hat and the legs are the strips' own (only rows the old arm or gun covered change); dead 1 (League's
    death@0 = the idle pose) wears the new idle body; dead 2 drops the guns as League hides them; dead 2-6 hips teal.
The squares were then checked per frame (one 8-connected piece, no enclosed hole of 1-6 squares, no outline square
hanging off one square, the face untouched, palette only, binary alpha) and looked at next to League at 3x and zoomed.

Round 1 (the same day, after a review of every frame):
  - dead 2 is still upright (League death@300 keeps the teal bodice, the bare midriff and the white sleeves): it wears
    the idle's torso under its neck like dead 1 (the bare chest, its gold line r66-68 c47 and the dark red block r68 go),
    the far arm hanging down-left and the near arm out to the right traced from death@300 (-1 row, -2 columns);
    dead 3 (death@700) gets the bodice, the far sleeve with its forearm across the belly and the near sleeve and hand;
    dead 4-5 (death@1200/2000) the white sleeves at either side, both hands on the chest, the bodice beside them, the
    midriff and the belt (Codex drew those arms as flat white blocks, round 0 had turned them to skin);
  - run 1-8: the far forearm (navy squares sat between the sleeve and the hand) is a 2-square skin forearm joining the
    sleeve to the hand on the grip; the far gun and the legs are unchanged;
  - the near gun follows League's angle: ult 2 and 6 hang it straight down from the hanging near arm (the long sleeve
    down the side, the hand at the hip, the bell between the knees), ult 3 and 7 point it ~30 deg down-forward (the bell
    by the near shin), skill 6 holds it upright at the end of an arm held out to the right; hit 1 and 2 hold the
    shared gun where League holds it in both (Codex's tangle in hit 1 and its other gun in hit 2 go);
  - the level and ESE guns have a flared bell with the dark mouth facing out (no grip knob behind the hand: they read
    as a bone at 3x); the idle's gun slopes down-right as League's does (the bell two rows lower);
  - every sleeve block (W joined to its m squares, away from the face) is split along the light from the upper left:
    the near ~58% W, the far ~42% m (option (a), MF's own colours; option (b), a cloth ramp F2F4F4/C4D0DA/8A9AAC that
    would take the palette to 28, is the user's to choose and is not applied);
  - skill2 5's two hands on the crossed guns share one ramp (W s o); attack 5's dark lump with gold specks beside the
    near thigh (r69-77 c54-61, left from Codex's drawing, not in League attack@380) goes to the leg's outline.
The patches are absolute over both the committed strips and round 0's output (every square round 0 set is written).

Round 2 (the same day, after a second review of every frame; its blocks follow round 1's in each <tag>.txt):
  - the E gun: idle 1's near gun straightened (barrel 2 rows, lit y / shade G; bell 4 rows with a 2x2 mouth) is the
    one gun sprite; every rebuilt gun is it rotated by area sampling (8x8 samples a square, RotSprite-like) to League's
    angle, shaded from the upper left, outlined, its barrel coming out of a 2x2 fist (W s / s o);
  - attack 1-6: there was no far arm (the far gun came out of the hair on brown/navy smudges, attack 5 a dark-red
    block): each frame wears the idle's far sleeve at its torso (the TsWsT row), a 2-px skin forearm, a 2x2 hand and
    the gun down-left at League's angle (attack1@200 blend -139, @230/@265 -146, @305 -122, @380 -127, @500 -124;
    the hand a square left in 4-6 so the bell clears the far thigh); the hair behind is redrawn where the old gun was;
  - attack 4-6, skill 4-6: the raised near gun (a 2-px stick with a 2-row bell, skill's bell bent like a hook) is the
    E gun rotated (attack 80/95/100, skill 85/85/75 deg; League swings it to 107-111 over the head, which would cover
    the approved hat, so 5-6 stay beside the brim);
  - skill 1-4, skill2 1-2, hit 1-2: the far arm as attack's (League's white far sleeve and the gun down-left; skill 4's
    was a 1-px grey stick, skill 1-3's gun a gold/navy cross, skill2 1-2's a crumble on a mottled forearm);
  - skill2 2: the raised near arm re-shaded (sleeve W/m, a 2-px skin forearm) with the E gun at 55 deg (it had a navy
    barrel); skill2 3-5: idle 1's hat restored (on the eyes, +1 column; 3's had grey squares, 4's and 5's carried
    the guns and hands through the crown), both fists at the brim corners and the E guns out of them: 3 straight up
    (League spell3@400; they were two gold daggers with a crossbar), 4 a little apart, 5 a V (League crosses them
    beside the head; crossing our far arm over the approved face is left out); skill2 6: both guns rebuilt out/up
    (League @800: far ~120 deg, near 60) on 2-px skin forearms (the wrists were navy);
  - ult 1-8: the raised far forearm (mottled b B k u) is a 2-px skin forearm with a fist and the E gun straight up
    (4-px barrel, as long as the old stub); ult 8's raised near gun (a gold/navy tangle) the E gun at 75 deg;
  - hit 1: its head (a tilted, spiky hat for one 120 ms frame) is hit 2's, one row up, so the head no longer pops;
  - specks: gold squares on the face where idle 1 has skin or hair (aligned on the eyes: attack 1-6 cheeks and chins,
    skill 1-5 forehead and neck, run 4/5/8, skill2 1/3/5, ult 2, dead 1); skin/grey squares in skill 3's hat crown
    and skill2 2's brim -> the hat's navy;
  - idle 1-6 (and the design): the far gun's mouth is 2x2 like every other gun (3x2 read as a lantern at 3x);
  - missfortune_native.png: two loose outline crumbs (modelfix/native.txt).
  Left as they were: the run's far sleeve size and level near gun (approved; the review marked them optional) and
  dead 2-7. Every frame stays one 8-connected piece with no enclosed hole; gaps a new gun closed against a thigh were
  painted with the outline or the hair's dark red.

Round 3 (the same day, after a third review; its blocks follow round 2's in each <tag>.txt):
  - skill2 3-6 (the overhead cheer: two gold rods on 2-px sticks growing out of sleeves at chin height, the guns 10-12
    rows above League's) traced from League spell3 @400/@560/@650/@800: idle 1's head (+1 column, the approved hat and
    face) on the frame's own body and hair cascade, the idle's sleeves at the r65 shoulder, 2-px skin forearms, 2x2
    fists and the E gun at League's angles - 3 both hands up at the chin, the far gun up beside the brim's left
    (103 deg), the near gun out right of the face (40); 4 the far gun upright at the far shoulder (95), the near arm
    raised (its sleeve along the upper arm from the shoulder, gun 85); 5 the far forearm across the chest with its
    gun out to the right (8), the near gun raised over the brim's corner (100); 6 both arms spread at shoulder height,
    guns up and out (125 / 55); the notch under the near sleeve (3, 6) is outline, as the import would close it;
  - attack 1-6, skill 1-6, skill2 1-2, hit 1-2: the dark-red hair strand between the far forearm and the belly
    (past the belt to the far thigh in attack 4-6, skill 5-6) -> the outline above the belt (the idle's "##" there)
    and the far thigh's 332220 below it; skill 5-6 its lower end under the far gun likewise;
  - run 1-4, 7-8: the near gun (held dead level, 3-5 columns further out than League's) is the E gun 28 deg down to
    the hip, 9 squares, from the fist's right edge (League run: the bell down by the hip at c57-62).
  Not changed: skill 5's raised gun stays beside the brim (League's over the crown would need an arm from the r65
  shoulder past the r46 crown, twice the idle's arm, and would cover the approved hat); the sleeve ramp stays (a)
  until the user picks (a) or (b) (a side-by-side render was made for that choice).

Round 4 (the same day, after the integrator's look at round 3 and the user's sleeve choice; its blocks follow round 3's):
  - the sleeves: option (b), the cloth-white ramp F2F4F4 / C4D0DA / 8A9AAC (palette w / c / l, the "white" material
    of poses.json that League's blouse is voted into), in every action. Why: rounds 0-3 drew them in the skin
    highlight FBDAC2 with the grey 565360 under it (option a, the strips' own 25 colours), so at 3x a sleeve read as
    bare white-pink skin running into the forearm; the user picked (b) from the side-by-side render
    (mf_fix3/sleeve_ab_3x.png, bottom row). Every sleeve block (a 4-connected W/m block that holds grey m, 3+ squares)
    stays lit from the upper left: m -> l, a W open above or to the left -> w, any other W -> c. The face, the
    midriff, the hands and the grey specks in the hat and hair keep their colours; the palette is now 28 colours;
  - skill2 4 and 6 (review of round 3: the far gun of 4 and both guns of 6 were still 3-5 rows above League's and
    3-5 columns further out): traced again from League spell3 @480 / @800 at game size, the guns are held by their
    middles as League's are (the bell 4-6 squares beyond the fist, the stock under the hand and behind the sleeve):
    4 the far fist at the far sleeve's end (r65 c37), the gun upright (92 deg), its bell beside the hair at r59-62;
    6 the far fist at the far sleeve's end (r65 c36, 115 deg, bell r59-62 c33-36) and the near fist at the end of a
    near sleeve one square longer (r65 c55, 72 deg, bell r58-61 c56-59): League's arms spread at shoulder height;
  - run 5-6: the near gun (Codex's thinner one with brown specks, a pop between the E guns of 4 and 7) is the E gun
    at League run@400/@500's angle (-40 deg, the bell by the near knee), 5 squares of barrel like 1-4 and 7-8.
  Reviewed and kept: round 3's skill2 3 and 5, the hair strand removal (attack, skill, skill2 1-2, hit), the run's
  angled near gun. Not changed: skill 5's raised gun beside the brim (League's over the crown needs an arm twice the
  idle's), ult's raised far arm (Codex's pose, kept since round 1).

Round 5 (the same day, the guns; its blocks follow round 4's in each <tag>.txt):
  Why: the user saw rounds 0-4 and said 「武器不自然啊」 - every gun was the one "E gun" (a straight 2-row gold barrel
  ending in a ring-like bell, rotated per frame), which read as a gold stick / key / wrench, not a pistol; Codex's own
  far guns left in the run were thin brown/gold sticks. Now every gun in every frame (both hands; raised guns, skill2,
  ult, attack, run, hit, dead 1 and the idle) is one pistol, drawn at game size after Codex's step-2 guns (HEAD idle 1 /
  attack 1: a dark part at the hand, a gold body and a flared mouth) in the strips' own colours:
      ........gg      g gold barrel and bell (shaded y / g / G / Y from the upper left)
      ...pggggkg      p the lock beside the hand and the grip, brown U / u
      .HHpggggkg      b the navy rail under the barrel, T / t
      .HHpbbbgkg      k the dark mouth inside the flared bell (1A2523), the rim beyond it
      .pp.....gg      H the frame's own 2x2 hand (never drawn over): the grip runs down and back under it,
      pg........        a gold butt cap at its end; 10 squares long, a square shorter than the E gun
  - the angles in use get exact versions, no resampling: 0/90/180/270 deg are flips/transposes of that drawing; 45 deg
    (NE, the bell a triangle flaring out with the dark mouth along its face), 26.6 deg (ENE/ESE, the barrel one step,
    the bell upright) and 63.4 deg (NNE, a short upright pistol with a tilted mouth, for raised guns) are hand-placed
    and only flipped/transposed; each gun takes the nearest version (its aim measured from the hand to the old mouth,
    within ~13 deg) preferring the one whose top (hammer side) faces up;
  - one drawing per held gun (the user: 「右边的枪移动时变形」 - per-frame nearest versions made the run's guns change
    shape, the -27 deg bell reading as a fork): run 1-8 carry exactly the idle's near gun (level, 0 deg) and the
    idle's far gun (-45 deg, NE transposed), only moved with the hand; every low far gun (attack, skill, skill2 1-2,
    hit, dead 1) is that same -45 deg gun; attack 4-6 and skill 4-6 keep one upright gun; ult 3/7's near gun is the
    level one like ult 1/4/5 (only real swings - raised, hanging - change version);
  - each old gun (its gold/k squares flooded from the mouth, plus Codex's brown u/U/B/b squares in the run's far guns)
    is cleared with the outline squares that only bordered it; the pistol goes on with its hand on the same 2x2 hand;
    near guns sit in front of the body, far guns behind it (only over background, hair and the cleared squares);
    hands, forearms, sleeves, faces and eyes are never written (0 skin / sleeve squares change); background next to
    the body where an old gun was gets the outline, loose outline crumbs go, enclosed pockets take their neighbours;
  - dead 2-7 keep no guns (as before). The six idle frames stay one drawing shifted.
  Built with %LOCALAPPDATA%/Temp/mf_guns (designs.py, pistol.py, build.py, table.py); checked per frame (one 8-connected
  piece, no enclosed hole of 1-6 squares, no outline square hanging off one coloured square, palette only, binary alpha)
  and looked at as HEAD | round 4 | round 5 at 3x.

Data. assets/source/missfortune/modelfix/<tag>.txt holds, per frame, the rectangle of squares this fix sets in the 1x
frame (cell 96x96, 8 px a square, frames left to right then top to bottom): '_' keeps the strip's square, '.' clears
it, a letter is a palette colour (PALETTE below); each row of squares starts with '|'. Every square is absolute, so running the script again changes
nothing. The six idle frames are one drawing on six pivots (import_native ORDER plays frame 1 in all six); their
patches are that drawing shifted. missfortune_native.png (the design, 128-square canvas) is the idle drawing 16 rows
down and 16 columns right: it takes idle frame 1's patch there, then modelfix/native.txt's own squares (in the
128-square canvas's coordinates).
import_native's missfortune passes (COMPLETE, CLEAN strict, BOB 6 in idle slots 3-5, EYES steadying) still run on top.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
DATA = os.path.join(ROOT, "assets", "source", "missfortune", "modelfix")
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
CELL, Z = 96, 8
NATIVE_OFF = (16, 16)        # idle frame 1 inside missfortune_native.png (rows, columns)
PALETTE = {"#": "030203", "%": "040213", "t": "133042", "T": "1F455E", "n": "0C273A", "R": "DE4022", "r": "B52215",
           "d": "800F0A", "D": "5A0206", "x": "480304", "W": "FBDAC2", "s": "CF876F", "o": "D7674B", "b": "4D3531",
           "B": "332220", "k": "1A2523", "u": "4E371B", "U": "8A521A", "g": "D09A3A", "G": "AF7621", "y": "ECBC5A",
           "Y": "EED87B", "m": "565360", "e": "2C81E2", "E": "2B7FE0",
           # round 4: the cloth-white ramp of the sleeves (the user's option b; poses.json's "white" material)
           "w": "F2F4F4", "c": "C4D0DA", "l": "8A9AAC"}
RGB = {ch: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for ch, h in PALETTE.items()}


def lp(path):
    """Extended-length path: the worktree sits under a long MSIX folder."""
    path = os.path.abspath(path)
    return path if path.startswith("\\\\?\\") or os.name != "nt" else "\\\\?\\" + path


def read_patches(tag):
    """{frame index: [(row, col, char)]} from modelfix/<tag>.txt."""
    out, cur, r = {}, None, 0
    with open(lp(os.path.join(DATA, f"{tag}.txt")), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("@"):
                k, r0, c0 = (int(v) for v in line[1:].split("#")[0].split())
                cur = out.setdefault(k - 1, []); r, base = r0, c0
                continue
            if not line.startswith("|"):     # comments and blank lines
                continue
            for j, ch in enumerate(line[1:]):
                if ch != "_":
                    cur.append((r, base + j, ch))
            r += 1
    return out


def layout(width):
    return width // (CELL * Z)


def apply(img, k, cols, edits, off=(0, 0), cell=CELL):
    """Set the squares of frame k (8x8 blocks); returns how many differed."""
    X0, Y0 = (k % cols) * cell * Z, (k // cols) * cell * Z
    n = 0
    for y, x, ch in edits:
        y, x = y + off[0], x + off[1]
        blk = img[Y0 + y * Z:Y0 + (y + 1) * Z, X0 + x * Z:X0 + (x + 1) * Z]
        new = np.zeros(4, np.uint8) if ch == "." else np.array(RGB[ch] + (255,), np.uint8)
        if not (blk == new).all():
            n += 1
            blk[:] = new
    return n


def frames(img, count, cell=CELL):
    cols = img.shape[1] // (cell * Z)
    out = []
    for k in range(count):
        X, Y = (k % cols) * cell * Z, (k // cols) * cell * Z
        out.append(img[Y + 4:Y + cell * Z:Z, X + 4:X + cell * Z:Z])
    return out


def checks(f):
    """(pieces, holes <= 6 squares, colours outside the palette, alpha values) of a 1x frame."""
    op = f[..., 3] > 0
    H, W = op.shape
    seen = np.zeros_like(op); pieces = 0
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        pieces += 1; st = [(y, x)]; seen[y, x] = True
        while st:
            cy, cx = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = cy + dy, cx + dx
                    if 0 <= yy < H and 0 <= xx < W and op[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True; st.append((yy, xx))
    seen = np.zeros_like(op); holes = []
    for y, x in zip(*np.nonzero(~op)):
        if seen[y, x]:
            continue
        st = [(y, x)]; seen[y, x] = True; comp = []; border = False
        while st:
            cy, cx = st.pop(); comp.append((cy, cx))
            border |= cy in (0, H - 1) or cx in (0, W - 1)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < H and 0 <= xx < W and not op[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True; st.append((yy, xx))
        if not border and len(comp) <= 6:
            holes.append(comp[0])
    pal = {tuple(v) for v in RGB.values()}
    foreign = {tuple(int(c) for c in f[y, x, :3]) for y, x in zip(*np.nonzero(op))} - pal
    return pieces, holes, foreign, sorted(set(np.unique(f[..., 3]).tolist()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    a = ap.parse_args()
    bad = 0
    for tag in TAGS:
        path = os.path.join(SRC, f"missfortune_{tag}.png")
        img = np.array(Image.open(lp(path)).convert("RGBA"))
        cols = layout(img.shape[1])
        patches = read_patches(tag)
        before = [f.copy() for f in frames(img, max(patches) + 1)]
        for k, e in sorted(patches.items()):
            apply(img, k, cols, e)
        # squares that differ from the strip on disk (later blocks may rewrite squares earlier ones set)
        changed = {k: int((f != b).any(-1).sum()) for k, (f, b) in enumerate(zip(frames(img, max(patches) + 1), before))}
        report = []
        for k, f in enumerate(frames(img, max(patches) + 1)):
            pieces, holes, foreign, alpha = checks(f)
            ok = pieces == 1 and not holes and not foreign and set(alpha) <= {0, 255}
            bad += not ok
            report.append(f"{k + 1}:{changed.get(k, 0)}" + ("" if ok else f"!pieces={pieces} holes={holes} foreign={len(foreign)}"))
        print(f"{tag}: squares set per frame " + " ".join(report))
        if not a.check and any(changed.values()):
            Image.fromarray(img, "RGBA").save(lp(path))
    # the design: idle frame 1's drawing 16 squares down and right in a 128-square canvas
    path = os.path.join(SRC, "missfortune_native.png")
    img = np.array(Image.open(lp(path)).convert("RGBA"))
    before = frames(img, 1, cell=128)[0].copy()
    apply(img, 0, 1, read_patches("idle")[0], off=NATIVE_OFF, cell=128)
    apply(img, 0, 1, read_patches("native").get(0, []), cell=128)     # the design's own squares (round 2)
    n = int((frames(img, 1, cell=128)[0] != before).any(-1).sum())
    print(f"native: squares set {n}")
    if not a.check and n:
        Image.fromarray(img, "RGBA").save(lp(path))
    if bad:
        print(f"{bad} frame(s) failed the checks")
    return 1 if bad and not a.check else 0


if __name__ == "__main__":
    sys.exit(main())
