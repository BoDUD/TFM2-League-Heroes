"""Build the add-on's copy of Zed from the main pack (Contempt for the Weak from real health, Death Mark from the damage
dealt).

    python addons/league_zed_mark/make_override.py

Rebuilds Zed with tools/kit/build_zed.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zed.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zed_mark/override/league_zed.data_champion and .../text/champion.i18n: the build with native=1 -
  * no data stand-ins: no cw_ready after a spell hit, no r_1..r_3 hit ladder (his attack marks the champion it hits
    with `league_zed_cw_probe` instead, and the burst keeps its base damage);
  * passive = the add-on's league_zed_mark:edge with {cw_hp, cw_lo, cw_mid, cw_hi, cw_cd, r_pct}: Contempt below
    cw_hp% health (6/8/10% of the max as magic damage by his level, cw_cd per target) and r_pct% of the damage he
    dealt under the mark added at the burst;
  * the attack's and the ult's tooltips point to description.league_zed_mark.attack / .ult with a "test build" lead
    and the add-on's wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Zed changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zed_mark")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zed as kit  # noqa: E402
import setup_zed as setup  # noqa: E402

MOD_ID = "league_zed_mark"
HERO = "league_zed"
A, O, E = setup.A, setup.O, setup.E
# lang -> (the lead, [(the main pack's wording, the add-on's wording) in the attack text], [(...) in the ult text])
NATIVE = {
    "zh-hans": ("【读血测试版】",
                [("技能命中英雄后，下次攻击英雄附加其{cw_pct}%最大生命真实伤害（" + A + "{cw_cd}秒" + E + "）",
                  "攻击生命低于{cw_hp}%的英雄时附加其{cw_lo}/{cw_mid}/{cw_hi}%最大生命魔法伤害（同一目标" + A + "{cw_cd}秒" + E + "）")],
                [("，期间每次命中+" + O + "{r_per}" + E + "（最多3次）", "，外加期间所造成伤害的" + O + "{r_pct}%" + E), ('击杀、被包围或被控时，和影子互换位置', '击杀、被包围、被控或生命低于{r_low}%时，和影子互换位置')]),
    "zh-hant": ("【讀血測試版】",
                [("技能命中英雄後，下次攻擊英雄附加其{cw_pct}%最大生命真實傷害（" + A + "{cw_cd}秒" + E + "）",
                  "攻擊生命低於{cw_hp}%的英雄時附加其{cw_lo}/{cw_mid}/{cw_hi}%最大生命魔法傷害（同一目標" + A + "{cw_cd}秒" + E + "）")],
                [("，期間每次命中+" + O + "{r_per}" + E + "（最多3次）", "，外加期間所造成傷害的" + O + "{r_pct}%" + E), ('擊殺、被包圍或被控時，和影子互換位置', '擊殺、被包圍、被控或生命低於{r_low}%時，和影子互換位置')]),
    "en": ("[Health-reading test build] ",
           [("after his spells hit a champion, his next attack on a champion adds {cw_pct}% of its max health as true damage (" +
             A + "{cw_cd}s" + E + ")",
             "his attacks on a champion below {cw_hp}% health add {cw_lo}/{cw_mid}/{cw_hi}% of its max health as magic damage "
             "(" + A + "{cw_cd}s" + E + " per target)")],
           [(" plus " + O + "{r_per}" + E + " per hit meanwhile (up to 3)", " plus " + O + "{r_pct}%" + E + " of the damage he dealt "
             "meanwhile"), ('On a kill, outnumbered or crowd-controlled,', 'On a kill, outnumbered, crowd-controlled or below {r_low}% health,')]),
    "ko": ("[체력 판정 테스트판] ",
           [("스킬이 챔피언에게 적중한 뒤 다음 챔피언 공격은 대상 최대 체력의 {cw_pct}% 고정 피해(" + A + "{cw_cd}초" + E + ")",
             "체력 {cw_hp}% 미만 챔피언 공격 시 최대 체력의 {cw_lo}/{cw_mid}/{cw_hi}% 마법 피해(대상마다 " + A + "{cw_cd}초" + E + ")")],
           [(", 그동안 적중마다 +" + O + "{r_per}" + E + "(최대 3)", ", 그동안 준 피해의 " + O + "{r_pct}%" + E + " 추가"), ('처치·포위·군중 제어 시', '처치·포위·군중 제어·체력 {r_low}% 미만 시')]),
    "ja": ("【体力判定テスト版】",
           [("スキルがチャンピオンに命中後、次のチャンピオンへの攻撃が最大体力の{cw_pct}%確定ダメージ（" + A + "{cw_cd}秒" + E + "）",
             "体力{cw_hp}%未満のチャンピオンへの攻撃が最大体力の{cw_lo}/{cw_mid}/{cw_hi}%魔法ダメージ（同じ対象" + A + "{cw_cd}秒" + E + "）")],
           [("、その間の命中ごとに+" + O + "{r_per}" + E + "（最大3）", "、その間に与えたダメージの" + O + "{r_pct}%" + E + "を追加"), ('撃破・包囲・行動妨害で', '撃破・包囲・行動妨害・体力{r_low}%未満で')]),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_zed.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_zed differs from build_zed.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if "league_zed_cw_ready" in text or "league_zed_r_1" in text:
        sys.exit("the copy still has the data stand-ins: update this script")
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":edge":
        sys.exit("the copy has no league_zed_mark:edge passive: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    champion["ult"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".ult"

    values = dict(setup.values(p), **{k: p[k] for k in ("cw_hp", "cw_lo", "cw_mid", "cw_hi", "r_pct", "r_low")})
    texts = {}
    for lang, (lead, att, ult) in NATIVE.items():
        out = {}
        for key, swaps in (("attack", att), ("ult", ult)):
            t = setup.TEXT[lang][key]
            for old, new in swaps:
                if t.count(old) != 1:
                    sys.exit(f"{lang} {key}: the main pack's text changed ({old!r} not found once): update NATIVE")
                t = t.replace(old, new)
            out[key] = ((lead if key == "attack" else "") + t).format(**values)
        texts[lang] = out
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in texts.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_zed.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
