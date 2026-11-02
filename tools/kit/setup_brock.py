"""Brock's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_brock.P.

    python tools/kit/setup_brock.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sentry.py writes for the Sentry: mod.mod_info
(VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for
tft.dll, the keys sorted), text/champion.i18n (tft_brock in every language, description + skill_name),
sound/sfx/tft_brock_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 16's own (CommunityDragon cdragon/tft/<locale>.json, TFT16_Brock, 2026-11-02): zh_CN 岩宝, zh_TW 布洛克, ja
ブロック, ko 브록, en Brock; his ability Seismic Slam = 震地猛击 (zh_TW 震地猛擊, ja サイズミックスラム, ko 지진 강타). Stone Heart
(岩心不动, TFT's passive: immune to crowd control), Quake Fist (震地拳), Boulder Toss (巨岩投掷) and Moss Grip (苔藤缠握) are ours
(the user's pick, plan A 「震地猛击」).
The texts are the rules he plays: the stone heart and the slam's falloff and first-hit knock-up in tft.dll
(addons/tft/src/brock.rs), the rest the data (the splash and every third blow, the boulder, the roots and the shield,
the leap and the rocks).
Sounds: tools/lol/extract_brock.py's clips in tft/sound/sfx/tft_brock_sfx_*.wav (git-ignored) - his own set-16 fists, crit
and slam, Malphite's Seismic Shard, Granite Shield and Ground Slam, Maokai's and Zyra's roots, the Krug's crumbling. A
clip name never equals an event name (vo-clip-names rule): event tft_brock_<x> plays clip tft_brock_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_brock import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33, Gromp 0.34, the encyclopedia
# centres 0.35 (PR #657), the log fixes 0.36 (PR #659), the Sentry 0.37, Brock 0.38
VERSION = "0.38.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from his soles' point, up negative): set from the rigged sheet (bp_card_audit.py --centers)
# when the art is in; until then Terra's (a 44-px top of the same pack)
VIEW = {"face": {"x": 3, "y": -32}, "center": {"x": 0, "y": -18}, "banpick_center": {"x": 0, "y": -14}}


def phys(d, r, h=None, hp=""):
    """d + r% AD (+ h% of his maximum health), physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}" + (f" + {O}{{{h}}}%{E}{hp}" if h else "")


