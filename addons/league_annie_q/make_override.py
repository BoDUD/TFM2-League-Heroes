"""Build the add-on's copy of Annie from the main pack (Disintegrate refunds on a kill, Tibbers a unit of his own).

    python addons/league_annie_q/make_override.py [--check]

Reads the main pack's league/champion/league_annie.data_champion and writes
addons/league_annie_q/override/league_annie.data_champion and .../text/champion.i18n: the same kit with -
  * both Q fireballs (TargetProjectile league_annie_q, 70 + 65% AP) calling the native effect league_annie_q:refund after
    their damage (it cuts Q's cooldown when the one struck died);
  * R keeping its summon (drop, hit, stun) but not Tibbers' follow: the Fire casted on the target and the 15 Delayed
    swipes / alive checks / vanish go; R marks its target with src/lib.rs's TIB_MARK instead, and the passive
    league_annie_q:tibbers runs Tibbers - since 0.3.0 as a unit of his own through the mod API's spawn_unit (his body the
    main pack's league/champions/league_annie_tibbers, which this add-on's mod.override_info puts under the unit's name;
    his attack's timing checked against that sheet here), and riding on the target with the main pack's pictures and
    numbers (checked here) when the host gives no unit;
  * a view effect TIB_BYE: the unit sheet's `dead` tag, his puff of smoke on his own ground line;
  * Q's and R's tooltips pointing to description.league_annie_q.<slot>: a sentence added to Q's, R's second half told
    as the unit he is (the numbers from src/lib.rs).
Every other champion stays untouched. Run it again whenever the main pack's Annie changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_annie_q")
MOD_ID = "league_annie_q"
HERO = "league_annie"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
AP, AD = "<#a974ffff>", "<#ff9028ff>"
ICON = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
SWAPS = {
    "skill": {
        "zh-hans": ("的<#a974ffff>魔法伤害<>。", "的<#a974ffff>魔法伤害<>。击杀目标时返还一半冷却。"),
        "zh-hant": ("的<#a974ffff>魔法傷害<>。", "的<#a974ffff>魔法傷害<>。擊殺目標時返還一半冷卻。"),
        "en": ("<#a974ffff>magic damage<>.", "<#a974ffff>magic damage<>. A kill refunds half its cooldown."),
        "ko": ("<#a974ffff>마법 피해<>를 입힙니다.", "<#a974ffff>마법 피해<>를 입힙니다. 대상을 처치하면 재사용 대기시간 절반을 돌려받습니다."),
        "ja": ("<#a974ffff>魔法ダメージ<>を与える。", "<#a974ffff>魔法ダメージ<>を与える。倒すとCDが半分戻る。"),
    },
}
# R: the main pack's text up to where Tibbers' stay begins (found once in it), then ours - the unit he is.
# {life} seconds, {hit} + {hit_ap}% AP a hit (physical: a unit's attack), {aura} + {aura_ap}% AP a second round him
STAY = {
    "zh-hans": ("提伯斯紧跟该英雄",
                "提伯斯留场" + Y + "{life}秒" + E + "，可以被击杀：自己追击、攻击敌人，每下造成" + AD + "{hit}" + E + " + " + ICON + AP
                + "{hit_ap}% 法术强度" + E + "的" + AD + "物理伤害" + E + "；每秒灼烧身边敌人，造成" + AP + "{aura}" + E + " + " + ICON + AP
                + "{aura_ap}% 法术强度" + E + "的" + AP + "魔法伤害" + E + "。"),
    "zh-hant": ("泰貝爾緊跟該英雄",
                "泰貝爾留場" + Y + "{life}秒" + E + "，可以被擊殺：自己追擊、攻擊敵人，每下造成" + AD + "{hit}" + E + " + " + ICON + AP
                + "{hit_ap}% 魔法強度" + E + "的" + AD + "物理傷害" + E + "；每秒灼燒身邊敵人，造成" + AP + "{aura}" + E + " + " + ICON + AP
                + "{aura_ap}% 魔法強度" + E + "的" + AP + "魔法傷害" + E + "。"),
    "en": ("For " + Y + "6s" + E + " Tibbers follows",
           "Tibbers stays for " + Y + "{life}s" + E + " and can be killed: he chases and attacks enemies on his own for " + AD
           + "{hit}" + E + " + " + ICON + AP + "{hit_ap}% Ability Power" + E + " " + AD + "physical damage" + E
           + " a hit and burns enemies around him for " + AP + "{aura}" + E + " + " + ICON + AP + "{aura_ap}% Ability Power" + E
           + " " + AP + "magic damage" + E + " every second."),
    "ko": ("티버는 " + Y + "6초" + E + " 동안",
           "티버는 " + Y + "{life}초" + E + " 동안 남아 스스로 적을 쫓아 공격해 한 번에 " + AD + "{hit}" + E + " + " + ICON + AP
           + "주문력의 {hit_ap}%" + E + " " + AD + "물리 피해" + E + "를 입히고, 매초 주변 적을 불태워 " + AP + "{aura}" + E + " + " + ICON + AP
           + "주문력의 {aura_ap}%" + E + " " + AP + "마법 피해" + E + "를 입힙니다. 처치될 수 있습니다."),
    "ja": ("ティバーズは" + Y + "6秒" + E + "間",
           "ティバーズは" + Y + "{life}秒" + E + "間場に残り、自ら敵を追い攻撃して1回ごとに" + AD + "{hit}" + E + " + " + ICON + AP
           + "魔力の{hit_ap}%" + E + "の" + AD + "物理ダメージ" + E + "、毎秒周囲の敵を燃やして" + AP + "{aura}" + E + " + " + ICON + AP
           + "魔力の{aura_ap}%" + E + "の" + AP + "魔法ダメージ" + E + "。倒されることもある。"),
}


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def consts():
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(float(value.replace("_", "")))
    return out


def tibbers(ult, c):
    """R without Tibbers' follow; its numbers checked against src/lib.rs."""
    eff = ult["effect"]["effects"]
    loop = [x for x in eff if x.get("type") == "Delayed" and "league_annie_tibbers" in json.dumps(x)
            and '"casted_type": "Fire"' in json.dumps(x)]
    if len(loop) != 1:
        sys.exit("Tibbers' follow loop changed in the main pack: update this script")
    casted = loop[0]["effects"][0]
    burn = re.search(r'"name": "league_annie_r_burn", "shape": \{"Circle": \{"radius": (\d+)\}\}.*?"damage": (\d+), "attack_ratio": (\d+)',
                     json.dumps(casted))
    got = {"TIB_FIRST": loop[0]["tick"], "TIB_PERIOD": casted["period"], "TIB_R": int(burn.group(1)),
           "TIB_BURN": int(burn.group(2)), "TIB_BURN_AP": int(burn.group(3))}
    wrong = {k: (c[k], v) for k, v in got.items() if c[k] != v}
    if wrong:
        sys.exit(f"Tibbers differs from src/lib.rs (lib, kit): {wrong}")

    def drop(x):
        s = json.dumps(x)
        if x.get("type") == "AddCasted" and x.get("casted_type") == "Fire":
            return True  # the vanish at the end on the target
        return x.get("type") == "Delayed" and any(k in s for k in ("league_annie_tib_alive", "league_annie_tibbers\"",
                                                                    "league_annie_r_burn"))
    kept = [x for x in eff if not drop(x)]
    if len(eff) - len(kept) != 16:
        sys.exit(f"R dropped {len(eff) - len(kept)} pieces, not 16: update this script")
    mark = {"type": "AddBuff", "buff_state": {"name": c["TIB_MARK"], "duration": {"Time": {"tick": 3 + c["TIB_FIRST"]}}}}
    ult["effect"]["effects"] = kept + [mark]


