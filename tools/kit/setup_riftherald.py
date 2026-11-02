"""The Rift Herald's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_riftherald.P.

    python tools/kit/setup_riftherald.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_brock.py writes for Brock: mod.mod_info (VERSION, the
pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys
sorted), text/champion.i18n (tft_riftherald in every language, description + skill_name),
sound/sfx/tft_riftherald_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT's own (CommunityDragon cdragon/tft/<locale>.json, TFT16_RiftHerald and set 9's TFT_RiftHerald, 2026-11-02):
zh_CN 峡谷先锋, zh_TW 預示者, ja リフトヘラルド, ko 협곡의 전령, en Rift Herald; its set-16 ability Warp Armor = 扭曲护甲 (zh_TW 扭曲
護甲, ja ワープアーマー, ko 왜곡 외피) and set 9's Void Charge = 虚空冲锋 (zh_TW 虛空衝鋒, ja ヴォイドチャージ, ko 공허 돌진). Void Shell
(虚空甲壳), Rending Pincer (裂钳) and Spin Sweep (回旋横扫) are ours (the user's OK of the proposed kit, top, 2026-11-02).
The texts are the rules it plays: the void shell counted in tft.dll (addons/tft/src/riftherald.rs), the rest the data.
Sounds: tools/lol/extract_riftherald.py's clips in tft/sound/sfx/tft_riftherald_sfx_*.wav (git-ignored) - all its own:
the Rift's Herald (Map11) and set 16's (Map22). A clip name never equals an event name (vo-clip-names rule): event
tft_riftherald_<x> plays clip tft_riftherald_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_riftherald import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33, Gromp 0.34, the encyclopedia
# centres 0.35 (PR #657), the log fixes 0.36 (PR #659), the Sentry 0.37, Brock 0.38, the Cinderling 0.39, the Rift Herald
# 0.40
VERSION = "0.40.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its soles' point, up negative): the face point between its magenta eyes (ppu_restyle's
# face_to: hd/idle.png's eyes (81, 39) from the pivot (55, 88) at PPU 2.0); the centre by League's rule
# (tools/art/bp_card_audit.py --centers: its solid top 44 px up -> -17, as Brock's); the ban/pick card as Brock's (the
# same 44 px)
VIEW = {"face": {"x": 13, "y": -25}, "center": {"x": 0, "y": -17}, "banpick_center": {"x": 0, "y": -6}}


def phys(d, r, h=None, hp=""):
    """d + r% AD (+ h% of its maximum health), physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}" + (f" + {O}{{{h}}}%{E}{hp}" if h else "")


def mag(d, r=None, h=None, hp=""):
    """d (+ r% AP) (+ h% of its maximum health), magic."""
    return f"{M}{{{d}}}{E}" + (f" + {APi}{M}{{{r}}}%{E}" if r else "") + (f" + {M}{{{h}}}%{E}{hp}" if h else "")


