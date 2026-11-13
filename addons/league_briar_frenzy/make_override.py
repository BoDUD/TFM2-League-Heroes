"""Build the add-on's copy of Briar from the main pack (E stuns on walls, her ult's frenzy lasts while the prey lives).

    python addons/league_briar_frenzy/make_override.py [--check]

Reads the main pack's league/champion/league_briar.data_champion and writes
addons/league_briar_frenzy/override/league_briar.data_champion and .../text/champion.i18n: the same kit with -
  * E's stun at the end of the knock-back (the RangeEffect on EnemyChampion: Delayed 16 -> Stun 60) swapped for an AddBuff
    of src/lib.rs's E_MARK at the hit (the passive stuns the ones pushed short: a wall, the map's edge, a unit);
  * the passive league_briar_frenzy:frenzy (E's walls, R's frenzy kept while the prey lives); the AI hook
    league_briar_frenzy:lock needs nothing in the data;
  * Crimson Curse's other half (0.1.4): every skill's cast (skill, skill2, ult) ends with the native effect
    league_briar_frenzy:cost (5% of her current health), and each of her own heals - the bleed's ticks, Snack Attack,
    the scream's charge - is the native league_briar_frenzy:mend_bleed / mend_snack / mend_scream instead of the
    data's Heal (the same amounts, up to 40% more by her missing health; src/lib.rs's MEND_* are checked here);
  * E's and R's tooltips pointing to description.league_briar_frenzy.<slot> with those words swapped, and the
    attack's (it carries the passive) with the cost and the missing-health healing added.
Every other champion stays untouched. Run it again whenever the main pack's Briar changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_briar_frenzy")
MOD_ID = "league_briar_frenzy"
HERO = "league_briar"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, R, E = "<#ffb900ff>", "<#ef5350ff>", "<>"
SWAPS = {
    "skill2": {
        "zh-hans": ("被击退的英雄", "撞上墙或单位的英雄"),
        "zh-hant": ("被擊退的英雄", "撞上牆或單位的英雄"),
        "en": ("champions knocked back are", "champions knocked into a wall or unit are"),
        "ko": ("밀려난 챔피언은", "벽이나 유닛에 부딪힌 챔피언은"),
        "ja": ("飛ばされたチャンピオンは", "壁かユニットにぶつかったチャンピオンは"),
    },
    "ult": {
        "zh-hans": ("随后" + Y + "6秒" + E + "进入", "猎物倒下前一直"),
        "zh-hant": ("隨後" + Y + "6秒" + E + "進入", "獵物倒下前一直"),
        "en": ("For " + Y + "6s" + E + " she is in", "Till the prey falls she's in"),
        "ko": (Y + "6초" + E + " 동안 피의 갈증", "먹잇감이 쓰러질 때까지 피의 갈증"),
        "ja": (Y + "6秒" + E + "渇血状態", "獲物が倒れるまで渇血状態"),
    },
}
G = "<#6aff55ff>"
# lang -> the sentence the add-on adds to the attack's text (Crimson Curse: the costs, the missing-health healing)
CURSE = {
    "zh-hans": "技能各耗当前生命{cost}%；生命越低回复越多（最多" + G + "+{mend}%" + E + "）。",
    "zh-hant": "技能各耗目前生命{cost}%；生命越低回復越多（最多" + G + "+{mend}%" + E + "）。",
    "en": " Each ability costs {cost}% of her current health; the lower her health, the more she heals (up to " + G + "+{mend}%" + E + ").",
    "ko": " 스킬은 현재 체력 {cost}% 소모, 저체력 시 회복 " + G + "+{mend}%" + E + "까지.",
    "ja": "各スキルは現在体力の{cost}%を消費。低体力ほど回復増加（最大" + G + "+{mend}%" + E + "）。",
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    mark = re.search(r'pub const E_MARK: &str = "([^"]+)";', src).group(1)
    knock = int(re.search(r"pub const KNOCK: usize = (\d+);", src).group(1))
    cost_pct = int(re.search(r"pub const COST_PCT: usize = (\d+);", src).group(1))
    mend_max = int(re.search(r"pub const MEND_MAX: usize = (\d+);", src).group(1))
    mends = {tuple(int(x) for x in m.groups()[1:]): "mend_" + m.group(1).lower()
             for m in re.finditer(r"pub const MEND_(BLEED|SNACK|SCREAM): \(usize, usize\) = \((\d+), (\d+)\);", src)}
    if len(mends) != 3:
        sys.exit("src/lib.rs: MEND_BLEED / MEND_SNACK / MEND_SCREAM not found, or two of them alike")
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Briar has a passive in the main pack now: update this script")

    def is_stun(o):
        if not (o.get("type") == "RangeEffect" and o.get("target") == "EnemyChampion"):
            return False
        inner = o["effects"]
        return (len(inner) == 1 and inner[0].get("type") == "Delayed" and inner[0]["tick"] == knock
                and inner[0]["effects"][0] == {"type": "Stun", "duration": 60})

    n = []
    champion["skill2"] = replace(champion["skill2"], is_stun, lambda o: dict(o, effects=[
        {"type": "AddBuff", "buff_state": {"name": mark, "duration": {"Time": {"tick": knock + 4}}}}]), n)
    if len(n) != 1 or '"speed": 2500, "tick": 16' not in json.dumps(champion["skill2"]):
        sys.exit("Briar's E knock-back / stun changed in the main pack: update src/lib.rs and this script")
    if '"name": "league_briar_hema", "duration": {"Time": {"tick": 360}}, "attack_speed_mult": 70, "move_speed_mult": 45, ' \
       '"defence": 20, "magic_resistance": 20, "vamp": 10' not in json.dumps(champion["ult"]):
        sys.exit("Briar's Hemomania changed in the main pack: update src/lib.rs's HEMA_STATS")
    # Crimson Curse natively: her own heals (heal_type Caster, no AP part) by her missing health, a cost a cast
    seen = []

    def is_heal(o):
        return o.get("type") == "Heal"

    def to_mend(o):
        key = (o["amount"], o["attack_ratio"])
        if o.get("heal_type") != "Caster" or o.get("ap_ratio") or key not in mends:
            sys.exit(f"a Heal the add-on does not know ({o}): update src/lib.rs's MEND_* and this script")
        seen.append(mends[key])
        return {"type": "Native", "effect_ref": f"{MOD_ID}:{mends[key]}"}

    for slot in ("attack", "skill", "skill2", "ult"):
        champion[slot] = replace(champion[slot], is_heal, to_mend, [])
    if set(seen) != set(mends.values()):
        sys.exit(f"the main pack's Briar no longer has all three heals ({sorted(set(seen))}): update src/lib.rs and this script")
    for slot in ("skill", "skill2", "ult"):
        top = champion[slot]["effect"]
        if top.get("type") != "Combine":
            sys.exit(f"Briar's {slot} is no longer a Combine at the top: update this script")
        top["effects"].append({"type": "Native", "effect_ref": f"{MOD_ID}:cost"})
    champion["passive"] = {"passive_ref": MOD_ID + ":frenzy", "params": {}}
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    text = {lang: {"description": {MOD_ID: {}}} for lang in main_text}
    for slot, swaps in SWAPS.items():
        champion[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{slot}"
        for lang, tab in main_text.items():
            old, new = swaps[lang]
            t = tab["description"][HERO][slot]
            if old not in t:
                sys.exit(f"{lang} {HERO}.{slot}: the main pack's text changed ({old!r} not found): update this script")
            t = LEAD[lang] + t.replace(old, new)
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            text[lang]["description"][MOD_ID][slot] = t
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.attack"
    for lang, tab in main_text.items():
        t = LEAD[lang] + tab["description"][HERO]["attack"] + CURSE[lang].format(cost=cost_pct, mend=mend_max)
        if shown_length(t) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang} attack: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
        text[lang]["description"][MOD_ID]["attack"] = t
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