TEXT = {
    "zh-hans": {
        "name": "岩宝",
        "attack": "双拳砸下，造成" + AD + O + "物理伤害" + E + "，目标周围敌人受" + ADi + O + "{a_splash}%" + E + "溅射；每第三下" + R + "击飞" +
                  E + "目标" + A + "{a_up}秒" + E + "。" + O + "岩心不动" + E + "：免疫控制。",
        "skill": "抡起大石头砸向目标，造成" + phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理伤害" + E + "，减速" + A + "{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "树根从目标脚下钻出，造成" + phys("e_dmg", "e_ratio") + O + "物理伤害" + E + "并" + R + "定身{e_root}秒" + E + "；自己获得" +
                  phys("e_sh", "e_sh_ad") + "护盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "跃起砸向敌方英雄：周围敌人受到" + phys("r_dmg", "r_ratio", "r_hp", "最大生命") + O + "物理伤害" + E + "，每远一格" + A + "-{r_fall}%" +
               E + "（最低" + A + "{r_min}%" + E + "），本场第一次被砸中的" + R + "击飞{r_up}秒" + E + "；随后落下" + A + "{r_rocks}" + E + "块碎石。",
        "names": ("巨岩投掷", "苔藤缠握", "震地猛击"),
    },
    "zh-hant": {
        "name": "布洛克",
        "attack": "雙拳砸下，造成" + AD + O + "物理傷害" + E + "，目標周圍敵軍受" + ADi + O + "{a_splash}%" + E + "濺射；每第三下" + R + "擊飛" +
                  E + "目標" + A + "{a_up}秒" + E + "。" + O + "岩心不動" + E + "：免疫控制。",
        "skill": "掄起大石頭砸向目標，造成" + phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理傷害" + E + "，緩速" + A + "{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "樹根從目標腳下鑽出，造成" + phys("e_dmg", "e_ratio") + O + "物理傷害" + E + "並" + R + "定身{e_root}秒" + E + "；自己獲得" +
                  phys("e_sh", "e_sh_ad") + "護盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "躍起砸向敵方英雄：周圍敵軍受到" + phys("r_dmg", "r_ratio", "r_hp", "最大生命") + O + "物理傷害" + E + "，每遠一格" + A + "-{r_fall}%" +
               E + "（最低" + A + "{r_min}%" + E + "），本場第一次被砸中的" + R + "擊飛{r_up}秒" + E + "；隨後落下" + A + "{r_rocks}" + E + "塊碎石。",
        "names": ("巨岩投擲", "苔藤纏握", "震地猛擊"),
    },
    "en": {
        "name": "Brock",
        "attack": "Slams both fists down for " + AD + " " + O + "physical damage" + E + ", splashing " + ADi + O + "{a_splash}%" + E +
                  " to enemies around the target; every third blow " + R + "knocks it up" + E + " for " + A + "{a_up}s" + E + ". " + O +
                  "Stone Heart" + E + ": immune to crowd control.",
        "skill": "Hurls a boulder at the target for " + phys("q_dmg", "q_ratio", "q_hp", " max health") + " " + O + "physical damage" + E +
                 ", slowing it by " + A + "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Roots burst from under the target for " + phys("e_dmg", "e_ratio") + " " + O + "physical damage" + E + ", " + R +
                  "rooting it for {e_root}s" + E + "; he gains a " + phys("e_sh", "e_sh_ad") + " shield for " + A + "{e_sh_t}s" + E + ".",
        "ult": "Leaps onto an enemy champion: nearby enemies take " + phys("r_dmg", "r_ratio", "r_hp", " max health") + " " + O +
               "physical damage" + E + ", " + A + "{r_fall}%" + E + " less per hex away (" + A + "{r_min}%" + E + " minimum); the first "
               "time this fight, they are " + R + "knocked up for {r_up}s" + E + ". Then " + A + "{r_rocks}" + E + " rocks fall.",
        "names": ("Boulder Toss", "Moss Grip", "Seismic Slam"),
    },
    "ko": {
        "name": "브록",
        "attack": "두 주먹을 내리쳐 " + AD + " " + O + "물리 피해" + E + ", 대상 주변 적에게 " + ADi + O + "{a_splash}%" + E + " 범위 피해; "
                  "세 번째 공격마다 대상을 " + A + "{a_up}초" + E + " " + R + "에어본" + E + ". " + O + "바위 심장" + E + ": 군중 제어 면역.",
        "skill": "대상에게 바위를 던져 " + phys("q_dmg", "q_ratio", "q_hp", " 최대 체력") + " " + O + "물리 피해" + E + ", " + A + "{q_slow_t}초" +
                 E + " 동안 " + A + "{q_slow}%" + E + " 둔화.",
        "skill2": "대상 발밑에서 뿌리가 솟아 " + phys("e_dmg", "e_ratio") + " " + O + "물리 피해" + E + "와 " + R + "속박 {e_root}초" + E +
                  "; 자신은 " + phys("e_sh", "e_sh_ad") + " 보호막(" + A + "{e_sh_t}초" + E + ").",
        "ult": "적 챔피언에게 도약해 주변 적에게 " + phys("r_dmg", "r_ratio", "r_hp", " 최대 체력") + " " + O + "물리 피해" + E + "(한 칸 멀어질 "
               "때마다 " + A + "-{r_fall}%" + E + ", 최소 " + A + "{r_min}%" + E + "); 이번 전투에서 처음 맞으면 " + R + "{r_up}초 에어본" + E +
               ". 이어서 바위 " + A + "{r_rocks}" + E + "개가 떨어집니다.",
        "names": ("바위 던지기", "이끼 움켜쥐기", "지진 강타"),
    },
    "ja": {
        "name": "ブロック",
        "attack": "両拳を叩きつけ" + AD + "の" + O + "物理ダメージ" + E + "、対象の周囲の敵に" + ADi + O + "{a_splash}%" + E + "の範囲ダメージ。"
                  "3回目ごとに対象を" + A + "{a_up}秒" + E + R + "打ち上げ" + E + "。" + O + "岩の心" + E + "：行動妨害無効。",
        "skill": "対象に大岩を投げつけ" + phys("q_dmg", "q_ratio", "q_hp", "最大体力") + "の" + O + "物理ダメージ" + E + "、" + A + "{q_slow}%" +
                 E + "スロウ（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "対象の足元から根が噴き出し" + phys("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "と" + R + "{e_root}秒のスネア" + E +
                  "。自身は" + phys("e_sh", "e_sh_ad") + "のシールド（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "敵チャンピオンへ跳びかかり周囲の敵に" + phys("r_dmg", "r_ratio", "r_hp", "最大体力") + "の" + O + "物理ダメージ" + E + "（1マス"
               "ごとに" + A + "-{r_fall}%" + E + "、最低" + A + "{r_min}%" + E + "）。この戦闘で初めて当たった敵は" + R + "{r_up}秒打ち上げ" + E +
               "。続いて岩が" + A + "{r_rocks}" + E + "個落ちる。",
        "names": ("巨岩投げ", "苔の握撃", "サイズミックスラム"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_brock's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.4), ("a_up", 0.45),
    ("q", 0.45), ("q_hit", 0.45),
    ("e", 0.45), ("e_root", 0.4), ("e_shield", 0.4),
    ("r", 0.55), ("r_slam", 0.55), ("r_hit", 0.45), ("r_rock", 0.35),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/brock.rs: the slam's knock-up, his crumbling)
DLL_SOUNDS = {f"{ID}_r_hit", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("a_splash", "q_dmg", "q_ratio", "q_hp", "q_slow", "e_dmg", "e_ratio", "e_sh", "e_sh_ad", "r_dmg",
                           "r_ratio", "r_hp", "r_fall", "r_min", "r_rocks")}
    for k in ("a_up", "q_slow_t", "e_root", "e_sh_t", "r_up"):
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
        lens = {k: shown_length(d[k]) for k in ("attack", "skill", "skill2", "ult")}
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_brock.py")
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
    mi["last_updated"] = "2026-11-02"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
