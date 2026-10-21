"""Build the add-on's copy of Neeko from the main pack (Inherent Glamour, the disguise as an ally).

    python addons/league_neeko/make_override.py

Rebuilds Neeko with tools/kit/build_neeko.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_neeko.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_neeko/override/league_neeko.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * passive = league_neeko:glamour (the disguise) with its numbers, and the picture league_neeko_p_poof it plays;
  * the attack's tooltip (description.league_neeko.attack, a key of the add-on's own id) names the passive, so the
    tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Neeko changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_neeko")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_neeko as kit  # noqa: E402
import setup_neeko as setup  # noqa: E402

MOD_ID = "league_neeko"
HERO = "league_neeko"
O, A, M, E = setup.O, setup.A, setup.M, setup.E
mag, t = setup.mag, setup.t
# lang -> the add-on's attack text (the passive and W's)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】" + O + "天生幻魅" + E + "：脱战" + t("{p_calm}秒") + "后假扮成最近的友方英雄；放技能、被控或受到{p_hp}%最大生命的伤害时现形，"
                  "放技能现形后{p_pen}%法术穿透" + t("{p_pen_t}秒") + "。" + O + "两生花影" + E + "：每第三次攻击额外" + mag("w_dmg", "w_ratio") +
                  "魔法伤害并加速。",
    },
    "zh-hant": {
        "attack": "【附加包】" + O + "原生模影" + E + "：脫戰" + t("{p_calm}秒") + "後偽裝成最近的友方英雄；施放技能、被控或受到{p_hp}%最大生命的傷害時現形，"
                  "施放技能現形後{p_pen}%魔法穿透" + t("{p_pen_t}秒") + "。" + O + "擬態分裂" + E + "：每第三次攻擊額外" + mag("w_dmg", "w_ratio") +
                  "魔法傷害並加速。",
    },
    "en": {
        "attack": "[Add-on] " + O + "Inherent Glamour" + E + ": after " + t("{p_calm}s") + " out of combat she disguises as the nearest "
                  "allied champion; casting, crowd control or {p_hp}% of her max health in damage reveals her, a cast with {p_pen}% "
                  "magic penetration for " + t("{p_pen_t}s") + ". " + O + "Shapesplitter" + E + ": every third attack deals " +
                  mag("w_dmg", "w_ratio") + " bonus " + M + "magic damage" + E + " and speeds her up.",
    },
    "ko": {
        "attack": "[확장] " + O + "태고의 마력" + E + ": 전투에서 " + t("{p_calm}초") + " 벗어나면 가장 가까운 아군 챔피언으로 변장. 스킬 사용, "
                  "군중 제어, 최대 체력 {p_hp}% 피해 시 해제, 스킬로 해제하면 " + t("{p_pen_t}초") + " 마법 관통력 {p_pen}%. " + O + "형상 분리" +
                  E + ": 세 번째 공격마다 " + mag("w_dmg", "w_ratio") + " 추가 마법 피해와 이동 속도.",
    },
    "ja": {
        "attack": "【拡張】" + O + "駆け巡る色彩" + E + "：戦闘を" + t("{p_calm}秒") + "離れると最寄りの味方チャンピオンに変装。スキル、"
                  "行動妨害、最大体力{p_hp}%のダメージで解除、スキルで解除すると" + t("{p_pen_t}秒") + "魔法防御貫通{p_pen}%。" + O +
                  "シェイプスプリッター" + E + "：3回目の攻撃ごとに" + mag("w_dmg", "w_ratio") + "の追加魔法ダメージと移動速度。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
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
        sys.exit("the main pack's league_neeko differs from build_neeko.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":glamour":
        sys.exit("the copy has no league_neeko:glamour passive: update this script")
    if not any(v["name"] == HERO + "_p_poof" for v in champion["view_effects"]):
        sys.exit("the copy lacks the p_poof picture the passive plays: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = dict(setup.values(p), p_hp=p["p_hp"], p_pen=p["p_pen"], p_calm=setup.secs(p["p_calm"]),
                  p_pen_t=setup.secs(p["p_pen_t"]))
    texts = {lang: {k: x.format(**values) for k, x in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(x) for lang, d in NATIVE.items() for k, x in d.items()
            if setup.shown_length(x) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(x)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, x in d.items()})


if __name__ == "__main__":
    main()
