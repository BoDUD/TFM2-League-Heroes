#!/usr/bin/env python3
"""league_nami redone at PPU from Codex's picture, every action posed after League's own clip, frame by frame (the
user: 「锐雯诺手贾克斯还有曙光和娜美的动作极度没有还原LOL里面」): tools/lol/league_joints.py reads League's skeleton through
native_pose's camera and ppu_rig.Driver turns the design's parts with it.

    python tools/lol/league_joints.py assets/source/nami/poses.json --out <dir>     # League's joints (once)
    python tools/art/rig_nami_hd.py --joints <dir>/nami_joints.json --parts DIR    # the parts tinted (8x)
    python tools/art/rig_nami_hd.py --joints <dir>/nami_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_nami_hd.py --joints <dir>/nami_joints.json                # orig strips + the 1x sheet

Parts (design squares at PPU 1.5, 50 game rows crown to the fin's tip): her staff arm (forearm and the hand round the
shaft) turned about the shoulder with League's shoulder-to-hand, the staff (head and shaft, the shaft a straight line)
turned about her grip and aimed at where League's staff head end is (its mesh's far end: the head's buffbone sits
off the shaft's line; the hand drawn over the shaft), the upper body (head,
hair, torso, the other arm) moved with League's pelvis and leaning with its chest, the tail under it, the fin (the
tail's end, its columns lifted as League's tail tip rises against the pelvis). Her idle stays as drawn (the staff
upright; League's leans it forward); the death ends lying: the figure a quarter turn. Every tag keeps its timing.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "nami"
PPU = 1.5
ROWS = 50
SPEC_HEIGHT = 47                             # assets/source/nami/poses.json "height"
PIVOT_COL = 31                               # the tail's root under her waist: the line she stands on
SHOULDER = (38.5, 29.5)                      # her far shoulder
GRIP = (46.8, 27.5)                          # her hand round the shaft
STAFF_TIP = (46.5, 3.0)                      # the shaft's line at the head's top
CHEST = (32.0, 29.0)                         # League's chest joint on her
ARM = [(38.5, 27.5), (41, 28.3), (45, 27.5), (45.5, 25), (49.5, 25), (49.8, 29.5), (46, 31.8), (42.5, 34.5),
       (40, 34), (38.5, 32)]
STAFF = [(40, 1), (57, 1), (57, 24), (49, 24), (49, 50), (51, 50), (51, 68), (42, 68), (42, 50), (44, 50), (44, 24),
         (40, 24)]
FIN = [(0, 43), (26, 43), (26, 76), (0, 76)]
MS = {"idle": [140] * 8, "run": [125] * 8, "attack": [60, 60, 70, 70, 90, 110], "skill": [60, 70, 80, 90, 100, 100],
      "skill2": [60, 70, 60, 70, 100, 120], "ult": [60, 70, 80, 80, 100, 120, 140], "hit": [100, 100],
      "dead": [100, 100, 120, 120, 120, 150, 150, 500]}


def design():
    D = R.Design(HERO, PPU, ROWS, coarse=True)
    D.px = PIVOT_COL
    # the staff is held beside her, hiding nothing: close=0 (closed over, its squares came back as a strip of body)
    D.cut_props({"arm": ARM, "staff": STAFF}, close=0)
    D.shaft("staff", (46.5, 23), (46.5, 51), 1.2)       # the shaft: a straight line at every angle
    D.part("fin", FIN)
    D.part("upper", D.poly([(0, 0), (57, 0), (57, 42), (24, 42), (24, 46), (0, 46)]) & D.rest(), take=False)
    D.part("tail", D.rest(), take=False)
    return D


def make_rig(D):
    return R.Rig(D)


def driver(rig, joints):
    s = PPU * ROWS / SPEC_HEIGHT
    d = joints["design"]

    def tail(j, ux, dy):
        # the fin lifted as League's tail tip rises against her pelvis (rows, at most 4)
        rise = ((d["tail6"][1] - d["pelvis"][1]) - (j["tail6"][1] - j["pelvis"][1])) * s * 0.4
        fin = int(round(max(-4, min(4, rise))))
        return [("fin", dict(dx=ux, dy=dy, sway=(0, 26, fin, "right"))), ("tail", dict(dx=ux, dy=dy))], []

    drv = R.Driver(rig, joints, SPEC_HEIGHT, ROWS,
                   arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, over_weapon=True, short=0.6, league_hand="l"),
                   weapons=[dict(name="staff", grip=GRIP, tip=STAFF_TIP, league=("weapon_b", "weapon_a"), aim=True,
                                 chest=CHEST)])
    return drv, tail


def frames(rig, joints):
    drv, tail = driver(rig, joints)
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in MS:
            continue
        rows = R.fit_rows(rows, len(MS[tag]))
        o = dict(extra=tail)
        if tag == "idle":
            o["keep"] = True
        fr = [drv.frame(r["j"], o) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            # the last frames lying: the figure as it falls (League's frame 4) a quarter turn onto the ground, her
            # head forward as League's falls
            lie = R.lie(rig, drv.frame(rows[3]["j"], o), k=-1, dx=2)
            fr = fr[:4] + [lie] + [lie.copy() for _ in fr[5:]]
        out[tag] = fr
    for t in MS:
        if t not in out or len(out[t]) != len(MS[t]):
            sys.exit(f"{t}: {len(out.get(t, []))} frames for {len(MS[t])}")
    return {t: list(zip(out[t], MS[t])) for t in MS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's nami_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D.ruler(os.path.join(a.parts, f"{HERO}_parts.png"), z=8)
        return
    if not a.joints:
        sys.exit("--joints is needed")
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = make_rig(D)
    acts = frames(rig, joints)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
