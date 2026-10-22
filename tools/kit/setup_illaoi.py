"""Illaoi's text (5 languages), sound_info files and her keys in the shared files, numbers from build_illaoi.P.

    python tools/kit/setup_illaoi.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_illaoi in every language, description + skill_name),
sound/sfx/league_illaoi_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Illaoi named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 俄洛伊 (海兽祭司): 古神先知; 触手猛击, 严酷训诫, 灵魂试炼, 过界信仰; zh_TW 伊羅旖: 遠古預言;
鞭笞觸手, 嚴酷考驗, 祖靈之試, 虔信一躍; ja イラオイ: 旧神の預言者; 触手の鉄槌, 過酷なる教訓, 魂の試練, 信仰震; ko 일라오이:
고대신의 예언자; 촉수 강타, 혹독한 가르침, 영혼의 시험, 믿음의 도약.
Slots: skill = Harsh Lesson, skill2 = Test of Spirit, ult = Leap of Faith; the passive (Tentacle Smash folded in) in the
attack's text. No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_illaoi import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_illaoi"
VERSION = "0.196.0"     # the next free number above main 0.195.6 (Mundo #472) (2026-10-23)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point just over her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card (set at
# export: tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 3, "y": -35}, "center": {"x": 0, "y": -17}, "banpick_center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def hl(x):
    return G + x + E


TEXT = {
    "zh-hans": {
        "name": "俄洛伊",
        "attack": "抡神像砸下。" + n("古神先知") + "：普攻时每" + t("{p_cd}秒") + "身前长出触手" + t("{t_life}秒") + "，每" + t("{t_per}秒") +
                  "抽附近一个敌人" + phys("t_dmg", "t_ratio") + "物理伤害，抽中英雄" + hl("回复") + phys("p_heal", "p_heal_r") + "生命。",
        "skill": "跃向目标，造成" + phys("w_dmg", "w_ratio") + " + 目标{w_thp}%最大生命值的物理伤害，她的每条触手都抽他一下。",
        "skill2": "扯出敌方英雄的灵魂" + t("{e_t}秒") + "：受到的伤害+{e_echo}%，" + cc("减速") + "{e_slow}%；之后成为躯壳" + t("{e_vt}秒") +
                  "，身边长出触手。",
        "ult": "跃起把神像砸进地里，对周围敌人造成" + phys("r_dmg", "r_ratio") + "物理伤害，每命中一名英雄长出一条触手；" + t("{r_on}秒") +
               "内触手每" + t("{r_per}秒") + "抽一次，严酷训诫冷却" + t("{w_cd_r}秒") + "。",
        "names": ("严酷训诫", "灵魂试炼", "过界信仰"),
    },
    "zh-hant": {
        "name": "伊羅旖",
        "attack": "掄神像砸下。" + n("遠古預言") + "：普攻時每" + t("{p_cd}秒") + "身前長出觸手" + t("{t_life}秒") + "，每" + t("{t_per}秒") +
                  "抽附近一個敵人" + phys("t_dmg", "t_ratio") + "物理傷害，抽中英雄" + hl("回復") + phys("p_heal", "p_heal_r") + "生命。",
        "skill": "躍向目標，造成" + phys("w_dmg", "w_ratio") + " + 目標{w_thp}%最大生命值的物理傷害，她的每條觸手都抽他一下。",
        "skill2": "扯出敵方英雄的靈魂" + t("{e_t}秒") + "：受到的傷害+{e_echo}%，" + cc("緩速") + "{e_slow}%；之後成為軀殼" + t("{e_vt}秒") +
                  "，身邊長出觸手。",
        "ult": "躍起把神像砸進地裡，對周圍敵人造成" + phys("r_dmg", "r_ratio") + "物理傷害，每命中一名英雄長出一條觸手；" + t("{r_on}秒") +
               "內觸手每" + t("{r_per}秒") + "抽一次，嚴酷考驗冷卻" + t("{w_cd_r}秒") + "。",
        "names": ("嚴酷考驗", "祖靈之試", "虔信一躍"),
    },
    "en": {
        "name": "Illaoi",
        "attack": "Swings her idol down. " + n("Prophet of an Elder God") + ": an attack grows a tentacle before her every " +
                  t("{p_cd}s") + " for " + t("{t_life}s") + "; it strikes an enemy nearby every " + t("{t_per}s") + " for " +
                  phys("t_dmg", "t_ratio") + " physical damage, and " + hl("heals") + " her " + phys("p_heal", "p_heal_r") +
                  " when it hits a champion.",
        "skill": "Leaps at her target: " + phys("w_dmg", "w_ratio") + " + {w_thp}% of its max health as physical damage, and "
                 "every tentacle of hers lashes it.",
        "skill2": "Rips the spirit out of an enemy champion for " + t("{e_t}s") + ": it takes {e_echo}% more damage and is " +
                  cc("slowed") + " {e_slow}%; then it is a Vessel for " + t("{e_vt}s") + " and a tentacle grows by it.",
        "ult": "Leaps and smashes her idol into the ground: " + phys("r_dmg", "r_ratio") + " physical damage to the enemies "
               "around, a tentacle for each champion hit; for " + t("{r_on}s") + " her tentacles strike every " +
               t("{r_per}s") + " and the cooldown of Harsh Lesson is " + t("{w_cd_r}s") + ".",
        "names": ("Harsh Lesson", "Test of Spirit", "Leap of Faith"),
    },
    "ko": {
        "name": "일라오이",
        "attack": "신상을 내리친다. " + n("고대신의 예언자") + ": 기본 공격 시 " + t("{p_cd}초") + "마다 앞에 촉수가 " + t("{t_life}초") +
                  " 자라 " + t("{t_per}초") + "마다 근처 적에게 " + phys("t_dmg", "t_ratio") + " 물리 피해, 챔피언 적중 시 " +
                  phys("p_heal", "p_heal_r") + " " + hl("회복") + ".",
        "skill": "대상에게 도약해 " + phys("w_dmg", "w_ratio") + " + 대상 최대 체력의 {w_thp}% 물리 피해, 그녀의 모든 촉수가 대상을 "
                 "내려친다.",
        "skill2": "적 챔피언의 영혼을 " + t("{e_t}초") + " 끌어낸다: 받는 피해 +{e_echo}%, {e_slow}% " + cc("둔화") + "; 이후 " +
                  t("{e_vt}초") + " 동안 그릇이 되어 곁에 촉수가 자란다.",
        "ult": "도약해 신상을 땅에 내리꽂아 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해, 맞힌 챔피언마다 촉수 하나; " +
               t("{r_on}초") + " 동안 촉수는 " + t("{r_per}초") + "마다 내려치고 혹독한 가르침 재사용 대기시간 " + t("{w_cd_r}초") + ".",
        "names": ("혹독한 가르침", "영혼의 시험", "믿음의 도약"),
    },
    "ja": {
        "name": "イラオイ",
        "attack": "神像を振り下ろす。" + n("旧神の預言者") + "：通常攻撃時" + t("{p_cd}秒") + "ごとに前へ触手が" + t("{t_life}秒") + "生え、" +
                  t("{t_per}秒") + "ごとに近くの敵へ" + phys("t_dmg", "t_ratio") + "の物理ダメージ、英雄に当たると" +
                  phys("p_heal", "p_heal_r") + hl("回復") + "。",
        "skill": "対象へ跳び" + phys("w_dmg", "w_ratio") + " + 対象の最大体力の{w_thp}%の物理ダメージ、彼女の触手すべてが対象を打つ。",
        "skill2": "敵英雄の魂を" + t("{e_t}秒") + "引き出す：受けるダメージ+{e_echo}%、{e_slow}%" + cc("スロウ") + "。その後" +
                  t("{e_vt}秒") + "器となり、そばに触手が生える。",
        "ult": "跳んで神像を地面に叩きつけ周囲の敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージ、当たった英雄ごとに触手1本。" +
               t("{r_on}秒") + "間触手は" + t("{r_per}秒") + "ごとに打ち、過酷なる教訓のクールダウン" + t("{w_cd_r}秒") + "。",
        "names": ("過酷なる教訓", "魂の試練", "信仰震"),
    },
}

C = "league_illaoi_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the attack and the tentacles' strikes lower: they
# come often), the voice as the other heroes'
SOUNDS = {f"league_illaoi_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("p_spawn", 0.6), ("p_hit", 0.5), ("w", 0.75), ("w_hit", 0.8), ("e", 0.75),
    ("e_hit", 0.75), ("e_break", 0.8), ("r", 0.85), ("r_slam", 0.9), ("r_hit", 0.6), ("vo_w", 0.85), ("vo_e", 0.85),
    ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("t_dmg", "t_ratio", "p_heal", "p_heal_r", "w_dmg", "w_ratio", "w_thp", "e_echo", "e_slow",
                           "r_dmg", "r_ratio")}
    for k in ("p_cd", "t_life", "t_per", "e_t", "e_vt", "r_on", "r_per", "w_cd_r"):
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
    if "Illaoi" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Illaoi. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
