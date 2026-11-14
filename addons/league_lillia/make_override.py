"""Build the add-on's copy of Lillia from the main pack (Dream Dust as % max-health magic, a sleep that breaks on damage).

    python addons/league_lillia/make_override.py

Rebuilds Lillia with tools/kit/build_lillia.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_lillia.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_lillia/override/league_lillia.data_champion and .../text/champion.i18n: build(p, native=True) -
  * the champion dust is the buff league_lillia_dust (the data's true-damage AddCasted and R's listener in it go),
    the data's wake twins go, and passive = league_lillia:dream with native_params(P) as its params;
  * the attack's (the passive) and the ult's tooltips point to description.league_lillia.attack / .ult with a "test
    build" lead and the add-on's rules, so the tooltip in game shows whether the override took;
  * E's seed rolls on (2026-11-14, League's Swirlseed): a landing that hit nobody calls league_lillia:e_roll a tick
    later (the add-on sends the rolling seed from the landing point), with the two pictures of the rolling seed
    (league_lillia_e_roll / _e_roll_l: tags e_roll / e_roll_l of the main pack's league_lillia_fx, drawn by
    tools/art/fx_lillia_roll.py); E's tooltip (description.league_lillia.skill2) is the main pack's with a "test
    build" lead and one sentence on the roll after the seed's.
Every other champion stays untouched. Run it again whenever the main pack's Lillia changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_lillia")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_lillia as kit  # noqa: E402
import setup_lillia as setup  # noqa: E402

MOD_ID = "league_lillia"
A, E, O, R, M, SPi, Wh = setup.A, setup.E, setup.O, setup.R, setup.M, setup.SPi, setup.Wh
mag, hea = setup.mag, setup.hea
PCT = "{d_hp_pct}% + " + setup.APi + "{d_ap_pct}%"
# lang -> (attack, ult) of the test build
NATIVE = {
    "zh-hans": (
        "【梦尘测试版】被动" + O + "梦满枝" + E + "：技能命中英雄时附上" + O + "梦尘" + E + "，每" + A + "{period}秒" + E + "造成" + PCT +
        "最大生命值的" + M + "魔法伤害" + E + "，并回复她" + hea("d_heal", "d_heal_ratio") + "生命；对其他敌人造成" +
        mag("d_dmg", "d_ratio") + "。施法叠" + O + "腾跃" + E + "，每层" + SPi + Wh + "移速+{pr_ms}%" + E + "。",
        "【昏睡测试版】所有带梦尘的敌方英雄" + R + "困倦" + E + A + "{r_drowsy}秒" + E + "（" + R + "减速{r_slow}%" + E + "），随后" + R +
        "昏睡" + E + A + "{n_sleep}秒" + E + "；受到任何伤害就会醒来，并额外受到" + mag("r_wake", "r_wake_ratio") + M + "魔法伤害" + E +
        "。"),
    "zh-hant": (
        "【夢境之塵測試版】被動" + O + "夢沉枝枒" + E + "：技能命中英雄時附上" + O + "夢境之塵" + E + "，每" + A + "{period}秒" + E + "造成" +
        PCT + "最大生命值的" + M + "魔法傷害" + E + "，並回復她" + hea("d_heal", "d_heal_ratio") + "生命；對其他敵人造成" +
        mag("d_dmg", "d_ratio") + "。施法疊加跑速，每層" + SPi + Wh + "移速+{pr_ms}%" + E + "。",
        "【沉睡測試版】所有帶夢境之塵的敵方英雄" + R + "疲倦" + E + A + "{r_drowsy}秒" + E + "（" + R + "緩速{r_slow}%" + E + "），隨後" +
        R + "沉睡" + E + A + "{n_sleep}秒" + E + "；受到任何傷害就會醒來，並額外受到" + mag("r_wake", "r_wake_ratio") + M + "魔法傷害" +
        E + "。"),
    "en": (
        "[Dream Dust test build] Passive " + O + "Dream-Laden Bough" + E + ": her ability hits on champions leave " + O +
        "Dream Dust" + E + ": every " + A + "{period}s" + E + " " + PCT + " of their max health as " + M + "magic damage" + E +
        ", and she heals " + hea("d_heal", "d_heal_ratio") + "; other enemies take " + mag("d_dmg", "d_ratio") +
        ". Each cast stacks " + O + "Prance" + E + ": " + SPi + Wh + "+{pr_ms}% Move Speed" + E + ".",
        "[Sleep test build] Every enemy champion with Dream Dust turns " + R + "Drowsy" + E + " (" + R + "{r_slow}% slow" + E +
        ") for " + A + "{r_drowsy}s" + E + ", then falls " + R + "Asleep" + E + " for " + A + "{n_sleep}s" + E +
        "; any damage wakes them, with " + mag("r_wake", "r_wake_ratio") + " more " + M + "magic damage" + E + "."),
    "ko": (
        "[꿈가루 테스트판] 기본 지속 효과 " + O + "꿈나무 지팡이" + E + ": 스킬이 챔피언에게 적중하면 " + O + "꿈가루" + E + ": " + A +
        "{period}초" + E + "마다 최대 체력의 " + PCT + " " + M + "마법 피해" + E + ", 릴리아는 " + hea("d_heal", "d_heal_ratio") +
        " 회복. 다른 적은 " + mag("d_dmg", "d_ratio") + ". 스킬마다 " + SPi + Wh + "이동 속도 {pr_ms}%" + E + " 중첩.",
        "[수면 테스트판] 꿈가루가 묻은 모든 적 챔피언이 " + A + "{r_drowsy}초" + E + " " + R + "졸음" + E + "(" + R + "{r_slow}% 둔화" +
        E + ") 후 " + A + "{n_sleep}초" + E + " " + R + "잠듭니다" + E + ". 피해를 입으면 깨어나며 " + mag("r_wake", "r_wake_ratio") +
        "의 " + M + "마법 피해" + E + "를 추가로 받습니다."),
    "ja": (
        "【夢のかけらテスト版】パッシブ " + O + "夢を集める大枝" + E + "：スキルがチャンピオンに命中で" + O + "夢のかけら" + E + "、" +
        A + "{period}秒" + E + "ごとに最大体力の" + PCT + "の" + M + "魔法ダメージ" + E + "、リリアは" + hea("d_heal", "d_heal_ratio") +
        "回復。他の敵には" + mag("d_dmg", "d_ratio") + "。スキルごとに" + SPi + Wh + "移動速度{pr_ms}%" + E + "。",
        "【睡眠テスト版】夢のかけらを受けた敵チャンピオン全員に" + R + "眠気" + E + A + "{r_drowsy}秒" + E + "（" + R + "{r_slow}%スロウ" +
        E + "）、その後" + R + "睡眠" + E + A + "{n_sleep}秒" + E + "。ダメージを受けると目覚め、" + mag("r_wake", "r_wake_ratio") +
        "の" + M + "魔法ダメージ" + E + "を追加で受ける。"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# E: lang -> (lead, where the seed's sentence ends, the roll's sentence put right after it)
ROLL = {
    "zh-hans": ("【滚种测试版】", "。", "落点没有敌人就继续往前滚，碰到敌人或地形才炸开。"),
    "zh-hant": ("【滾種測試版】", "。", "落點沒有敵人就繼續往前滾，碰到敵人或地形才炸開。"),
    "en": ("[Rolling seed test build] ", ".", " Landing on no enemy, it rolls on until it hits an enemy or terrain."),
    "ko": ("[구르는 씨앗 테스트판] ", ".", " 착지 지점에 적이 없으면 계속 굴러가 적이나 지형에 닿을 때 터집니다."),
    "ja": ("【転がる種テスト版】", "。", "着地点に敵がいなければ転がり続け、敵か地形に当たると炸裂。"),
}


def e_text(lang, main):
    """E's tooltip: the main pack's, the roll's sentence after the seed's (its first, the one with the slow)."""
    lead, stop, roll = ROLL[lang]
    at = main.find(stop)
    if at < 0 or "<#ef5350ff>" not in main[:at]:
        sys.exit(f"{lang}: the main pack's E text no longer opens with the seed's sentence (with its slow): update this script")
    return lead + main[:at + len(stop)] + roll + main[at + len(stop):]


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_lillia.data_champion")), encoding="utf-8",
              newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_lillia differs from build_lillia.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != f"{MOD_ID}:dream":
        sys.exit("the native build has no league_lillia:dream passive: update this script")
    text = json.dumps(champion)
    if "w_wake" in text or '"FixedAttack"' in text or "league_lillia_dust" not in text:
        sys.exit("the native build still has the data's dust or wake twins: update this script")
    views = {v["name"]: v.get("tag") for v in champion["view_projectiles"]}
    if text.count('"effect_ref": "league_lillia:e_roll"') != 1 or views.get("league_lillia_e_roll") != "e_roll" \
            or views.get("league_lillia_e_roll_l") != "e_roll_l":
        sys.exit("the native build does not hand an unhit landing to league_lillia:e_roll with both pictures: update this script")
    with open(lp(os.path.join(ROOT, "league", "effects", "league_lillia_fx#anim.fanim")), encoding="utf-8") as f:
        tags = json.load(f)["anims"]
    if any(t not in tags for t in ("e_roll", "e_roll_l", "hd_e_roll", "hd_e_roll_l")):
        sys.exit("league_lillia_fx has no rolling seed: python -I tools/art/fx_lillia_roll.py")
    for k in ("attack", "skill2", "ult"):
        champion[k]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + k

    v = setup.values(p)
    v.update(period=setup.secs(p["d_period"]), n_sleep=setup.secs(p["n_sleep"]),
             d_hp_pct=f"{p['d_hp']:g}", d_ap_pct=f"{p['d_ap_bp'] / 100:g}")
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: {"attack": pair[0].format(**v), "skill2": e_text(lang, main_text[lang]["description"][MOD_ID]["skill2"]),
                    "ult": pair[1].format(**v)} for lang, pair in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in texts.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_lillia.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text}, ensure_ascii=False,
                           indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
