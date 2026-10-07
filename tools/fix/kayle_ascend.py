"""Kayle's ascension shows (the user, 2026-10-08: 「天使可不可以在到达特定的等级变身呢？还有特效强化」 -> 「做第一种吧」).

    python tools/fix/kayle_ascend.py [league/champion/league_kayle.data_champion]

Her stages (Divine Ascent at levels 5, 8 and 12) are the `Permanent` caster buffs rank5 / rank8 / rank12 her level
probes add (and re-read every life). Idle, run, hit and death are picked by the engine, so the transformation is drawn
as wings riding on her (view_buffs, behind her, z -1) and the level-12 effects are swapped for bigger ones:
  1. the wings, one layer a stage, the three stacking as League's pairs do: rank5 -> wings1 (a pair of golden light wings
     down from the waist), rank8 -> wings2 (a pair of fire wings out from the shoulders), form3 -> wings3 (white-gold
     flame wings up past the head and a halo). rank12 already shows her permanent holy fire (`exalted`), so every
     `AddCasterBuff rank12` gets a `form3` beside it (a `Combine`; the same guard keeps both to one instance);
  2. at level 12 every projectile named bolt / wave / q_sword / e_bolt and every ViewEffect named bolt_hit / e_hit /
     q_blast / e_blast is wrapped in `SwitchByBuff rank12` that plays a copy named <name>_x (the projectiles' subtrees are
     2-7 nodes, so each tree grows by a dozen nodes);
  3. view entries for the new names on the sheet league_kayle_ascend (tools/art/import_kayle_ascend.py).
Run once: a kit that already has form3 is left as it is.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PATH = os.path.join(ROOT, "league", "champion", "league_kayle.data_champion")
ID = "league_kayle"
SHEET = "asset/league/effects/league_kayle_ascend"
PROJ = ("bolt", "wave", "q_sword", "e_bolt")
VIEWS = ("bolt_hit", "e_hit", "q_blast", "e_blast")
WINGS = {"rank5": "wings1", "rank8": "wings2", "form3": "wings3"}


def n(x):
    return f"{ID}_{x}"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else PATH
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    d = json.loads(raw)
    if n("form3") in raw:
        sys.exit(f"{path}: form3 is there already - left as it is")
    count = {"form3": 0, "proj": 0, "view": 0}

    def form3(node):
        return {"type": "Combine", "effects": [node, {"type": "AddCasterBuff", "buff_state": {
            "name": n("form3"), "duration": "Permanent"}, "only_to_enemy": False}]}

    def upgraded(node):
        x = copy.deepcopy(node)
        x["name"] = node["name"] + "_x"
        return {"type": "SwitchByBuff", "buff_name": n("rank12"), "effect_buff": x, "effect_none": node}

    def fix(node):
        """The node with its own subtree fixed first, then itself swapped when it is one of ours."""
        if isinstance(node, list):
            return [fix(v) for v in node]
        if not isinstance(node, dict):
            return node
        node = {k: fix(v) for k, v in node.items()}
        t, name = node.get("type", ""), node.get("name", "")
        if t == "AddCasterBuff" and node.get("buff_state", {}).get("name") == n("rank12"):
            count["form3"] += 1
            return form3(node)
        if t.endswith("Projectile") and name in [n(p) for p in PROJ]:
            count["proj"] += 1
            return upgraded(node)
        if t == "ViewEffect" and name in [n(v) for v in VIEWS]:
            count["view"] += 1
            return upgraded(node)
        return node

    for slot in ("attack", "skill", "skill2", "ult"):
        d[slot] = fix(d[slot])
    # an effect that `applied_effects` wraps is {casting_type, effect}: the swap above returns a SwitchByBuff in its
    # place, which is itself a plain effect, so the wrapping stays valid
    for key, names in (("view_projectiles", PROJ), ("view_effects", VIEWS)):
        base = {v["name"]: v for v in d[key]}
        for nm in names:
            v = copy.deepcopy(base[n(nm)])      # the base picture's z, follow and repeat
            v.update(name=n(nm + "_x"), anim=SHEET, tag=nm + "_x")
            d[key].append(v)
    d["view_buffs"] += [{"type": "Animated", "name": n(b), "anim": SHEET, "tag": w, "repeat": True, "z": -1}
                        for b, w in WINGS.items()]
    text = json.dumps(d, ensure_ascii=False, indent=2)
    if "\r\n" in raw:
        text = text.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text + ("\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""))
    print(path, count)


if __name__ == "__main__":
    main()
