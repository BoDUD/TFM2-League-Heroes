"""Build the add-on's copy of Aatrox from the main pack (League's Infernal Chains, v0.2).

    python addons/league_aatrox_chain/make_override.py

Reads league/champion/league_aatrox.data_champion and league/text/champion.i18n and writes
addons/league_aatrox_chain/override/league_aatrox.data_champion and .../text/champion.i18n:
the same kit with W's chain handed to the add-on. The add-on decides (which unit is chained, when it breaks free,
the pull to the ring's centre) and leaves flags on Aatrox; everything seen or dealt stays in data, read from those
flags (v0.1 played the ring and dealt the second hit natively, and none of it showed in the game):
  * the chain's hit (LinearProjectile league_aatrox_w_chain, on the first enemy it meets) calls
    league_aatrox_chain:chain on that unit, then
      w_minion -> the hit once more (League: double to minions),
      w_champ  -> the first hit's extras on a champion (E's heal, the passive's IOU, World Ender's kill mark),
      and READ_AT ticks later w_pull -> the second hit + the chains wrapping the target (w_yank),
                                w_pull_c -> the second hit's extras on a champion;
  * the chain's end (its stop: the ring's centre) plays the ring when w_tether is set, and at READ_AT the snap
    (w_snap) when w_pull is;
  * the main pack's champion branch (a search for a champion beside the chain, which also finds one behind the
    minion that stopped it: the w_champ mark, the extras and the second hit with its Pull toward Aatrox) and its ring
    are dropped; the nodes above are copied from them;
  * a view entry for the links the add-on flies to the ring's centre (league_aatrox_w_link, main pack's sheet);
  * W's tooltip points to description.league_aatrox_chain.skill2 (League's rules, with a "W chain test build" lead,
    so the tooltip in game shows whether the override took).
The flag names and READ_AT are read from src/lib.rs. Every other champion stays untouched. Run it again whenever
the main pack's Aatrox changes.
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_aatrox_chain")
MOD_ID = "league_aatrox_chain"
HERO = "league_aatrox"
TEXT_KEY = "description.league_aatrox_chain.skill2"
FX = "asset/league/effects/league_aatrox_fx"
AD = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
O, R, Y, E = "<#ff9028ff>", "<#ef5350ff>", "<#ffb900ff>", "<>"
# the skill details panel's limits (lint_mod.TOOLTIP_MAX)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def texts(c):
    dmg = f"{O}{c['W_DMG']}{E} + {AD}{O}{c['W_RATIO']}%{E}"
    s = f"{c['HOLD'] / 60:g}"
    return {
        "zh-hans": f"【W锁链测试版】甩出锁链，第一个敌人受到{dmg}物理伤害并{R}减速{c['SLOW']}%{E}（小兵双倍伤害）；英雄或野怪"
                   f"被锁在原地{Y}{s}秒{E}：走出圈锁链就断，没走出就被{R}拖回圈中心{E}再受一次伤害。",
        "zh-hant": f"【W鎖鏈測試版】甩出鎖鏈，第一個敵人受到{dmg}物理傷害並{R}緩速{c['SLOW']}%{E}（小兵雙倍傷害）；英雄或野怪"
                   f"被鎖在原地{Y}{s}秒{E}：走出圈鎖鏈就斷，沒走出就被{R}拖回圈中心{E}再受一次傷害。",
        "en": f"[W chain test build] Aatrox fires a chain: the first enemy hit takes {dmg} {O}physical damage{E} (double to "
              f"minions) and is {R}slowed by {c['SLOW']}%{E}; a champion or monster is chained to the spot for {Y}{s}s{E}: "
              f"leaving the ring breaks the chain, otherwise it is {R}pulled back to its centre{E} and hit again.",
        "ko": f"[W 사슬 테스트판] 사슬을 던져 처음 맞은 적에게 {dmg} {O}물리 피해{E}(미니언 2배)와 {R}{c['SLOW']}% 둔화{E}; "
              f"챔피언이나 몬스터는 {Y}{s}초{E} 동안 그 자리에 묶입니다: 범위를 벗어나면 사슬이 끊기고, 아니면 "
              f"{R}중심으로 끌려와{E} 다시 피해를 입습니다.",
        "ja": f"【W鎖テスト版】鎖を放ち最初の敵に{dmg}の{O}物理ダメージ{E}（ミニオンには2倍）と{R}{c['SLOW']}%スロウ{E}。"
              f"チャンピオンとモンスターは{Y}{s}秒{E}その場に繋がれ、範囲外に出れば鎖が切れ、出なければ{R}中心へ引き戻され{E}"
              f"再びダメージ。",
    }


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def consts():
    """The flag names and timings src/lib.rs uses."""
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        src = f.read()
    out = {}
    m = re.search(r"pub const HOLD: usize = ([0-9_]+);", src)
    k = re.search(r"pub const READ_AT: usize = HOLD \+ ([0-9]+);", src)
    if not m or not k:
        sys.exit("no HOLD / READ_AT in src/lib.rs: update this script")
    out["HOLD"] = int(m.group(1).replace("_", ""))
    out["READ_AT"] = out["HOLD"] + int(k.group(1))
    for name in ("TETHER", "CHAMP", "MINION", "PULL", "PULL_C"):
        m = re.search(r'pub const %s: &str = "([a-z_]+)";' % name, src)
        if not m:
            sys.exit("no %s in src/lib.rs: update this script" % name)
        out[name] = m.group(1)
    return out


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def inner(entry):
    """A projectile's applied effect is {casting_type, effect}."""
    return entry.get("effect", entry) if isinstance(entry, dict) else entry


