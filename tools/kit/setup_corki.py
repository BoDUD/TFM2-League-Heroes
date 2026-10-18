"""Corki's text (5 languages), sound_info files and his keys in the shared files, numbers from build_corki.P.

    python tools/kit/setup_corki.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_corki in every language, description + skill_name),
sound/sfx/league_corki_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.102.0, Corki named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (库奇 / 英勇投弹手; 海克斯科技军备, 磷光炸弹, 瓦尔基里俯冲, 格林机枪, 火箭轰击, 特别快递;
the client swaps name and title) and Data Dragon 16.20.1 (zh_TW 庫奇 / 海克斯軍火 / 磷光炸彈 / 女武神特攻 / 格林機槍 / 火箭轟擊,
ja コーキ / ヘクステック榴散弾 / 閃光弾 / ワルキューレ機行 / ガトリングガン / 連発ミサイル, ko 코르키 / 마법공학 탄약 / 인광탄 / 발키리 /
개틀링 건 / 미사일 폭격). Slots: skill = Q, skill2 = E (Valkyrie, W, told in its text), ult = R; the passive and the
Package are told in the attack's text. No combo sentence in any text (the user's rule). No `league_corki_attack`
sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_corki import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_corki"
VERSION = "0.102.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
Wh = "<#ffffffff>"     # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# 2026-10-18 ban/pick card audit (frame centre, HD from lo_idle / 1.5; user: 「还有哪些英雄BP位置不对的一起改了」): none -> -10: 1 px over the card's top edge (Talon's rule: at or above -28)
VIEW = {"face": {"x": 3, "y": -33}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -10}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E}"


def ad(k):
    return f"{ADi}{O}{{{k}_ad}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "库奇",
        "attack": O + "海克斯科技军备" + E + "：普攻" + Wh + "{p_true}%" + E + "伤害转为" + Wh + "真实伤害" + E + "。" + O + "特别快递" + E +
                  "：开局、复活后及每" + A + "{pk_cd}秒" + E + "，下次瓦尔基里俯冲变成弹药包：起飞时" + R + "击退" + E + "附近英雄并造成" +
                  mag("pk") + M + "魔法伤害" + E + "，飞得更远、火焰更宽更久，加速{pk_ms}%。",
        "skill": "向目标位置扔出磷光炸弹，范围内敌人受到" + mag("q") + M + "魔法伤害" + E + "和" + ad("q") + O + "物理伤害" + E + "。",
        "skill2": O + "格林机枪" + E + "：" + A + "{e_t}秒" + E + "内向前方锥形扫射，每次造成" + O + "{e_dmg}" + E + " + " + ad("e") + O + "物理" +
                  E + "和" + APi + M + "{e_ap}%魔法伤害" + E + "，叠加降低护甲和魔抗。冷却中被英雄贴近时改为" + O + "瓦尔基里俯冲" + E +
                  "：向后俯冲，沿途留下火焰，每" + A + "{w_per}秒" + E + "造成" + mag("w") + M + "魔法伤害" + E + "。",
        "ult": "储存" + A + "{r_n}发" + E + "火箭（每" + A + "{r_rech}秒" + E + "补一发），命中第一个敌人后爆炸，范围内造成" + mag("r") + M +
               "魔法伤害" + E + "和" + ad("r") + O + "物理伤害" + E + "；每第3发是大火箭：范围更大，伤害{r_big}%。",
        "names": ("磷光炸弹", "格林机枪", "火箭轰击"),
    },
    "zh-hant": {
        "name": "庫奇",
        "attack": O + "海克斯軍火" + E + "：普攻" + Wh + "{p_true}%" + E + "傷害轉為" + Wh + "真實傷害" + E + "。" + O + "特別快遞" + E +
                  "：開局、復活後及每" + A + "{pk_cd}秒" + E + "，下次女武神特攻變成彈藥包：起飛時" + R + "擊退" + E + "附近英雄並造成" +
                  mag("pk") + M + "魔法傷害" + E + "，飛得更遠、火焰更寬更久，加速{pk_ms}%。",
        "skill": "向目標位置扔出磷光炸彈，範圍內敵人受到" + mag("q") + M + "魔法傷害" + E + "和" + ad("q") + O + "物理傷害" + E + "。",
        "skill2": O + "格林機槍" + E + "：" + A + "{e_t}秒" + E + "內向前方錐形掃射，每次造成" + O + "{e_dmg}" + E + " + " + ad("e") + O + "物理" +
                  E + "和" + APi + M + "{e_ap}%魔法傷害" + E + "，疊加降低護甲和魔抗。冷卻中被英雄貼近時改為" + O + "女武神特攻" + E +
                  "：向後俯衝，沿途留下火焰，每" + A + "{w_per}秒" + E + "造成" + mag("w") + M + "魔法傷害" + E + "。",
        "ult": "儲存" + A + "{r_n}發" + E + "火箭（每" + A + "{r_rech}秒" + E + "補一發），命中第一個敵人後爆炸，範圍內造成" + mag("r") + M +
               "魔法傷害" + E + "和" + ad("r") + O + "物理傷害" + E + "；每第3發是大火箭：範圍更大，傷害{r_big}%。",
        "names": ("磷光炸彈", "格林機槍", "火箭轟擊"),
    },
    "en": {
        "name": "Corki",
        "attack": O + "Hextech Munitions" + E + ": {p_true}% of his attacks' damage is " + Wh + "true damage" + E + ". " + O +
                  "Special Delivery" + E + ": at the start, after a respawn and every " + A + "{pk_cd}s" + E + " his next Valkyrie is the "
                  "Package: the take-off " + R + "knocks back" + E + " champions near him for " + mag("pk") + " " + M + "magic damage" + E +
                  ", he flies farther, the fire is wider and lasts longer, and he gains {pk_ms}% move speed.",
        "skill": "Lobs a phosphorus bomb at a spot: enemies in the blast take " + mag("q") + " " + M + "magic damage" + E + " and " +
                 ad("q") + " " + O + "physical damage" + E + ".",
        "skill2": O + "Gatling Gun" + E + ": sprays a cone ahead for " + A + "{e_t}s" + E + ", each burst " + O + "{e_dmg}" + E + " + " +
                  ad("e") + " " + O + "physical" + E + " and " + APi + M + "{e_ap}% magic damage" + E + ", stacking armour and magic "
                  "resistance shred. On cooldown with a champion close: " + O + "Valkyrie" + E + ", a dash back leaving fire that deals " +
                  mag("w") + " " + M + "magic damage" + E + " every " + A + "{w_per}s" + E + ".",
        "ult": "Stores " + A + "{r_n} missiles" + E + " (one back every " + A + "{r_rech}s" + E + "); each bursts on the first enemy hit for " +
               mag("r") + " " + M + "magic damage" + E + " and " + ad("r") + " " + O + "physical damage" + E + " around it. Every third is "
               "the Big One: a wider blast for {r_big}% damage.",
        "names": ("Phosphorus Bomb", "Gatling Gun", "Missile Barrage"),
    },
    "ko": {
        "name": "코르키",
        "attack": O + "마법공학 탄약" + E + ": 기본 공격 피해의 {p_true}%가 " + Wh + "고정 피해" + E + ". " + O + "특급 배송" + E +
                  ": 시작 시, 부활 후, " + A + "{pk_cd}초" + E + "마다 다음 발키리가 탄약 꾸러미: 이륙 시 주변 챔피언을 " + R + "밀쳐내고" + E +
                  " " + mag("pk") + " " + M + "마법 피해" + E + ", 더 멀리 날고 불길이 더 넓고 오래가며 이동 속도 {pk_ms}% 증가.",
        "skill": "지정 위치에 인광탄을 던져 범위 내 적에게 " + mag("q") + " " + M + "마법 피해" + E + "와 " + ad("q") + " " + O + "물리 피해" +
                 E + ".",
        "skill2": O + "개틀링 건" + E + ": " + A + "{e_t}초" + E + " 동안 전방 원뿔로 난사, 매번 " + O + "{e_dmg}" + E + " + " + ad("e") + " " +
                  O + "물리" + E + "와 " + APi + M + "{e_ap}% 마법 피해" + E + ", 방어력·마법 저항력 감소 중첩. 재사용 대기 중 챔피언이 붙으면 " +
                  O + "발키리" + E + ": 뒤로 돌진하며 불길을 남겨 " + A + "{w_per}초" + E + "마다 " + mag("w") + " " + M + "마법 피해" + E + ".",
        "ult": "미사일 " + A + "{r_n}발" + E + " 저장(" + A + "{r_rech}초" + E + "마다 1발 충전), 처음 맞힌 적에서 폭발해 주변에 " + mag("r") +
               " " + M + "마법 피해" + E + "와 " + ad("r") + " " + O + "물리 피해" + E + ". 3발째는 대형 미사일: 범위 확대, 피해 {r_big}%.",
        "names": ("인광탄", "개틀링 건", "미사일 폭격"),
    },
    "ja": {
        "name": "コーキ",
        "attack": O + "ヘクステック榴散弾" + E + "：通常攻撃ダメージの{p_true}%が" + Wh + "確定ダメージ" + E + "。" + O + "荷物便" + E +
                  "：開始時・復活後・" + A + "{pk_cd}秒" + E + "ごとに次のワルキューレ機行が強化：離陸時に周囲のチャンピオンを" + R +
                  "ノックバック" + E + "し" + mag("pk") + "の" + M + "魔法ダメージ" + E + "、より遠く飛び炎が広く長く、移動速度{pk_ms}%増加。",
        "skill": "指定地点に閃光弾を投げ、範囲内の敵に" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + ad("q") + "の" + O + "物理ダメージ" +
                 E + "。",
        "skill2": O + "ガトリングガン" + E + "：" + A + "{e_t}秒" + E + "間前方の扇状に掃射、毎回" + O + "{e_dmg}" + E + " + " + ad("e") + "の" +
                  O + "物理" + E + "と" + APi + M + "{e_ap}%魔法ダメージ" + E + "、防御低下が累積。CD中に敵チャンピオンが接近すると" + O +
                  "ワルキューレ機行" + E + "：後方へ飛び炎を残し、" + A + "{w_per}秒" + E + "ごとに" + mag("w") + "の" + M + "魔法ダメージ" + E +
                  "。",
        "ult": "ミサイルを" + A + "{r_n}発" + E + "蓄える（" + A + "{r_rech}秒" + E + "ごとに1発）。最初に当たった敵で爆発し周囲に" + mag("r") +
               "の" + M + "魔法ダメージ" + E + "と" + ad("r") + "の" + O + "物理ダメージ" + E + "。3発目は大型：範囲拡大、ダメージ{r_big}%。",
        "names": ("閃光弾", "ガトリングガン", "連発ミサイル"),
    },
}

C = "league_corki_sfx_"
S_ = "league_corki_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_fire", "a_fire", 0.4, 0.0), ("a_hit", "a_hit", 0.35, 0.0), ("q", "q", 0.5, 0.0), ("q_boom", "q_boom", 0.6, 0.0),
    ("e", "e", 0.5, 0.0), ("w", "w", 0.55, 0.0), ("w_boom", "w_boom", 0.5, 0.0), ("w_pkg", "w_pkg", 0.65, 0.0),
    ("w_pkg_hit", "w_pkg_hit", 0.6, 0.0), ("r", "r", 0.5, 0.0), ("r_boom", "r_boom", 0.55, 0.0),
    ("r_big", "r_big", 0.6, 0.0), ("r_big_boom", "r_big_boom", 0.7, 0.0),
    ("vo_q", "vo_q", 0.85, 0.0), ("vo_e", "vo_e", 0.85, 0.0), ("vo_r", "vo_r", 0.85, 0.0), ("vo_w", "vo_w", 0.9, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_true", "pk_dmg", "pk_ap", "pk_ms", "q_dmg", "q_ap", "q_ad", "e_dmg", "e_ad", "e_ap",
                           "w_dmg", "w_ap", "r_n", "r_dmg", "r_ap", "r_ad", "r_big")}
    v.update({k: secs(p[k]) for k in ("pk_cd", "e_t", "w_per")})
    v["r_rech"] = secs(p["r_cd"] // p["r_n"])
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
    for lang, t in TEXT.items():
        d = {"name": t["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = t[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), t["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is above -28")
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
    for k in [k for k in ov if ID in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Corki" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Corki. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
