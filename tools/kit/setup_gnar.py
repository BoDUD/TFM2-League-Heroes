"""Gnar's text (5 languages), sound_info files and his keys in the shared files, numbers from build_gnar.P.

    python tools/kit/setup_gnar.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_gnar in every language, description + skill_name),
sound/sfx/league_gnar_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Gnar named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 纳尔 (迷失之牙): 狂怒基因, 投掷回力标 / 投掷顽石, 亢奋 / 痛殴, 轻跳 / 猛踏, 呐啊！; zh_TW 吶兒
(失落之子): 狂怒基因, 骨頭迴力鏢 / 巨岩拋擲, 野獸本能 / 原始衝撞, 吶兒跳跳 / 重磅輾壓, 狂嘯猛擊！; ja ナー: ぷんすこ, ブーメラン / ぽいっ,
ごきげん / こてんぱん, ぴょんぴょん / ドーン！, ナー！; ko 나르: 분노 유전자, 부메랑 던지기 / 돌덩이 던지기, 슝슝 / 쿵쾅, 폴짝 /
우지끈, 나르!. Slots: skill = Q (both forms), skill2 = E (both forms) with Mega's W, ult = R; Rage Gene and Mini's W
Hyper are in the attack's text. No combo sentence in any text (the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_gnar import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_gnar"
VERSION = "0.178.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # physical damage, AD, names
A = "<#ffb900ff>"      # durations, counts
C = "<#ef5350ff>"      # crowd control
W = "<#ffffffff>"      # move speed
R = "<#ffdd8eff>"      # health / armour / magic resistance
E = "<>"
# champion_view: provisional until the sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 0, "y": -19}, "center": {"x": 0, "y": -11}}


def phys(k, r="ratio"):
    return f"{O}{{{k}_dmg}}{E}+{ADi}{O}{{{k}_{r}}}%{E}"


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "纳尔",
        "attack": O + "狂怒基因" + E + "：迷你纳尔命中攒怒气，满后下个动作变" + O + "巨型纳尔" + E + t("{mega_t}秒") + "（近战，" + R +
                  "生命+{mg_hp}%、双抗+{mg_def}%" + E + "）。" + O + "亢奋" + E + "：每第3次攻击额外造成" + O + "{w_dmg}" + E +
                  "+英雄最大生命{w_hp}%的伤害，" + W + "移速+{w_ms}%" + E + "。",
        "skill": "迷你：回力标飞出再飞回，往返各造成" + phys("q") + O + "物理伤害" + E + "并" + C + "减速{q_slow}%" + E + "，接住后冷却变为" +
                 t("{q_catch}秒") + "。巨型：顽石砸中首个敌人，周围受到" + phys("q2") + O + "物理伤害" + E + "并" + C + "减速{q2_slow}%" + E +
                 "，捡回石头冷却变为" + t("{q_pick}秒") + "。",
        "skill2": "迷你：跳到敌人头上再弹远，造成" + O + "{e_dmg}" + E + "+自身最大生命{e_hp}%的伤害并" + C + "减速" + E + "。巨型：" + O + "猛踏" +
                  E + "落地造成" + O + "{c_dmg}" + E + "+最大生命{c_hp}%的伤害；" + O + "痛殴" + E + "重击前方，造成" + phys("w2") + O +
                  "物理伤害" + E + "并" + C + "眩晕" + E + t("{w2_stun}秒") + "。",
        "ult": "只有巨型纳尔能放（迷你纳尔怒气满时先变身）：把身边的敌人全部掀飞，造成" + phys("r") + O + "物理伤害" + E + "，" + C +
               "眩晕" + E + t("{r_stun}秒") + "并" + C + "减速{r_slow}%" + E + "。",
        "names": ("投掷回力标/投掷顽石", "轻跳/猛踏", "呐啊！"),
    },
    "zh-hant": {
        "name": "吶兒",
        "attack": O + "狂怒基因" + E + "：迷你吶兒命中累積怒氣，滿後下個動作變" + O + "巨型吶兒" + E + t("{mega_t}秒") + "（近戰，" + R +
                  "生命+{mg_hp}%、雙防+{mg_def}%" + E + "）。" + O + "野獸本能" + E + "：每第3次攻擊額外造成" + O + "{w_dmg}" + E +
                  "+英雄最大生命{w_hp}%的傷害，" + W + "跑速+{w_ms}%" + E + "。",
        "skill": "迷你：迴力鏢飛出再飛回，往返各造成" + phys("q") + O + "物理傷害" + E + "並" + C + "緩速{q_slow}%" + E + "，接住後冷卻變為" +
                 t("{q_catch}秒") + "。巨型：巨岩砸中首個敵人，周圍受到" + phys("q2") + O + "物理傷害" + E + "並" + C + "緩速{q2_slow}%" + E +
                 "，撿回石頭冷卻變為" + t("{q_pick}秒") + "。",
        "skill2": "迷你：跳到敵人頭上再彈遠，造成" + O + "{e_dmg}" + E + "+自身最大生命{e_hp}%的傷害並" + C + "緩速" + E + "。巨型：" + O +
                  "重磅輾壓" + E + "落地造成" + O + "{c_dmg}" + E + "+最大生命{c_hp}%的傷害；" + O + "原始衝撞" + E + "重擊前方，造成" +
                  phys("w2") + O + "物理傷害" + E + "並" + C + "暈眩" + E + t("{w2_stun}秒") + "。",
        "ult": "只有巨型吶兒能施放（迷你吶兒怒氣滿時先變身）：把身邊的敵人全部掀飛，造成" + phys("r") + O + "物理傷害" + E + "，" + C +
               "暈眩" + E + t("{r_stun}秒") + "並" + C + "緩速{r_slow}%" + E + "。",
        "names": ("骨頭迴力鏢/巨岩拋擲", "吶兒跳跳/重磅輾壓", "狂嘯猛擊！"),
    },
    "en": {
        "name": "Gnar",
        "attack": O + "Rage Gene" + E + ": Mini Gnar's hits build Rage; at full Rage his next action turns him " + O + "Mega Gnar" + E +
                  " for " + t("{mega_t}s") + " (melee, " + R + "+{mg_hp}% health, +{mg_def}% armour and magic resist" + E + "). " +
                  O + "Hyper" + E + ": every third attack deals " + O + "{w_dmg}" + E + " + {w_hp}% of a champion's max health more "
                  "and grants " + W + "{w_ms}% move speed" + E + ".",
        "skill": "Mini: a boomerang flies out and back, each pass dealing " + phys("q") + " " + O + "physical damage" + E + " and " +
                 C + "slowing {q_slow}%" + E + "; caught, its cooldown becomes " + t("{q_catch}s") + ". Mega: a boulder stops on "
                 "the first enemy, dealing " + phys("q2") + " " + O + "physical damage" + E + " around it and " + C +
                 "slowing {q2_slow}%" + E + "; picked up, its cooldown becomes " + t("{q_pick}s") + ".",
        "skill2": "Mini: hops onto an enemy's head and bounces on, dealing " + O + "{e_dmg}" + E + " + {e_hp}% of his max health "
                  "and " + C + "slowing" + E + " it. Mega: " + O + "Crunch" + E + " lands for " + O + "{c_dmg}" + E + " + {c_hp}% of "
                  "his max health around him; " + O + "Wallop" + E + " smashes the ground ahead for " + phys("w2") + " " + O +
                  "physical damage" + E + " and a " + t("{w2_stun}s") + " " + C + "stun" + E + ".",
        "ult": "Mega Gnar only (Mini Gnar at full Rage transforms first): throws every enemy around him away, dealing " +
               phys("r") + " " + O +
               "physical damage" + E + ", " + C + "stunning" + E + " them for " + t("{r_stun}s") + " and " + C +
               "slowing {r_slow}%" + E + ".",
        "names": ("Boomerang Throw / Boulder Toss", "Hop / Crunch", "GNAR!"),
    },
    "ko": {
        "name": "나르",
        "attack": O + "분노 유전자" + E + ": 꼬마 나르가 적중하면 분노가 쌓이고, 가득 차면 다음 행동에 " + t("{mega_t}초") + " 동안 " + O +
                  "메가 나르" + E + "로 변신(근접, " + R + "체력 +{mg_hp}%, 방어력·마법 저항력 +{mg_def}%" + E + "). " + O + "슝슝" + E +
                  ": 세 번째 공격마다 " + O + "{w_dmg}" + E + "+챔피언 최대 체력의 {w_hp}% 추가 피해, " + W + "이동 속도 +{w_ms}%" + E + ".",
        "skill": "꼬마: 부메랑이 날아갔다 돌아오며 매번 " + phys("q") + " " + O + "물리 피해" + E + "와 " + C + "{q_slow}% 둔화" + E +
                 ", 받으면 재사용 대기시간 " + t("{q_catch}초") + ". 메가: 돌덩이가 첫 적에게 멈춰 주변에 " + phys("q2") + " " + O +
                 "물리 피해" + E + "와 " + C + "{q2_slow}% 둔화" + E + ", 주우면 재사용 대기시간 " + t("{q_pick}초") + ".",
        "skill2": "꼬마: 적의 머리를 밟고 더 멀리 튀어 " + O + "{e_dmg}" + E + "+자신 최대 체력의 {e_hp}% 피해와 " + C + "둔화" + E +
                  ". 메가: " + O + "우지끈" + E + " 착지 시 " + O + "{c_dmg}" + E + "+최대 체력의 {c_hp}% 피해; " + O + "쿵쾅" + E +
                  "으로 앞을 내리쳐 " + phys("w2") + " " + O + "물리 피해" + E + "와 " + t("{w2_stun}초") + " " + C + "기절" + E + ".",
        "ult": "메가 나르만 사용(꼬마 나르는 분노가 가득 차면 먼저 변신): 주변 적을 모두 내던져 " + phys("r") + " " + O + "물리 피해" + E + ", " +
               t("{r_stun}초") + " " + C + "기절" + E + ", " + C + "{r_slow}% 둔화" + E + ".",
        "names": ("부메랑 던지기 / 돌덩이 던지기", "폴짝 / 우지끈", "나르!"),
    },
    "ja": {
        "name": "ナー",
        "attack": O + "ぷんすこ" + E + "：ミニ・ナーの命中で怒りが溜まり、最大で次の行動から" + t("{mega_t}秒") + O + "メガ・ナー" + E +
                  "に変身（近接、" + R + "体力+{mg_hp}%、物防・魔防+{mg_def}%" + E + "）。" + O + "ごきげん" + E + "：3回目の攻撃ごとに" +
                  O + "{w_dmg}" + E + "+チャンピオンの最大体力{w_hp}%の追加ダメージ、" + W + "移動速度+{w_ms}%" + E + "。",
        "skill": "ミニ：ブーメランが往復し、毎回" + phys("q") + "の" + O + "物理ダメージ" + E + "と" + C + "{q_slow}%スロウ" + E +
                 "、キャッチでCD" + t("{q_catch}秒") + "。メガ：岩が最初の敵で止まり周囲に" + phys("q2") + "の" + O + "物理ダメージ" + E +
                 "と" + C + "{q2_slow}%スロウ" + E + "、拾うとCD" + t("{q_pick}秒") + "。",
        "skill2": "ミニ：敵の頭を踏んでさらに跳び、" + O + "{e_dmg}" + E + "+自身の最大体力{e_hp}%のダメージと" + C + "スロウ" + E +
                  "。メガ：" + O + "ドーン！" + E + "の着地で" + O + "{c_dmg}" + E + "+最大体力{c_hp}%のダメージ、" + O + "こてんぱん" +
                  E + "で前方を叩き" + phys("w2") + "の" + O + "物理ダメージ" + E + "と" + t("{w2_stun}秒") + C + "スタン" + E + "。",
        "ult": "メガ・ナー専用（ミニ・ナーは怒り最大で先に変身）：周囲の敵をすべて投げ飛ばし、" + phys("r") + "の" + O + "物理ダメージ" + E + "、" +
               t("{r_stun}秒") + C + "スタン" + E + "、" + C + "{r_slow}%スロウ" + E + "。",
        "names": ("ブーメラン/ぽいっ", "ぴょんぴょん/ドーン！", "ナー！"),
    },
}

CL = "league_gnar_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_gnar_{k}": [(CL + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("a_hyper", 0.45), ("q", 0.4), ("q_hit", 0.35), ("q_catch", 0.4), ("e", 0.4),
    ("e_hit", 0.4), ("full", 0.45), ("tf_mega", 0.55), ("tf_mini", 0.45), ("m_a", 0.35), ("m_hit", 0.4), ("q2", 0.45),
    ("q2_hit", 0.45), ("q_land", 0.4), ("q_pick", 0.4), ("w", 0.4), ("w_land", 0.5), ("w_hit", 0.35), ("c", 0.4),
    ("c_land", 0.5), ("c_hit", 0.35), ("r", 0.45), ("r_land", 0.55), ("r_hit", 0.4), ("vo_q", 0.85), ("vo_e", 0.85),
    ("vo_mega", 0.9), ("vo_big", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("mg_hp", "mg_def", "w_dmg", "w_hp", "w_ms", "q_dmg", "q_ratio", "q_slow", "q2_dmg", "q2_ratio",
                           "q2_slow", "e_dmg", "e_hp", "c_dmg", "c_hp", "w2_dmg", "w2_ratio", "r_dmg", "r_ratio", "r_slow")}
    for k in ("mega_t", "q_catch", "q_pick", "w2_stun", "r_stun"):
        v[k] = secs(p[k])
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def texts(p):
    v = values(p)
    out = {}
    for lang, t_ in TEXT.items():
        d = {"name": t_["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = t_[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), t_["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 + the idle's top over the frame centre)")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n > TOOLTIP_MAX[lang] for n in lens.values())
        print(lang, " ".join(f"{k}:{n}/{TOOLTIP_MAX[lang]}" for k, n in lens.items()))
    if a.check:
        sys.stdout.reconfigure(encoding="utf-8")
        for lang, (d, _) in tx.items():
            for k in ("attack", "skill", "skill2", "ult"):
                print(lang, k, re.sub(r"<[^>]*>", "", d[k]))
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"))
    for lang, (d, names) in tx.items():
        i18n[lang]["description"][ID] = d
        i18n[lang]["skill_name"][ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    for name, plays in SOUNDS.items():
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"))
    for k in [k for k in ov if ID + "_" in k]:      # his keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in list(SOUNDS) + CLIPS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a.face:
        x, y = (int(v) for v in a.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a.banpick is not None:
        if a.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Gnar" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Gnar. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
