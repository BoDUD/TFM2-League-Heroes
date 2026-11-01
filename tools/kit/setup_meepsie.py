"""Meepsie's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_meepsie.P.

    python tools/kit/setup_meepsie.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_elderdragon.py writes for the Elder Dragon:
mod.mod_info (VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type
native for tft.dll, the keys sorted), text/champion.i18n (tft_meepsie in every language, description + skill_name),
sound/sfx/tft_meepsie_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 17's own (CommunityDragon cdragon/tft/<locale>.json, TFT17_IvernMinion, 2026-11-01): zh_CN 小木灵 (the
user's pick over 米普西), zh_TW 小米普, ja ミィプシー, ko 꼬마 정령, en Meepsie; its ability The Big Bang = 宇宙大爆炸 (zh_TW
大霹靂星系, ja ビッグバン, ko 빅뱅). Meep Pilot (木灵驾驶员), Moon-Rock Punch (月岩重拳), Moon-Dust Quake (月尘震地) and Healing
Meeps (治疗木灵) are our own (the user's pick, plan A 「木灵守护」).
The texts are the rules it plays with tft.dll (addons/tft/src/meepsie.rs): the meeps to the allies with the lowest
health share (itself with a slot left), the landing spot among the most enemy champions, the falloff a hex out, the
nearest knocked up.
Sounds: tools/lol/extract_meepsie.py's clips in tft/sound/sfx/tft_meepsie_sfx_*.wav (git-ignored) - its own set-17
slam (the cast, coming down, the hit), Ivern's Daisy (the punches, the slam's wind-up, her giggle, roar and goodbye) and
Bard's meeps (the zap, the meeps appearing, flying and healing, the slow).
A clip name never equals an event name (vo-clip-names rule): event tft_meepsie_<x> plays clip tft_meepsie_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_meepsie import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31
VERSION = "0.31.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on the pilot's eyes (the design's eyes at
# column 80, row 36 of 115 at PPU 2.875: 27 over the ground, 6 ahead of its standing point, the design's pivot column
# 64 - ppu_restyle's face_to); the centre in its body (half its 40 px); the ban/pick card by bp_card_audit.py's rule
VIEW = {"face": {"x": 6, "y": -27}, "center": {"x": 0, "y": -20}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    """base + AP ratio, magic."""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "小木灵",
        "attack": "挥出月岩重拳，造成" + AD + O + "物理伤害" + E + "。" + O + "木灵驾驶员" + E + "：每一拳额外造成" + mag("p_dmg", "p_ap") + M +
                  "魔法伤害" + E + "。",
        "skill": "一拳砸向前方地面，扇形范围内的敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并减速" + R + "{q_slow}%" + E + "（" + A +
                 "{q_slow_t}秒" + E + "）。",
        "skill2": "驾驶员一招手，" + A + "{e_n}只" + E + "小木灵飞向身边生命比例最低的队友（名额有剩时也治疗自己），每" + A + "{e_every}秒" + E +
                  "回复" + mag("e_hot", "e_hot_ap") + "生命，持续" + A + "{e_t}秒" + E + "。",
        "ult": "跳向附近敌方英雄最多的地方砸地，周围的敌人受到" + mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "，离中心每远一格少" + R + "{r_fall}%" +
               E + "；离落点最近的" + A + "{r_n}个" + E + "敌方英雄被" + R + "击飞" + E + A + "{r_up}秒" + E + "。",
        "names": ("月尘震地", "治疗木灵", "宇宙大爆炸"),
    },
    "zh-hant": {
        "name": "小米普",
        "attack": "揮出月岩重拳，造成" + AD + O + "物理傷害" + E + "。" + O + "米普駕駛員" + E + "：每一拳額外造成" + mag("p_dmg", "p_ap") + M +
                  "魔法傷害" + E + "。",
        "skill": "一拳砸向前方地面，扇形範圍內的敵軍受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並緩速" + R + "{q_slow}%" + E + "（" + A +
                 "{q_slow_t}秒" + E + "）。",
        "skill2": "駕駛員一招手，" + A + "{e_n}隻" + E + "米普飛向身邊生命比例最低的隊友（名額有剩時也治療自身），每" + A + "{e_every}秒" + E +
                  "回復" + mag("e_hot", "e_hot_ap") + "生命，持續" + A + "{e_t}秒" + E + "。",
        "ult": "跳向附近敵方英雄最多的地方砸地，周圍的敵軍受到" + mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "，離中心每遠一格減少" + R + "{r_fall}%" +
               E + "；離落點最近的" + A + "{r_n}名" + E + "敵方英雄被" + R + "擊飛" + E + A + "{r_up}秒" + E + "。",
        "names": ("月塵震地", "治療米普", "大霹靂星系"),
    },
    "en": {
        "name": "Meepsie",
        "attack": "Punches for " + AD + " " + O + "physical damage" + E + ". " + O + "Meep Pilot" + E + ": every punch deals " +
                  mag("p_dmg", "p_ap") + " bonus " + M + "magic damage" + E + ".",
        "skill": "Punches the ground ahead: enemies in a cone take " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E +
                 " and are slowed " + R + "{q_slow}%" + E + " (" + A + "{q_slow_t}s" + E + ").",
        "skill2": "The pilot waves and " + A + "{e_n}" + E + " meeps fly to the nearby allies with the lowest health share (itself "
                  "with one to spare), each healing " + mag("e_hot", "e_hot_ap") + " every " + A + "{e_every}s" + E + " for " + A +
                  "{e_t}s" + E + ".",
        "ult": "Leaps to the spot with the most enemy champions and slams: enemies around take " + mag("r_dmg", "r_ap") + " " + M +
               "magic damage" + E + ", " + R + "{r_fall}%" + E + " less a hex out; the " + A + "{r_n}" + E + " enemy champions nearest "
               "are " + R + "knocked up" + E + " " + A + "{r_up}s" + E + ".",
        "names": ("Moon-Dust Quake", "Healing Meeps", "The Big Bang"),
    },
    "ko": {
        "name": "꼬마 정령",
        "attack": "월석 주먹으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "정령 조종사" + E + ": 주먹마다 " + mag("p_dmg", "p_ap") + " " + M +
                  "마법 피해" + E + "를 추가로 입힙니다.",
        "skill": "앞쪽 땅을 내리쳐 부채꼴 범위의 적에게 " + mag("q_dmg", "q_ap") + " " + M + "마법 피해" + E + ", " + R + "{q_slow}%" + E + " 둔화(" +
                 A + "{q_slow_t}초" + E + ").",
        "skill2": "조종사가 손짓하면 정령 " + A + "{e_n}마리" + E + "가 체력 비율이 가장 낮은 주변 아군에게 날아가(자리가 남으면 자신도) " + A +
                  "{e_t}초" + E + " 동안 " + A + "{e_every}초" + E + "마다 " + mag("e_hot", "e_hot_ap") + " 회복.",
        "ult": "적 챔피언이 가장 많은 곳으로 뛰어올라 내려찍어 주변 적에게 " + mag("r_dmg", "r_ap") + " " + M + "마법 피해" + E + "(중심에서 한 칸마다 " +
               R + "-{r_fall}%" + E + "). 가장 가까운 적 챔피언 " + A + "{r_n}명" + E + " " + R + "에어본" + E + " " + A + "{r_up}초" + E + ".",
        "names": ("달먼지 진동", "치유 정령", "빅뱅"),
    },
    "ja": {
        "name": "ミィプシー",
        "attack": "月岩の拳で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ミープの操縦士" + E + "：パンチごとに" + mag("p_dmg", "p_ap") + "の" + M +
                  "魔法ダメージ" + E + "を追加。",
        "skill": "前方の地面を殴り、扇状範囲の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_slow}%" + E + "スロウ（" + A +
                 "{q_slow_t}秒" + E + "）。",
        "skill2": "操縦士が手を振ると" + A + "{e_n}匹" + E + "のミープが体力割合の最も低い周囲の味方へ飛び（枠が余れば自身も）、" + A + "{e_t}秒" + E +
                  "間" + A + "{e_every}秒" + E + "ごとに" + mag("e_hot", "e_hot_ap") + "回復。",
        "ult": "敵チャンピオンが最も多い地点へ跳んで叩きつけ、周囲の敵に" + mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E + "（中心から1マスごとに" +
               R + "-{r_fall}%" + E + "）。最も近い敵チャンピオン" + A + "{r_n}体" + E + "を" + R + "ノックアップ" + E + A + "{r_up}秒" + E + "。",
        "names": ("ムーンダストクエイク", "癒しのミープ", "ビッグバン"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_meepsie's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.35), ("p", 0.3),
    ("q", 0.45), ("q_hit", 0.45), ("q_slow", 0.3),
    ("e", 0.4), ("e_vo", 0.45), ("e_fly", 0.3), ("e_heal", 0.3),
    ("r", 0.5), ("r_vo", 0.5), ("r_into", 0.45), ("r_hit", 0.55),
    ("d", 0.5))}
# the sounds tft.dll plays itself (addons/tft/src/meepsie.rs: a meep flying off, a meep's heal landing, coming down,
# the slam, its fall)
DLL_SOUNDS = {f"{ID}_e_fly", f"{ID}_e_heal", f"{ID}_r_into", f"{ID}_r_hit", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "q_dmg", "q_ap", "q_slow", "e_n", "e_hot", "e_hot_ap", "r_dmg", "r_ap", "r_fall",
                           "r_n")}
    for k in ("q_slow_t", "e_every", "e_t", "r_up"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_meepsie.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # its sound keys rebuilt
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
    mi["last_updated"] = "2026-11-01"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
