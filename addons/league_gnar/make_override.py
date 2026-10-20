"""Build the add-on's copy of Gnar from the main pack (the whole-body Mega needs nothing in the data; GNAR!'s wall stun).

    python addons/league_gnar/make_override.py

Rebuilds Gnar with tools/kit/build_gnar.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_gnar.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_gnar/override/league_gnar.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the forms, Rage Gene, the combos);
  * GNAR!'s knock-back and stun are league_gnar:wall (everyone thrown the way that slams most of them into a wall), the
    passive league_gnar:slam lands the slams (stun, the extra damage) with the numbers of P the add-on uses (checked
    against src/lib.rs's constants);
  * the ult's tooltip points to description.league_gnar.ult with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Gnar changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_gnar")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_gnar as kit  # noqa: E402
import setup_gnar as setup  # noqa: E402

MOD_ID = "league_gnar"
HERO = "league_gnar"
SLOTS = ("ult",)
O, A, C, E = setup.O, setup.A, setup.C, setup.E
phys, t = setup.phys, setup.t
TEXT = {
    "zh-hans": {"ult": "【附加包】只有巨型纳尔能放（迷你纳尔怒气满时先变身）：把身边的敌人往同一个方向掀飞，造成" + phys("r") + O + "物理伤害" + E +
                       "并" + C + "减速{r_slow}%" + E + "；撞到墙上的再受一半伤害并" + C + "眩晕" + E + t("{r_stun}秒") + "。"},
    "zh-hant": {"ult": "【附加包】只有巨型吶兒能施放（迷你吶兒怒氣滿時先變身）：把身邊的敵人往同一個方向掀飛，造成" + phys("r") + O + "物理傷害" + E +
                       "並" + C + "緩速{r_slow}%" + E + "；撞到牆上的再受一半傷害並" + C + "暈眩" + E + t("{r_stun}秒") + "。"},
    "en": {"ult": "[Add-on] Mega Gnar only (Mini Gnar at full Rage transforms first): throws every enemy around him the same way, "
                  "dealing " + phys("r") + " " + O + "physical damage" + E + " and " + C + "slowing {r_slow}%" + E + "; those "
                  "slammed into a wall take half again and are " + C + "stunned" + E + " " + t("{r_stun}s") + "."},
    "ko": {"ult": "[애드온] 메가 나르만 사용(꼬마 나르는 분노가 가득 차면 먼저 변신): 주변 적을 모두 한 방향으로 내던져 " + phys("r") + " " + O +
                  "물리 피해" + E + "와 " + C + "{r_slow}% 둔화" + E + "; 벽에 부딪힌 적은 피해를 절반 더 받고 " + t("{r_stun}초") + " " +
                  C + "기절" + E + "."},
    "ja": {"ult": "【アドオン】メガ・ナー専用（ミニ・ナーは怒り最大で先に変身）：周囲の敵をすべて同じ方向へ投げ飛ばし、" + phys("r") + "の" + O +
                  "物理ダメージ" + E + "と" + C + "{r_slow}%スロウ" + E + "；壁に叩きつけられた敵はさらに半分のダメージを受け" +
                  t("{r_stun}秒") + C + "スタン" + E + "。"},
}
CONSTS = {k: k.upper() for k in ("r_dmg", "r_ratio", "r_stun", "r_wall", "r_r", "r_push", "r_push_v")}


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
        sys.exit("the main pack's league_gnar differs from build_gnar.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P[{key!r}] = {p[key]}: update the add-on")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":slam":
        sys.exit("the copy has no league_gnar:slam passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: v.format(**values) for k, v in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(v) for lang, d in TEXT.items() for k, v in d.items()
            if setup.shown_length(v) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(v)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, v in d.items()})


if __name__ == "__main__":
    main()
