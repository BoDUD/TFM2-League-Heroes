"""Build the add-on's copies from the main pack (effects that ask whether the target carries a mark).

    python addons/league_marks/make_override.py [--check]

Reads the main pack's kits and writes addons/league_marks/override/<hero>.data_champion and .../text/champion.i18n:
  * league_kennen: every Mark of the Storm hit marks the champion with KENNEN_HIT instead of reading and counting his
    own flags (the add-on counts per target and stuns on the third); passive league_marks:kennen;
  * league_kaisa: the four Plasma ladders on her own flags become KAISA_ATTACK / KAISA_CC / KAISA_W2 / KAISA_W3 marks
    on the champion struck (the add-on counts per target, deals the extra hits and the pop with the main pack's
    numbers, read here into passive.params); passive league_marks:kaisa;
  * league_lux: the skills' Illumination lands on the struck enemy (LUX_LIT), the attack fires the plain bolt marking
    its target (LUX_HIT; the add-on ignites a lit one with the main pack's numbers); passive league_marks:lux;
  * league_missfortune: the attack asks MF_ASK on its target and fires two ticks later, the Love Tap bullet on MF_NEW
    (the add-on raises it when the target is not her last); passive league_marks:missfortune;
  * league_diana: Lunar Rush's start no longer reads her own league_diana_moonlight (any Q hit); it marks its target
    with src/lib.rs's DIANA_ASK and, 2 ticks later, reads DIANA_YES (the add-on raises it when that target carries Q's
    league_diana_moon_mark) to queue the second dash (league_diana_e_again, as the main pack); passive league_marks:diana.
Changed tooltips point to description.league_marks.<name>_<slot>. Run it again whenever one of them changes in the main
pack (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_marks")
MOD_ID = "league_marks"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
M, E, Y = "<#a974ffff>", "<>", "<#ffb900ff>"
TEXT = {
    ("league_diana", "skill2"): {
        "zh-hans": ("有" + M + "月光" + E + "时立刻再冲一次（优先英雄）", "目标带" + M + "月光" + E + "时再冲一次"),
        "zh-hant": ("有" + M + "月光精華" + E + "時立刻再衝一次（優先英雄）", "目標帶" + M + "月光精華" + E + "時再衝一次"),
        "en": ("with " + M + "Moonlight" + E + " up she dashes", "if the target bears " + M + "Moonlight" + E + " she dashes"),
        "ko": (M + "달빛" + E + "이 있으면", "대상에게 " + M + "달빛" + E + "이 있으면"),
        "ja": (M + "月光" + E + "があれば", "対象に" + M + "月光" + E + "があれば"),
    },
    ("league_kennen", "attack"): {
        "zh-hans": ("第三层", "同一人第三层"), "zh-hant": ("第三層", "同一人第三層"),
        "en": ("the third mark", "the third on one champion"), "ko": ("세 번째 표식은", "한 챔피언의 세 번째 표식은"),
        "ja": ("3つ目で", "同じ相手に3つ目で"),
    },
    ("league_missfortune", "attack"): {
        "zh-hans": ("（她击杀上一个目标后，或" + Y + "1.25秒" + E + "没开枪后）", "（换了目标就算）"),
        "zh-hant": ("（她擊殺上一個目標後，或" + Y + "1.25秒" + E + "沒開槍後）", "（換了目標就算）"),
        "en": (" (after she kills her last one, or when she has not fired for " + Y + "1.25s" + E + ")", " (any target other than her last)"),
        "ko": ("(직전 대상을 처치했거나 " + Y + "1.25초" + E + " 동안 쏘지 않았을 때)", "(직전 대상이 아니면)"),
        "ja": ("（前の対象を倒した後か、" + Y + "1.25秒" + E + "撃っていない時）", "（前の対象と違えば）"),
    },
    ("league_lux", "attack"): {
        "zh-hans": ("技能命中敌人后" + Y + "5秒" + E + "内，下一次普攻引爆光芒", "技能命中的敌人带光芒" + Y + "5秒" + E + "，普攻打中他时引爆"),
        "zh-hant": ("技能命中敵人後" + Y + "5秒" + E + "內，下一次普攻引爆光芒", "技能命中的敵人帶光芒" + Y + "5秒" + E + "，普攻打中他時引爆"),
        "en": ("for " + Y + "5s" + E + " after her abilities hit an enemy, her next basic attack ignites the light",
               "enemies her abilities hit carry the light for " + Y + "5s" + E + "; her basic attack on one ignites it"),
        "ko": ("스킬이 적에게 적중한 뒤 " + Y + "5초" + E + " 안에 하는 다음 기본 공격이 빛을 폭발시켜",
               "스킬에 맞은 적에게 " + Y + "5초" + E + " 동안 빛이 남고, 그 적을 기본 공격하면 폭발해"),
        "ja": ("スキルが敵に命中してから" + Y + "5秒" + E + "以内の次の通常攻撃が光を炸裂させ",
               "スキルが当たった敵に" + Y + "5秒" + E + "光が残り、その敵への通常攻撃で炸裂し"),
    },
    ("league_kaisa", "attack"): {
        "zh-hans": ("普攻命中英雄叠电浆", "普攻在英雄身上叠电浆"), "zh-hant": ("普攻命中英雄疊電漿", "普攻在英雄身上疊電漿"),
        "en": ("hits on a champion add Plasma (2 if crowd-controlled)", "hits stack Plasma on that champion (2 if CC'd)"),
        "ko": ("챔피언을 맞히면 플라즈마 중첩", "맞힌 챔피언에게 플라즈마 중첩"), "ja": ("命中でプラズマ", "相手にプラズマ"),
    },
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    return {k: re.search(k + r': &str = "([^"]+)"', src).group(1)
            for k in ("DIANA_MOON", "DIANA_ASK", "DIANA_YES", "KENNEN_HIT", "KAISA_ATTACK", "KAISA_CC", "KAISA_W2", "KAISA_W3",
                      "LUX_LIT", "LUX_HIT", "MF_ASK", "MF_NEW")}


def load(hero):
    with open(lp(os.path.join(ROOT, "league", "champion", hero + ".data_champion")), encoding="utf-8-sig") as f:
        return json.load(f)


def diana(c):
    d = load("league_diana")
    if c["DIANA_MOON"] not in json.dumps(d["skill"]):
        sys.exit("Diana's Q no longer marks league_diana_moon_mark: update src/lib.rs")
    eff = d["skill2"]["effect"]["effects"]
    old = [i for i, x in enumerate(eff) if x.get("type") == "SwitchByBuff" and x.get("buff_name") == "league_diana_moonlight"]
    if len(old) != 1:
        sys.exit("Lunar Rush's moonlight check moved in the main pack: update this script")
    again = old and eff[old[0]]["effect_buff"]
    if "league_diana_e_again" not in json.dumps(again):
        sys.exit("Lunar Rush's moonlight check no longer queues league_diana_e_again: update this script")
    ask = {"type": "AddBuff", "buff_state": {"name": c["DIANA_ASK"], "duration": {"Time": {"tick": 3}}}}
    read = {"type": "Delayed", "tick": 2, "effects": [{
        "type": "SwitchByBuff", "buff_name": c["DIANA_YES"],
        "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": c["DIANA_YES"]}] + again["effects"]},
        "effect_none": {"type": "Combine", "effects": []}}]}
    eff[old[0]] = {"type": "Combine", "effects": [ask, read]}
    d["passive"] = {"passive_ref": MOD_ID + ":diana", "params": {}}
    return d, [("league_diana", "skill2")]


def mark(name):
    return {"type": "AddBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": 3}}}}


def kennen(c):
    """Every Mark of the Storm hit: the pair [SwitchByBuff k_2 (stun or mark view), SwitchByBuff k_lock_<x> (her own
    counter)] becomes one mark on the struck champion."""
    d = load("league_kennen")
    n = []

    def walk(o):
        if isinstance(o, dict):
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            out, i = [], 0
            while i < len(o):
                x = o[i]
                if (isinstance(x, dict) and x.get("type") == "SwitchByBuff" and x.get("buff_name") == "league_kennen_k_2"
                        and i + 1 < len(o) and o[i + 1].get("buff_name", "").startswith("league_kennen_k_lock_")):
                    out.append(mark(c["KENNEN_HIT"]))
                    n.append(1)
                    i += 2
                    continue
                out.append(walk(x))
                i += 1
            return out
        return o

    d = walk(d)
    if len(n) != 8:
        sys.exit(f"Kennen: {len(n)} mark hits found, expected 8: check the main pack and update this script")
    d["passive"] = {"passive_ref": MOD_ID + ":kennen", "params": {}}
    return d, [("league_kennen", "attack")]


def kaisa(c):
    """The four Plasma ladders (SwitchByBuff league_kaisa_pl_4 .. pl_1 on her own flags) become marks on the struck
    champion: the attack's (it carries the extra hits) KAISA_ATTACK, its crowd-control twin KAISA_CC, W's KAISA_W2 /
    KAISA_W3 (the ladder whose first step adds pl_2 / pl_3)."""
    d = load("league_kaisa")
    found = []
    params = {}

    def ladder(o):
        steps, x = [], o
        while isinstance(x, dict) and x.get("type") == "SwitchByBuff" and x["buff_name"].startswith("league_kaisa_pl_"):
            steps.append(x["effect_buff"]["effects"])
            x = x["effect_none"]
        return steps, x["effects"]

    def kind(o):
        steps, base = ladder(o)
        first = [e["buff_state"]["name"] for e in base if e.get("type") == "AddCasterBuff"]
        aps = [e for e in base if e.get("type") == "ApAttack"]
        if aps:
            pop = [e for e in steps[0] if e.get("type") == "FixedAttack"][0]
            params.update(base=aps[0]["damage"], ap=aps[0]["attack_ratio"],
                          step=[e for e in steps[-1] if e.get("type") == "ApAttack"][0]["damage"] - aps[0]["damage"],
                          pop=pop["damage"], pop_ad=pop["attack_ratio"], pop_hp=pop["target_hp_ratio"])
            return c["KAISA_ATTACK"]
        if any(e.get("type") == "FixedAttack" for e in steps[0]):
            return c["KAISA_CC"]
        return {"league_kaisa_pl_2": c["KAISA_W2"], "league_kaisa_pl_3": c["KAISA_W3"]}[first[0]]

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "SwitchByBuff" and o.get("buff_name") == "league_kaisa_pl_4":
                k = kind(o)
                found.append(k)
                return mark(k)
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        return o

    d = walk(d)
    if sorted(found) != sorted([c["KAISA_ATTACK"], c["KAISA_CC"], c["KAISA_W2"], c["KAISA_W3"]]):
        sys.exit(f"Kai'Sa's Plasma ladders changed ({found}): update this script")
    d["passive"] = {"passive_ref": MOD_ID + ":kaisa", "params": params}
    return d, [("league_kaisa", "attack")]


def lux(c):
    """Illumination on the target: the skills' AddCasterBuff league_lux_illumination becomes LUX_LIT on the struck enemy;
    the attack fires the plain bolt with a LUX_HIT mark (the add-on ignites it on a lit target)."""
    d = load("league_lux")
    n = []

    def walk(o):
        if isinstance(o, dict):
            b = o.get("buff_state")
            if o.get("type") == "AddCasterBuff" and isinstance(b, dict) and b.get("name") == "league_lux_illumination":
                n.append(1)
                return {"type": "AddBuff", "buff_state": {"name": c["LUX_LIT"], "duration": b["duration"]}}
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        return o

    for slot in ("skill", "skill2", "ult"):
        d[slot] = walk(d[slot])
    if not n:
        sys.exit("Lux's skills no longer add league_lux_illumination: update this script")
    a = d["attack"]["effect"]
    if not (a.get("type") == "SwitchByBuff" and a.get("buff_name") == "league_lux_illumination"):
        sys.exit("Lux's attack no longer branches on league_lux_illumination: update this script")
    ignite = [e for x in a["effect_buff"]["effects"] if x.get("type") == "TargetProjectile"
              for ae in x["applied_effects"] for e in [ae["effect"]] if e.get("type") == "ApAttack"]
    if len(ignite) != 1:
        sys.exit("Lux's ignite hit changed: update this script")
    plain = a["effect_none"]
    bolts = [x for x in plain["effects"] if x.get("type") == "TargetProjectile"]
    if len(bolts) != 1:
        sys.exit("Lux's plain bolt changed: update this script")
    bolts[0]["applied_effects"].append({"casting_type": "Targeting", "effect": mark(c["LUX_HIT"])})
    d["attack"]["effect"] = plain
    d["passive"] = {"passive_ref": MOD_ID + ":lux", "params": {"base": ignite[0]["damage"], "ap": ignite[0]["attack_ratio"]}}
    return d, [("league_lux", "attack")]


def missfortune(c):
    """Love Tap on a new target: the attack asks (MF_ASK on its target) and fires two ticks later - the Love Tap bullet
    when the add-on raised MF_NEW, else the plain one."""
    d = load("league_missfortune")
    eff = d["attack"]["effect"]["effects"]
    k = [i for i, x in enumerate(eff) if x.get("type") == "SwitchByBuff" and x.get("buff_name") == "league_missfortune_lt_ready"]
    if len(k) != 1:
        sys.exit("Miss Fortune's attack no longer branches on lt_ready: update this script")
    sw = eff[k[0]]
    tap = [x for x in sw["effect_buff"]["effects"] if x.get("name") == "league_missfortune_bullet_lt"]
    fight = sw["effect_none"]
    plain = [fight["effect_buff"]] if fight.get("type") == "SwitchByBuff" else []
    if len(tap) != 1 or len(plain) != 1 or plain[0].get("name") != "league_missfortune_bullet":
        sys.exit("Miss Fortune's bullets changed: update this script")
    eff[k[0]] = {"type": "Combine", "effects": [mark(c["MF_ASK"]), {"type": "Delayed", "tick": 2, "effects": [{
        "type": "SwitchByBuff", "buff_name": c["MF_NEW"],
        "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": c["MF_NEW"]}, tap[0]]},
        "effect_none": plain[0]}]}]}
    d["passive"] = {"passive_ref": MOD_ID + ":missfortune", "params": {}}
    return d, [("league_missfortune", "attack")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: {} for lang in main_text}
    files = {}
    for make in (diana, kennen, kaisa, lux, missfortune):
        d, slots = make(c)
        hero = d["id"]
        for _, slot in slots:
            d[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{hero[7:]}_{slot}"
            for lang, tab in main_text.items():
                old, new = TEXT[(hero, slot)][lang]
                t = tab["description"][hero][slot]
                if old not in t:
                    sys.exit(f"{lang} {hero}.{slot}: the main pack's text changed ({old!r} not found): update this script")
                t = LEAD[lang] + t.replace(old, new)
                if shown_length(t) > TOOLTIP_MAX[lang]:
                    sys.exit(f"{lang} {hero}.{slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
                texts[lang][f"{hero[7:]}_{slot}"] = t
        files[os.path.join(ADDON, "override", hero + ".data_champion")] = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
    files[os.path.join(ADDON, "text", "champion.i18n")] = json.dumps(
        {lang: {"description": {MOD_ID: k}} for lang, k in texts.items()}, ensure_ascii=False, indent=2) + "\n"
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.exists(lp(p)) or open(lp(p), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for p, t in files.items():
        os.makedirs(lp(os.path.dirname(p)), exist_ok=True)
        with open(lp(p), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in files))


if __name__ == "__main__":
    main()
