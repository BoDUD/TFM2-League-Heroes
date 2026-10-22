"""Akshan's text (5 languages), sound_info files and his keys in the shared files, numbers from build_akshan.P.

    python tools/kit/setup_akshan.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_akshan in every language, description + skill_name),
sound/sfx/league_akshan_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Akshan named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 阿克尚 (影哨): 无所不用, 去而复还, 赴险夺人, 骄行荡寇, 恩怨相抵; zh_TW 埃可尚 (俠盜哨兵):
無賴之道, 復仇迴力鏢, 離經叛道, 英勇勾索, 因果蓄能彈; ja アクシャン: ダーティーファイト, 報復のブーメラン, 義賊の流儀,
ヒーロースイング, 当然の報い; ko 아크샨: 비열한 싸움, 복수의 부메랑, 악당 처단, 영웅의 비상, 인과응보.
Slots: skill = Q Avengerang, skill2 = E Heroic Swing, ult = R Comeuppance; the passive and W Going Rogue in the attack's
text. No combo sentence in any text (the user's rule). The main pack's rules are the ones written (the third hit counted
on anyone, R's later bullets stronger); the add-on league_akshan says its own (per target, missing health, Scoundrels
and the revive).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_akshan import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_akshan"
VERSION = "0.151.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view (10-18 slim redo): face (4, -31) under the crown, banpick -8 (bp_card_audit rule, the gun now held lower)
VIEW = {"face": {"x": 4, "y": -31}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -8}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def shield():
    return f"{G}{{p_sh}}{E} + {ADi}{G}{{p_sh_r}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "阿克尚",
        "attack": "每次普攻开两枪，第二枪对英雄只有{a2_ratio}%伤害。" + O + "无所不用" + E + "：普攻和技能每打中3下，多造成" + phys("p_dmg", "p_ratio") +
                  "物理伤害，打中英雄还获得" + shield() + "护盾" + A + "{p_sh_t}秒" + E + "。" + O + "赴险夺人" + E + "：被2个以上敌方英雄围住时伪装" +
                  A + "{w_inv}秒" + E + "并加速{w_ms}%。",
        "skill": "朝敌人扔出回旋镖（先瞄准再出手，能躲开），去程和回程各造成" + phys("q_dmg", "q_ratio") + "物理伤害；打中英雄加速{q_ms}%，持续" +
                 A + "{q_ms_t}秒" + E + "。",
        "skill2": "甩出钩索朝敌方英雄荡过去，" + A + "{e_t}秒" + E + "内每" + A + "{e_every}秒" + E + "朝最近的敌人开一枪，造成" + phys("e_dmg", "e_ratio") +
                  "物理伤害，最后翻滚离开再开一枪。",
        "ult": "锁定受伤的敌方英雄蓄力" + A + "{r_ch}秒" + E + "，最多存{r_n}发子弹，被" + R + "控制" + E + "会中断；然后连射，每发打中路上第一个敌人，"
               "造成" + phys("r_dmg", "r_ratio") + "物理伤害，前面每打中一发，后面的子弹多{r_up}%。",
        "names": ("去而复还", "骄行荡寇", "恩怨相抵"),
    },
    "zh-hant": {
        "name": "埃可尚",
        "attack": "每次普攻開兩槍，第二槍對英雄只有{a2_ratio}%傷害。" + O + "無賴之道" + E + "：普攻和技能每打中3下，多造成" + phys("p_dmg", "p_ratio") +
                  "物理傷害，打中英雄還獲得" + shield() + "護盾" + A + "{p_sh_t}秒" + E + "。" + O + "離經叛道" + E + "：被2個以上敵方英雄圍住時偽裝" +
                  A + "{w_inv}秒" + E + "並加速{w_ms}%。",
        "skill": "朝敵人扔出迴力鏢（先瞄準再出手，能躲開），去程和回程各造成" + phys("q_dmg", "q_ratio") + "物理傷害；打中英雄加速{q_ms}%，持續" +
                 A + "{q_ms_t}秒" + E + "。",
        "skill2": "甩出勾索朝敵方英雄盪過去，" + A + "{e_t}秒" + E + "內每" + A + "{e_every}秒" + E + "朝最近的敵人開一槍，造成" + phys("e_dmg", "e_ratio") +
                  "物理傷害，最後翻滾離開再開一槍。",
        "ult": "鎖定受傷的敵方英雄蓄力" + A + "{r_ch}秒" + E + "，最多存{r_n}發子彈，被" + R + "控制" + E + "會中斷；然後連射，每發打中路上第一個敵人，"
               "造成" + phys("r_dmg", "r_ratio") + "物理傷害，前面每打中一發，後面的子彈多{r_up}%。",
        "names": ("復仇迴力鏢", "英勇勾索", "因果蓄能彈"),
    },
    "en": {
        "name": "Akshan",
        "attack": "Every attack fires two shots, the second dealing {a2_ratio}% to champions. " + O + "Dirty Fighting" + E + ": every third hit of his "
                  "attacks and abilities deals " + phys("p_dmg", "p_ratio") + " physical damage more and, on a champion, gives him a " + shield() +
                  " shield for " + A + "{p_sh_t}s" + E + ". " + O + "Going Rogue" + E + ": with 2+ enemy champions near he camouflages for " + A +
                  "{w_inv}s" + E + " and gains {w_ms}% move speed.",
        "skill": "Throws a boomerang at an enemy (aimed first, so it can be dodged) that deals " + phys("q_dmg", "q_ratio") + " physical damage going "
                 "out and again coming back; a champion hit gives him {q_ms}% move speed for " + A + "{q_ms_t}s" + E + ".",
        "skill2": "Hooks and swings toward an enemy champion: for " + A + "{e_t}s" + E + " he shoots the nearest enemy every " + A + "{e_every}s" + E +
                  " for " + phys("e_dmg", "e_ratio") + " physical damage, then rolls off with a last shot.",
        "ult": "Locks onto a wounded enemy champion and charges for " + A + "{r_ch}s" + E + ", storing up to {r_n} bullets (" + R + "crowd control" + E +
               " stops it), then fires them: each hits the first enemy in its path for " + phys("r_dmg", "r_ratio") + " physical damage, {r_up}% more "
               "for every bullet that hit before.",
        "names": ("Avengerang", "Heroic Swing", "Comeuppance"),
    },
    "ko": {
        "name": "아크샨",
        "attack": "공격마다 두 발 발사, 두 번째는 챔피언에게 {a2_ratio}% 피해. " + O + "비열한 싸움" + E + ": 공격과 스킬 3회 적중마다 " + phys("p_dmg", "p_ratio") +
                  " 물리 피해 추가, 챔피언이면 " + shield() + " 보호막 " + A + "{p_sh_t}초" + E + ". " + O + "악당 처단" + E + ": 적 챔피언 2명 이상이 "
                  "가까우면 " + A + "{w_inv}초" + E + " 위장, 이동 속도 +{w_ms}%.",
        "skill": "적에게 부메랑을 던짐(조준 후 발사, 피할 수 있음): 갈 때와 돌아올 때 각각 " + phys("q_dmg", "q_ratio") + " 물리 피해, 챔피언 적중 시 " + A +
                 "{q_ms_t}초" + E + "간 이동 속도 +{q_ms}%.",
        "skill2": "갈고리를 걸고 적 챔피언 쪽으로 날아감: " + A + "{e_t}초" + E + " 동안 " + A + "{e_every}초" + E + "마다 가장 가까운 적에게 " +
                  phys("e_dmg", "e_ratio") + " 물리 피해, 마지막에 구르며 한 발 더.",
        "ult": "부상당한 적 챔피언을 조준해 " + A + "{r_ch}초" + E + " 충전, 최대 {r_n}발 저장(" + R + "군중 제어" + E + " 시 중단) 후 발사: 각 탄환은 처음 맞는 "
               "적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해, 앞서 맞힌 탄환마다 +{r_up}%.",
        "names": ("복수의 부메랑", "영웅의 비상", "인과응보"),
    },
    "ja": {
        "name": "アクシャン",
        "attack": "通常攻撃は2発、2発目はチャンピオンに{a2_ratio}%。" + O + "ダーティーファイト" + E + "：攻撃とスキルの3回目の命中で" + phys("p_dmg", "p_ratio") +
                  "の物理ダメージを追加、チャンピオンなら" + shield() + "のシールド（" + A + "{p_sh_t}秒" + E + "）。" + O + "義賊の流儀" + E +
                  "：敵2体以上に囲まれると" + A + "{w_inv}秒" + E + "迷彩、移動速度+{w_ms}%。",
        "skill": "ブーメランを投げる（狙ってから投げるので避けられる）：行きと帰りに各" + phys("q_dmg", "q_ratio") + "の物理ダメージ、チャンピオン命中で" +
                 A + "{q_ms_t}秒" + E + "移動速度+{q_ms}%。",
        "skill2": "フックで敵チャンピオンへスイング：" + A + "{e_t}秒" + E + "間、" + A + "{e_every}秒" + E + "毎に最も近い敵へ" + phys("e_dmg", "e_ratio") +
                  "の物理ダメージ、最後に転がってもう1発。",
        "ult": "負傷した敵チャンピオンを狙い" + A + "{r_ch}秒" + E + "チャージ、最大{r_n}発（" + R + "行動妨害" + E + "で中断）、その後発射：各弾は最初に当たった"
               "敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージ、先に当たった弾毎に+{r_up}%。",
        "names": ("報復のブーメラン", "ヒーロースイング", "当然の報い"),
    },
}

C = "league_akshan_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; w_mark / w_revive / w_gold are played by the add-on
SOUNDS = {
    "league_akshan_a_shot": [(C + "a", 0.3, 0.0)],
    "league_akshan_a_shot2": [(C + "a2", 0.25, 0.0)],
    "league_akshan_a_hit": [(C + "a_hit", 0.25, 0.0)],
    "league_akshan_a_hit2": [(C + "a_hit2", 0.2, 0.0)],
    "league_akshan_p_hit": [(C + "p_hit", 0.45, 0.0)],
    "league_akshan_q_cast": [(C + "q", 0.45, 0.0), (C + "vo_q", 0.85, 0.0)],
    "league_akshan_q_turn": [(C + "q_turn", 0.3, 0.0)],
    "league_akshan_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_akshan_e_cast": [(C + "e", 0.45, 0.0), (C + "vo_e", 0.85, 0.0)],
    "league_akshan_e_swing": [(C + "e_swing", 0.35, 0.0)],
    "league_akshan_e_shot": [(C + "e_shot", 0.25, 0.0)],
    "league_akshan_e_hit": [(C + "e_hit", 0.2, 0.0)],
    "league_akshan_e_roll": [(C + "e_roll", 0.4, 0.0)],
    "league_akshan_w_cast": [(C + "w", 0.45, 0.0), (C + "vo_w", 0.85, 0.0)],
    "league_akshan_w_mark": [(C + "w_mark", 0.45, 0.0)],
    "league_akshan_w_revive": [(C + "w_revive", 1.0, 0.0)],   # louder (2026-10-22: 「复活加更响的音效」)
    "league_akshan_w_gold": [(C + "w_gold", 0.45, 0.0)],
    "league_akshan_r_cast": [(C + "r", 0.55, 0.0), (C + "vo_r", 0.9, 0.0)],
    "league_akshan_r_store": [(C + "r_store", 0.35, 0.0)],
    "league_akshan_r_shot": [(C + "r_shot", 0.5, 0.0)],
    "league_akshan_r_hit": [(C + "r_hit", 0.45, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("a2_ratio", "p_dmg", "p_ratio", "p_sh", "p_sh_r", "w_ms", "q_dmg", "q_ratio", "q_ms", "e_dmg",
                           "e_ratio", "r_dmg", "r_ratio", "r_n", "r_up")}
    for k in ("p_sh_t", "w_inv", "q_ms_t", "e_every", "r_ch"):
        v[k] = secs(p[k])
    v["e_t"] = secs(p["e_n"] * p["e_every"])
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
    if "Akshan" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Akshan. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
