"""Daeja's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_daeja.P.

    python tools/kit/setup_daeja.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_nomsy.py writes for Nomsy: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_daeja in every language, description + skill_name), sound/sfx/tft_daeja_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_DragonBlue, 2026-10-30): zh_CN 迭嘉, zh_TW 戴枷,
ja デイジャ, ko 다에야, en Daeja; his ability Windblast = 罡风轰击 / 猛烈狂風 / 突風 / 돌풍 (its passive half, the barrages, is the
attack's Barrage 三连弹幕). Wingbeat Retreat (振翼退风) and Sky Gale (苍穹罡风) are our own (the user's pick, plan A 「罡风弹幕」).
The texts are the rules he plays with tft.dll (addons/tft/src/daeja.rs): the waves down the line with the most enemies.
Sounds: tools/lol/extract_daeja.py's clips in tft/sound/sfx/tft_daeja_sfx_*.wav (git-ignored) - his own set-7 TFT sounds
(Windblast's cast, launch and hit), Janna (the wind bolt, the gust and its slow, the rising gale), Ezreal (the barrage
bolts, Trueshot Barrage for the big waves) and the Rift's drakes (the wing beat, the roar, the landing, the death). A
clip name never equals an event name (vo-clip-names rule): event tft_daeja_<x> plays clip tft_daeja_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_daeja import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Daeja 0.20 (Idas,
# built beside him, takes the next one that is free when either merges)
VERSION = "0.20.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from his feet's point, up negative): the face point between his eyes (the design's eye row 27.5
# of 69 at PPU 1.72: 24 over the ground; 2 ahead of his standing column, ppu_restyle's face_to); the centre in his
# chest; the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -28.5: the wing tips 1 game px under the
# card's top)
VIEW = {"face": {"x": 2, "y": -24}, "center": {"x": -1, "y": -17}, "banpick_center": {"x": -1, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "迭嘉",
        "attack": "推出风弹，造成" + AD + O + "物理伤害" + E + "。" + O + "三连弹幕" + E + "：每次普攻再射出" + A + "{p_n}" + E +
                  "颗小风弹，各造成" + mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "，魔抗" + A + "-{p_mr}" + E + "（" + A +
                  "{p_mr_t}秒" + E + "，可叠加）。",
        "skill": "双翼前扫，朝敌人最多的直线轰出穿透的风波，造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "。",
        "skill2": "振翅朝身边的敌人扇出一阵风，造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "并减速" + A + "{e_slow}%" + E +
                  "（" + A + "{e_slow_t}秒" + E + "），自己借风后跳。",
        "ult": "展翅飞起（减伤" + A + "{r_dr}%" + E + "、免疫控制），朝敌人最多的直线连续轰出" + A + "{r_n}" + E + "道大冲击波，各造成" +
               mag("r_dmg", "r_ratio") + M + "魔法伤害" + E + "。",
        "names": ("罡风轰击", "振翼退风", "苍穹罡风"),
    },
    "zh-hant": {
        "name": "戴枷",
        "attack": "推出風彈，造成" + AD + O + "物理傷害" + E + "。" + O + "三連彈幕" + E + "：每次普攻再射出" + A + "{p_n}" + E +
                  "顆小風彈，各造成" + mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "，魔抗" + A + "-{p_mr}" + E + "（" + A +
                  "{p_mr_t}秒" + E + "，可疊加）。",
        "skill": "雙翼前掃，朝敵人最多的直線轟出穿透的風波，造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "。",
        "skill2": "振翅朝身邊的敵人搧出一陣風，造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "並緩速" + A + "{e_slow}%" + E +
                  "（" + A + "{e_slow_t}秒" + E + "），自己借風後跳。",
        "ult": "展翅飛起（減傷" + A + "{r_dr}%" + E + "、免疫控制），朝敵人最多的直線連續轟出" + A + "{r_n}" + E + "道大衝擊波，各造成" +
               mag("r_dmg", "r_ratio") + M + "魔法傷害" + E + "。",
        "names": ("猛烈狂風", "振翼退風", "蒼穹罡風"),
    },
    "en": {
        "name": "Daeja",
        "attack": "Punches out a wind bolt for " + AD + " " + O + "physical damage" + E + ". " + O + "Barrage" + E + ": each attack "
                  "sends " + A + "{p_n}" + E + " small wind bolts after it, each " + mag("p_dmg", "p_ap") + " " + M + "magic damage" +
                  E + " and " + A + "-{p_mr}" + E + " magic resist for " + A + "{p_mr_t}s" + E + " (stacks).",
        "skill": "Sweeps his wings forward: a wind wave runs down the line with the most enemies, " + mag("q_dmg", "q_ratio") +
                 " " + M + "magic damage" + E + " to each.",
        "skill2": "Beats his wings at a nearby enemy: a gust for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  " and a " + A + "{e_slow}%" + E + " slow for " + A + "{e_slow_t}s" + E + ", and he hops back on the wind.",
        "ult": "Flies up (" + A + "{r_dr}%" + E + " less damage, immune to crowd control) and blasts " + A + "{r_n}" + E +
               " big waves down the line with the most enemies, each " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               ".",
        "names": ("Windblast", "Wingbeat Retreat", "Sky Gale"),
    },
    "ko": {
        "name": "다에야",
        "attack": "주먹으로 바람 탄을 날려 " + AD + " " + O + "물리 피해" + E + ". " + O + "삼연 탄막" + E + ": 기본 공격마다 작은 바람 탄 " +
                  A + "{p_n}" + E + "개를 더 날려 각각 " + mag("p_dmg", "p_ap") + " " + M + "마법 피해" + E + ", 마법 저항력 " + A +
                  "-{p_mr}" + E + "(" + A + "{p_mr_t}초" + E + ", 중첩).",
        "skill": "날개를 앞으로 휘둘러 적이 가장 많은 일직선으로 관통하는 바람 파동을 날려 " + mag("q_dmg", "q_ratio") + " " + M +
                 "마법 피해" + E + ".",
        "skill2": "가까운 적에게 날갯짓으로 돌풍을 일으켜 " + mag("e_dmg", "e_ratio") + " " + M + "마법 피해" + E + ", " + A +
                  "{e_slow}%" + E + " 둔화(" + A + "{e_slow_t}초" + E + "), 바람을 타고 뒤로 도약.",
        "ult": "날아올라(받는 피해 " + A + "{r_dr}%" + E + " 감소, 군중 제어 면역) 적이 가장 많은 일직선으로 큰 충격파 " + A + "{r_n}" + E +
               "개를 연달아 날려 각각 " + mag("r_dmg", "r_ratio") + " " + M + "마법 피해" + E + ".",
        "names": ("돌풍", "날갯짓 후퇴", "창공의 돌풍"),
    },
    "ja": {
        "name": "デイジャ",
        "attack": "拳から風の弾を放ち" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "三連弾幕" + E + "：通常攻撃のたびに小さな風の弾を" +
                  A + "{p_n}" + E + "個追加で放ち、それぞれ" + mag("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E + "と魔法防御" + A +
                  "-{p_mr}" + E + "（" + A + "{p_mr_t}秒" + E + "、重複）。",
        "skill": "翼を前へ振り、敵が最も多い直線に貫通する風の波を放ち" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "。",
        "skill2": "近くの敵へ羽ばたいて突風を起こし" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "と" + A +
                  "{e_slow}%" + E + "スロウ（" + A + "{e_slow_t}秒" + E + "）、風に乗って後ろへ跳ぶ。",
        "ult": "飛び上がり（被ダメージ" + A + "{r_dr}%" + E + "軽減、行動妨害無効）、敵が最も多い直線に大きな衝撃波を" + A + "{r_n}" + E +
               "発連続で放ちそれぞれ" + mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E + "。",
        "names": ("突風", "羽ばたき後退", "蒼穹の突風"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_daeja's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.3), ("p_hit", 0.25),
    ("q", 0.5), ("q_launch", 0.55), ("q_hit", 0.5),
    ("e", 0.5), ("e_wind", 0.45), ("e_slow", 0.35),
    ("r", 0.5), ("r_roar", 0.55), ("r_blast", 0.55), ("r_hit", 0.45), ("r_land", 0.5),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/daeja.rs: the waves' hits, his death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("q_hit", "r_hit", "d")}


def values(p):
    v = {k: p[k] for k in ("p_n", "p_dmg", "p_ap", "p_mr", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_slow", "r_dr", "r_n",
                           "r_dmg", "r_ratio")}
    for k in ("p_mr_t", "e_slow_t"):
        v[k] = secs(p[k])
    return v


def kit_sounds():
    """Every Sfx / TargetSfx name the kit plays."""
    found = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx"):
                found.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(load(os.path.join(MOD, "champion", f"{ID}.data_champion")))
    return found


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
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    p = dict(P)
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

    played = kit_sounds() | DLL_SOUNDS
    if played != set(SOUNDS):
        sys.exit(f"the kit plays {sorted(played - set(SOUNDS))} without a sound_info, SOUNDS has unused "
                 f"{sorted(set(SOUNDS) - played)}")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"), {})
    for lang, (d, names) in tx.items():
        i18n.setdefault(lang, {}).setdefault("description", {})[ID] = d
        i18n[lang].setdefault("skill_name", {})[ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    clips = set()
    for name, plays in SOUNDS.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
            if not os.path.isfile(lp(os.path.join(MOD, "sound", "sfx", c + ".wav"))):
                print(f"warning: {c}.wav missing - run tools/lol/extract_daeja.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # his sound keys rebuilt
        del ov[k]
    for name in list(SOUNDS) + sorted(clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": {}})
    cv["entries"][ID] = json.loads(json.dumps(VIEW))
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    mi["description"] = pack.DESC.format(heroes=", ".join(pack.HEROES))
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): the rules the data cannot play
    mi["last_updated"] = "2026-10-30"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
