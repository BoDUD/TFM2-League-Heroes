"""Build the add-on's copy of Neeko from the main pack (Inherent Glamour, the disguise as an ally).

    python addons/league_neeko/make_override.py

Rebuilds Neeko with tools/kit/build_neeko.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_neeko.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_neeko/override/league_neeko.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * passive = league_neeko:glamour (the disguise) with its numbers, and the picture league_neeko_p_poof it plays;
  * the attack's tooltip (description.league_neeko.attack, a key of the add-on's own id) names the passive, so the
    tooltip in game shows whether the override took;
  * 0.2.0: the same tooltip has one more sentence for W Shapesplitter's active, which the add-on casts itself
    (src/split.rs: no slot of the copy changed for it). Its numbers are League's, read from src/split.rs; the clone's
    attack (none: its reach and timing) must be her bolt's (build_neeko.P atk_range / atk_cd / atk_dur / a_rel) - a
    mismatch stops this script. The glamour sentence is a little shorter in every language to leave it the room
    (setup_neeko.TOOLTIP_MAX).
Every other champion stays untouched. Run it again whenever the main pack's Neeko changes.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_neeko")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_neeko as kit  # noqa: E402
import setup_neeko as setup  # noqa: E402
import generated  # noqa: E402  --check

MOD_ID = "league_neeko"
HERO = "league_neeko"
O, A, M, E = setup.O, setup.A, setup.M, setup.E
mag, t = setup.mag, setup.t
# lang -> the add-on's attack text (the passive and W's: its passive in her attack, 0.2.0 its active cast by the add-on)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】" + O + "天生幻魅" + E + "：脱战" + t("{p_calm}秒") + "后假扮成最近的队友；放技能、被控或挨{p_hp}%最大生命的伤害时现形，"
                  "施法现形后{p_pen}%法术穿透" + t("{p_pen_t}秒") + "。" + O + "两生花影" + E + "：每第三次攻击额外" + mag("w_dmg", "w_ratio") +
                  "魔法伤害并加速；挨重击时隐身" + t("{w_invis}秒") + "、加速，留下分身" + t("{w_life}秒") + "（" + t("{w_cd}秒") + "一次）。",
    },
    "zh-hant": {
        "attack": "【附加包】" + O + "原生模影" + E + "：脫戰" + t("{p_calm}秒") + "後偽裝成最近的隊友；施法、被控或受到{p_hp}%最大生命傷害時現形，"
                  "施法現形後{p_pen}%魔法穿透" + t("{p_pen_t}秒") + "。" + O + "擬態分裂" + E + "：每第三次攻擊額外" + mag("w_dmg", "w_ratio") +
                  "魔法傷害並加速；遭重擊時隱形" + t("{w_invis}秒") + "、加速，留下分身" + t("{w_life}秒") + "（" + t("{w_cd}秒") + "一次）。",
    },
    "en": {
        "attack": "[Add-on] " + O + "Inherent Glamour" + E + ": " + t("{p_calm}s") + " out of combat she disguises as the nearest ally; "
                  "a cast (then {p_pen}% magic pen " + t("{p_pen_t}s") + "), crowd control or {p_hp}% max health in damage reveals her. " +
                  O + "Shapesplitter" + E + ": every third attack deals " + mag("w_dmg", "w_ratio") + " bonus " + M + "magic damage" + E +
                  " and speeds her up; big hits make her vanish " + t("{w_invis}s") + " and leave a " + t("{w_life}s") + " clone (every " +
                  t("{w_cd}s") + ").",
    },
    "ko": {
        "attack": "[확장] " + O + "태고의 마력" + E + ": 전투에서 " + t("{p_calm}초") + " 벗어나면 가장 가까운 아군으로 변장. 스킬, "
                  "군중 제어, 최대 체력 {p_hp}% 피해 시 해제, 스킬로 해제하면 " + t("{p_pen_t}초") + " 마법 관통력 {p_pen}%. " + O + "형상 분리" +
                  E + ": 세 번째 공격마다 " + mag("w_dmg", "w_ratio") + " 추가 마법 피해와 이동 속도. 큰 피해 시 " + t("{w_invis}초") +
                  " 투명화와 가속, 분신 " + t("{w_life}초") + "(" + t("{w_cd}초") + "마다).",
    },
    "ja": {
        "attack": "【拡張】" + O + "駆け巡る色彩" + E + "：戦闘を" + t("{p_calm}秒") + "離れると近くの味方に変装。スキル、"
                  "行動妨害、最大体力{p_hp}%ダメージで解除、スキル解除で" + t("{p_pen_t}秒") + "魔法貫通{p_pen}%。" + O +
                  "シェイプスプリッター" + E + "：3回目の攻撃ごとに" + mag("w_dmg", "w_ratio") + "の魔法ダメージと加速。大ダメージで" +
                  t("{w_invis}秒") + "透明・加速、分身" + t("{w_life}秒") + "（" + t("{w_cd}秒") + "毎）。",
    },
}
SPLIT = os.path.join(ADDON, "src", "split.rs")
# the clone's attack constants in src/split.rs -> her bolt's parameters in build_neeko.P
CLONE_ATTACK = {"W_RANGE": "atk_range", "W_COOL": "atk_cd", "W_ACT": "atk_dur", "W_LANDS": "a_rel"}


def split_consts():
    """W's whole-number constants in src/split.rs (`pub const W_X: usize = 1_234;`)."""
    with open(lp(SPLIT), encoding="utf-8") as f:
        src = f.read()
    return {m.group(1): int(m.group(2).replace("_", ""))
            for m in re.finditer(r"pub const (W_[A-Z_]+): (?:usize|i32) = ([0-9_]+);", src)}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="CI: rebuild what does not need the game and fail if the committed files differ")
    a = ap.parse_args()
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

    w = split_consts()
    off = {k: (w.get(k), p[key]) for k, key in CLONE_ATTACK.items() if w.get(k) != p[key]}
    if off:
        sys.exit("src/split.rs: the clone's attack is not her bolt's (split.rs, build_neeko.P): %s" % off)
    missing_w = [k for k in ("W_INVIS", "W_LIFE", "W_CD") if k not in w]
    if missing_w:
        sys.exit("src/split.rs lacks %s: update this script" % missing_w)
    values = dict(setup.values(p), p_hp=p["p_hp"], p_pen=p["p_pen"], p_calm=setup.secs(p["p_calm"]),
                  p_pen_t=setup.secs(p["p_pen_t"]), w_invis=setup.secs(w["W_INVIS"]), w_life=setup.secs(w["W_LIFE"]),
                  w_cd=setup.secs(w["W_CD"]))
    texts = {lang: {k: x.format(**values) for k, x in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(x) for lang, d in NATIVE.items() for k, x in d.items()
            if setup.shown_length(x) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    copy_text = json.dumps(champion, ensure_ascii=False, indent=2) + "\n"
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    text_text = json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n"
    if a.check:
        generated.check(MOD_ID, [(out, copy_text), (out_text, text_text)])
        return
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(copy_text)
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(text_text)
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(x)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, x in d.items()})


if __name__ == "__main__":
    main()
