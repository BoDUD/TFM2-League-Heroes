"""Ambessa's text (5 languages), sound_info files and their keys in the shared files, numbers from build_ambessa.P
(setup_yorick.py's way).

    python tools/kit/setup_ambessa.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_ambessa in every language, description + skill_name),
sound/sfx/league_ambessa_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Ambessa named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 安蓓萨 (铁血狼母): 龙犬诡步; 暗袭 / 裂斩, 铁令, 血戮, 公开处刑; zh_TW 安比薩: 龍犬詭步;
暗襲 / 裂斬, 鐵令, 血戮, 殛刑; ja アンベッサ: ドレイクハウンドの猛攻; カニングスイープ / サンダリングスラム, 断交, ラセレイト,
公開処刑; ko 암베사: 용사냥개의 발걸음; 교활한 휩쓸기 / 파멸의 일격, 배척, 찢어 가르기, 공개 처형.
Slots: skill = Cunning Sweep (its recast Sundering Slam in the same text), skill2 = Lacerate, ult = Public Execution;
Drakehound's Step (the passive) and Repudiation (cast by the controller) in the attack's text. The texts say the main
pack's rules (the add-on's copy has its own: addons/league_ambessa/make_override.py). No combo sentence in any text
(the user's rule: the combos are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_ambessa import P  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_ambessa"
VERSION = "0.220.0"     # above main 0.218.2 and Rumble's open #526 (0.219.0), 2026-10-25
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 2, "y": -35}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -4}}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "安蓓萨",
        "attack": "双刀。" + n("龙犬诡步") + "：每放一个技能就朝目标冲一步，" + t("{pw_t}秒") + "内攻速+{pw_as}%，下一刀加" +
                  phys("pw_dmg", "pw_ratio") + "+最大生命{pw_pct}%。" + n("铁令") + "：敌方英雄靠近时举刀格挡，护盾{w_sh}+" + ADi +
                  "{w_ad}%，然后砸地" + phys("w_dmg", "w_ratio") + "，英雄再加最大生命{w_pct}%。",
        "skill": n("暗袭") + "：身前横扫半圈，造成" + phys("q_dmg", "q_ratio") + "+最大生命{q_pct}%物理伤害；扫中后可接" + n("裂斩") +
                 "：直线劈下" + phys("q2_dmg", "q2_ratio") + "，目标再加最大生命{q2_pct}%。",
        "skill2": n("血戮") + "：甩链刀绕身一圈，造成" + phys("e_dmg", "e_ratio") + "物理伤害并" + cc("减速") + "{e_slow}%，持续" +
                  t("{e_slow_t}秒") + "；冲刺后再甩一圈。",
        "ult": n("公开处刑") + "：闪到敌方英雄身边" + cc("压制") + t("{r_sup}秒") + "，再砸进地里：" + phys("r_dmg", "r_ratio") +
               "+最大生命{r_pct}%，" + cc("眩晕") + t("{r_stun}秒") + "；此后护甲穿透+{r_pen}%。",
        "names": ("暗袭", "血戮", "公开处刑"),
    },
    "zh-hant": {
        "name": "安比薩",
        "attack": "雙刀。" + n("龍犬詭步") + "：每放一個技能就朝目標衝一步，" + t("{pw_t}秒") + "內攻速+{pw_as}%，下一刀加" +
                  phys("pw_dmg", "pw_ratio") + "+最大生命{pw_pct}%。" + n("鐵令") + "：敵方英雄靠近時舉刀格擋，護盾{w_sh}+" + ADi +
                  "{w_ad}%，然後砸地" + phys("w_dmg", "w_ratio") + "，英雄再加最大生命{w_pct}%。",
        "skill": n("暗襲") + "：身前橫掃半圈，造成" + phys("q_dmg", "q_ratio") + "+最大生命{q_pct}%物理傷害；掃中後可接" + n("裂斬") +
                 "：直線劈下" + phys("q2_dmg", "q2_ratio") + "，目標再加最大生命{q2_pct}%。",
        "skill2": n("血戮") + "：甩鏈刀繞身一圈，造成" + phys("e_dmg", "e_ratio") + "物理傷害並" + cc("緩速") + "{e_slow}%，持續" +
                  t("{e_slow_t}秒") + "；衝刺後再甩一圈。",
        "ult": n("殛刑") + "：閃到敵方英雄身邊" + cc("壓制") + t("{r_sup}秒") + "，再砸進地裡：" + phys("r_dmg", "r_ratio") +
               "+最大生命{r_pct}%，" + cc("暈眩") + t("{r_stun}秒") + "；此後護甲穿透+{r_pen}%。",
        "names": ("暗襲", "血戮", "殛刑"),
    },
    "en": {
        "name": "Ambessa",
        "attack": "Twin blades. " + n("Drakehound's Step") + ": every ability ends in a dash at her target; for " + t("{pw_t}s") +
                  " she attacks {pw_as}% faster and her next attack deals " + phys("pw_dmg", "pw_ratio") + " + {pw_pct}% max "
                  "health more. " + n("Repudiation") + ": with an enemy champion close she braces for a shield of "
                  "{w_sh} + " + ADi + "{w_ad}%, then slams for " + phys("w_dmg", "w_ratio") + ", champions taking "
                  "{w_pct}% max health more.",
        "skill": n("Cunning Sweep") + ": sweeps a half circle in front of her for " + phys("q_dmg", "q_ratio") + " + {q_pct}% "
                 "max health physical damage; after a hit it recasts as " + n("Sundering Slam") + ", slamming down a line "
                 "for " + phys("q2_dmg", "q2_ratio") + ", the target taking {q2_pct}% max health more.",
        "skill2": n("Lacerate") + ": whirls her chained blades round her for " + phys("e_dmg", "e_ratio") + " physical damage, " +
                  cc("slowing") + " {e_slow}% for " + t("{e_slow_t}s") + "; the step after it whirls them again.",
        "ult": n("Public Execution") + ": blinks onto an enemy champion, " + cc("suppresses") + " it for " + t("{r_sup}s") +
               " and slams it down for " + phys("r_dmg", "r_ratio") + " + {r_pct}% max health, " + cc("stunning") + " for " +
               t("{r_stun}s") + "; she keeps {r_pen}% armour penetration after.",
        "names": ("Cunning Sweep", "Lacerate", "Public Execution"),
    },
    "ko": {
        "name": "암베사",
        "attack": "쌍검. " + n("용사냥개의 발걸음") + ": 스킬마다 대상에게 짧게 돌진, " + t("{pw_t}초") + " 동안 공격 속도 +{pw_as}%, "
                  "다음 공격 " + phys("pw_dmg", "pw_ratio") + " + 최대 체력 {pw_pct}% 추가. " + n("배척") + ": 적 챔피언이 가까우면 "
                  "검을 들어 막아 보호막 {w_sh} + " + ADi + "{w_ad}%, 이어 내려찍어 " + phys("w_dmg", "w_ratio") + ", 챔피언은 "
                  "최대 체력 {w_pct}% 추가.",
        "skill": n("교활한 휩쓸기") + ": 앞쪽 반원을 휩쓸어 " + phys("q_dmg", "q_ratio") + " + 최대 체력 {q_pct}% 물리 피해; 적중 후 " +
                 n("파멸의 일격") + ": 직선으로 내려찍어 " + phys("q2_dmg", "q2_ratio") + ", 대상은 최대 체력 {q2_pct}% 추가.",
        "skill2": n("찢어 가르기") + ": 사슬 검을 휘둘러 주변에 " + phys("e_dmg", "e_ratio") + " 물리 피해, " + t("{e_slow_t}초") +
                  " 동안 {e_slow}% " + cc("둔화") + "; 돌진 후 한 번 더.",
        "ult": n("공개 처형") + ": 적 챔피언 옆으로 순간이동해 " + t("{r_sup}초") + " " + cc("제압") + " 후 내려찍어 " +
               phys("r_dmg", "r_ratio") + " + 최대 체력 {r_pct}%, " + t("{r_stun}초") + " " + cc("기절") + "; 이후 방어구 관통 "
               "{r_pen}%.",
        "names": ("교활한 휩쓸기", "찢어 가르기", "공개 처형"),
    },
    "ja": {
        "name": "アンベッサ",
        "attack": "双剣。" + n("ドレイクハウンドの猛攻") + "：スキル毎に対象へ突進、" + t("{pw_t}秒") + "攻撃速度+{pw_as}%、次の攻撃に" +
                  phys("pw_dmg", "pw_ratio") + "+最大体力{pw_pct}%。" + n("断交") + "：敵チャンピオンが近いと剣で防御しシールド"
                  "{w_sh}+" + ADi + "{w_ad}%、叩きつけ" + phys("w_dmg", "w_ratio") + "、チャンピオンは最大体力{w_pct}%追加。",
        "skill": n("カニングスイープ") + "：前方半円を薙ぎ払い" + phys("q_dmg", "q_ratio") + "+最大体力{q_pct}%の物理ダメージ；命中後" +
                 n("サンダリングスラム") + "：直線に叩きつけ" + phys("q2_dmg", "q2_ratio") + "、対象は最大体力{q2_pct}%追加。",
        "skill2": n("ラセレイト") + "：鎖の剣を振り回し周囲に" + phys("e_dmg", "e_ratio") + "の物理ダメージ、{e_slow}%" + cc("スロウ") +
                  "（" + t("{e_slow_t}秒") + "）；突進後もう一度。",
        "ult": n("公開処刑") + "：敵チャンピオンの側へ瞬間移動し" + t("{r_sup}秒") + cc("制圧") + "、叩きつけて" + phys("r_dmg", "r_ratio") +
               "+最大体力{r_pct}%、" + t("{r_stun}秒") + cc("スタン") + "；以後物理防御貫通{r_pen}%。",
        "names": ("カニングスイープ", "ラセレイト", "公開処刑"),
    },
}

C = "league_ambessa_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_ambessa_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("a_pw", 0.6), ("st", 0.5), ("q", 0.6), ("q_sweep", 0.6), ("q_hit", 0.55), ("q2", 0.6),
    ("q2_hit", 0.75), ("e", 0.6), ("e_lash", 0.6), ("e_hit", 0.5), ("w", 0.6), ("w_slam", 0.7), ("w_hit", 0.55),
    ("r", 0.8), ("r_pin", 0.7), ("r_crash", 0.85), ("vo_q", 0.85), ("vo_q2", 0.85), ("vo_e", 0.85), ("vo_w", 0.85),
    ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("pw_as", "pw_dmg", "pw_ratio", "pw_pct", "w_sh", "w_ad", "w_dmg", "w_ratio", "w_pct", "q_dmg",
                           "q_ratio", "q_pct", "q2_dmg", "q2_ratio", "q2_pct", "e_dmg", "e_ratio", "e_slow", "r_dmg",
                           "r_ratio", "r_pct", "r_pen")}
    for k in ("pw_t", "e_slow_t", "r_sup", "r_stun"):
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
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
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    for k in [k for k in ov if ID + "_" in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Ambessa" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Ambessa. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
