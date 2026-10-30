"""Zippy's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_zippy.P.

    python tools/kit/setup_zippy.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sohm.py writes for Sohm: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_zippy in every language, description + skill_name), sound/sfx/tft_zippy_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only its keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_DragonGuild, 2026-10-31): zh_CN 呲呲, zh_TW 橘皮,
ja ジッピー, ko 쌩쌩이, en Zippy; its ability Somersault Assault = 翻滚突袭 / 筋斗突進 / サマーソルトアサルト / 공중제비 공격, the Guild
trait 冒险家 / 冒險者公會 / ギルド / 길드 (the passive 冒险家之魂). Backflip Kick (后空翻踢) and Rolling Charge (翻滚冲锋) are our own
(the user's pick, plan A 「冒险家突击」).
The texts are the rules it plays with tft.dll (addons/tft/src/zippy.rs): the armour per nearby ally, the leap at the
healthiest enemy champion.
Sounds: tools/lol/extract_zippy.py's clips in tft/sound/sfx/tft_zippy_sfx_*.wav (git-ignored) - its own set-7 TFT sounds
(its kicks, the ball roll, the leap, the speed buff, the guild's chime, its voice), Kled (the roll's bump, the shield,
the landing) and the Rift's Razorbeak (the death). A clip name never equals an event name (vo-clip-names rule): event
tft_zippy_<x> plays clip tft_zippy_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zippy import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Zippy 0.25 (Terra's branch takes the next free one when it merges first)
VERSION = "0.25.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its eye (the design's eye at column 42,
# row 26 of 83 at PPU 2.2: 26 over the ground, 10 ahead of its standing column 20 - ppu_restyle's face_to); the centre in
# its chest; the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -26.5 over the frame centre: the head
# spikes 1 game px under the card's top)
VIEW = {"face": {"x": 10, "y": -26}, "center": {"x": 2, "y": -16}, "banpick_center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "呲呲",
        "attack": "抬腿一蹬，造成" + AD + O + "物理伤害" + E + "。" + O + "冒险家之魂" + E + "：身边每有一个友方英雄，护甲和魔抗" + A +
                  "+{p_def}" + E + "（最多" + A + "{p_max}" + E + "个）。",
        "skill": "后空翻踢中目标，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并击飞" + A + "{q_up}秒" + E + "。",
        "skill2": "缩成羽毛球滚向敌人，路上的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "；身边友方英雄移速" + A +
                  "+{e_ms}%" + E + "（" + A + "{e_ms_t}秒" + E + "）。",
        "ult": "获得" + phys("r_sh", "r_sh_ad") + "护盾（" + A + "{r_sh_t}秒" + E + "），跃起砸向生命百分比最高的敌方英雄（免疫控制），"
               "造成" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "，晕眩" + A + "{r_stun}秒" + E + "并略微击退。",
        "names": ("后空翻踢", "翻滚冲锋", "翻滚突袭"),
    },
    "zh-hant": {
        "name": "橘皮",
        "attack": "抬腿一蹬，造成" + AD + O + "物理傷害" + E + "。" + O + "冒險者之魂" + E + "：身邊每有一個友方英雄，物防和魔防" + A +
                  "+{p_def}" + E + "（最多" + A + "{p_max}" + E + "個）。",
        "skill": "後空翻踢中目標，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並擊飛" + A + "{q_up}秒" + E + "。",
        "skill2": "縮成羽毛球滾向敵人，路上的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "；身邊友方英雄移速" + A +
                  "+{e_ms}%" + E + "（" + A + "{e_ms_t}秒" + E + "）。",
        "ult": "獲得" + phys("r_sh", "r_sh_ad") + "護盾（" + A + "{r_sh_t}秒" + E + "），躍起砸向生命百分比最高的敵方英雄（免疫控制），"
               "造成" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "，暈眩" + A + "{r_stun}秒" + E + "並略微擊退。",
        "names": ("後空翻踢", "翻滾衝鋒", "筋斗突進"),
    },
    "en": {
        "name": "Zippy",
        "attack": "A claw kick for " + AD + " " + O + "physical damage" + E + ". " + O + "Adventurer's Spirit" + E + ": " + A +
                  "+{p_def}" + E + " armor and magic resist for each allied champion nearby (up to " + A + "{p_max}" + E + ").",
        "skill": "Backflips and kicks the target for " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E +
                 ", knocking it up for " + A + "{q_up}s" + E + ".",
        "skill2": "Curls into a ball and rolls at an enemy: " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E +
                  " to enemies rolled over; nearby allied champions gain " + A + "{e_ms}%" + E + " move speed for " + A +
                  "{e_ms_t}s" + E + ".",
        "ult": "Gains a " + phys("r_sh", "r_sh_ad") + " shield for " + A + "{r_sh_t}s" + E + ", then leaps at the enemy champion "
               "with the highest percent health (immune to crowd control): " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + ", a " + A + "{r_stun}s" + E + " stun and a short knockback.",
        "names": ("Backflip Kick", "Rolling Charge", "Somersault Assault"),
    },
    "ko": {
        "name": "쌩쌩이",
        "attack": "발톱 차기로 " + AD + " " + O + "물리 피해" + E + ". " + O + "모험가의 혼" + E + ": 주변 아군 챔피언 하나마다 방어력·"
                  "마법 저항력 " + A + "+{p_def}" + E + "(최대 " + A + "{p_max}" + E + "명).",
        "skill": "공중제비로 대상을 차서 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", " + A + "{q_up}초" + E +
                 " 동안 띄워 올림.",
        "skill2": "공처럼 몸을 말아 적에게 굴러가 경로의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + ", 주변 아군 "
                  "챔피언 이동 속도 " + A + "+{e_ms}%" + E + "(" + A + "{e_ms_t}초" + E + ").",
        "ult": phys("r_sh", "r_sh_ad") + " 보호막(" + A + "{r_sh_t}초" + E + ") 후 체력 비율이 가장 높은 적 챔피언에게 도약(군중 제어 "
               "면역), " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ", 기절 " + A + "{r_stun}초" + E + ", 살짝 밀쳐냄.",
        "names": ("공중제비 차기", "구르기 돌진", "공중제비 공격"),
    },
    "ja": {
        "name": "ジッピー",
        "attack": "爪で蹴り" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "冒険者の魂" + E + "：近くの味方チャンピオン1体ごとに"
                  "物理防御・魔法防御" + A + "+{p_def}" + E + "（最大" + A + "{p_max}" + E + "体）。",
        "skill": "バク宙キックで対象に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、" + A + "{q_up}秒" + E +
                 "打ち上げる。",
        "skill2": "羽毛の玉になって敵へ転がり、通った敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "、近くの味方"
                  "チャンピオンの移動速度" + A + "+{e_ms}%" + E + "（" + A + "{e_ms_t}秒" + E + "）。",
        "ult": phys("r_sh", "r_sh_ad") + "のシールド（" + A + "{r_sh_t}秒" + E + "）を得て、体力割合が最も高い敵チャンピオンへ跳ぶ"
               "（行動妨害無効）：" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "、スタン" + A + "{r_stun}秒" + E +
               "、少しノックバック。",
        "names": ("バク宙キック", "ローリングチャージ", "サマーソルトアサルト"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_zippy's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.3),
    ("q", 0.5), ("q_hit", 0.45),
    ("e", 0.5), ("e_roll", 0.45), ("e_hit", 0.45), ("e_speed", 0.35),
    ("r", 0.5), ("r_vo", 0.55), ("r_shield", 0.45), ("r_spin", 0.45), ("r_hit", 0.55), ("r_land", 0.45),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/zippy.rs: the guild's chime, the crash, the landing, its death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "r_hit", "r_land", "d")}


def values(p):
    v = {k: p[k] for k in ("p_def", "p_max", "q_dmg", "q_ad", "e_dmg", "e_ad", "e_ms", "r_sh", "r_sh_ad", "r_dmg", "r_ad")}
    for k in ("q_up", "e_ms_t", "r_sh_t", "r_stun"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_zippy.py")
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
    mi["last_updated"] = "2026-10-31"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
