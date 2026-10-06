"""Build the add-on's copy of Kayn from the main pack (The Darkin Scythe as in League) and its range table.

    python addons/league_kayn_form/make_override.py [--game <TFM2 folder>]

Reads league/champion/league_kayn.data_champion, league/text/champion.i18n, every league/champion/*.data_champion
and the base game's champion sheet (bundle.game_data: asset/base/setting/champion_info) and writes
  * addons/league_kayn_form/override/league_kayn.data_champion: the same kit with three changes -
      - each of the main pack's charge blocks (a Combine opening with the no-op marker RemoveCasterBuff
        league_kayn_mk_charge: Q's spin, W's near and far lines, R's exit) becomes an AddBuff league_kayn_tag
        (30 ticks) on the champion hit, and the attack's champion twin tags too;
      - the attack starts by playing the main pack's transformation when the add-on's ready flag is on
        (league_kayn_ready_d / _s: the main pack's own transform block, plus removing the flag);
      - passive = the add-on's passive league_kayn_form:orbs {darkin_need, shadow_need}, which counts the tags by the
        champion's attack range (melee -> Darkin, ranged -> Shadow Assassin), sets the ready flag for the first full
        side and keeps the form for the rest of the match (death included);
    and the attack's tooltip points to description.league_kayn_form.attack: the main text with the charge rule
    (between the invisible markers <#fffffffe><> ... <#ffffffff><>) swapped for League's rule;
  * addons/league_kayn_form/text/champion.i18n: that text in every language;
  * addons/league_kayn_form/src/ranges.rs: every base and pack champion's attack range.
Run it again whenever the main pack's Kayn or any pack hero's attack range changes.
"""
import argparse
import copy
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kayn_form")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
MOD_ID = "league_kayn_form"
TEXT_KEY = "description.league_kayn_form.attack"
MARK = "league_kayn_mk_charge"
TAG = "league_kayn_tag"
TAG_T = 30
NEED = {"darkin_need": 14, "shadow_need": 14}     # tried 25, 40, 30; back to 14 (the user, 2026-10-06: 「还是全部调成14次吧 不然打野太慢了」)
MK1, MK2 = "<#fffffffe><>", "<#ffffffff><>"
Y, R, B, E = "<#ffb900ff>", "<#fe5c50ff>", "<#8484fbff>", "<>"
RULE = {
    "zh-hans": "【附加包·照英雄联盟】打中近战英雄攒" + R + "暗裔" + E + "、打中远程英雄攒" + B + "影流" + E + "（各" + Y + "{n}" + E +
               "次），先满的变身，整局保留",
    "zh-hant": "【附加包·照英雄聯盟】打中近戰英雄累積" + R + "闇裔" + E + "、打中遠程英雄累積" + B + "影流" + E + "（各" + Y + "{n}" + E +
               "次），先滿的變身，整局保留",
    "en": "[Add-on, as League] melee champion hits charge the " + R + "Darkin" + E + ", ranged ones the " + B + "Shadow" + E +
          " (" + Y + "{n}" + E + " each); the first full one stays his form all match",
    "ko": "[확장팩·LoL처럼] 근거리 챔피언 적중은 " + R + "다르킨" + E + ", 원거리는 " + B + "그림자 암살자" + E + " 충전(각 " + Y + "{n}" + E +
          "), 먼저 차는 쪽으로 변신해 게임 끝까지 유지",
    "ja": "【拡張・LoL準拠】近接チャンピオン命中で" + R + "ダーキン" + E + "、遠隔で" + B + "暗殺者" + E + "（各" + Y + "{n}" + E +
          "）が溜まり、先に満ちた方に変身し試合中ずっと維持",
}
# the skill details panel's limits (lint_mod.TOOLTIP_MAX)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def load(path):
    with open(lp(path), encoding="utf-8-sig") as f:
        return json.load(f)


def write(path, text):
    os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
    with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def tag():
    return {"type": "AddBuff", "buff_state": {"name": TAG, "duration": {"Time": {"tick": TAG_T}}}}


def is_charge(node):
    return (isinstance(node, dict) and node.get("type") == "Combine" and node.get("effects")
            and node["effects"][0] == {"type": "RemoveCasterBuff", "name": MARK})


def swap_charges(node, counts):
    """Every charge block -> a tag on the champion hit."""
    items = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else []
    for key, value in list(items):
        if is_charge(value):
            node[key] = tag()
            counts["charges"] += 1
        else:
            swap_charges(value, counts)


def find(node, pred):
    if pred(node):
        return node
    items = node.values() if isinstance(node, dict) else node if isinstance(node, list) else []
    for v in items:
        hit = find(v, pred)
        if hit is not None:
            return hit
    return None


def transform_block(champion, form):
    """The main pack's transformation for `form`: the Combine that adds the Permanent league_kayn_form_<form>."""
    buff = f"league_kayn_form_{form}"

    def pred(n):
        return (isinstance(n, dict) and n.get("type") == "Combine" and any(
            isinstance(e, dict) and e.get("type") == "AddCasterBuff" and e["buff_state"].get("name") == buff
            and e["buff_state"].get("duration") == "Permanent" for e in n.get("effects", [])))
    for slot in ("attack", "skill", "skill2", "ult"):
        hit = find(champion[slot], pred)
        if hit is not None:
            return copy.deepcopy(hit)
    sys.exit(f"no transformation into {buff} in the main pack: update this script")


