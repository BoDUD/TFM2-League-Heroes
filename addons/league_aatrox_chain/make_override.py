"""Build the add-on's copy of Aatrox from the main pack (League's Infernal Chains).

    python addons/league_aatrox_chain/make_override.py

Reads league/champion/league_aatrox.data_champion and league/text/champion.i18n and writes
addons/league_aatrox_chain/override/league_aatrox.data_champion and .../text/champion.i18n:
the same kit with W's chain handed to the add-on -
  * the chain's hit (LinearProjectile league_aatrox_w_chain, applied to the first enemy it meets) also calls
    league_aatrox_chain:chain on that unit: a champion or monster is chained (the ring, the links, the pull to the
    ring's centre and the second hit at 1.5 s, or nothing when it leaves the ring first), a minion takes the
    damage once more (League: double to minions); a champion also gives the hit's extras (E's heal, the passive's
    IOU, World Ender's kill mark) - the add-on knows which unit the chain really hit;
  * the main pack's champion branch (a search for a champion beside the chain, which also finds one behind the
    minion that stopped it: the w_champ mark, the hit's extras and the second hit with its Pull) and the ring it
    lays at the impact point (the chain's end_effects) are dropped, so nobody else is hit or pulled;
  * view entries for the add-on's pictures, from the main pack's effect sheets: league_aatrox_w_link (a chain link
    flying to the ring's centre), league_aatrox_w_ring_in / league_aatrox_w_ring_beat (the ring, replayed while the
    chain holds);
  * W's tooltip points to description.league_aatrox_chain.skill2 (League's rules, with a "W chain test build" lead,
    so the tooltip in game shows whether the override took).
The numbers the add-on repeats (W damage, the 1.5 s, E's heal on a W hit, the passive's IOU, the kill mark) are
read from src/lib.rs and checked against the kit. Every other champion stays untouched. Run it again whenever the main
pack's Aatrox changes.
"""
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
BIG = "asset/league/effects/league_aatrox_big"
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
    """The numbers src/lib.rs repeats from the kit."""
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        src = f.read()
    out = {}
    for name in ("W_DMG", "W_RATIO", "HOLD", "E_HEAL_AMOUNT", "E_HEAL_RATIO", "E_HEAL_R_AMOUNT", "E_HEAL_R_RATIO",
                 "PC_HOLD", "K_HOLD"):
        m = re.search(r"pub const %s: usize = ([0-9_]+);" % name, src)
        if not m:
            sys.exit("no %s in src/lib.rs: update this script" % name)
        out[name] = int(m.group(1).replace("_", ""))
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


