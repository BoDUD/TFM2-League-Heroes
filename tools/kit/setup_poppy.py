"""Poppy's text (5 languages), sound_info files and her keys in the shared files, numbers from build_poppy.P.

    python tools/kit/setup_poppy.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_poppy in every language, description + skill_name),
sound/sfx/league_poppy_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Poppy named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 波比 (圣锤之毅): 钢铁大使, 圣锤猛击, 坚定风采, 英勇冲锋, 持卫的裁决; zh_TW 波比 (聖鎚守護者):
鋼鐵使者, 戰槌衝擊, 堅定不移, 英勇衝鋒, 守護者裁決; ja ポッピー: 鋼鉄の大使, ハンマーショック, ステッドファスト, ヒロイックチャージ,
守護者の鉄鎚; ko 뽀삐: 강철의 외교관, 망치 강타, 굳건한 태세, 용감한 돌진, 수호자의 심판.
Slots: skill = Q Hammer Shock, skill2 = E Heroic Charge, ult = R Keeper's Verdict; the passive and W Steadfast Presence
(its active rides in her casts) are in the attack's text. No combo sentence in any text (the user's rule). The main
pack's rules are the ones written (W grounds, E stuns at the end of every carry, R knocks away from her); the add-on
league_poppy interrupts dashes, stuns only on a wall and sends R's targets toward their fountain, and says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_poppy import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_poppy"
VERSION = "0.152.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle face_to); banpick_center -12: the card rule (-39 - top)
# measured her hammer's pommel (-31.3, 6 game px over her pigtails); on the pigtails (-25.1) it gives -14, which left
# them touching the card's top - -12 keeps two px over them (the pommel clipped, league_wukong's tail the same way)
VIEW = {"face": {"x": 5, "y": -22}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def shield(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "波比",
        "attack": O + "钢铁大使" + E + "：每" + A + "{p_cd}秒" + E + "普攻远远扔出圆盾，多造成" + mag("p_dmg", "p_ap") + "魔法伤害；盾落在地上，捡起得" +
                  shield("p_sh", "p_sh_ad") + "护盾。" + O + "坚定风采" + E + "：双抗+{w_def}%；敌方英雄靠近时移速+{w_ms}%，" + A + "{w_t}秒" + E +
                  "内身边敌人" + R + "不能位移" + E + "。",
        "skill": "锤击地面，造成" + phys("q_dmg", "q_ratio") + "物理伤害（英雄另受{q_hp}%最大生命），地面" + R + "减速{q_slow}%" + E + "，" + A +
                 "{q_t}秒" + E + "后再炸一次。",
        "skill2": "冲向敌方英雄，造成" + phys("e_dmg", "e_ratio") + "物理伤害并推着他走，结束时" + R + "眩晕{e_stun_m}秒" + E + "。",
        "ult": "身边有2个以上敌方英雄时砸地：" + phys("r_tap_dmg", "r_tap_ratio") + "物理伤害并" + R + "击飞{r_up}秒" + E + "；否则蓄力抡锤推出冲击波，"
               "打中的英雄受" + phys("r_dmg", "r_ratio") + "物理伤害并" + R + "被打飞到远处" + E + "。",
        "names": ("圣锤猛击", "英勇冲锋", "持卫的裁决"),
    },
    "zh-hant": {
        "name": "波比",
        "attack": O + "鋼鐵使者" + E + "：每" + A + "{p_cd}秒" + E + "普攻遠遠擲出圓盾，多造成" + mag("p_dmg", "p_ap") + "魔法傷害；盾落在地上，撿起得" +
                  shield("p_sh", "p_sh_ad") + "護盾。" + O + "堅定不移" + E + "：雙抗+{w_def}%；敵方英雄靠近時移速+{w_ms}%，" + A + "{w_t}秒" + E +
                  "內身邊敵人" + R + "不能位移" + E + "。",
        "skill": "錘擊地面，造成" + phys("q_dmg", "q_ratio") + "物理傷害（英雄另受{q_hp}%最大生命），地面" + R + "緩速{q_slow}%" + E + "，" + A +
                 "{q_t}秒" + E + "後再炸一次。",
        "skill2": "衝向敵方英雄，造成" + phys("e_dmg", "e_ratio") + "物理傷害並推著他走，結束時" + R + "暈眩{e_stun_m}秒" + E + "。",
        "ult": "身邊有2個以上敵方英雄時砸地：" + phys("r_tap_dmg", "r_tap_ratio") + "物理傷害並" + R + "擊飛{r_up}秒" + E + "；否則蓄力掄錘推出衝擊波，"
               "打中的英雄受" + phys("r_dmg", "r_ratio") + "物理傷害並" + R + "被打飛到遠處" + E + "。",
        "names": ("戰槌衝擊", "英勇衝鋒", "守護者裁決"),
    },
    "en": {
        "name": "Poppy",
        "attack": O + "Iron Ambassador" + E + ": every " + A + "{p_cd}s" + E + " her attack throws her buckler from afar for " +
                  mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + " more; it lands nearby and picking it up gives a " +
                  shield("p_sh", "p_sh_ad") + " " + G + "shield" + E + ". " + O + "Steadfast Presence" + E + ": +{w_def}% armour and magic "
                  "resist; with an enemy champion close she gains {w_ms}% move speed and for " + A + "{w_t}s" + E + " enemies near her " + R +
                  "can't dash" + E + ".",
        "skill": "Slams the ground for " + phys("q_dmg", "q_ratio") + " physical damage (+{q_hp}% max health to champions); the ground " + R +
                 "slows {q_slow}%" + E + " and ruptures again after " + A + "{q_t}s" + E + ".",
        "skill2": "Charges an enemy champion for " + phys("e_dmg", "e_ratio") + " physical damage and carries them; at the end they are " +
                  R + "stunned {e_stun_m}s" + E + ".",
        "ult": "With 2+ enemy champions close she slams the ground: " + phys("r_tap_dmg", "r_tap_ratio") + " physical damage and " + R +
               "knock-up {r_up}s" + E + ". Otherwise she charges and swings a shockwave: champions hit take " + phys("r_dmg", "r_ratio") +
               " physical damage and are " + R + "knocked far away" + E + ".",
        "names": ("Hammer Shock", "Heroic Charge", "Keeper's Verdict"),
    },
    "ko": {
        "name": "뽀삐",
        "attack": O + "강철의 외교관" + E + ": " + A + "{p_cd}초" + E + "마다 기본 공격이 방패를 멀리 던져 " + mag("p_dmg", "p_ap") + " 마법 피해 추가; "
                  "떨어진 방패를 주우면 " + shield("p_sh", "p_sh_ad") + " 보호막. " + O + "굳건한 태세" + E + ": 방어력·마법 저항력 +{w_def}%; "
                  "적 챔피언이 가까우면 이동 속도 +{w_ms}%, " + A + "{w_t}초" + E + " 동안 주변 적 " + R + "돌진 불가" + E + ".",
        "skill": "땅을 내리쳐 " + phys("q_dmg", "q_ratio") + " 물리 피해(챔피언은 최대 체력 {q_hp}% 추가), 땅이 " + R + "{q_slow}% 둔화" + E + ", " +
                 A + "{q_t}초" + E + " 뒤 다시 폭발.",
        "skill2": "적 챔피언에게 돌진해 " + phys("e_dmg", "e_ratio") + " 물리 피해를 주고 밀고 나가며, 끝에 " + R + "{e_stun_m}초 기절" + E + ".",
        "ult": "주변에 적 챔피언 2명 이상이면 땅을 내리쳐 " + phys("r_tap_dmg", "r_tap_ratio") + " 물리 피해와 " + R + "{r_up}초 에어본" + E + "; 아니면 "
               "모았다 휘둘러 충격파: 맞은 챔피언은 " + phys("r_dmg", "r_ratio") + " 물리 피해를 입고 " + R + "멀리 날아감" + E + ".",
        "names": ("망치 강타", "용감한 돌진", "수호자의 심판"),
    },
    "ja": {
        "name": "ポッピー",
        "attack": O + "鋼鉄の大使" + E + "：" + A + "{p_cd}秒" + E + "ごとに通常攻撃で盾を遠くへ投げ" + mag("p_dmg", "p_ap") + "の魔法ダメージ追加；"
                  "落ちた盾を拾うと" + shield("p_sh", "p_sh_ad") + "のシールド。" + O + "ステッドファスト" + E + "：物防・魔防+{w_def}%；"
                  "敵チャンピオンが近いと移動速度+{w_ms}%、" + A + "{w_t}秒" + E + "周りの敵は" + R + "ダッシュ不可" + E + "。",
        "skill": "地面を叩き" + phys("q_dmg", "q_ratio") + "の物理ダメージ（チャンピオンは最大体力の{q_hp}%追加）、地面は" + R + "{q_slow}%スロウ" +
                 E + "、" + A + "{q_t}秒" + E + "後に再び爆発。",
        "skill2": "敵チャンピオンへ突進し" + phys("e_dmg", "e_ratio") + "の物理ダメージを与えて押し運び、最後に" + R + "{e_stun_m}秒スタン" + E + "。",
        "ult": "近くに敵チャンピオン2体以上なら地面を叩き" + phys("r_tap_dmg", "r_tap_ratio") + "の物理ダメージと" + R + "{r_up}秒ノックアップ" +
               E + "；そうでなければ溜めて衝撃波：当たったチャンピオンは" + phys("r_dmg", "r_ratio") + "の物理ダメージで" + R + "遠くへ吹き飛ぶ" +
               E + "。",
        "names": ("ハンマーショック", "ヒロイックチャージ", "守護者の鉄鎚"),
    },
}

C = "league_poppy_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_poppy_a_hit": [(C + "a_hit", 0.4, 0.0)],
    "league_poppy_p_throw": [(C + "p_throw", 0.4, 0.0)],
    "league_poppy_p_hit": [(C + "p_hit", 0.4, 0.0)],
    "league_poppy_p_land": [(C + "p_land", 0.3, 0.0)],
    "league_poppy_p_pick": [(C + "p_pick", 0.4, 0.0)],
    "league_poppy_q": [(C + "q", 0.4, 0.0)],
    "league_poppy_q_slam": [(C + "q_slam", 0.5, 0.0)],
    "league_poppy_q_burst": [(C + "q_burst", 0.4, 0.0)],
    "league_poppy_q_hit": [(C + "q_hit", 0.3, 0.0)],
    "league_poppy_w": [(C + "w", 0.4, 0.0)],
    "league_poppy_w_block": [(C + "w_block", 0.4, 0.0)],
    "league_poppy_e": [(C + "e", 0.4, 0.0)],
    "league_poppy_e_hit": [(C + "e_hit", 0.4, 0.0)],
    "league_poppy_e_stun": [(C + "e_stun", 0.5, 0.0)],
    "league_poppy_r_charge": [(C + "r_charge", 0.4, 0.0)],
    "league_poppy_r_swing": [(C + "r_swing", 0.55, 0.0)],
    "league_poppy_r_tap": [(C + "r_tap", 0.55, 0.0)],
    "league_poppy_r_hit": [(C + "r_hit", 0.5, 0.0)],
    "league_poppy_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_poppy_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_poppy_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_poppy_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "p_sh", "p_sh_ad", "w_def", "w_ms", "q_dmg", "q_ratio", "q_hp", "q_slow",
                           "e_dmg", "e_ratio", "r_dmg", "r_ratio", "r_tap_dmg", "r_tap_ratio")}
    for k in ("p_cd", "p_sh_t", "w_t", "q_t", "e_stun_m", "r_up"):
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
    if "Poppy" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Poppy. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