def ranges(game):
    """name -> attack range: the base game's sheet (incl. its data champions) and this pack's heroes."""
    import bundle_tool as B
    b = B.Bundle(B.find_game_dir(game))
    sheet = b.read_json("asset/base/setting/champion_info")
    out = {k: v["attack"]["range"] for k, v in sheet.items() if isinstance(v, dict) and "attack" in v}
    for c in sheet.get("mod_champions", []):
        out[c["id"]] = c["attack"]["range"]
    for path in sorted(glob.glob(os.path.join(ROOT, "league", "champion", "*.data_champion"))):
        c = load(path)
        out[c["id"]] = c["attack"]["range"]
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", help="Teamfight Manager 2 folder (default: the usual Steam places)")
    a = ap.parse_args()
    champion = load(os.path.join(ROOT, "league", "champion", "league_kayn.data_champion"))
    if "passive" in champion:
        sys.exit("the main pack's Kayn has a passive now: update this script")
    blocks = {f: transform_block(champion, f) for f in ("d", "s")}
    counts = {"charges": 0}
    for slot in ("attack", "skill", "skill2", "ult"):
        swap_charges(champion[slot], counts)
    if counts["charges"] != 4:
        sys.exit("expected 4 charge blocks (Q spin, W near, W far, R exit), found %d: update this script" % counts["charges"])
    kit = json.dumps([champion[slot] for slot in ("attack", "skill", "skill2", "ult")])
    left = re.findall(r'"name": "league_kayn_(?:dc|sc)\d+", "duration": "Permanent"', kit)
    if left:
        sys.exit("charge steps still added after the swap: %s" % left)
    twin = find(champion["attack"], lambda n: isinstance(n, dict) and n.get("name") == "league_kayn_atk_twin")
    if twin is None:
        sys.exit("no champion twin on the attack: update this script")
    twin["applied_effects"].append({"casting_type": "Targeting", "effect": tag()})
    ready = []
    for f in ("d", "s"):
        flag = f"league_kayn_ready_{f}"
        ready.append({"type": "SwitchByBuff", "buff_name": flag,
                      "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": flag}, blocks[f]]},
                      "effect_none": {"type": "Combine", "effects": []}})
    eff = champion["attack"]["effect"]
    if eff.get("type") != "Combine":
        sys.exit("the attack's effect is not a Combine: update this script")
    eff["effects"][:0] = ready
    champion["passive"] = {"passive_ref": MOD_ID + ":orbs", "params": NEED}
    champion["attack"]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    # the Shadow Step through a wall (src/wall.rs, src/lib.rs): the passive puts league_kayn_in_wall{,_d,_s} on him
    # while he stands in a wall cell (the shroud, looping over him) and plays league_kayn_wall_burst{,_d,_s} as he goes
    # in and comes out; their pictures are in the main pack's league_kayn_fx (tools/art/import_kayn.py --wall), bound
    # here only: nothing in the main pack's data uses them
    fx = "asset/league/effects/league_kayn_fx"
    for suf in ("", "_d", "_s"):
        champion["view_buffs"].append({"type": "Animated", "name": f"league_kayn_in_wall{suf}", "anim": fx,
                                       "tag": f"wall_aura{suf}", "z": 1})
        champion["view_effects"].append({"type": "Animation", "name": f"league_kayn_wall_burst{suf}", "anim": fx,
                                         "tag": f"wall_burst{suf}", "z": 1, "is_follow": False})

    main_text = load(os.path.join(ROOT, "league", "text", "champion.i18n"))
    text, long = {}, {}
    for lang in main_text:
        if lang not in RULE:
            sys.exit("no add-on rule text for %s" % lang)
        base = main_text[lang]["description"]["league_kayn"]["attack"]
        if base.count(MK1) != 1 or base.count(MK2) != 1:
            sys.exit(f"{lang}: the charge rule markers are missing from the main text: update setup_kayn / this script")
        i, j = base.index(MK1), base.index(MK2) + len(MK2)
        t = base[:i] + MK1 + RULE[lang].format(n=NEED["darkin_need"]) + MK2 + base[j:]
        if shown_length(t) > TOOLTIP_MAX[lang]:
            long[lang] = shown_length(t)
        text[lang] = {"description": {MOD_ID: {"attack": t}}}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_kayn.data_champion")
    write(out, json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    write(os.path.join(ADDON, "text", "champion.i18n"), json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    table = ranges(a.game)
    rs = ["//! Attack range of every champion the add-on knows, by champion id (generated by make_override.py from the base",
          "//! game's champion sheet and this pack's league/champion/*.data_champion - do not edit by hand).",
          "", "pub const RANGES: &[(&str, u32)] = &["]
    rs += [f'    ("{k}", {v}),' for k, v in table.items()]
    rs += ["];", ""]
    write(os.path.join(ADDON, "src", "ranges.rs"), "\n".join(rs))
    ranged = sum(1 for v in table.values() if v >= 35000)
    print("wrote override, text and ranges.rs:", counts["charges"], "charge blocks tagged, ready checks on the attack,",
          len(table), "champions (", ranged, "ranged )")


if __name__ == "__main__":
    main()