def unit(champion, c):
    """Tibbers the unit: his sheet in the main pack and its tags, his attack's timing against it, the add-on's
    mod.override_info putting the sheet under the unit's name, his puff as a view effect of the copy."""
    name = c["TIB_UNIT"]
    stem = os.path.join(ROOT, "league", "champions", name)
    if not os.path.exists(lp(stem + "#sheet.png")):
        sys.exit(f"league/champions/{name}#sheet.png is not there: python tools/art/unit_annie_tibbers.py")
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    missing = [t for t in ("idle", "run", "attack", "hit", "dead") if t not in anims]
    if missing:
        sys.exit(f"{name}'s sheet has no {missing}: the tags the engine's own summons carry")
    attack = [fr["duration"] for fr in anims["attack"]["frames"]]
    act, lands = round(sum(attack) * 60), int(sum(attack[:2]) * 60)   # the swipe is the third frame
    if (act, lands) != (c["TIB_ACT"], c["TIB_LANDS"]):
        sys.exit(f"{name}'s attack is {act} ticks with the claws down at {lands}; src/lib.rs has TIB_ACT {c['TIB_ACT']}, "
                 f"TIB_LANDS {c['TIB_LANDS']}")
    with open(lp(os.path.join(ADDON, "mod.override_info")), encoding="utf-8-sig") as f:
        over = json.load(f)
    for part in ("sheet", "anim"):
        want = {"remapping": f"asset/league/champions/{name}#{part}", "type": "override"}
        if over.get(f"asset/base/aseprite_resources/champions/{name}#{part}") != want:
            sys.exit(f"mod.override_info does not put the main pack's {name}#{part} under the unit's name")
    if any(v["name"] == c["TIB_BYE"] for v in champion["view_effects"]):
        sys.exit("the main pack's Annie already has a view effect named like the add-on's TIB_BYE")
    vanish = [v for v in champion["view_effects"] if v["name"] == c["TIB_VANISH"]]
    if len(vanish) != 1:
        sys.exit("the main pack's Tibbers vanish view changed: update this script")
    # like the riding one's puff (under the units, at a spot), from the unit's own sheet
    champion["view_effects"].append({"type": "Animation", "name": c["TIB_BYE"], "anim": f"asset/league/champions/{name}",
                                     "tag": "dead", "z": vanish[0].get("z", -1)})
    views = {v["name"] for v in champion["view_effects"]}
    for k in ("TIB_VIEW", "TIB_RING", "TIB_BURN_VIEW", "TIB_VANISH", "TIB_BYE"):
        if c[k] not in views:
            sys.exit(f"src/lib.rs's {k} = {c[k]} is no view effect of the copy")


