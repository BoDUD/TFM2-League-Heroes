"""Build the add-on's copy of Rammus from the main pack (League V26.21's Spiked Shell, curl and rolling Powerball).

    python addons/league_rammus/make_override.py

Rebuilds Rammus with tools/kit/build_rammus.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_rammus.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_rammus/override/league_rammus.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the tumble, Defensive Ball Curl by the watch, Frenzying Taunt, Soaring Slam);
  * passive = the add-on's league_rammus:shell with the numbers of P it reads (build_rammus.NATIVE_KEYS, checked
    against the defaults in src/lib.rs): Spiked Shell's attack damage from his armour and MR, the curl's return of
    basic attacks, the rolling ball's speed and its touch;
  * the attack has no Spiked Shell magic and the curl no percentage reflect; rolling, his attack is the ball's impact;
  * Powerball only curls him up into the ball (q_ball) - the add-on rolls him and lays the touch (q_go) its 1-tick watch
    turns into the impact;
  * the attack's, skill's and skill2's tooltips point to description.league_rammus.<slot> with the add-on's wording.
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
SLOTS = ("attack", "skill", "skill2")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag = setup.mag
ARMi = "<i#asset/base/ui/banpick/champion_stat_icon:armor_0>"
APi = setup.APi


def shell(arm="护甲"):
    # p_ad_arm == p_ad_mr (main() checks): one share of armour + MR
    return f"获得{ARMi}{arm}与魔抗之和{M}{{p_ad_arm}}%{E}的攻击力"


def spit(arm="护甲"):
    return f"{M}{{w_hit}}{E}+{ARMi}{M}{{w_hit_arm}}%{E}{arm}+{M}{{w_hit_mr}}%{E}魔抗"


TEXT = {
    "zh-hans": {
        "attack": "【扩展包】翻身撞击。" + O + "锥刺甲壳" + E + "：" + shell() + "。" + O + "尖刺防御" + E +
                  "：敌方英雄靠近时蜷起来，" + A + "{w_t}秒" + E + "内护甲+{w_arm_s}（+{w_arm_p}%）、魔抗+{w_mr_s}（+{w_mr_p}%），"
                  "普攻他的敌人受到" + spit() + "魔法伤害；放动力冲刺、冲天猛撞时收起。",
        "skill": "【扩展包】缩成球滚动，越滚越快（移速每秒+{q_acc0}%~{q_acc1}%，随等级，最多" + A + "{q_ball_t}秒" + E + "），撞上第一个敌人"
                 "时对周围造成" + mag("q_dmg", "q_ap") + "魔法伤害，" + R + "击退" + E + "、" + R + "眩晕" + E + A + "{q_stun}秒" + E +
                 "并" + R + "减速{q_slow}%" + E + A + "{q_slow_t}秒" + E + "。",
        "skill2": "【扩展包】" + R + "嘲讽" + E + "一名敌方英雄" + A + "{e_taunt}秒" + E + "。滚动时不能施放。",
    },
    "zh-hant": {
        "attack": "【擴充包】翻身撞擊。" + O + "錐刺甲殼" + E + "：" +
                  shell("護甲").replace("获得", "獲得").replace("与", "與").replace("的攻击力", "的攻擊力") + "。" + O + "尖刺防禦" + E +
                  "：敵方英雄靠近時蜷起來，" + A + "{w_t}秒" + E + "內護甲+{w_arm_s}（+{w_arm_p}%）、魔抗+{w_mr_s}（+{w_mr_p}%），"
                  "普攻他的敵人受到" + spit("護甲") + "魔法傷害；施放動力衝刺、飛天動地時收起。",
        "skill": "【擴充包】縮成球滾動，越滾越快（移速每秒+{q_acc0}%~{q_acc1}%，隨等級，最多" + A + "{q_ball_t}秒" + E + "），撞上第一個敵人"
                 "時對周圍造成" + mag("q_dmg", "q_ap") + "魔法傷害，" + R + "擊退" + E + "、" + R + "暈眩" + E + A + "{q_stun}秒" + E +
                 "並" + R + "緩速{q_slow}%" + E + A + "{q_slow_t}秒" + E + "。",
        "skill2": "【擴充包】" + R + "嘲諷" + E + "一名敵方英雄" + A + "{e_taunt}秒" + E + "。滾動時不能施放。",
    },
    "en": {
        "attack": "[Add-on] A tumbling slam. " + O + "Spiked Shell" + E + ": bonus attack damage of " + M + "{p_ad_arm}%" + E +
                  " of his " + ARMi + "armour + magic resist. " + O + "Defensive Ball Curl" + E + ": near an "
                  "enemy champion he curls up for " + A + "{w_t}s" + E + ": +{w_arm_s} (+{w_arm_p}%) armour, +{w_mr_s} (+{w_mr_p}%) "
                  "magic resist, and his basic attackers take " + M + "{w_hit}" + E + " + " + ARMi + M + "{w_hit_arm}%" + E +
                  " armour + " + M + "{w_hit_mr}%" + E + " magic resist " + M + "magic damage" + E + "; Powerball or Soaring Slam "
                  "ends it.",
        "skill": "[Add-on] Curls into a ball and rolls, faster and faster (+{q_acc0}% to +{q_acc1}% move speed a second by level, "
                 "up to " + A + "{q_ball_t}s" + E + "); the first enemy he meets: nearby enemies take " + mag("q_dmg", "q_ap") + " " +
                 M + "magic damage" + E + ", are " + R + "knocked back" + E + ", " + R + "stunned" + E + " " + A + "{q_stun}s" + E +
                 " and " + R + "slowed {q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "[Add-on] " + R + "Taunts" + E + " an enemy champion for " + A + "{e_taunt}s" + E + ". Not while rolling.",
    },
    "ko": {
        "attack": "[확장] 몸통 박치기. " + O + "가시박힌 껍질" + E + ": " + ARMi + "방어력·마법 저항력 합의 " +
                  M + "{p_ad_arm}%" + E + "만큼 공격력 증가. " + O + "몸 말아 웅크리기" + E + ": 적 챔피언이 가까우면 웅크려 " + A +
                  "{w_t}초" + E + " 동안 방어력 +{w_arm_s}(+{w_arm_p}%), 마법 저항력 +{w_mr_s}(+{w_mr_p}%), 기본 공격한 적에게 " + M +
                  "{w_hit}" + E + "+" + ARMi + "방어력 " + M + "{w_hit_arm}%" + E + "+마법 저항력 " + M + "{w_hit_mr}%" + E +
                  " 마법 피해. 대회전·지진 폭격 시 풀림.",
        "skill": "[확장] 몸을 말아 점점 빠르게 굴러가고(이동 속도 매초 +{q_acc0}%~{q_acc1}%, 레벨 비례, 최대 " + A + "{q_ball_t}초" + E +
                 ") 처음 만난 적에게 부딪히면 주변 적에게 " + mag("q_dmg", "q_ap") + " 마법 피해, " + R + "밀쳐내기" + E + ", " + A +
                 "{q_stun}초" + E + " " + R + "기절" + E + ", " + A + "{q_slow_t}초" + E + " " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "[확장] 적 챔피언 하나를 " + A + "{e_taunt}초" + E + " " + R + "도발" + E + ". 구르는 동안에는 쓸 수 없음.",
    },
    "ja": {
        "attack": "【拡張】体当たり。" + O + "トゲトゲ" + E + "：" + ARMi + "物防と魔防の合計の" + M + "{p_ad_arm}%" +
                  E + "だけ攻撃力アップ。" + O + "かたくなる" + E + "：敵チャンピオンが近いと丸まり、" + A + "{w_t}秒" + E +
                  "物防+{w_arm_s}(+{w_arm_p}%)・魔防+{w_mr_s}(+{w_mr_p}%)、通常攻撃してきた敵に" + M + "{w_hit}" + E + "+" + ARMi +
                  "物防" + M + "{w_hit_arm}%" + E + "+魔防" + M + "{w_hit_mr}%" + E + "の魔法ダメージ。ころころ・どーんどーんで解除。",
        "skill": "【拡張】丸まって転がり、だんだん速くなる（移動速度毎秒+{q_acc0}%～{q_acc1}%、レベルで増加、最大" + A + "{q_ball_t}秒" +
                 E + "）。最初の敵にぶつかると周りの敵に" + mag("q_dmg", "q_ap") + "の魔法ダメージ、" + R + "ノックバック" + E + "、" + A +
                 "{q_stun}秒" + E + R + "スタン" + E + "と" + A + "{q_slow_t}秒" + E + "の" + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "【拡張】敵チャンピオン1体を" + A + "{e_taunt}秒" + E + R + "挑発" + E + "。転がっている間は使えない。",
    },
}

# every number the add-on reads from passive.params, against its default in src/lib.rs
CONSTS = {"p_ad_arm": "P_AD_ARM", "p_ad_mr": "P_AD_MR", "w_hit": "W_HIT", "w_hit_arm": "W_HIT_ARM", "w_hit_mr": "W_HIT_MR",
          "w_t": "W_T", "q_ball_t": "Q_BALL_T", "q_acc0": "Q_ACC0", "q_acc1": "Q_ACC1", "q_touch": "Q_TOUCH"}


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

    if set(CONSTS) != set(kit.NATIVE_KEYS):
        sys.exit("CONSTS here and build_rammus.NATIVE_KEYS differ: update this script")
    if p["p_ad_arm"] != p["p_ad_mr"]:
        sys.exit("the texts say one share of armour + MR (p_ad_arm == p_ad_mr): update TEXT")
    values = setup.values(p)
    values.update({k: p[k] for k in ("p_ad_arm", "p_ad_mr", "w_hit", "w_hit_arm", "w_hit_mr")})
    values["q_ball_t"] = setup.secs(p["q_ball_t"])
    values["q_acc0"] = round(p["q_acc0"] / 100)
    values["q_acc1"] = round(p["q_acc1"] / 100)
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