def main():
    c = consts()
    src = os.path.join(ROOT, "league", "champion", HERO + ".data_champion")
    with open(lp(src), encoding="utf-8") as f:
        champion = json.load(f)
    w = champion["skill2"]
    chains = [n for n in walk(w) if n.get("type") == "LinearProjectile" and n.get("name") == HERO + "_w_chain"]
    if len(chains) != 1:
        sys.exit("expected one W chain projectile, found %d: update this script" % len(chains))
    chain = chains[0]
    applied = chain["applied_effects"]
    effects = [inner(e) for e in applied]

    # the kit's numbers the add-on repeats
    hits = [e for e in effects if e.get("type") == "Attack"]
    if len(hits) != 1 or (hits[0]["damage"], hits[0]["attack_ratio"]) != (c["W_DMG"], c["W_RATIO"]):
        sys.exit("W's hit is not %d + %d%% AD any more: update src/lib.rs" % (c["W_DMG"], c["W_RATIO"]))
    slows = [e for e in effects if e.get("type") == "AddBuff" and e["buff_state"]["name"] == HERO + "_w_slowed"]
    if len(slows) != 1 or slows[0]["buff_state"]["duration"]["Time"]["tick"] != c["HOLD"]:
        sys.exit("W's slow does not last HOLD (%d) ticks any more: update src/lib.rs" % c["HOLD"])
    c["SLOW"] = -slows[0]["buff_state"]["move_speed_mult"]
    kit = json.dumps(champion)
    for name, tick in (("pc1", c["PC_HOLD"]), ("k_b", c["K_HOLD"])):
        if not re.search(r'"name": "%s_%s", "duration": \{"Time": \{"tick": %d\}\}' % (HERO, name, tick), kit):
            sys.exit("%s_%s no longer lasts %d ticks: update src/lib.rs" % (HERO, name, tick))

    # the champion branch: the w_champ mark, the hit's extras (E's heal, the passive's IOU, the kill mark) and the
    # second hit (a Delayed with the Pull) - all of it moves into the add-on
    picks = [e for e in effects if e.get("type") == "RandomTarget" and e.get("casting_target") == "EnemyChampion"]
    if len(picks) != 1:
        sys.exit("expected one champion branch on the chain's hit, found %d: update this script" % len(picks))
    branch = picks[0]["effects"]
    second = [e for e in branch if e.get("type") == "Delayed" and any(n.get("type") == "Pull" for n in walk(e))]
    marks = [e for e in branch if e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == HERO + "_w_champ"]
    amps = [e for e in branch if e.get("type") == "SwitchByBuff" and e.get("buff_name") == HERO + "_r"
            and e["effect_buff"].get("type") == "Heal"]
    owes = [e for e in branch if e.get("type") == "RangeEffect" and HERO + "_p_lw" in json.dumps(e)]
    kills = [e for e in branch if e.get("type") == "SwitchByBuff" and HERO + "_k_b" in json.dumps(e)]
    if [len(second), len(marks), len(amps), len(owes), len(kills)] != [1] * 5 or len(branch) != 5:
        sys.exit("the main pack's champion branch changed shape: update this script and src/lib.rs")
    amp = amps[0]
    heal = [(h["amount"], h["attack_ratio"]) for h in (amp["effect_none"], amp["effect_buff"])]
    if heal != [(c["E_HEAL_AMOUNT"], c["E_HEAL_RATIO"]), (c["E_HEAL_R_AMOUNT"], c["E_HEAL_R_RATIO"])]:
        sys.exit("E's heal on a W hit is %s now: update src/lib.rs" % heal)
    applied.remove(next(e for e in applied if inner(e) is picks[0]))
    # the ring at the impact point
    rings = [e for e in chain["end_effects"] if HERO + "_w_ring" in json.dumps(e)]
    if len(rings) != 1:
        sys.exit("the main pack's ring at the impact point changed shape: update this script")
    chain["end_effects"] = [e for e in chain["end_effects"] if e is not rings[0]]
    # the add-on on the unit the chain hit, after the slow (the add-on finds a slowed unit when given a position)
    at = applied.index(next(e for e in applied if inner(e) is slows[0])) + 1
    applied.insert(at, {"casting_type": "Targeting", "effect": {"type": "Native", "effect_ref": MOD_ID + ":chain"}})
    left = json.dumps(w)
    for gone in ('"type": "Pull"', HERO + "_w_champ\", \"duration", HERO + "_w_ring", HERO + "_w_snap", HERO + "_w_yank"):
        if gone in left:
            sys.exit("%s is still in W after the swap: update this script" % gone)

    # the add-on's pictures (tags in the main pack's sheets, tools/art/import_aatrox.py)
    views_p = {v["name"] for v in champion["view_projectiles"]}
    if HERO + "_w_link" not in views_p:
        champion["view_projectiles"].append({"type": "Animated", "name": HERO + "_w_link", "anim": FX, "tag": "w_link",
                                             "repeat": True, "z": 1})
    views_e = {v["name"] for v in champion["view_effects"]}
    for tag in ("w_ring_in", "w_ring_beat"):
        if HERO + "_" + tag not in views_e:
            champion["view_effects"].append({"type": "Animation", "name": HERO + "_" + tag, "anim": BIG, "tag": tag,
                                             "z": -1, "is_follow": False})
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
          "- W's second hit and ring handed to %s:chain" % MOD_ID)


if __name__ == "__main__":
    main()
