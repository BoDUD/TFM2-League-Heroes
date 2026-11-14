"""Build the add-on's copy of Wukong from the main pack (Stone Skin regenerating a share of his max health; W's clone a
unit of its own).

    python addons/league_wukong/make_override.py [--check]

Rebuilds Wukong with tools/kit/build_wukong.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_wukong.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_wukong/override/league_wukong.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (Crushing Blow, Nimbus Strike, the clone, Cyclone and their moments);
  * passive = the add-on's league_wukong:stone with the numbers of P (p_pct, p_every);
  * Stone Skin's five stacks keep their armour but carry no data regeneration (the add-on heals % max health);
  * W (0.2.0) taking an earlier clone's W_UNIT off before league_wukong:clone, which spawns the clone as a unit and lays
    W_UNIT on him when the host gives one; the anchor's zone strike and its spin slots play only without W_UNIT (each
    hit and each slot reads it), so a host without the unit plays the main pack's W as it is and the AI's estimate (no
    flag when it is made) reads the same branch as before. The numbers the natives use for the unit and its spin
    (src/lib.rs: W_*, SPIN_*) are checked against the kit here: change the main pack and this script stops until lib.rs
    follows. The attack slot is left exactly as the native build makes it;
  * the attack's and W's tooltips pointing to description.league_wukong.<slot> with the add-on's wording, keys of the
    add-on's own id, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Wukong changes (--check: compare only).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_wukong")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_wukong as kit  # noqa: E402
import setup_wukong as setup  # noqa: E402

MOD_ID = "league_wukong"
HERO = "league_wukong"
SLOTS = ("attack", "skill2")
O, A, R, G, E = setup.O, setup.A, setup.R, setup.G, setup.E
# the add-on's W text (0.2.0): the clone a unit - it stands, has his health then and can be killed
SKILL2 = {
    "zh-hans": "【扩展包】隐身" + A + "{w_inv}秒" + E + "冲到敌方英雄身后，原地留下分身" + A + "{w_t}秒" + E + "：分身不会走，生命和他当时一样，"
               "可以被击杀；每秒攻击身边一个敌人，造成" + setup.ad("w_ratio") + "物理伤害；他放大招时分身也跟着转。",
    "zh-hant": "【擴充包】隱身" + A + "{w_inv}秒" + E + "衝到敵方英雄身後，原地留下分身" + A + "{w_t}秒" + E + "：分身不會走，生命和他當時一樣，"
               "可以被擊殺；每秒攻擊身邊一個敵人，造成" + setup.ad("w_ratio") + "物理傷害；他放大招時分身也跟著轉。",
    "en": "[Add-on] Turns invisible for " + A + "{w_inv}s" + E + " and dashes behind an enemy champion, leaving a clone for " + A + "{w_t}s" + E +
          ": it stands where he was with his health then and can be killed; each second it attacks an enemy near it for " +
          setup.ad("w_ratio") + " physical damage, and spins when he does.",
    "ko": "[확장] " + A + "{w_inv}초" + E + "간 투명해져 적 챔피언 뒤로 돌진하고 " + A + "{w_t}초" + E + "간 분신을 남김: 분신은 움직이지 않고 그때의 "
          "체력을 가지며 처치될 수 있음, 매초 주변 적 하나에게 " + setup.ad("w_ratio") + " 물리 피해, 궁극기 때 함께 회전.",
    "ja": "【拡張】" + A + "{w_inv}秒" + E + "透明になり敵チャンピオンの背後へ、" + A + "{w_t}秒" + E + "分身を残す：分身は動かず、その時の体力を持ち、"
          "倒されることもある。毎秒近くの敵1体に" + setup.ad("w_ratio") + "の物理ダメージ、アルティメット中は一緒に回転。",
}
# the add-on's attack text (the main pack's wording with Stone Skin's % max-health regeneration)
ATTACK = {
    "zh-hans": "【扩展包】金箍棒横扫。" + O + "金刚不坏" + E + "：打中英雄叠1层（最多5层），每层护甲+{p_def}；每5秒" + G + "回复{pct}%最大生命" + E +
               "，每层再多{pct}%（叠满{top}%）。" + O + "粉碎打击" + E + "：每" + A + "{q_t}秒" + E + "下一次普攻伸长棒子，多造成" +
               setup.phys("q_dmg", "q_ratio") + "物理伤害，目标" + R + "护甲-{q_shred}%" + E + "，持续" + A + "{q_shred_t}秒" + E + "。",
    "zh-hant": "【擴充包】金箍棒橫掃。" + O + "仙山石猴" + E + "：打中英雄疊1層（最多5層），每層護甲+{p_def}；每5秒" + G + "回復{pct}%最大生命" + E +
               "，每層再多{pct}%（疊滿{top}%）。" + O + "定海神兵" + E + "：每" + A + "{q_t}秒" + E + "下一次普攻伸長棒子，多造成" +
               setup.phys("q_dmg", "q_ratio") + "物理傷害，目標" + R + "護甲-{q_shred}%" + E + "，持續" + A + "{q_shred_t}秒" + E + "。",
    "en": "[Add-on] Staff strikes. " + O + "Stone Skin" + E + ": each hit on a champion adds a stack (5 at most), +{p_def} armour each; every 5s "
          "he " + G + "regenerates {pct}% of his max health" + E + ", {pct}% more a stack ({top}% at five). " + O + "Crushing Blow" + E + ": every " +
          A + "{q_t}s" + E + " his next attack reaches farther and deals " + setup.phys("q_dmg", "q_ratio") + " physical damage more, " + R +
          "-{q_shred}% armour" + E + " on the target for " + A + "{q_shred_t}s" + E + ".",
    "ko": "[확장] 여의봉 공격. " + O + "바위 피부" + E + ": 챔피언 적중 시 중첩(최대 5), 중첩당 방어력 +{p_def}; 5초마다 " + G + "최대 체력의 {pct}% 회복" + E +
          ", 중첩당 {pct}% 추가(5중첩 {top}%). " + O + "파쇄격" + E + ": " + A + "{q_t}초" + E + "마다 다음 공격의 사거리가 늘고 " +
          setup.phys("q_dmg", "q_ratio") + " 물리 피해 추가, 대상 " + R + "방어력 -{q_shred}%" + E + " " + A + "{q_shred_t}초" + E + ".",
    "ja": "【拡張】如意棒で攻撃。" + O + "岩の皮膚" + E + "：チャンピオン命中でスタック（最大5）、毎スタック物理防御+{p_def}；5秒毎に" + G +
          "最大体力の{pct}%回復" + E + "、スタック毎に{pct}%追加。" + O + "強棒打" + E + "：" + A + "{q_t}秒" + E +
          "毎に次の通常攻撃が伸び" + setup.phys("q_dmg", "q_ratio") + "の物理ダメージを追加、対象の" + R + "物理防御-{q_shred}%" + E + "（" + A +
          "{q_shred_t}秒" + E + "）。",
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def walk(o):
    """every dict of a tree"""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(float(value.replace("_", "")))
    return out


def sw(buff, yes, no):
    return {"type": "SwitchByBuff", "buff_name": buff, "effect_buff": yes, "effect_none": no}


NONE = {"type": "Combine", "effects": []}


def unit(champion, c, p):
    """W's clone as a unit (0.2.0): the natives' numbers (c: src/lib.rs) checked against the kit, then the copy's W taking
    an earlier W_UNIT off at the cast and its anchor's strikes and spin slots each played only without W_UNIT."""
    w = champion["skill2"]["effect"]["effects"]
    natives = [i for i, x in enumerate(w) if x.get("type") == "Native" and x.get("effect_ref") == MOD_ID + ":clone"]
    anchors = [x for x in w if x.get("type") == "LinearProjectile" and x.get("name") == HERO + "_w_anchor"]
    if len(natives) != 1 or len(anchors) != 1:
        sys.exit("W's league_wukong:clone or its anchor changed in the kit: update this script")
    end = anchors[0]["end_effects"]
    zones = [x for x in end if x.get("type") == "RangePeriodProjectile" and x.get("name") == HERO + "_w_zone"]
    slots = [x for x in end if x.get("type") == "Delayed"]
    if len(zones) != 1 or len(zones) + len(slots) != len(end) or any(len(s["effects"]) != 1 for s in slots):
        sys.exit("the anchor's end_effects are no longer the zone and its slots: update this script")
    zone = zones[0]
    strikes = [x for x in walk(zone["applied_effects"]) if x.get("type") == "Attack"]
    spins = [x for x in walk(slots) if x.get("type") == "RangeProjectile" and x["name"] in (HERO + "_w_spin", HERO + "_w_spin_up")]
    if len(strikes) != 1 or len(spins) != 2 * len(slots):
        sys.exit("the clone's strike or its spin pulses changed in the kit: update this script")
    spin_hits = {(a["damage"], a["attack_ratio"]) for s in spins for a in walk(s["applied_effects"]) if a.get("type") == "Attack"}
    ups = {a["duration"] for s in spins for a in walk(s["applied_effects"]) if a.get("type") == "Airborne"}
    radii = {s["shape"]["Circle"]["radius"] for s in spins}
    if len(spin_hits) != 1 or len(ups) != 1 or len(radii) != 1:
        sys.exit("the clone's spin pulses differ from one another in the kit: update this script")
    ticks = [s["tick"] for s in slots]
    every = {b - a for a, b in zip(ticks, ticks[1:])}
    # the attack slot (read only): the action's length, and the plain swing's hit - start_timing, the decision's Delayed,
    # the swing's Delayed with Attack 0 / 100
    attack = champion["attack"]
    plain = [x for x in walk(attack) if x.get("type") == "Delayed" and any(
        y.get("type") == "Attack" and (y["damage"], y["attack_ratio"]) == (0, 100) for y in x["effects"])]
    decide = [x for x in attack["effect"]["effects"] if x.get("type") == "Delayed"]
    spin_flag = [x["buff_state"]["duration"]["Time"]["tick"] for x in walk(attack)
                 if x.get("type") == "AddCasterBuff" and x["buff_state"]["name"] == HERO + "_r_on"]
    swing = {x["tick"] for x in plain}      # the swing sits in both branches of the range buff's switch
    if len(swing) != 1 or len(decide) != 1 or len(set(spin_flag)) != 1:
        sys.exit("the attack's swing, its decision or the spin's r_on changed in the kit: update this script")
    (hit, hit_ad), = spin_hits
    got = {
        "W_LIFE": zone["tick"],
        "W_HIT": strikes[0]["damage"],
        "W_HIT_AD": strikes[0]["attack_ratio"],
        "W_COOL": zone["period"],
        "W_REACH": zone["shape"]["Circle"]["radius"],
        "W_ACT": attack["duration"],
        "W_LANDS": attack["start_timing"] + decide[0]["tick"] + swing.pop(),
        "SPIN_T": spin_flag[0],
        "SPIN_EVERY": every.pop() if len(every) == 1 else None,
        "SPIN_HIT": hit,
        "SPIN_HIT_AD": hit_ad,
        "SPIN_R": radii.pop(),
        "SPIN_UP": ups.pop(),
    }
    wrong = {k: (c.get(k), v) for k, v in got.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the clone's numbers differ from src/lib.rs (lib, kit): {wrong}")
    # the same numbers as the parameter table says them
    if (got["W_LIFE"], got["W_HIT_AD"], got["W_COOL"], got["W_REACH"], got["SPIN_EVERY"], got["SPIN_R"], got["SPIN_UP"],
            got["SPIN_T"]) != (p["w_t"], p["w_ratio"], p["w_period"], p["w_rad"], p["w_slot"], p["r_rad"], p["r_up"], p["r_t"]):
        sys.exit("the kit's clone and build_wukong.P disagree: update this script")
    views = {v["name"] for v in champion["view_effects"]}
    if c["SPIN_VIEW"] not in views:
        sys.exit(f"src/lib.rs's SPIN_VIEW = {c['SPIN_VIEW']} is no view effect of Wukong")
    if c["UNIT_NAME"] != HERO:
        sys.exit("the clone's unit name is not the hero's id: the game would not draw it from his sheet")
    buffs = {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    buffs |= {x.get("name") for x in walk(champion) if x.get("type") == "RemoveCasterBuff"}
    buffs |= {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    if c["W_UNIT"] in buffs or any(str(b).startswith(c["W_UID"]) for b in buffs):
        sys.exit("Wukong's kit already uses one of the add-on's buff names: update src/lib.rs")
    # the cast: an earlier clone's flag off before league_wukong:clone (which lays it again on a unit)
    w.insert(natives[0], {"type": "RemoveCasterBuff", "name": c["W_UNIT"]})
    zone["applied_effects"] = [dict(a, effect=sw(c["W_UNIT"], NONE, a["effect"])) for a in zone["applied_effects"]]
    for s in slots:
        s["effects"] = [sw(c["W_UNIT"], NONE, s["effects"][0])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_wukong differs from build_wukong.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":stone":
        sys.exit("the copy has no league_wukong:stone passive: update this script")
    attack = copy.deepcopy(champion["attack"])
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        unit(champion, consts(f.read()), p)
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
    # the attack slot is measured elsewhere: nothing here may change it but its tooltip's key
    if dict(champion["attack"], description=attack["description"]) != attack:
        sys.exit("this script changed the attack slot: it must stay as the native build makes it")

    values = dict(setup.values(p), pct=f"{p['p_pct'] / 100:g}", top=f"{p['p_pct'] * 6 / 100:g}")
    words = {"attack": ATTACK, "skill2": SKILL2}
    texts = {lang: {slot: t[lang].format(**values) for slot, t in words.items()} for lang in ATTACK}
    long = {f"{lang}.{slot}": setup.shown_length(t[lang]) for slot, t in words.items() for lang in t
            if setup.shown_length(t[lang]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                                  ensure_ascii=False, indent=2) + "\n"}
    if a.check:
        stale = [os.path.relpath(f, ROOT) for f, t in files.items()
                 if not os.path.exists(lp(f)) or open(lp(f), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for f, t in files.items():
        os.makedirs(lp(os.path.dirname(f)), exist_ok=True)
        with open(lp(f), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(t)
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{slot}": f"{setup.shown_length(t[lang])}/{setup.TOOLTIP_MAX[lang]}"
                              for slot, t in words.items() for lang in t})


if __name__ == "__main__":
    main()
