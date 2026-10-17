#!/usr/bin/env python3
"""league_rakan's half of the Xayah duo (league_xayah, #74): branches that only buffs from her kit open.

    python tools/fix/rakan_xayah_duo.py [--check]

The user's option 1 (2026-10-08, 「霞和洛有联动」): League's Deadly Plumage reaches Rakan, his Battle Dance flies farther
to Xayah, and they talk. Nothing in the data picks an ally by who he is (SwitchByBuff reads the caster's own buffs), but a
buff another hero's kit puts on Rakan is read by his own SwitchByBuff (work/xy/probe_duo.py, 50 reads a game). So
Xayah's kit marks him (tools/kit/build_xayah.py: every attack adds league_xayah_duo to the allies within duo_r, W adds
league_xayah_duo_w to those within duo_w_r) and this script adds to main's league_rakan.data_champion - patched in
place, not rebuilt: work/rk/build_rakan.py would revert four later fixes (red side e8034f7f, the dead-caster guard
e09a5393, the bake b03e7ced, the R walk 0a94a96f) - only:
  attack  league_xayah_duo_w on him -> a refreshed league_rakan_duo_w (W's attack speed and move speed, DUO_T ticks) and
          a second feather W_BLADE ticks later for W_PCT% (Xayah's W numbers);
  E       when the three rings (25000, 50000, 90000) found nobody and league_xayah_duo is on him (Xayah within her
          duo_r): a fourth ring of DUO_R (League: Battle Dance 700 -> 1000 to Xayah), the flight's reach with it;
          on every ring, with league_xayah_duo on him, his E line is his Xayah one (RakanE_hit3DXayah).
Without Xayah none of these buffs is ever on him: his game is the same (the simulator's before / after check).
Also writes league_rakan_e_xayah.sound_info, its override entries and the E tooltip's duo half-sentence (5 languages).
--check only says whether the kit is patched.
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
from build_xayah import P as XP  # noqa: E402

MOD = os.path.join(ROOT, "league")
KIT = os.path.join(MOD, "champion", "league_rakan.data_champion")
DUO, DUO_W = "league_xayah_duo", "league_xayah_duo_w"
DUO_R = XP["duo_r"]
DUO_T = 90
W_AS, W_MS, W_PCT, W_BLADE = XP["w_as"], XP["w_ms"], XP["w_pct"], XP["w_blade"]
NONE = {"type": "Combine", "effects": []}
TEXT = {"zh-hans": "霞在附近时飞得更远。", "zh-hant": "剎雅在附近時飛得更遠。",
        "en": " With Xayah near he flies farther.", "ko": " 자야가 가까이 있으면 더 멀리 날아갑니다.",
        "ja": "ザヤが近くにいればより遠くへ飛ぶ。"}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": buff, "effect_buff": yes, "effect_none": no or NONE}


def nodes(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from nodes(v)
    elif isinstance(o, list):
        for v in o:
            yield from nodes(v)


def patched(kit):
    return any(n.get("buff_name") in (DUO, DUO_W) for n in nodes(kit))


def attack_share(kit):
    feather = next(n for n in nodes(kit["attack"]["effect"]) if n.get("name") == "league_rakan_a_feather"
                   and n.get("type") == "TargetProjectile")
    second = copy.deepcopy(feather)
    for ae in second["applied_effects"]:
        if ae["effect"]["type"] == "Attack":
            ae["effect"]["attack_ratio"] = W_PCT
    second["applied_effects"] = [ae for ae in second["applied_effects"] if ae["effect"]["type"] != "TargetSfx"]
    share = sw(DUO_W, {"type": "Combine", "effects": [
        {"type": "RemoveCasterBuff", "name": "league_rakan_duo_w"},
        {"type": "AddCasterBuff", "only_to_enemy": False,
         "buff_state": {"name": "league_rakan_duo_w", "duration": {"Time": {"tick": DUO_T}},
                        "attack_speed_mult": W_AS, "move_speed_mult": W_MS}},
        {"type": "Delayed", "tick": W_BLADE, "effects": [second]}]})
    kit["attack"]["effect"]["effects"].insert(0, share)


def e_rings(kit):
    e = kit["skill2"]["effect"]
    rings = [n for n in nodes(e) if n.get("type") == "RandomTarget" and n.get("casting_target") == "AllyNotSelf"]
    assert sorted(r["range"] for r in rings) == [25000, 50000, 90000], [r["range"] for r in rings]
    outer = next(r for r in rings if r["range"] == 90000)
    # the Combine holding the 90000 ring, and its "nobody found" branch (the shield on himself)
    holder = next(n for n in nodes(e) if n.get("type") == "Combine" and any(x is outer for x in n["effects"]))
    miss = next(x for x in holder["effects"] if x.get("type") == "SwitchByBuff" and x["buff_name"] == "league_rakan_e_got")
    alone = miss["effect_none"]
    ring = copy.deepcopy(outer)
    ring["range"] = DUO_R
    for n in nodes(ring):
        if n.get("type") == "MoveToTarget":
            n["range"] = DUO_R + 20000
    miss["effect_none"] = sw(DUO, {"type": "Combine", "effects": [
        ring, sw("league_rakan_e_got", NONE, copy.deepcopy(alone))]}, alone)
    # the line: on every ring (the new one too) his Xayah line while she is near
    n_lines = 0
    for r in [n for n in nodes(e) if n.get("type") == "RandomTarget" and n.get("casting_target") == "AllyNotSelf"]:
        for i, x in enumerate(r["effects"]):
            if x.get("type") == "Sfx" and x["name"] == "league_rakan_e_cast":
                r["effects"][i] = sw(DUO, {"type": "Sfx", "name": "league_rakan_e_xayah"}, x)
                n_lines += 1
    return n_lines


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def texts():
    path = os.path.join(MOD, "text", "champion.i18n")
    i18n = load(path)
    for lang, add in TEXT.items():
        d = i18n[lang]["description"]["league_rakan"]
        if not d["skill2"].endswith(add):
            d["skill2"] += add
        assert shown_length(d["skill2"]) <= TOOLTIP_MAX[lang], (lang, shown_length(d["skill2"]))
    save(path, i18n)


def sounds():
    save(os.path.join(MOD, "sound", "sfx", "league_rakan_e_xayah.sound_info"),
         {"plays": [{"delay": 0.0, "clip": "league_rakan_sfx_e", "volume": 0.6},
                    {"delay": 0.05, "clip": "league_rakan_vo_e_xayah", "volume": 0.9}]})
    ov = load(os.path.join(MOD, "mod.override_info"))
    for name in ("league_rakan_e_xayah", "league_rakan_vo_e_xayah"):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    kit = load(KIT)
    if a.check:
        print("patched" if patched(kit) else "not patched")
        sys.exit(0 if patched(kit) else 1)
    if patched(kit):
        print("already patched")
        return
    attack_share(kit)
    n = e_rings(kit)
    save(KIT, kit)
    texts()
    sounds()
    print(f"league_rakan: W share in the attack, E ring {DUO_R} behind the 90000 one, {n} E lines")


if __name__ == "__main__":
    main()