def on(flag_name, effects):
    """The effects when Aatrox carries the flag (SwitchByBuff reads the caster's buffs)."""
    return {"type": "SwitchByBuff", "buff_name": flag_name, "effect_buff": {"type": "Combine", "effects": effects},
            "effect_none": {"type": "Combine", "effects": []}}


def used(flag_name):
    return {"type": "RemoveCasterBuff", "name": flag_name}


def targeting(effect):
    return {"casting_type": "Targeting", "effect": effect}


def one(nodes, what):
    if len(nodes) != 1:
        sys.exit("expected one %s in the main pack's W, found %d: update this script" % (what, len(nodes)))
    return nodes[0]


def main():
    c = consts()
    src = os.path.join(ROOT, "league", "champion", HERO + ".data_champion")
    with open(lp(src), encoding="utf-8") as f:
        champion = json.load(f)
    w = champion["skill2"]
    chain = one([n for n in walk(w) if n.get("type") == "LinearProjectile" and n.get("name") == HERO + "_w_chain"],
                "chain projectile")
    applied = chain["applied_effects"]
    effects = [inner(e) for e in applied]
    hit = one([e for e in effects if e.get("type") == "Attack"], "chain hit")
    slow = one([e for e in effects if e.get("type") == "AddBuff" and e["buff_state"]["name"] == HERO + "_w_slowed"],
               "slow")
    if slow["buff_state"]["duration"]["Time"]["tick"] != c["HOLD"]:
        sys.exit("W's slow does not last HOLD (%d) ticks any more: update src/lib.rs" % c["HOLD"])
    c.update(W_DMG=hit["damage"], W_RATIO=hit["attack_ratio"], SLOW=-slow["buff_state"]["move_speed_mult"])

    # the main pack's champion branch: the w_champ mark, the first hit's extras, the second hit (a Delayed with Pull)
    pick = one([e for e in effects if e.get("type") == "RandomTarget" and e.get("casting_target") == "EnemyChampion"],
               "champion branch")
    branch = pick["effects"]
    second = one([e for e in branch if e.get("type") == "Delayed" and any(n.get("type") == "Pull" for n in walk(e))],
                 "second hit")
    mark = one([e for e in branch if e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == HERO + "_w_champ"],
               "w_champ mark")
    first_extras = [copy.deepcopy(e) for e in branch if e is not second and e is not mark]
    if len(first_extras) != 3 or HERO + "_p_lw\"" not in json.dumps(first_extras):
        sys.exit("the first hit's extras changed shape (heal, passive IOU p_lw, kill mark): update this script")
    picture = {HERO + "_w_yank"}
    second_hit = [copy.deepcopy(e) for e in second["effects"]
                  if e.get("type") == "Attack" or (e.get("type") in ("ViewEffect", "TargetSfx") and e["name"] in picture)]
    second_extras = [copy.deepcopy(e) for e in second["effects"]
                     if e.get("type") not in ("Attack", "Pull", "ViewEffect", "TargetSfx")]
    if len(second_hit) != 3 or len(second_extras) != 3 or HERO + "_p_lw2" not in json.dumps(second_extras):
        sys.exit("the second hit changed shape (Attack, w_yank picture and sound; heal, IOU p_lw2, kill mark)")

    # the main pack's ring at the chain's stop: its picture and sound, the snap
    ring = one([e for e in chain["end_effects"] if HERO + "_w_ring" in json.dumps(e)], "ring at the chain's stop")
    ring_nodes = [copy.deepcopy(n) for n in walk(ring) if n.get("type") in ("ViewEffect", "Sfx")]
    snap = [n for n in ring_nodes if n["name"] == HERO + "_w_snap"]
    ring_pic = [n for n in ring_nodes if n["name"] == HERO + "_w_ring"]
    if len(snap) != 1 or len(ring_pic) != 2:
        sys.exit("the ring's picture/sound/snap changed shape: update this script")

    # the new W: the add-on on the unit the chain hit, then the data reading its flags
    at = applied.index(next(e for e in applied if inner(e) is slow)) + 1
    applied.insert(at, targeting({"type": "Native", "effect_ref": MOD_ID + ":chain"}))
    applied.remove(next(e for e in applied if inner(e) is pick))
    applied += [
        targeting(on(c["MINION"], [used(c["MINION"]), copy.deepcopy(hit)])),
        targeting(on(c["CHAMP"], [used(c["CHAMP"])] + first_extras)),
        targeting({"type": "Delayed", "tick": c["READ_AT"], "effects": [on(c["PULL"], second_hit)]}),
        targeting({"type": "Delayed", "tick": c["READ_AT"], "effects": [on(c["PULL_C"], second_extras)]}),
    ]
    chain["end_effects"] = [e for e in chain["end_effects"] if e is not ring] + [
        {"type": "Delayed", "tick": 1, "effects": [on(c["TETHER"], [used(c["TETHER"])] + ring_pic)]},
        {"type": "Delayed", "tick": c["READ_AT"], "effects": [on(c["PULL"], snap)]},
    ]
    left = json.dumps(w)
    if '"type": "Pull"' in left or '"type": "RandomTarget"' in left:
        sys.exit("the main pack's pull toward Aatrox or its champion search is still in W: update this script")

    # the links the add-on flies (a tag in the main pack's sheet, tools/art/import_aatrox.py)
    if HERO + "_w_link" not in {v["name"] for v in champion["view_projectiles"]}:
        champion["view_projectiles"].append({"type": "Animated", "name": HERO + "_w_link", "anim": FX, "tag": "w_link",
                                             "repeat": True, "z": 1})
    champion["skill2"]["description"] = "#asset/base/text/champion?" + TEXT_KEY

    text_by_lang = texts(c)
    long = {lang: shown_length(t) for lang, t in text_by_lang.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(text_by_lang)
    if missing:
        sys.exit("no W chain text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"skill2": text_by_lang[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT),
          "- W's tether, break and pull in %s, its pictures and hits on the flags at %d" % (MOD_ID, c["READ_AT"]))


if __name__ == "__main__":
    main()
