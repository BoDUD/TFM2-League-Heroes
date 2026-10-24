"""Build the add-on's copies of Jinx, Tristana and Master Yi from the main pack (their takedown effects on every kill
and assist).

    python addons/league_takedowns/make_override.py [--check]

Reads the main pack's kits, checks that src/lib.rs's numbers are theirs (Jinx's four Get Excited! buffs, Tristana's
Rocket Jump cooldown flag, Master Yi's Highlander buff) and writes addons/league_takedowns/override/<hero>.data_champion
and .../text/champion.i18n -
  * league_jinx: the kill checks gone (her attack's and her rocket's twins, the ult rocket's check: the add-on excites
    her on every takedown instead); passive league_takedowns:jinx; her attack's tooltip (it carries Get Excited!);
  * league_tristana: the kit as it is (her own kill check stays: the add-on only adds the assists); passive
    league_takedowns:tristana; Rocket Jump's tooltip;
  * league_masteryi: Highlander without the main pack's 40% cooldown share (the add-on cuts the cooldowns on takedowns
    and attacks instead); passive league_takedowns:masteryi; Highlander's tooltip.
Every tooltip changed points to description.league_takedowns.<hero>_<slot>, so the tooltip in game shows whether the
override took. Run it again whenever one of the three changes in the main pack (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_takedowns")
MOD_ID = "league_takedowns"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, O, E = "<#ffb900ff>", "<#ff9028ff>", "<>"
# (hero, slot) -> lang -> (the main pack's words, the add-on's), or a list of such pairs
SWAPS = {
    ("league_jinx", "attack"): {
        "zh-hans": [("亲手击杀英雄后", "参与击杀后"), ("（逐渐回落）", "")],
        "zh-hant": [("親手擊殺英雄後", "參與擊殺後"), ("（逐漸回落）", "")],
        "en": [("a champion kill grants", "a takedown grants"), (" (fading)", "")],
        "ko": [("적 챔피언 처치 시", "챔피언 처치 관여 시")], "ja": [("敵チャンピオンを倒すと", "撃破に関わると")]},
    ("league_tristana", "skill2"): {
        "zh-hans": ("她击杀敌方英雄", "她参与击杀敌方英雄"), "zh-hant": ("她擊殺敵方英雄", "她參與擊殺敵方英雄"),
        "en": [("when she kills an enemy champion", "when she takes down a champion"), ("firing with an enemy champion on top of her", "firing with one on top of her")],
        "ko": ("적 챔피언을 처치하거나", "적 챔피언 처치에 관여하거나"), "ja": ("敵チャンピオンを倒すか", "敵チャンピオン撃破に関わるか")},
}
YI_TAIL = {
    "zh-hans": ("，" + O + "阿尔法突袭" + E + "和" + O + "无极剑道" + E + "的冷却加快" + Y + "40%" + E + "。",
                "，免疫减速；期间参与击杀英雄延长" + Y + "4秒" + E + "。参与击杀英雄时" + O + "阿尔法突袭" + E + "和" + O + "无极剑道" + E +
                "的剩余冷却减少" + Y + "70%" + E + "；普攻使" + O + "阿尔法突袭" + E + "冷却减少" + Y + "1秒" + E + "。"),
    "zh-hant": ("，" + O + "先聲奪人" + E + "和" + O + "無極劍道" + E + "的冷卻加快" + Y + "40%" + E + "。",
                "，免疫緩速；期間參與擊殺英雄延長" + Y + "4秒" + E + "。參與擊殺英雄時" + O + "先聲奪人" + E + "和" + O + "無極劍道" + E +
                "的剩餘冷卻減少" + Y + "70%" + E + "；普攻使" + O + "先聲奪人" + E + "冷卻減少" + Y + "1秒" + E + "。"),
    "en": (", and " + O + "Alpha Strike" + E + " and " + O + "Wuju Style" + E + " recharge " + Y + "40%" + E + " faster.",
           " and is immune to slows; a champion takedown extends it by " + Y + "4s" + E + ". Champion takedowns cut " + O +
           "Alpha Strike" + E + "'s and " + O + "Wuju Style" + E + "'s remaining cooldowns by " + Y + "70%" + E + "; each attack cuts " +
           O + "Alpha Strike" + E + "'s by " + Y + "1s" + E + "."),
    "ko": (" 증가하고 " + O + "일격 필살" + E + "과 " + O + "우주류 검술" + E + "의 재사용 대기시간이 " + Y + "40%" + E + " 빠르게 돌아옵니다.",
           " 증가하고 둔화에 면역, 그동안 챔피언 처치에 관여하면 " + Y + "4초" + E + " 연장. 챔피언 처치 관여 시 " + O + "일격 필살" + E + "과 " + O +
           "우주류 검술" + E + "의 남은 재사용 대기시간 " + Y + "70%" + E + " 감소, 기본 공격마다 " + O + "일격 필살" + E + " " + Y + "1초" + E + " 감소."),
    "ja": ("増加し、" + O + "アルファストライク" + E + "と" + O + "ウージュースタイル" + E + "のクールダウンの回復が" + Y + "40%" + E + "速くなる。",
           "増加しスロウ無効、その間にチャンピオン撃破に関わると" + Y + "4秒" + E + "延長。撃破に関わると" + O + "アルファストライク" + E + "と" + O +
           "ウージュースタイル" + E + "の残りCD" + Y + "70%" + E + "短縮、通常攻撃ごとに" + O + "アルファストライク" + E + "のCD" + Y + "1秒" + E + "短縮。"),
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


def lib_consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    excited = re.findall(r'\("(league_jinx_excited[a-z0-9_]*)", (\d+), (\d+), (\d+)\)', src)
    return {"excited": [(n, int(t), int(a), int(m)) for n, t, a, m in excited],
            "tris_w_cd": re.search(r'TRIS_W_CD: &str = "([^"]+)"', src).group(1),
            "yi_r": re.search(r'YI_HIGHLANDER: &str = "([^"]+)"', src).group(1)}


def buffs_named(o, name, out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        b = o.get("buff_state")
        if o.get("type") == "AddCasterBuff" and isinstance(b, dict) and b.get("name") == name:
            out.append(b)
        for v in o.values():
            buffs_named(v, name, out)
    elif isinstance(o, list):
        for v in o:
            buffs_named(v, name, out)
    return out


def strip(o, drop):
    if isinstance(o, dict):
        return {k: strip(v, drop) for k, v in o.items()}
    if isinstance(o, list):
        return [strip(v, drop) for v in o if not drop(v)]
    return o


def jinx(c):
    d = load("league_jinx")
    for name, ticks, aspd, ms in c["excited"]:
        found = buffs_named(d, name)
        if not found or any(b["duration"] != {"Time": {"tick": ticks}} or b.get("attack_speed_mult", 0) != aspd
                            or b.get("move_speed_mult", 0) != ms for b in found):
            sys.exit(f"Jinx's {name} differs from src/lib.rs JINX_EXCITED: update it")

    def drop(v):
        if not isinstance(v, dict):
            return False
        if v.get("name") in ("league_jinx_kill_check", "league_jinx_rocket_check"):
            return True
        # the ult rocket's own check: an applied effect raising league_jinx_kc_r
        return set(v) == {"casting_type", "effect"} and "league_jinx_kc_r" in json.dumps(v["effect"])

    d = strip(d, drop)
    if "league_jinx_kc" in json.dumps(d):
        sys.exit("the Jinx copy still carries a kill check: update this script")
    d["passive"] = {"passive_ref": MOD_ID + ":jinx", "params": {}}
    return d, [("league_jinx", "attack")]


def tristana(c):
    d = load("league_tristana")
    if c["tris_w_cd"] not in json.dumps(d):
        sys.exit("Tristana's Rocket Jump flag is gone from the main pack: update src/lib.rs")
    d["passive"] = {"passive_ref": MOD_ID + ":tristana", "params": {}}
    return d, [("league_tristana", "skill2")]


def masteryi(c):
    d = load("league_masteryi")
    found = buffs_named(d["ult"], c["yi_r"])
    if len(found) != 1 or found[0].get("skill_cooldown_mult") != 40:
        sys.exit("Master Yi's Highlander changed in the main pack: update this script")
    found[0].pop("skill_cooldown_mult", None)
    found[0].pop("ult_cooldown_mult", None)
    d["passive"] = {"passive_ref": MOD_ID + ":masteryi", "params": {}}
    return d, [("league_masteryi", "ult")]


def texts(changed):
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main = json.load(f)
    out = {}
    for lang, tab in main.items():
        keys = {}
        for hero, slot in changed:
            t = tab["description"][hero][slot]
            pairs = SWAPS[(hero, slot)][lang] if (hero, slot) in SWAPS else YI_TAIL[lang]
            for old, new in pairs if isinstance(pairs, list) else [pairs]:
                if old not in t:
                    sys.exit(f"{lang} {hero}.{slot}: the main pack's text changed ({old!r} not found): update this script")
                t = t.replace(old, new)
            t = LEAD[lang] + t
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {hero}.{slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            keys[f"{hero[7:]}_{slot}"] = t
        out[lang] = {"description": {MOD_ID: keys}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    c = lib_consts()
    files, changed = {}, []
    for make in (jinx, tristana, masteryi):
        d, slots = make(c)
        for hero, slot in slots:
            d[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{hero[7:]}_{slot}"
        changed += slots
        files[os.path.join(ADDON, "override", d["id"] + ".data_champion")] = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
    files[os.path.join(ADDON, "text", "champion.i18n")] = json.dumps(texts(changed), ensure_ascii=False, indent=2) + "\n"
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
