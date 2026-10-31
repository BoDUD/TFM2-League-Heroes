"""The Elder Dragon's text (5 languages), sound_info files and the tft pack's shared files, numbers from
build_elderdragon.P.

    python tools/kit/setup_elderdragon.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_raptor.py writes for the Crimson Raptor:
mod.mod_info (VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type
native for tft.dll, the keys sorted), text/champion.i18n (tft_elderdragon in every language, description + skill_name),
sound/sfx/tft_elderdragon_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound:
its event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_18_ElderDragon, 2026-11-01): zh_CN 远古巨龙,
zh_TW 遠古巨龍, ja エルダードラゴン, ko 장로 드래곤, en Elder Dragon; its ability Heat Without Equal = 绝伦火热 (zh_TW
無與倫比的熱力, ja 比類なき熱, ko 비할 데 없는 열기), Flame Breath = 烈焰吐息 (zh_TW 龍之吐息, ja フレイムブレス, ko 화염 숨결),
the Elder buff = 远古巨龙霸符 (zh_TW 遠古巨龍增益, ja エルダードラゴンのバフ, ko 장로 드래곤 버프) and Ignite = 引燃 (zh_TW 點燃, ja
発火, ko 점화) from the same text. Dragonfire Bite (龙焰撕咬) and Wing Storm (龙翼风暴) are our own (the user's pick, plan A
「绝伦火热」).
The texts are the rules it plays with tft.dll (addons/tft/src/elderdragon.rs): the execute on champions only, the
breath's decay, the Ignite on what is no tower.
Sounds: tools/lol/extract_elderdragon.py's clips in tft/sound/sfx/tft_elderdragon_sfx_*.wav (git-ignored) - the Rift's
own Elder Dragon (its bite, breath, cries, take-off, landing, roar and death), Brand, Janna and Malphite for the rest.
A clip name never equals an event name (vo-clip-names rule): event tft_elderdragon_<x> plays clip
tft_elderdragon_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_elderdragon import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30
VERSION = "0.30.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its near eye (the design's eye at
# column 125, row 95 of 125 at PPU 2.84: 11 over the ground, 18 ahead of its standing point, the design's pivot column
# 74 - ppu_restyle's face_to); the centre in its body (half its 44 px); the ban/pick card by bp_card_audit.py's rule
# with hd.rs's UI_SIZES 0.85 (-39 less the idle frame's top over its centre, -27.8 at 0.85: its raised wing tip 1 game px
# under the card's top; the idle reel's snippet is the wings beaten down and the card plays no ult, whose flight would
# leave the card)
VIEW = {"face": {"x": 18, "y": -11}, "center": {"x": 0, "y": -22}, "banpick_center": {"x": 0, "y": -11}}


def phys(d, r):
    """base + AD ratio, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "远古巨龙",
        "attack": "撕咬目标，造成" + AD + O + "物理伤害" + E + "，目标身边的敌人受到" + ADi + O + "{a_splash}%" + E + "溅射。" + O + "远古巨龙霸符" + E +
                  "：被它伤害后生命低于" + R + "{p_exec}%" + E + "的敌方英雄直接被处决。",
        "skill": "朝穿过目标、敌人最多的直线喷吐龙焰，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "，每烧过一人伤害" + R + "-{q_decay}%" + E +
                 "（最低" + A + "{q_min}%" + E + "），并" + O + "引燃" + E + "：" + A + "{ig_t}秒" + E + "内每秒受到" + R + "{ig_pct}%" + E + "最大生命的物理伤害。",
        "skill2": "立起身猛拍双翼，身边的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "、被击退并减速" + A + "{e_slow}%" + E + "（" + A + "{e_t}秒" + E +
                  "），自己受到的伤害" + R + "-{e_dr}%" + E + "。",
        "ult": "无敌飞上天空，" + A + "{r_air}秒" + E + "后砸落：大范围敌人受到" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "、晕眩" + A + "{r_stun}秒" + E +
               "并被" + O + "引燃" + E + "；获得" + A + "{r_vamp}%" + E + "全能吸血（" + A + "{r_vamp_t}秒" + E + "），立刻喷一次" + O + "烈焰吐息" + E + "。",
        "names": ("烈焰吐息", "龙翼风暴", "绝伦火热"),
    },
    "zh-hant": {
        "name": "遠古巨龍",
        "attack": "撕咬目標，造成" + AD + O + "物理傷害" + E + "，目標身邊的敵軍受到" + ADi + O + "{a_splash}%" + E + "濺射。" + O + "遠古巨龍增益" + E +
                  "：被牠傷害後生命低於" + R + "{p_exec}%" + E + "的敵方英雄直接被處決。",
        "skill": "朝穿過目標、敵軍最多的直線噴火，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "，每穿過一人傷害" + R + "-{q_decay}%" + E +
                 "（最低" + A + "{q_min}%" + E + "），並" + O + "點燃" + E + "：" + A + "{ig_t}秒" + E + "內每秒受到" + R + "{ig_pct}%" + E + "最大生命的物理傷害。",
        "skill2": "挺身猛拍雙翼，身邊的敵軍受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "、被擊退並緩速" + A + "{e_slow}%" + E + "（" + A + "{e_t}秒" + E +
                  "），自身受到的傷害" + R + "-{e_dr}%" + E + "。",
        "ult": "進入無敵飛上天空，" + A + "{r_air}秒" + E + "後落下：大範圍敵軍受到" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "、暈眩" + A + "{r_stun}秒" +
               E + "並被" + O + "點燃" + E + "；獲得" + A + "{r_vamp}%" + E + "全能吸血（" + A + "{r_vamp_t}秒" + E + "），立即施放" + O + "龍之吐息" + E + "。",
        "names": ("龍之吐息", "龍翼風暴", "無與倫比的熱力"),
    },
    "en": {
        "name": "Elder Dragon",
        "attack": "Bites for " + AD + " " + O + "physical damage" + E + "; enemies next to the target take " + ADi + O + "{a_splash}%" + E +
                  ". " + O + "Elder buff" + E + ": enemy champions it leaves under " + R + "{p_exec}%" + E + " health are executed.",
        "skill": "Breathes fire along the line through the target with the most enemies: " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + ", " + R + "{q_decay}%" + E + " less per enemy passed (min " + A + "{q_min}%" + E + "), and " + O +
                 "Ignites" + E + " them: " + R + "{ig_pct}%" + E + " max health physical a second for " + A + "{ig_t}s" + E + ".",
        "skill2": "Rears up and beats its wings: nearby enemies take " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E +
                  ", are knocked back and slowed " + A + "{e_slow}%" + E + " (" + A + "{e_t}s" + E + "); it takes " + R + "{e_dr}%" + E +
                  " less damage.",
        "ult": "Invulnerable, it flies up and lands after " + A + "{r_air}s" + E + ": enemies in a wide area take " + phys("r_dmg", "r_ad") +
               " " + O + "physical damage" + E + ", are stunned " + A + "{r_stun}s" + E + " and " + O + "Ignited" + E + "; it gains " + A +
               "{r_vamp}%" + E + " omnivamp (" + A + "{r_vamp_t}s" + E + ") and casts " + O + "Flame Breath" + E + " at once.",
        "names": ("Flame Breath", "Wing Storm", "Heat Without Equal"),
    },
    "ko": {
        "name": "장로 드래곤",
        "attack": "대상을 물어 " + AD + " " + O + "물리 피해" + E + ", 대상과 인접한 적에게 " + ADi + O + "{a_splash}%" + E + ". " + O + "장로 드래곤 버프" + E +
                  ": 피해를 입은 뒤 체력이 " + R + "{p_exec}%" + E + " 이하인 적 챔피언을 처형합니다.",
        "skill": "대상을 관통하며 적이 가장 많은 일직선에 불을 내뿜어 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", 관통한 적 하나당 " + R +
                 "-{q_decay}%" + E + "(최소 " + A + "{q_min}%" + E + "). " + O + "점화" + E + ": " + A + "{ig_t}초" + E + " 동안 매초 최대 체력의 " + R +
                 "{ig_pct}%" + E + " 물리 피해.",
        "skill2": "몸을 일으켜 날개를 내리쳐 주변 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + ", 밀쳐 내고 " + A + "{e_slow}%" + E +
                  " 둔화(" + A + "{e_t}초" + E + "). 받는 피해 " + R + "-{e_dr}%" + E + ".",
        "ult": "무적 상태로 날아올라 " + A + "{r_air}초" + E + " 뒤 내려찍습니다: 넓은 범위의 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E +
               ", " + A + "{r_stun}초" + E + " 기절, " + O + "점화" + E + ". 모든 피해 흡혈 " + A + "{r_vamp}%" + E + "(" + A + "{r_vamp_t}초" + E + ") 후 즉시 " +
               O + "화염 숨결" + E + ".",
        "names": ("화염 숨결", "용날개 폭풍", "비할 데 없는 열기"),
    },
    "ja": {
        "name": "エルダードラゴン",
        "attack": "噛みついて" + AD + "の" + O + "物理ダメージ" + E + "、対象に隣接する敵に" + ADi + O + "{a_splash}%" + E + "。" + O + "エルダードラゴンのバフ" + E +
                  "：ダメージ後に体力" + R + "{p_exec}%" + E + "以下の敵チャンピオンをキルする。",
        "skill": "対象を通り敵が最も多い直線に炎を吐き" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、敵1体ごとに" + R + "-{q_decay}%" + E +
                 "（最小" + A + "{q_min}%" + E + "）。" + O + "発火" + E + "：" + A + "{ig_t}秒" + E + "間毎秒最大体力の" + R + "{ig_pct}%" + E + "の物理ダメージ。",
        "skill2": "立ち上がって翼を打ち下ろし、周囲の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "、ノックバックと" + A + "{e_slow}%" + E +
                  "スロウ（" + A + "{e_t}秒" + E + "）。被ダメージ" + R + "-{e_dr}%" + E + "。",
        "ult": "無敵となって飛び上がり、" + A + "{r_air}秒" + E + "後に降下：広範囲の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "、" + A +
               "{r_stun}秒" + E + "スタンと" + O + "発火" + E + "。オムニヴァンプ" + A + "{r_vamp}%" + E + "（" + A + "{r_vamp_t}秒" + E + "）を得て即座に" + O +
               "フレイムブレス" + E + "。",
        "names": ("フレイムブレス", "竜翼の嵐", "比類なき熱"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_elderdragon's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.35),
    ("p", 0.45),
    ("q", 0.5), ("q_vo", 0.45), ("q_hit", 0.3), ("burn", 0.25),
    ("e", 0.45), ("e_vo", 0.45), ("e_hit", 0.3),
    ("r", 0.5), ("r_vo", 0.55), ("r_land", 0.5), ("r_slam", 0.45),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/elderdragon.rs: the execute, a breath's hit, the Ignite catching,
# its death)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_q_hit", f"{ID}_burn", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_exec", "a_splash", "q_dmg", "q_ad", "q_decay", "q_min", "e_dmg", "e_ad", "e_slow", "e_dr",
                           "r_dmg", "r_ad", "r_vamp")}
    for k in ("ig_t", "e_t", "r_air", "r_stun", "r_vamp_t"):
        v[k] = secs(p[k])
    v["ig_pct"] = f"{p['ig_hp'] * 60 / p['ig_every'] / 10:g}"   # per mille a tick of ig_every -> % a second
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_elderdragon.py")
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
