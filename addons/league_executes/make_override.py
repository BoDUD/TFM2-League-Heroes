"""Build the add-on's copies of Evelynn and Akali from the main pack (their ults on the target's health).

    python addons/league_executes/make_override.py [--check]

Reads the main pack's kits and writes addons/league_executes/override/<hero>.data_champion and .../text/champion.i18n:
  * league_evelynn: Last Caress's cone keeps its base hit (150 + 75% AP); the ladder of extra hits by her recent
    champion hits (SwitchByBuff league_evelynn_h4 .. h1) becomes an AddBuff of src/lib.rs's EVELYNN_MARK on the struck
    target; passive league_executes:evelynn with the base hit's numbers (the add-on adds 140% below 30% health);
  * league_akali: Perfect Execution's second dash keeps its base hit (86 + 43% AP); the ladder by her hits in between
    (SwitchByBuff league_akali_r_s8 .. s1 around ApAttacks) becomes that base hit and an AddBuff of AKALI_MARK;
    passive league_executes:akali (the add-on adds 0-200% by the target's missing health);
  * their ult tooltips point to description.league_executes.<hero>_ult in the add-on's wording.
Run it again whenever one of them changes in the main pack (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_executes")
MOD_ID = "league_executes"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E, O = "<#ffb900ff>", "<>", "<#ff9028ff>"
SWAPS = {
    "league_evelynn": {
        "zh-hans": ("，最近每打中英雄一次+" + Y + "35%" + E + "（最多×2.4）", "，对生命不高于" + Y + "30%" + E + "的目标×2.4"),
        "zh-hant": ("，最近每擊中英雄一次+" + Y + "35%" + E + "（最多×2.4）", "，對生命不高於" + Y + "30%" + E + "的目標×2.4"),
        "en": (", +" + Y + "35%" + E + " for each recent champion hit (up to x2.4)", ", x2.4 on targets at " + Y + "30%" + E + " health or below"),
        "ko": (", 최근 챔피언 적중마다 +" + Y + "35%" + E + "(최대 x2.4)", ", 체력 " + Y + "30%" + E + " 이하 대상에게 x2.4"),
        "ja": ("、最近のチャンピオン命中ごとに+" + Y + "35%" + E + "(最大x2.4)", "、体力" + Y + "30%" + E + "以下の対象にはx2.4"),
    },
    "league_akali": {
        "zh-hans": ("，两段之间每命中英雄一次 +" + Y + "25%" + E + "（最多" + Y + "200%" + E + "）", "，按目标已损失生命最多+" + Y + "200%" + E),
        "zh-hant": ("，兩段之間每命中英雄一次 +" + Y + "25%" + E + "（最多" + Y + "200%" + E + "）", "，按目標已損失生命最多+" + Y + "200%" + E),
        "en": (", +" + Y + "25%" + E + " per champion hit in between (up to +" + Y + "200%" + E + ")",
               ", up to +" + Y + "200%" + E + " by missing health"),
        "ko": (", 그 사이 챔피언 적중마다 +" + Y + "25%" + E + "(최대 " + Y + "200%" + E + ")", ", 대상의 잃은 체력에 비례해 최대 +" + Y + "200%" + E),
        "ja": ("、その間の命中ごとに+" + Y + "25%" + E + "（最大" + Y + "200%" + E + "）", "、対象の減少体力に応じて最大+" + Y + "200%" + E),
    },
    "league_riven": {
        "zh-hans": [("开启" + Y + "5秒" + E + "后向身边的敌方英雄放出", "开启" + Y + "5秒" + E + "后，有人残血、可斩杀或大招将尽时放出"),
                    (" + " + O + "8% 最大生命值" + E + "的" + O + "物理伤害" + E, "的" + O + "物理伤害" + E + "，按已损失生命最多+" + Y + "200%" + E)],
        "zh-hant": [("啟動" + Y + "5秒" + E + "後向身邊的敵方英雄發射", "啟動" + Y + "5秒" + E + "後，有人殘血、可斬殺或大招將盡時發射"),
                    (" + " + O + "8% 最大生命" + E + "的" + O + "物理傷害" + E, "的" + O + "物理傷害" + E + "，按已損失生命最多+" + Y + "200%" + E)],
        "en": [("After " + Y + "5s" + E + " she fires " + O + "Wind Slash" + E + " at an enemy champion near her",
                "After " + Y + "5s" + E + " she fires " + O + "Wind Slash" + E + " when a foe is low or killable, or R ends"),
               (" + " + O + "8% max health" + E + " " + O + "physical damage" + E + " to enemies in a line",
                " " + O + "physical damage" + E + " in a line, up to +" + Y + "200%" + E + " by missing health")],
        "ko": [(Y + "5초" + E + " 후 주변의 적 챔피언에게", Y + "5초" + E + " 후 적이 빈사·처치 가능하거나 궁극기가 끝날 때"),
               (" + " + O + "최대 체력의 8%" + E + " " + O + "물리 피해" + E + "를 입힙니다",
                " " + O + "물리 피해" + E + "(잃은 체력 비례 최대 +" + Y + "200%" + E + ")")],
        "ja": [(Y + "5秒" + E + "後、近くの敵チャンピオンへ", Y + "5秒" + E + "後、瀕死・倒せる敵がいるか終了間際に"),
               (" + " + O + "最大体力の8%" + E + "の" + O + "物理ダメージ" + E + "を与える",
                "の" + O + "物理ダメージ" + E + "（減少体力に応じ最大+" + Y + "200%" + E + "）")],
    },
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def load(hero):
    with open(lp(os.path.join(ROOT, "league", "champion", hero + ".data_champion")), encoding="utf-8-sig") as f:
        return json.load(f)


def marks():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    return {k: re.search(k + r': &str = "([^"]+)"', src).group(1) for k in ("EVELYNN_MARK", "AKALI_MARK", "RIVEN_MARK", "RIVEN_GO", "RIVEN_WAIT")}


def mark_effect(name):
    return {"type": "AddBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": 3}}}}


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(1)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def evelynn(m):
    d = load("league_evelynn")
    n = []
    d = replace(d, lambda o: o.get("type") == "SwitchByBuff" and o.get("buff_name") == "league_evelynn_h4"
                and "ApAttack" in json.dumps(o["effect_buff"]), lambda o: mark_effect(m["EVELYNN_MARK"]), n)
    if not n:
        sys.exit("Evelynn's R ladder (league_evelynn_h4) is gone from the main pack: update this script")
    if (150, 75) not in {(x["damage"], x["attack_ratio"]) for x in walk_ap(d)}:
        sys.exit("Evelynn's R base hit (150 + 75% AP) changed: update this script")
    d["passive"] = {"passive_ref": MOD_ID + ":evelynn", "params": {"base": 150, "ap": 75, "below": 30, "bonus": 140}}
    return d, len(n)


def akali(m):
    d = load("league_akali")
    n = []

    def is_ladder(o):
        return (o.get("type") == "SwitchByBuff" and o.get("buff_name", "").startswith("league_akali_r_s")
                and "ApAttack" in json.dumps(o["effect_buff"]))

    def flatten(o):
        while is_ladder(o):
            o = o["effect_none"]
        if not (o.get("type") == "Combine" and any(e.get("type") == "ApAttack" and e["damage"] == 86 and e["attack_ratio"] == 43
                                                   for e in o["effects"])):
            sys.exit("Akali's R2 base hit changed: update this script")
        return {"type": "Combine", "effects": o["effects"] + [mark_effect(m["AKALI_MARK"])]}

    d = replace(d, is_ladder, flatten, n)
    if not n:
        sys.exit("Akali's R2 ladder is gone from the main pack: update this script")
    d["passive"] = {"passive_ref": MOD_ID + ":akali", "params": {"base": 86, "ap": 43, "full": 70, "max": 200}}
    return d, len(n)


def riven(m):
    """Wind Slash waits for the add-on's RIVEN_GO at every check and marks whoever it hits (no 8% max health)."""
    d = load("league_riven")
    n, w = [], []

    def is_check(o):
        return (o.get("type") == "SwitchByBuff" and o.get("buff_name") == m["RIVEN_WAIT"]
                and o["effect_none"].get("type") == "RandomTarget")

    def gate(o):
        fire = o["effect_none"]
        go = {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": m["RIVEN_GO"]}, fire]}
        return dict(o, effect_none={"type": "SwitchByBuff", "buff_name": m["RIVEN_GO"], "effect_buff": go,
                                    "effect_none": {"type": "Combine", "effects": []}})

    def is_wave(o):
        return o.get("type") == "LinearProjectile" and o.get("name") == "league_riven_r_wave"

    def wave(o):
        hit = [a["effect"] for a in o["applied_effects"] if a["effect"].get("type") == "Attack"]
        if [(x["damage"], x["attack_ratio"], x["target_hp_ratio"]) for x in hit] != [(100, 100, 8)]:
            sys.exit("Riven's Wind Slash hit (100 + 100% AD + 8% max health) changed: update this script")
        applied = [dict(a, effect=dict(a["effect"], target_hp_ratio=0)) if a["effect"].get("type") == "Attack" else a
                   for a in o["applied_effects"]]
        return dict(o, applied_effects=applied + [{"casting_type": "Targeting", "effect": mark_effect(m["RIVEN_MARK"])}])

    d = replace(d, is_check, gate, n)
    d = replace(d, is_wave, wave, w)
    if not n or len(w) != len(n):
        sys.exit(f"Riven's Wind Slash checks ({len(n)}) / waves ({len(w)}) changed in the main pack: update this script")
    if d.get("passive"):
        sys.exit("Riven has a passive in the main pack now: update this script")
    d["passive"] = {"passive_ref": MOD_ID + ":riven", "params": {"base": 100, "ad": 100, "full": 75, "max": 200}}
    return d, len(n)


def walk_ap(o, out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        if o.get("type") == "ApAttack":
            out.append(o)
        for v in o.values():
            walk_ap(v, out)
    elif isinstance(o, list):
        for v in o:
            walk_ap(v, out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    m = marks()
    files = {}
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: {} for lang in main_text}
    for make in (evelynn, akali, riven):
        d, n = make(m)
        hero = d["id"]
        d["ult"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{hero[7:]}_ult"
        files[os.path.join(ADDON, "override", hero + ".data_champion")] = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
        for lang, tab in main_text.items():
            swaps = SWAPS[hero][lang]
            t = tab["description"][hero]["ult"]
            for old, new in swaps if isinstance(swaps, list) else [swaps]:
                if old not in t:
                    sys.exit(f"{lang} {hero}.ult: the main pack's text changed ({old!r} not found): update this script")
                t = t.replace(old, new)
            t = LEAD[lang] + t
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {hero}.ult: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            texts[lang][f"{hero[7:]}_ult"] = t
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
