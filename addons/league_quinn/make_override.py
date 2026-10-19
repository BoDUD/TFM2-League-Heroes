"""Build the add-on's copy of Quinn from the main pack (League's ride on Valor).

    python addons/league_quinn/make_override.py

Rebuilds Quinn with tools/kit/build_quinn.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_quinn.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_quinn/override/league_quinn.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (Harrier and Heightened Senses in the attack, Blinding Assault, Vault);
  * passive = the add-on's league_quinn:ride (the ride's timer: it lays league_quinn_r_end a little before the ride runs
    out) with the numbers of P the add-on uses (checked against src/lib.rs's constants);
  * Behind Enemy Lines only calls Valor down and mounts her (r_ride, r_ride_t ticks at +r_ride_ms% move speed) with a
    1-tick watch that turns r_end into Skystrike; her attack, Q and E while riding cast Skystrike first;
  * the ult's tooltip points to description.league_quinn.ult with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Quinn changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_quinn")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_quinn as kit  # noqa: E402
import setup_quinn as setup  # noqa: E402

MOD_ID = "league_quinn"
HERO = "league_quinn"
SLOTS = ("ult",)
O, A, R, E = setup.O, setup.A, setup.R, setup.E
phys = setup.phys

TEXT = {
    "zh-hans": {
        "ult": "【扩展包】召来华洛骑上，" + A + "{r_ride_t}秒" + E + "内移速+{r_ride_ms}%；骑着时下一次普攻或技能、或骑行结束时施放" + O +
               "鹰翼天翔" + E + "：周围敌人受" + phys("r_dmg", "r_ratio") + "物理伤害并被标记。",
    },
    "zh-hant": {
        "ult": "【擴充包】召來威洛騎上，" + A + "{r_ride_t}秒" + E + "內移速+{r_ride_ms}%；騎著時下一次普攻或技能、或騎行結束時施放" + O +
               "天空強襲" + E + "：周圍敵人受" + phys("r_dmg", "r_ratio") + "物理傷害並被標記。",
    },
    "en": {
        "ult": "[Add-on] Calls Valor down and rides him for " + A + "{r_ride_t}s" + E + " at +{r_ride_ms}% move speed; her next "
               "attack or spell while riding, or the ride's end, lands with " + O + "Skystrike" + E + ": enemies around take " +
               phys("r_dmg", "r_ratio") + " physical damage and are marked.",
    },
    "ko": {
        "ult": "[확장] 발러를 불러 타고 " + A + "{r_ride_t}초" + E + " 동안 이동 속도 +{r_ride_ms}%; 타는 동안 다음 공격이나 스킬, 또는 비행이 "
               "끝날 때 " + O + "공중 강습" + E + ": 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해와 표식.",
    },
    "ja": {
        "ult": "【拡張】ヴァロールに乗り" + A + "{r_ride_t}秒" + E + "移動速度+{r_ride_ms}%；乗っている間の次の攻撃かスキル、または飛行の終わりに" +
               O + "空中強襲" + E + "：周りの敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージとマーク。",
    },
}

CONSTS = {"r_ride_t": "R_RIDE_T"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_quinn differs from build_quinn.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P[{key!r}] = {p[key]}: update the add-on")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":ride":
        sys.exit("the copy has no league_quinn:ride passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values.update({"r_ride_t": setup.secs(p["r_ride_t"]), "r_ride_ms": p["r_ride_ms"]})
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in TEXT.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
