"""Build the add-on's copy of Rammus from the main pack (Spiked Shell by armour, League's rolling Powerball).

    python addons/league_rammus/make_override.py

Rebuilds Rammus with tools/kit/build_rammus.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_rammus.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_rammus/override/league_rammus.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the tumble, Defensive Ball Curl by the watch, Frenzying Taunt, Soaring Slam);
  * passive = the add-on's league_rammus:shell (the rolling ball's speed and its touch) with the numbers of P the add-on
    uses (checked against src/lib.rs's constants);
  * the attack's Spiked Shell is league_rammus:spikes (by his armour); rolling, his attack is the ball's impact;
  * Powerball only curls him up into the ball (q_ball) - the add-on rolls him and lays the touch (q_go) its 1-tick watch
    turns into the impact;
  * the attack's and skill's tooltips point to description.league_rammus.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Rammus changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_rammus")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_rammus as kit  # noqa: E402
import setup_rammus as setup  # noqa: E402

MOD_ID = "league_rammus"
HERO = "league_rammus"
SLOTS = ("attack", "skill")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag = setup.mag
ARMi = "<i#asset/base/ui/banpick/champion_stat_icon:armor_0>"
APi = setup.APi


def spikes():
    return f"{M}{{p_dmg}}{E} + {APi}{M}{{p_ap}}%{E} + {ARMi}{M}{{p_arm}}%{E}"


TEXT = {
    "zh-hans": {
        "attack": "【扩展包】翻身撞击。" + O + "锥刺甲壳" + E + "：普攻多造成" + spikes() + "魔法伤害。" + O + "尖刺防御" + E +
                  "：敌方英雄靠近时蜷起来，" + A + "{w_t}秒" + E + "内双抗+{w_def}%，反弹{w_ref}%受到的伤害。",
        "skill": "【扩展包】缩成球滚动，越滚越快（移速+{q_ms0}%到+{q_ms1}%，最多" + A + "{q_ball_t}秒" + E + "），撞上第一个敌人时对周围造成" +
                 mag("q_dmg", "q_ap") + "魔法伤害，" + R + "击退" + E + "并" + R + "减速{q_slow}%" + E + A + "{q_slow_t}秒" + E + "。",
    },
    "zh-hant": {
        "attack": "【擴充包】翻身撞擊。" + O + "錐刺甲殼" + E + "：普攻多造成" + spikes() + "魔法傷害。" + O + "尖刺防禦" + E +
                  "：敵方英雄靠近時蜷起來，" + A + "{w_t}秒" + E + "內雙抗+{w_def}%，反彈{w_ref}%受到的傷害。",
        "skill": "【擴充包】縮成球滾動，越滾越快（移速+{q_ms0}%到+{q_ms1}%，最多" + A + "{q_ball_t}秒" + E + "），撞上第一個敵人時對周圍造成" +
                 mag("q_dmg", "q_ap") + "魔法傷害，" + R + "擊退" + E + "並" + R + "緩速{q_slow}%" + E + A + "{q_slow_t}秒" + E + "。",
    },
    "en": {
        "attack": "[Add-on] A tumbling slam. " + O + "Spiked Shell" + E + ": attacks deal " + spikes() + " " + M + "magic damage" + E +
                  " more. " + O + "Defensive Ball Curl" + E + ": with an enemy champion close he curls up: for " + A + "{w_t}s" + E +
                  " +{w_def}% armour and magic resist, and {w_ref}% of the damage he takes is returned.",
        "skill": "[Add-on] Curls into a ball and rolls, faster and faster (+{q_ms0}% to +{q_ms1}% move speed, up to " + A +
                 "{q_ball_t}s" + E + "); the first enemy he meets: nearby enemies take " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + ", are " + R + "knocked back" + E + " and " + R + "slowed {q_slow}%" + E + " for " + A +
                 "{q_slow_t}s" + E + ".",
    },
    "ko": {
        "attack": "[확장] 몸통 박치기. " + O + "가시박힌 껍질" + E + ": 기본 공격이 " + spikes() + " 마법 피해 추가. " + O +
                  "몸 말아 웅크리기" + E + ": 적 챔피언이 가까우면 웅크려 " + A + "{w_t}초" + E + " 동안 방어력·마법 저항력 +{w_def}%, "
                  "받은 피해의 {w_ref}% 반사.",
        "skill": "[확장] 몸을 말아 점점 빠르게 굴러가고(이동 속도 +{q_ms0}%에서 +{q_ms1}%, 최대 " + A + "{q_ball_t}초" + E + ") 처음 만난 적에게 "
                 "부딪히면 주변 적에게 " + mag("q_dmg", "q_ap") + " 마법 피해, " + R + "밀쳐내기" + E + ", " + A + "{q_slow_t}초" + E + " " + R +
                 "{q_slow}% 둔화" + E + ".",
    },
    "ja": {
        "attack": "【拡張】体当たり。" + O + "トゲトゲ" + E + "：通常攻撃に" + spikes() + "の魔法ダメージ追加。" + O + "かたくなる" + E +
                  "：敵チャンピオンが近いと丸まり、" + A + "{w_t}秒" + E + "物防・魔防+{w_def}%、受けたダメージの{w_ref}%を反射。",
        "skill": "【拡張】丸まって転がり、だんだん速くなる（移動速度+{q_ms0}%から+{q_ms1}%、最大" + A + "{q_ball_t}秒" + E + "）。最初の敵に"
                 "ぶつかると周りの敵に" + mag("q_dmg", "q_ap") + "の魔法ダメージ、" + R + "ノックバック" + E + "と" + A + "{q_slow_t}秒" + E +
                 "の" + R + "{q_slow}%スロウ" + E + "。",
    },
}

CONSTS = {"p_dmg": "P_DMG", "p_ap": "P_AP", "p_arm": "P_ARM", "q_ms0": "Q_MS0", "q_ms1": "Q_MS1", "q_ramp": "Q_RAMP",
          "q_touch": "Q_TOUCH"}


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
        sys.exit("the main pack's league_rammus differs from build_rammus.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P[{key!r}] = {p[key]}: update the add-on")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":shell":
        sys.exit("the copy has no league_rammus:shell passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values.update({k: p[k] for k in ("p_arm", "q_ms0", "q_ms1")})
    values["q_ball_t"] = setup.secs(p["q_ball_t"])
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
