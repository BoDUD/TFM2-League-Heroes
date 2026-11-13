"""Build the add-on's copy of Veigar from the main pack (Phenomenal Evil Power kept through death; the cage's edge).

    python addons/league_veigar_power/make_override.py

Copies league/champion/league_veigar.data_champion to addons/league_veigar_power/override/league_veigar.data_champion
with these changes:
  * passive = the add-on's league_veigar_power:keep, which puts back every ability power stack death clears
    (src/lib.rs), and the attack's tooltip (the passive) points to description.league_veigar_power.attack - the main
    text with its "lost on death" clause swapped for "kept (add-on)". Checks first that every stack the main pack adds
    is a Permanent league_veigar_p_stack carrying magic power only (the add-on copies the stacks it saw, whatever their
    amount);
  * E Event Horizon as League's (2026-11-14): only the cage's edge stuns. The two stun zones in the cage's landing
    (`e_zone`: the stun on every enemy unit; `e_zone_champ`: the sound, a stack and a hit in a row for a champion) are
    taken out and the native effect league_veigar_power:cage goes in their place; the passive's params carry the
    zones' numbers (cage_r, cage_t, stun, hit_t) and its code stuns whoever touches the circle. The zones are checked
    against what the code does in their stead (cage_edge below, the hits-in-a-row ladder played through); skill2's
    tooltip points to description.league_veigar_power.skill2, the main text with "touches it" swapped for the edge.
Run it again whenever the main pack's Veigar or his text changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_veigar_power")
MOD_ID = "league_veigar_power"
HERO = "league_veigar"
STACK = "league_veigar_p_stack"
# lang -> (the main pack's clause, the add-on's)
SWAP = {
    "zh-hans": ("死亡时清空。", "【扩展包】死后保留。"),
    "zh-hant": ("死亡時清空。", "【擴充包】死後保留。"),
    "en": ("Lost on death.", "[Add-on] Kept through death."),
    "ko": ("사망하면 사라집니다.", "[확장팩] 사망해도 유지됩니다."),
    "ja": ("デスで失う。", "【拡張】デスでも失わない。"),
}
# skill2 (E): lang -> (the main pack's words, the add-on's)
SWAP_E = {
    "zh-hans": ("碰到它的敌人", "【扩展包】碰到牢笼边缘的敌人（站在里面不动的不算）"),
    "zh-hant": ("碰到它的敵人", "【擴充包】碰到牢籠邊緣的敵人（站在裡面不動的不算）"),
    "en": ("each enemy that touches it", "[Add-on] each enemy that touches its edge (not one who stays inside)"),
    "ko": ("닿은 적을", "[확장팩] 가장자리에 닿은 적을(안에 가만히 있는 적은 제외)"),
    "ja": ("触れた敵を", "【拡張】縁に触れた敵を（中で動かない敵は除く）"),
}
N = HERO + "_"
CAGE = {"type": "Native", "effect_ref": f"{MOD_ID}:cage"}
# the skill details panel's limits (lint_mod.TOOLTIP_MAX)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def buff_states(node, out):
    if isinstance(node, dict):
        if node.get("type") in ("AddCasterBuff", "AddBuff"):
            out.append(node["buff_state"])
        for v in node.values():
            buff_states(v, out)
    elif isinstance(node, list):
        for v in node:
            buff_states(v, out)
    return out


def lists_with(node, name, out):
    """Every effect list holding the projectile `name`."""
    if isinstance(node, dict):
        for v in node.values():
            lists_with(v, name, out)
    elif isinstance(node, list):
        if any(isinstance(e, dict) and e.get("name") == name for e in node):
            out.append(node)
        for v in node:
            lists_with(v, name, out)
    return out


def play(node, flags, added):
    """The main pack's hits-in-a-row ladder run on a set of caster flags (the SwitchByBuff / Combine / add / remove it
    is made of); `added` collects the durations it adds."""
    t = node["type"]
    if t == "Combine":
        for e in node["effects"]:
            play(e, flags, added)
    elif t == "SwitchByBuff":
        play(node["effect_buff"] if node["buff_name"] in flags else node["effect_none"], flags, added)
    elif t == "RemoveCasterBuff":
        flags.discard(node["name"])
    elif t == "AddCasterBuff":
        b = node["buff_state"]
        if set(b) != {"name", "duration"}:
            sys.exit(f"a hit-in-a-row flag with fields: {b}: update src/lib.rs")
        flags.add(b["name"])
        added.add(b["duration"]["Time"]["tick"])
    else:
        sys.exit(f"{t} in the hits-in-a-row ladder: update this script")


def cage_edge(champion):
    """Take the two stun zones out of E's landing, put the native effect in; returns the passive's params."""
    lists = lists_with(champion["skill2"], N + "e_zone", [])
    if len(lists) != 1:
        sys.exit(f"E's stun zone found {len(lists)} times in skill2: update this script")
    effects = lists[0]
    zone = next(e for e in effects if isinstance(e, dict) and e.get("name") == N + "e_zone")
    champ = next((e for e in effects if isinstance(e, dict) and e.get("name") == N + "e_zone_champ"), None)
    if champ is None:
        sys.exit("no e_zone_champ beside e_zone: update this script")
    T = lambda e: {"casting_type": "Targeting", "effect": e}
    # what src/lib.rs does in their stead: the stun and its picture on every enemy unit ...
    shape, tick = zone["shape"], zone["tick"]
    if (zone["type"], zone["follow_caster"], zone["applied_target"]) != ("ApplyInProjectile", False, "EnemyWithoutTower") \
            or set(shape) != {"Circle"} or len(zone["applied_effects"]) != 2 \
            or zone["applied_effects"][0]["effect"].get("type") != "Stun" \
            or zone["applied_effects"][1] != T({"type": "ViewEffect", "name": N + "e_stun"}):
        sys.exit("e_zone is not the stun zone the add-on replaces: update this script and src/lib.rs")
    stun = zone["applied_effects"][0]["effect"]["duration"]
    # ... and for a champion the sound, a stack of the passive and one more hit in a row
    if (champ["type"], champ["follow_caster"], champ["applied_target"], champ["shape"], champ["tick"]) != \
            ("ApplyInProjectile", False, "EnemyChampion", shape, tick) or len(champ["applied_effects"]) != 2 \
            or champ["applied_effects"][0] != T({"type": "TargetSfx", "name": N + "e_stun"}):
        sys.exit("e_zone_champ is not the champion zone the add-on replaces: update this script and src/lib.rs")
    gain = champ["applied_effects"][1]["effect"]
    stack = {"type": "Combine", "effects": [
        {"type": "AddCasterBuff", "buff_state": {"name": STACK, "duration": "Permanent", "magic_power": 1},
         "only_to_enemy": False},
        {"type": "CasterViewEffect", "name": N + "p_gain"}]}
    if gain.get("type") != "Combine" or len(gain["effects"]) != 2 or gain["effects"][0] != stack:
        sys.exit("the cage's stack on a champion changed: update this script and src/lib.rs")
    ladder, durations = gain["effects"][1], set()
    flag = lambda k: f"{N}r_s{k}"
    for have in range(5):
        flags = {flag(k) for k in range(1, have + 1)}
        play(ladder, flags, durations)
        if flags != {flag(k) for k in range(1, min(have + 1, 4) + 1)}:
            sys.exit(f"the hits-in-a-row ladder from {have} gives {sorted(flags)}: update src/lib.rs (next_hits)")
    if len(durations) != 1:
        sys.exit(f"the hits-in-a-row flags last {sorted(durations)}: update src/lib.rs")
    at = effects.index(zone)
    effects[:] = [e for e in effects if e is not zone and e is not champ]
    effects.insert(at, dict(CAGE))
    return {"cage_r": shape["Circle"]["radius"], "cage_t": tick, "stun": stun, "hit_t": durations.pop()}


def main():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if "passive" in champion:
        sys.exit("the main pack's Veigar has a passive now: update this script")
    stacks = [b for b in buff_states([champion[s] for s in ("attack", "skill", "skill2", "ult")], []) if b["name"] == STACK]
    if not stacks:
        sys.exit(f"no {STACK} in the main pack: update src/lib.rs")
    for b in stacks:
        if b.get("duration") != "Permanent" or set(b) != {"name", "duration", "magic_power"}:
            sys.exit(f"{STACK} is {b} in the main pack: the add-on expects Permanent magic power stacks")
    params = cage_edge(champion)
    champion["passive"] = {"passive_ref": f"{MOD_ID}:keep", "params": params}
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.attack"
    champion["skill2"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.skill2"

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, (old, new) in SWAP.items():
        attack = main_text[lang]["description"][HERO]["attack"]
        if attack.count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update SWAP")
        texts[lang] = attack.replace(old, new)
    texts_e = {}
    for lang, (old, new) in SWAP_E.items():
        skill2 = main_text[lang]["description"][HERO]["skill2"]
        if skill2.count(old) != 1:
            sys.exit(f"{lang}: the main pack's E text changed ({old!r} not found once): update SWAP_E")
        texts_e[lang] = skill2.replace(old, new)
    long = {f"{lang}.{k}": shown_length(t) for k, d in (("attack", texts), ("skill2", texts_e)) for lang, t in d.items()
            if shown_length(t) > TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    missing = (set(main_text) - set(texts)) | (set(main_text) - set(texts_e))
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang], "skill2": texts_e[lang]}}}
                            for lang in main_text}, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(params), "-", len(stacks), "stack adds checked")
    print("tooltip lengths", {lang: f"{shown_length(t)}/{TOOLTIP_MAX[lang]}" for lang, t in texts.items()},
          "E", {lang: f"{shown_length(t)}/{TOOLTIP_MAX[lang]}" for lang, t in texts_e.items()})


if __name__ == "__main__":
    main()
