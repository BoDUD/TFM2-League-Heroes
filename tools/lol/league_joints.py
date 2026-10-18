#!/usr/bin/env python3
"""League's skeleton, frame by frame, as game-pixel points: what tools/art/rig_<hero>_hd.py poses the design's parts
after (the user, 2026-10-16: 「锐雯诺手贾克斯还有曙光和娜美的动作极度没有还原LOL里面」).

    python tools/lol/league_joints.py assets/source/jax/poses.json --out <dir> [--tag attack ...] [--sticks]

The chibi model of tools/lol/native_pose.py (the same spec: camera, chibi proportions, `height`, the tags' frames with
their blends, turns, rises and travels), posed per frame; every joint the hero's table below names is projected through
the spec's camera to game pixels: x forward (the way the sprite faces), y down, from the unit's origin on the floor,
plus its depth (larger = nearer the camera). The weapon's two ends are the weapon part's vertices farthest from its
grip joint (and farthest from that end), followed through the frames. Writes <hero>_joints.json:
{"unit": game px per world unit, "design": {joint: [x, y, depth]}, "tags": {tag: [{"ms": .., "j": {...}}, ...]}};
--sticks also draws <hero>_sticks_<tag>.png (each frame's skeleton, 6x) to check it against <hero>_pose_<tag>.png.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import native_pose as N  # noqa: E402

# canonical name -> the champion's joint
JOINTS = {
    "jax": dict(pelvis="Pelvis", chest="Chest", head="Head", l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot",
                r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", l_shoulder="L_Shoulder", l_elbow="L_Elbow",
                l_hand="L_Hand", r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand", weapon="Weapon",
                weapon_head="Weapon_Head", weapon_end="Weapon_End"),
    "riven": dict(pelvis="hip", chest="chest", head="head", l_hip="L_Thigh", l_knee="L_Knee", l_foot="L_Foot",
                  r_hip="R_Thigh", r_knee="R_Knee", r_foot="R_Foot", l_shoulder="L_UpArm", l_elbow="L_ForeArm",
                  l_hand="L_Hand", r_shoulder="R_UpArm", r_elbow="R_ForeArm", r_hand="R_Hand", weapon="WEAPON",
                  weapon_tip="BUFFBONE_CSTM_WEAPONTIP"),
    "darius": dict(pelvis="Pelvis", chest="Chest", head="Head", l_hip="L_Hip", l_knee="L_Knee", l_foot="L_Foot",
                   r_hip="R_Hip", r_knee="R_Knee", r_foot="R_Foot", l_shoulder="L_UpArm", l_elbow="L_ForeArm",
                   l_hand="L_Hand", r_shoulder="R_UpArm", r_elbow="R_ForeArm", r_hand="R_Hand", weapon="Weapon"),
    "leona": dict(pelvis="hip", chest="chest", head="head", l_hip="l_thigh", l_knee="l_knee", l_foot="l_foot",
                  r_hip="r_thigh", r_knee="r_knee", r_foot="r_foot", l_shoulder="l_uparm", l_elbow="l_forearm",
                  l_hand="l_hand", r_shoulder="r_uparm", r_elbow="r_forearm", r_hand="r_hand", weapon="weapon",
                  shield="shield", shield_top="BUFFBONE_CSTM_SHIELD_TOP"),
    "xinzhao": dict(pelvis="Pelvis", chest="Chest", head="Head", l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot",
                    r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", l_shoulder="L_Shoulder", l_elbow="L_Elbow",
                    l_hand="L_Hand", r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand", weapon="Weapon_Main",
                    spear_up="Upper_WeaponTip1", spear_low="Lower_WeaponTip1"),
    "nami": dict(pelvis="Pelvis", chest="Spine3", head="Head", l_shoulder="L_Shoulder", l_elbow="L_Elbow",
                 l_hand="L_Hand", r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand", weapon="Weapon",
                 weapon_head="Buffbone_Cstm_Weapon_1", tail1="Tail1", tail2="Tail2", tail3="Tail3", tail4="Tail4", tail5="Tail5", tail6="Tail6"),
}
BONES = [("pelvis", "chest"), ("chest", "head"), ("l_hip", "l_knee"), ("l_knee", "l_foot"), ("r_hip", "r_knee"),
         ("r_knee", "r_foot"), ("l_shoulder", "l_elbow"), ("l_elbow", "l_hand"), ("r_shoulder", "r_elbow"),
         ("r_elbow", "r_hand"), ("weapon_a", "weapon_b"), ("tail1", "tail2"), ("tail2", "tail3"), ("tail3", "tail4"),
         ("tail4", "tail5"), ("tail5", "tail6"), ("shield", "shield_top")]


def load(spec_path, lol):
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    chibi = dict(spec["chibi"])
    keep = chibi.pop("keep", None)
    ch = N.Champ(lol, spec["champ"], keep, spec.get("weapon", r"^weapon$"), spec.get("hide", ()),
                 spec.get("hair_part", False), spec.get("crown"), spec.get("parts", ()), spec.get("hide_submeshes", False),
                 spec.get("submesh_textures"), spec.get("glue"), spec.get("legs"), spec.get("head_joint", "head"),
                 spec.get("opaque", False), spec.get("wad"))
    ch.set_layers(spec.get("layer"))
    return spec, chibi, ch


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--tag", action="append")
    ap.add_argument("--sticks", action="store_true")
    a = ap.parse_args()
    spec, chibi, ch = load(a.spec, a.lol)
    hero, cam = spec["hero"], spec["camera"]
    rot = N.camera(cam)
    sign = -1.0 if cam.get("mirror") else 1.0
    names = JOINTS[hero]
    idx = {j["name"].lower(): i for i, j in enumerate(ch.joints)}
    pv, glob, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())
    floor = cv[ch.legv, 1].min()
    weap = np.nonzero(ch.part == 2)[0]
    tip_a = tip_b = None
    if len(weap) and "weapon" in names:
        grip = glob[idx[names["weapon"].lower()]][:3, 3]
        tip_a = weap[np.argmax(np.linalg.norm(pv[weap] - grip, axis=1))]
        tip_b = weap[np.argmax(np.linalg.norm(pv[weap] - pv[tip_a], axis=1))]

    def points(pv, glob):
        out = {}
        for k, n in names.items():
            p = rot @ glob[idx[n.lower()]][:3, 3]
            out[k] = [sign * p[0] * unit, -(p[1] - floor) * unit, float(p[2])]
        for k, v in (("weapon_a", tip_a), ("weapon_b", tip_b)):
            if v is not None:
                p = rot @ pv[v]
                out[k] = [sign * p[0] * unit, -(p[1] - floor) * unit, float(p[2])]
        return {k: [round(float(c), 3) for c in v] for k, v in out.items()}

    res = {"unit": unit, "design": points(pv, glob), "tags": {}}
    for tag, t in spec["tags"].items():
        if a.tag and tag not in a.tag:
            continue
        rows = []
        for fr in t["frames"]:
            fs, ms = fr[0], fr[1]
            opt = fr[2] if len(fr) > 2 else {}
            pv, glob, _ = ch.posed(fs, chibi, opt.get("turn", t.get("turn", 0.0)), t.get("head_like"),
                                   opt.get("rise", t.get("rise", 1.0)), opt.get("travel", t.get("travel", 1.0)))
            rows.append({"ms": ms, "frame": fs, "j": points(pv, glob)})
        res["tags"][tag] = rows
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, f"{hero}_joints.json"), "w", encoding="utf-8") as f:
        json.dump(res, f)
    print(f"{hero}: {len(res['tags'])} tags, {unit * 100:.3f} game px per 100 units")
    if a.sticks:
        z = 6
        for tag, rows in res["tags"].items():
            W, H = 80 * z, 60 * z
            img = Image.new("RGB", (W * len(rows), H), (230, 230, 230))
            d = ImageDraw.Draw(img)
            for i, r in enumerate(rows):
                ox, oy = i * W + 30 * z, 52 * z
                for b0, b1 in BONES:
                    if b0 in r["j"] and b1 in r["j"]:
                        p0, p1 = r["j"][b0], r["j"][b1]
                        col = (200, 0, 0) if b0.startswith("l_") else (0, 0, 200) if b0.startswith("r_") else \
                              (0, 150, 0) if b0.startswith("weapon") else (90, 90, 90)
                        d.line([(ox + p0[0] * z, oy + p0[1] * z), (ox + p1[0] * z, oy + p1[1] * z)], fill=col,
                               width=4)
                d.line([(i * W, oy), ((i + 1) * W, oy)], fill=(150, 150, 150))
            img.save(os.path.join(a.out, f"{hero}_sticks_{tag}.png"))


if __name__ == "__main__":
    main()
