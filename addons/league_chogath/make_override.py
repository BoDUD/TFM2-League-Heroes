"""Build the add-on's copy of Cho'Gath from the main pack (Feast stacks kept through death, Feast only for a kill).

    python addons/league_chogath/make_override.py

Rebuilds Cho'Gath with tools/kit/build_chogath.py (its parameter table P), checks that the build is the main pack's
league/champion/league_chogath.data_champion byte for byte (so the copy never drifts from the shipped kit), checks
src/lib.rs's constants against P, and writes addons/league_chogath/override/league_chogath.data_champion and
.../text/champion.i18n: the same kit with
  * passive = the add-on's league_chogath:keep (no params), which puts back every Feast stack his death clears;
  * the ult's tooltip pointing to description.league_chogath.ult with the add-on's wording (stacks kept, only for a
    kill - the AI hook league_chogath:feast needs nothing in the data).
Every other champion stays untouched. Run it again whenever the main pack's Cho'Gath changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_chogath")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_chogath as kit  # noqa: E402
import setup_chogath as setup  # noqa: E402

MOD_ID = "league_chogath"
HERO = "league_chogath"
SLOTS = ("ult",)
O, A, M, E, APi = setup.O, setup.A, setup.M, setup.E, setup.APi
TEXT = {
    "zh-hans": {
        "ult": "【扩展包】只在一口吃得死时吞噬敌方英雄：" + O + "{r_dmg}" + E + " + 自身{r_hp}%最大生命的真实伤害和" + APi + M + "{r_ap}%" +
               E + "无视魔抗的魔法伤害；吃掉则叠一层：最大生命+{r_stack_hp}、体型变大（不封顶，死后保留）。",
    },
    "zh-hant": {
        "ult": "【擴充包】只在一口吃得死時吞噬敵方英雄：" + O + "{r_dmg}" + E + " + 自身{r_hp}%最大生命的真實傷害和" + APi + M + "{r_ap}%" +
               E + "無視魔抗的魔法傷害；吃掉則疊一層：最大生命+{r_stack_hp}、體型變大（不封頂，死後保留）。",
    },
    "en": {
        "ult": "[Add-on] Devours an enemy champion only when one bite kills: " + O + "{r_dmg}" + E + " + {r_hp}% of his max "
               "health as true damage and " + APi + M + "{r_ap}%" + E + " magic damage through all magic resist. A kill is a "
               "stack: +{r_stack_hp} max health and a bigger body (no cap; kept through death).",
    },
    "ko": {
        "ult": "[확장] 한 번에 처치할 수 있을 때만 적 챔피언을 삼켜 " + O + "{r_dmg}" + E + " + 최대 체력 {r_hp}% 고정 피해와 " + APi + M +
               "{r_ap}%" + E + " 마법 피해(마법 저항 무시). 처치하면 중첩: 최대 체력 +{r_stack_hp}, 몸집 증가(제한 없음, 사망해도 유지).",
    },
    "ja": {
        "ult": "【拡張】一撃で倒せる時だけ敵チャンピオンを捕食し" + O + "{r_dmg}" + E + "+最大体力{r_hp}%の確定ダメージと" + APi + M + "{r_ap}%" +
               E + "の魔法ダメージ（魔法防御無視）。倒すとスタック：最大体力+{r_stack_hp}、体が大きくなる（上限なし、死亡後も残る）。",
    },
}
CONSTS = {"r_dmg": "R_DMG", "r_hp": "R_HP", "r_ap": "R_AP", "r_range": "R_RANGE"}


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
        sys.exit("the main pack's league_chogath differs from build_chogath.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not {key} = {p[key]}: update the add-on")
    if f'pub const STACK: &str = "{HERO}_r_stack";' not in src:
        sys.exit("src/lib.rs STACK is not the kit's r_stack")
    champion = kit.build(p)
    if "passive" in champion:
        sys.exit("the main pack's Cho'Gath has a passive now: update this script")
    champion["passive"] = {"passive_ref": f"{MOD_ID}:keep", "params": {}}
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
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
          champion["passive"]["passive_ref"])
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