def build():
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Annie has a passive in the main pack now: update this script")
    call = {"casting_type": "Targeting", "effect": {"type": "Native", "effect_ref": MOD_ID + ":refund"}}

    def is_ball(o):
        return o.get("type") == "TargetProjectile" and o.get("name") == "league_annie_q"

    def add(o):
        hits = [a["effect"] for a in o["applied_effects"] if a["effect"].get("type") == "ApAttack"]
        if [(h["damage"], h["attack_ratio"]) for h in hits] != [(70, 65)]:
            sys.exit("Annie's Q damage changed: update this script")
        return dict(o, applied_effects=o["applied_effects"] + [call])

    n = []
    champion["skill"] = replace(champion["skill"], is_ball, add, n)
    if len(n) != 2 or champion["skill"]["cooltime"] != 240:
        sys.exit(f"Annie's Q ({len(n)} fireballs, cooldown {champion['skill']['cooltime']}) changed: update src/lib.rs's REFUND")
    tibbers(champion["ult"], c)
    unit(champion, c)
    champion["passive"] = {"passive_ref": MOD_ID + ":tibbers", "params": {}}
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    text = {lang: {"description": {MOD_ID: {}}} for lang in main_text}
    for slot in ("skill", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{slot}"
        for lang, tab in main_text.items():
            t = tab["description"][HERO][slot]
            if slot == "skill":
                old, new = SWAPS[slot][lang]
                if old not in t:
                    sys.exit(f"{lang} {HERO}.{slot}: the main pack's text changed ({old!r} not found): update this script")
                t = t.replace(old, new)
            else:
                start, stay = STAY[lang]
                if t.count(start) != 1:
                    sys.exit(f"{lang} {HERO}.{slot}: the main pack's text changed ({start!r} found {t.count(start)} times): "
                             f"update this script")
                t = t[:t.index(start)] + stay.format(life=c["TIB_UNIT_LIFE"] // 60, hit=c["TIB_HIT"], hit_ap=c["TIB_HIT_AP"],
                                                     aura=c["TIB_AURA"], aura_ap=c["TIB_AURA_AP"])
            t = LEAD[lang] + t
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            text[lang]["description"][MOD_ID][slot] = t
    if c["TIB_UNIT_LIFE"] % 60 or c["TIB_AURA_EVERY"] != 60:
        sys.exit("the tooltip says whole seconds and a burn a second: update STAY")
    return champion, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    champion, text = build()
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps(text, ensure_ascii=False, indent=2) + "\n"}
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
