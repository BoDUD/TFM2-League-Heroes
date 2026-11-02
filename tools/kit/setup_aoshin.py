"""Ao Shin's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_aoshin.P.

    python tools/kit/setup_aoshin.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_alune.py's way), text/champion.i18n (tft_aoshin in every language, description + skill_name),
sound/sfx/tft_aoshin_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: from Community Dragon's TFT data (C:/t/sc_work/cd, set 7's TFT7_AoShin): zh_CN 敖兴, zh_TW 敖興, en Ao Shin, ja
アオ・シン, ko 아오 신; Lightning Rain = 闪电暴雨 / 雷霆暴雨 / 雷撃雨 / 번개 비 (set 7's ability). Thunder Breath, Cloud
Ride and Tempest Might (his trait Tempest made his own) are ours (the user's pick, plan A 「风暴龙神」), named in every
language by what they do. The texts are the rules he plays with tft.dll (addons/tft/src/aoshin.rs): the storm.
Sounds: tools/lol/extract_aoshin.py's clips in tft/sound/sfx/tft_aoshin_sfx_*.wav (git-ignored) - the Rift's Cloud Drake
(its attack and hit, the aggro roar, the take-off, its voice), Kennen (Bring the Light's bolt and hit, the Mark of the
Storm stun, the overload proc), Volibear (the storm cloud, its bolts) and Janna (the Eye of the Storm shield). A clip
name never equals an event name (vo-clip-names rule): event tft_aoshin_<x> plays clip tft_aoshin_sfx_<x>. package_mod
moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_aoshin import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.13.0"     # ... Kobuko 0.8, Vander 0.9, Violet 0.10, the Krug 0.11, Scar 0.12 (its own branch), Ao Shin 0.13
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
T = "<#f5f5f5ff>"      # true damage
# champion_view (game px from his soles' point, up negative): the face point between his eyes under the gold mask (the
# design's eye at column 47.5, row 21 of 74 x 76 at PPU 2.0: 27 over the ground, 4 ahead of his standing column 40);
# the centre in his coiled body; the ban/pick card by bp_card_audit.py's rule (checked there after the sheet is built)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 4, "y": -27}, "center": {"x": 0, "y": -11}, "banpick_center": {"x": 0, "y": -11}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "敖兴",
        "attack": "吐出球状闪电，造成" + AD + O + "物理伤害" + E + "。" + O + "风暴龙威" + E + "：交战" + A + "{p_delay}秒" + E +
                  "后天雷劈中周围所有敌方英雄，造成" + T + "{p_hp}%最大生命真实伤害" + E + "并" + R + "眩晕{p_stun}秒" + E +
                  "；随后自身法术强度" + A + "+{p_amp}%" + E + "（" + A + "{p_t}秒" + E + "，每" + A + "{p_cd}秒" + E + "一次）。",
        "skill": "喷出一道雷息，直线上的敌人受到" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "并被" + R + "沉默{q_sil}秒" + E +
                 "。",
        "skill2": "驾云飞离附近的敌方英雄，获得" + mag("e_sh", "e_ratio") + "的风暴护盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "召来雷暴：" + A + "{r_n}" + E + "道闪电接连劈向周围随机的敌方英雄，每道造成" + mag("r_dmg", "r_ratio") + M + "魔法伤害" +
               E + "并" + R + "沉默{r_sil}秒" + E + "。",
        "names": ("雷息", "腾云", "闪电暴雨"),
    },
    "zh-hant": {
        "name": "敖興",
        "attack": "吐出球狀閃電，造成" + AD + O + "物理傷害" + E + "。" + O + "風暴龍威" + E + "：交戰" + A + "{p_delay}秒" + E +
                  "後天雷劈中周圍所有敵方英雄，造成" + T + "{p_hp}%最大生命真實傷害" + E + "並" + R + "暈眩{p_stun}秒" + E +
                  "；隨後自身法術強度" + A + "+{p_amp}%" + E + "（" + A + "{p_t}秒" + E + "，每" + A + "{p_cd}秒" + E + "一次）。",
        "skill": "噴出一道雷息，直線上的敵人受到" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "並被" + R + "沉默{q_sil}秒" + E +
                 "。",
        "skill2": "駕雲飛離附近的敵方英雄，獲得" + mag("e_sh", "e_ratio") + "的風暴護盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "召來雷暴：" + A + "{r_n}" + E + "道閃電接連劈向周圍隨機的敵方英雄，每道造成" + mag("r_dmg", "r_ratio") + M + "魔法傷害" +
               E + "並" + R + "沉默{r_sil}秒" + E + "。",
        "names": ("雷息", "騰雲", "雷霆暴雨"),
    },
    "en": {
        "name": "Ao Shin",
        "attack": "Spits ball lightning for " + AD + " " + O + "physical damage" + E + ". " + O + "Tempest Might" + E + ": " + A +
                  "{p_delay}s" + E + " into a fight, lightning strikes every nearby enemy champion for " + T +
                  "{p_hp}% max health true damage" + E + " and " + R + "stuns for {p_stun}s" + E + "; then he deals " + A +
                  "+{p_amp}%" + E + " ability power for " + A + "{p_t}s" + E + " (every " + A + "{p_cd}s" + E + ").",
        "skill": "Breathes a bolt of lightning: enemies in the line take " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" +
                 E + " and are " + R + "silenced for {q_sil}s" + E + ".",
        "skill2": "Rides a cloud away from a nearby enemy champion and gains a " + mag("e_sh", "e_ratio") + " storm shield for " +
                  A + "{e_sh_t}s" + E + ".",
        "ult": "Calls the storm: " + A + "{r_n}" + E + " bolts strike random nearby enemy champions one after another, each for " +
               mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " and a " + R + "{r_sil}s silence" + E + ".",
        "names": ("Thunder Breath", "Cloud Ride", "Lightning Rain"),
    },
    "ko": {
        "name": "아오 신",
        "attack": "구체 번개를 뱉어 " + AD + " 물리 피해. " + O + "폭풍룡의 위엄" + E + ": 교전 " + A + "{p_delay}초" + E +
                  " 후 주변 모든 적 챔피언에게 번개가 떨어져 " + T + "최대 체력의 {p_hp}% 고정 피해" + E + ", " + R + "{p_stun}초 기절" +
                  E + "; 이후 " + A + "{p_t}초" + E + " 동안 주문력 " + A + "+{p_amp}%" + E + " (" + A + "{p_cd}초" + E + "마다).",
        "skill": "번개 숨결을 내뿜는다: 직선 위의 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해, " + R + "{q_sil}초 침묵" + E + ".",
        "skill2": "구름을 타고 근처 적 챔피언에게서 멀어지며 " + mag("e_sh", "e_ratio") + " 폭풍 보호막(" + A + "{e_sh_t}초" + E +
                  ")을 얻는다.",
        "ult": "폭풍을 부른다: 번개 " + A + "{r_n}" + E + "줄기가 주변 무작위 적 챔피언에게 연이어 떨어져 각각 " +
               mag("r_dmg", "r_ratio") + " 마법 피해, " + R + "{r_sil}초 침묵" + E + ".",
        "names": ("번개 숨결", "구름 타기", "번개 비"),
    },
    "ja": {
        "name": "アオ・シン",
        "attack": "球電を吐き" + AD + "の物理ダメージ。" + O + "嵐竜の威光" + E + "：戦闘" + A + "{p_delay}秒" + E +
                  "後、周囲の敵チャンピオン全員に雷が落ち" + T + "最大体力の{p_hp}%の確定ダメージ" + E + "と" + R + "{p_stun}秒スタン" +
                  E + "。その後" + A + "{p_t}秒" + E + "魔力" + A + "+{p_amp}%" + E + "（" + A + "{p_cd}秒" + E + "ごと）。",
        "skill": "雷の息吹を吐く：直線上の敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージと" + R + "{q_sil}秒サイレンス" + E + "。",
        "skill2": "雲に乗って近くの敵チャンピオンから離れ、" + mag("e_sh", "e_ratio") + "の嵐のシールド（" + A + "{e_sh_t}秒" + E +
                  "）を得る。",
        "ult": "嵐を呼ぶ：雷が" + A + "{r_n}" + E + "回、周囲のランダムな敵チャンピオンに次々と落ち、それぞれ" +
               mag("r_dmg", "r_ratio") + "の魔法ダメージと" + R + "{r_sil}秒サイレンス" + E + "。",
        "names": ("雷の息吹", "雲乗り", "雷撃雨"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_aoshin's sfx / tsfx) and tft.dll's; the
# ult's bolt layers Kennen's overload proc under Volibear's strike
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.4, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.45, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_shield": [(CLIP + "e_shield", 0.4, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0)],
    f"{ID}_r_roar": [(CLIP + "r_roar", 0.5, 0.0)],
    f"{ID}_r_bolt": [(CLIP + "r_bolt", 0.4, 0.0), (CLIP + "r_hit", 0.3, 0.05)],
    f"{ID}_p": [(CLIP + "p", 0.55, 0.0)],
    f"{ID}_p_bolt": [(CLIP + "p_bolt", 0.6, 0.0)],
    f"{ID}_p_stun": [(CLIP + "p_stun", 0.4, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/aoshin.rs: the storm's roar, its bolt and the stun)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_p_bolt", f"{ID}_p_stun"}


def values(p):
    v = {k: p[k] for k in ("p_hp", "p_amp", "q_dmg", "q_ratio", "e_sh", "e_ratio", "r_n", "r_dmg", "r_ratio")}
    for k in ("p_delay", "p_stun", "p_t", "p_cd", "q_sil", "e_sh_t", "r_sil"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_aoshin.py")
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
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): his rules the data cannot play
    mi["last_updated"] = "2026-10-28"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
