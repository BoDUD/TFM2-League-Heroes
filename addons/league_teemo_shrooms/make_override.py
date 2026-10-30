"""Build the add-on's copy of Teemo from the main pack (Noxious Traps stay in the ground for minutes).

    python addons/league_teemo_shrooms/make_override.py [--check]

Reads the main pack's league/champion/league_teemo.data_champion and writes
addons/league_teemo_shrooms/override/league_teemo.data_champion and .../text/champion.i18n: the same kit with -
  * each of R's three shroom branches (the ones throwing league_teemo_r_throw) keeping its throw and the arming picture
    (Delayed 20) and losing the rest (the trigger and cloud zones, the 49 shroom pictures): one more Delayed 20 calls the
    native effect league_teemo_shrooms:plant at the landing spot; the cloud's numbers are checked against src/lib.rs;
  * the passive league_teemo_shrooms:shrooms (it keeps the shrooms, sets them off and poisons);
  * R's tooltip pointing to description.league_teemo_shrooms.ult with the shroom's life swapped and (0.2.0) the bushes
    he sows in out of fights (the AI hook league_teemo_shrooms:sow, src/sow.rs) added to where it is thrown.
Every other champion stays untouched. Run it again whenever the main pack's Teemo changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_teemo_shrooms")
MOD_ID = "league_teemo_shrooms"
HERO = "league_teemo"
SLOT = "ult"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "zh-hans": ("后布好并潜伏" + Y + "12秒" + E + "。", "后布好并潜伏" + Y + "3分钟" + E + "，提莫阵亡也在。"),
    "zh-hant": ("後布好並潛伏" + Y + "12秒" + E + "。", "後布好並潛伏" + Y + "3分鐘" + E + "，提摩陣亡也在。"),
    "en": ("hides for up to " + Y + "12s" + E + ".", "hides for " + Y + "3 minutes" + E + ", even after Teemo dies."),
    "ko": ("최대 " + Y + "12초" + E + " 동안 숨어 있습니다.", Y + "3분" + E + " 동안 숨어 있으며 티모가 죽어도 남습니다."),
    "ja": ("最大" + Y + "12秒" + E + "潜む。", Y + "3分" + E + "潜み、ティーモが倒れても残る。"),
}
# 0.2.0: out of fights he sows his spare shrooms in the bushes near him (src/sow.rs)
SOWS = {
    "zh-hans": ("向敌方英雄脚下扔出蘑菇，", "向敌方英雄脚下扔出蘑菇（不打架时往身边草丛里种），"),
    "zh-hant": ("向敵方英雄腳下擲出蘑菇，", "向敵方英雄腳下擲出蘑菇（不打架時往身邊草叢裡種），"),
    "en": ("Teemo throws a mushroom at an enemy champion's feet.", "Teemo throws a mushroom at an enemy's feet, or a bush when idle."),
    "ko": ("적 챔피언의 발밑에 버섯을 던집니다.", "적 챔피언의 발밑에, 싸우지 않을 때는 근처 수풀에 버섯을 던집니다."),
    "ja": ("敵チャンピオンの足元に毒キノコを投げる。", "敵チャンピオンの足元に（戦闘外は近くの茂みに）毒キノコを投げる。"),
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


def consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {k: int(re.search(r"pub const " + k + r": usize = ([\d_]+);", src).group(1).replace("_", ""))
           for k in ("POISON", "POISON_AP", "POISON_TICKS", "POISON_PERIOD")}
    for k in ("TRIGGER", "CLOUD"):
        out[k] = int(re.search(r"pub const " + k + r": f64 = ([\d_]+)\.0;", src).group(1).replace("_", ""))
    return out


def build():
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Teemo has a passive in the main pack now: update this script")
    ult = json.dumps(champion[SLOT])
    want = [f'"name": "league_teemo_r_trigger", "shape": {{"Circle": {{"radius": {c["TRIGGER"]}}}}}',
            f'"name": "league_teemo_r_cloud", "shape": {{"Circle": {{"radius": {c["CLOUD"]}}}}}',
            f'"casted_type": "Poison", "duration": {c["POISON_TICKS"] * c["POISON_PERIOD"]}, "period": {c["POISON_PERIOD"]}',
            f'"damage": {c["POISON"]}, "attack_ratio": {c["POISON_AP"]}']
    missing = [w for w in want if w not in ult]
    if missing:
        sys.exit(f"Teemo's shroom differs from src/lib.rs: {missing}")
    plant = {"type": "Delayed", "tick": 20, "effects": [{"type": "Native", "effect_ref": MOD_ID + ":plant"}]}

    def is_branch(o):
        return o.get("type") == "Combine" and any(e.get("type") == "ParabolicProjectile" and e.get("name") == "league_teemo_r_throw"
                                                  for e in o["effects"])

    def cut(o):
        eff = o["effects"]
        arm = next(i for i, e in enumerate(eff) if e.get("type") == "Delayed" and e["tick"] == 20)
        return dict(o, effects=eff[:arm + 1] + [plant])

    n = []
    champion[SLOT] = replace(champion[SLOT], is_branch, cut, n)
    left = json.dumps(champion[SLOT])
    if len(n) != 3 or "league_teemo_r_trigger" in left or "league_teemo_r_trap" in left:
        sys.exit(f"Teemo's R ({len(n)} shroom branches) changed: update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":shrooms", "params": {}}
    champion[SLOT]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{SLOT}"
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    text = {}
    for lang, tab in main_text.items():
        t = tab["description"][HERO][SLOT]
        for old, new in (SWAPS[lang], SOWS[lang]):
            if old not in t:
                sys.exit(f"{lang} {HERO}.{SLOT}: the main pack's text changed ({old!r} not found): update this script")
            t = t.replace(old, new)
        t = LEAD[lang] + t
        if shown_length(t) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
        text[lang] = {"description": {MOD_ID: {SLOT: t}}}
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