TEXT = {
    "zh-hans": {
        "name": "峡谷先锋",
        "attack": "钳爪砸下，造成" + AD + O + "物理伤害" + E + "。" + O + "虚空甲壳" + E + "：身边每有一名敌方英雄，受到伤害" + A + "-{p_dr}%" + E +
                  "（最多" + A + "{p_max}名" + E + "）。",
        "skill": "原地转一圈，周围敌人受到" + phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理伤害" + E + "并减速" + A + "{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "直立蓄力后翻身冲向敌方英雄：沿途敌人受到" + mag("e_dmg", None, "e_hp", "最大生命") + M + "魔法伤害" + E + "并被撞开，撞到的英雄" +
                  "再受一次并" + R + "晕眩{e_stun}秒" + E + "。",
        "ult": "长啸变大，最大生命" + A + "+{r_hpb}" + E + "；猛击前方，敌人受到" + mag("r_dmg", "r_ap", "r_hp", "最大生命") + M + "魔法伤害" + E +
               "；" + A + "{r_t}秒" + E + "内受到伤害" + A + "-{r_dr}%" + E + "，虚空甲壳每名敌人再" + A + "-{r_per}%" + E + "。",
        "names": ("回旋横扫", "虚空冲锋", "扭曲护甲"),
    },
    "zh-hant": {
        "name": "預示者",
        "attack": "鉗爪砸下，造成" + AD + O + "物理傷害" + E + "。" + O + "虛空甲殼" + E + "：身邊每有一名敵方英雄，受到傷害" + A + "-{p_dr}%" + E +
                  "（最多" + A + "{p_max}名" + E + "）。",
        "skill": "原地轉一圈，周圍敵軍受到" + phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理傷害" + E + "並緩速" + A + "{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "直立蓄力後翻身衝向敵方英雄：沿途敵軍受到" + mag("e_dmg", None, "e_hp", "最大生命") + M + "魔法傷害" + E + "並被撞開，撞到的英雄" +
                  "再受一次並" + R + "暈眩{e_stun}秒" + E + "。",
        "ult": "長嘯變大，最大生命" + A + "+{r_hpb}" + E + "；猛擊前方，敵軍受到" + mag("r_dmg", "r_ap", "r_hp", "最大生命") + M + "魔法傷害" + E +
               "；" + A + "{r_t}秒" + E + "內受到傷害" + A + "-{r_dr}%" + E + "，虛空甲殼每名敵人再" + A + "-{r_per}%" + E + "。",
        "names": ("迴旋橫掃", "虛空衝鋒", "扭曲護甲"),
    },
    "en": {
        "name": "Rift Herald",
        "attack": "Brings a pincer down for " + AD + " " + O + "physical damage" + E + ". " + O + "Void Shell" + E + ": takes " + A + "{p_dr}%" + E +
                  " less damage for each enemy champion nearby (up to " + A + "{p_max}" + E + ").",
        "skill": "Spins round once: nearby enemies take " + phys("q_dmg", "q_ratio", "q_hp", " max Health") + " " + O + "physical damage" + E +
                 " and are slowed by " + A + "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Rears up, flips and charges an enemy champion: enemies in the way take " + mag("e_dmg", None, "e_hp", " max Health") + " " +
                  M + "magic damage" + E + " and are knocked aside; champions where it lands take it again and are " + R + "stunned for "
                  "{e_stun}s" + E + ".",
        "ult": "Roars and grows (" + A + "+{r_hpb}" + E + " max Health), then slams the ground ahead: enemies take " +
               mag("r_dmg", "r_ap", "r_hp", " max Health") + " " + M + "magic damage" + E + ". For " + A + "{r_t}s" + E + " it takes " + A +
               "{r_dr}%" + E + " less damage, and its Void Shell " + A + "{r_per}%" + E + " more per enemy.",
        "names": ("Spin Sweep", "Void Charge", "Warp Armor"),
    },
    "ko": {
        "name": "협곡의 전령",
        "attack": "집게발을 내리찍어 " + AD + " " + O + "물리 피해" + E + ". " + O + "공허 껍질" + E + ": 주변 적 챔피언 하나당 받는 피해 " + A + "-{p_dr}%" +
                  E + "(최대 " + A + "{p_max}명" + E + ").",
        "skill": "제자리에서 한 바퀴 돌아 주변 적에게 " + phys("q_dmg", "q_ratio", "q_hp", " 최대 체력") + " " + O + "물리 피해" + E + "와 " + A +
                 "{q_slow}%" + E + " 둔화(" + A + "{q_slow_t}초" + E + ").",
        "skill2": "일어섰다가 몸을 뒤집어 적 챔피언에게 돌진: 경로의 적은 " + mag("e_dmg", None, "e_hp", " 최대 체력") + " " + M + "마법 피해" + E +
                  "를 입고 밀려나며, 부딪힌 챔피언은 한 번 더 피해를 입고 " + R + "{e_stun}초 기절" + E + ".",
        "ult": "포효하며 커집니다(최대 체력 " + A + "+{r_hpb}" + E + "). 앞을 내리찍어 적에게 " + mag("r_dmg", "r_ap", "r_hp", " 최대 체력") + " " + M +
               "마법 피해" + E + ". " + A + "{r_t}초" + E + " 동안 받는 피해 " + A + "-{r_dr}%" + E + ", 공허 껍질은 적 하나당 " + A + "-{r_per}%" + E +
               " 더.",
        "names": ("회전 휩쓸기", "공허 돌진", "왜곡 외피"),
    },
    "ja": {
        "name": "リフトヘラルド",
        "attack": "ハサミを振り下ろし" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ヴォイドシェル" + E + "：近くの敵チャンピオン1体ごとに被ダメージ" +
                  A + "-{p_dr}%" + E + "（最大" + A + "{p_max}体" + E + "）。",
        "skill": "その場で一回転し、周囲の敵に" + phys("q_dmg", "q_ratio", "q_hp", "最大体力") + "の" + O + "物理ダメージ" + E + "と" + A +
                 "{q_slow}%" + E + "スロウ（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "立ち上がって体を翻し敵チャンピオンへ突進：通り道の敵に" + mag("e_dmg", None, "e_hp", "最大体力") + "の" + M + "魔法ダメージ" + E +
                  "と押しのけ、ぶつかったチャンピオンにもう一度与えて" + R + "{e_stun}秒スタン" + E + "。",
        "ult": "咆哮して巨大化（最大体力" + A + "+{r_hpb}" + E + "）。前方を叩きつけ敵に" + mag("r_dmg", "r_ap", "r_hp", "最大体力") + "の" + M +
               "魔法ダメージ" + E + "。" + A + "{r_t}秒" + E + "間被ダメージ" + A + "-{r_dr}%" + E + "、ヴォイドシェルは敵1体ごとにさらに" + A + "-{r_per}%" +
               E + "。",
        "names": ("回転スイープ", "ヴォイドチャージ", "ワープアーマー"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_riftherald's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.4),
    ("q", 0.45), ("q_vox", 0.4), ("q_hit", 0.4),
    ("e", 0.45), ("e_boom", 0.45), ("e_hit", 0.5),
    ("r", 0.5), ("r_roar", 0.5), ("r_hit", 0.55), ("r_armor", 0.4),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/riftherald.rs: its collapse)
DLL_SOUNDS = {f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_dr", "p_max", "q_dmg", "q_ratio", "q_hp", "q_slow", "e_dmg", "e_hp", "r_hpb", "r_dmg", "r_ap",
                           "r_hp", "r_dr", "r_per")}
    for k in ("q_slow_t", "e_stun", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_riftherald.py")
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
