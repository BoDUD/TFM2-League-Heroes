"""The Crimson Raptor's text (5 languages), sound_info files and the tft pack's shared files, numbers from
build_raptor.P.

    python tools/kit/setup_raptor.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_sentinel.py writes for the Blue Sentinel:
mod.mod_info (VERSION, the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type
native for tft.dll, the keys sorted), text/champion.i18n (tft_raptor in every language, description + skill_name),
sound/sfx/tft_raptor_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_CrimsonRaptor18, 2026-10-31): zh_CN 深红锋喙鸟,
zh_TW 巨喙鳥媽媽, ja ママ鳥, ko 어미 부리, en Mama Beak; its ability Flock Family = 鸟群之家 (zh_TW 飛禽家族, ja フロックファミリー,
ko 새 떼 가족), Orange Buff = 橙霸符 (zh_TW 橘色增益, ja オレンジバフ, ko 오렌지 버프) from the same text. Feather Shot (锋羽射击),
Feather Fan (羽刃扇射) and Startled Hop (惊飞跃退) are our own (the user's pick, plan A 「鸟群之家」).
The texts are the rules it plays with tft.dll (addons/tft/src/raptor.rs): the fan's feathers each stopping at the first
enemy, Orange Buff capped at p_max stacks.
Sounds: tools/lol/extract_raptor.py's clips in tft/sound/sfx/tft_raptor_sfx_*.wav (git-ignored) - the Rift's own
raptors (the big one's shot, hit, screeches and death; the little ones' spawn, pecks and death for the Tiny Beaks),
Xayah, Quinn, Vayne and Jarvan IV for the rest. A clip name never equals an event name (vo-clip-names rule): event
tft_raptor_<x> plays clip tft_raptor_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_raptor import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29
VERSION = "0.29.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its near eye (the design's eye at
# column 55, row 29 of 56 at PPU 1.56: 17 over the ground, 8 ahead of its standing point, the design's pivot column 42 -
# ppu_restyle's face_to); the centre in its body (half its 36 px); the ban/pick card by bp_card_audit.py's rule (-39
# less the idle frame's top over its centre, -24.5: its crest 1 game px under the card's top)
VIEW = {"face": {"x": 8, "y": -17}, "center": {"x": 0, "y": -18}, "banpick_center": {"x": 0, "y": -14}}


def phys(d, r):
    """base + AD ratio, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "深红锋喙鸟",
        "attack": "甩出一根锋羽，造成" + AD + O + "物理伤害" + E + "。" + O + "橙霸符" + E + "：它的物理伤害使目标护甲" + R + "-{p_arm}" + E + "（" +
                  A + "{p_t}秒" + E + "，最多" + A + "{p_max}层" + E + "）。",
        "skill": "张开翅膀，扇形甩出" + A + "{q_n}根" + E + "羽刃，每根命中第一个敌人，造成" + phys("q_dmg", "q_ratio") + O + "物理伤害" + E + "。",
        "skill2": "受惊尖叫，往后一跳，之后" + A + "{e_t}秒" + E + "攻速" + A + "+{e_as}%" + E + "。",
        "ult": "召唤" + A + "4只" + E + "不可选中的小锋喙鸟（" + A + "{r_t}秒" + E + "）：它每次普攻，小鸟们一起啄同一目标，各造成" +
               phys("r_dmg", "r_ratio") + O + "物理伤害" + E + "。",
        "names": ("羽刃扇射", "惊飞跃退", "鸟群之家"),
    },
    "zh-hant": {
        "name": "巨喙鳥媽媽",
        "attack": "甩出一根鋒羽，造成" + AD + O + "物理傷害" + E + "。" + O + "橘色增益" + E + "：牠的物理傷害使目標物防" + R + "-{p_arm}" + E + "（" +
                  A + "{p_t}秒" + E + "，最多" + A + "{p_max}層" + E + "）。",
        "skill": "張開翅膀，扇形甩出" + A + "{q_n}根" + E + "羽刃，每根命中第一個敵人，造成" + phys("q_dmg", "q_ratio") + O + "物理傷害" + E + "。",
        "skill2": "受驚尖叫，往後一跳，之後" + A + "{e_t}秒" + E + "攻速" + A + "+{e_as}%" + E + "。",
        "ult": "召喚" + A + "4隻" + E + "無法被指定的小巨喙鳥（" + A + "{r_t}秒" + E + "）：牠每次普攻，小鳥們一起啄同一目標，各造成" +
               phys("r_dmg", "r_ratio") + O + "物理傷害" + E + "。",
        "names": ("羽刃扇射", "驚飛躍退", "飛禽家族"),
    },
    "en": {
        "name": "Mama Beak",
        "attack": "Flings a sharp feather for " + AD + " " + O + "physical damage" + E + ". " + O + "Orange Buff" + E +
                  ": its physical damage takes " + R + "{p_arm}" + E + " armour off the target for " + A + "{p_t}s" + E +
                  " (up to " + A + "{p_max}" + E + " stacks).",
        "skill": "Spreads its wings and flings " + A + "{q_n}" + E + " blade feathers in a fan, each hitting the first enemy for " +
                 phys("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ".",
        "skill2": "Startled, it screeches and hops back, then gains " + A + "+{e_as}%" + E + " attack speed for " + A + "{e_t}s" +
                  E + ".",
        "ult": "Calls " + A + "4" + E + " untargetable Tiny Beaks for " + A + "{r_t}s" + E + ": each of its attacks, they peck the "
               "same enemy for " + phys("r_dmg", "r_ratio") + " " + O + "physical damage" + E + " each.",
        "names": ("Feather Fan", "Startled Hop", "Flock Family"),
    },
    "ko": {
        "name": "어미 부리",
        "attack": "날카로운 깃털을 던져 " + AD + " " + O + "물리 피해" + E + ". " + O + "오렌지 버프" + E + ": 물리 피해를 입히면 대상의 방어력 " + R +
                  "-{p_arm}" + E + "(" + A + "{p_t}초" + E + ", 최대 " + A + "{p_max}" + E + "중첩).",
        "skill": "날개를 펼쳐 깃날 " + A + "{q_n}개" + E + "를 부채꼴로 던집니다. 각각 처음 맞힌 적에게 " + phys("q_dmg", "q_ratio") + " " + O +
                 "물리 피해" + E + ".",
        "skill2": "깜짝 놀라 울며 뒤로 뛴 뒤 " + A + "{e_t}초" + E + " 동안 공격 속도 " + A + "+{e_as}%" + E + ".",
        "ult": "대상으로 지정할 수 없는 꼬마 부리 " + A + "4마리" + E + "를 " + A + "{r_t}초" + E + " 동안 소환합니다. 기본 공격할 때마다 같은 적을 쪼아 각각 " +
               phys("r_dmg", "r_ratio") + " " + O + "물리 피해" + E + ".",
        "names": ("깃날 부채", "화들짝 뜀", "새 떼 가족"),
    },
    "ja": {
        "name": "ママ鳥",
        "attack": "鋭い羽根を放ち" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "オレンジバフ" + E + "：物理ダメージを与えると対象の物理防御" + R +
                  "-{p_arm}" + E + "（" + A + "{p_t}秒" + E + "、最大" + A + "{p_max}" + E + "スタック）。",
        "skill": "翼を広げ、刃の羽根を" + A + "{q_n}本" + E + "扇状に放つ。それぞれ最初に当たった敵に" + phys("q_dmg", "q_ratio") + "の" + O +
                 "物理ダメージ" + E + "。",
        "skill2": "驚いて鳴き、後ろへ跳ねる。その後" + A + "{e_t}秒" + E + "間攻撃速度" + A + "+{e_as}%" + E + "。",
        "ult": "対象指定不可のミニヒナ鳥を" + A + "4体" + E + "召喚（" + A + "{r_t}秒" + E + "）：攻撃するたびに同じ敵をついばみ、それぞれ" +
               phys("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "names": ("羽刃の扇", "びっくり跳び", "フロックファミリー"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_raptor's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.35),
    ("p", 0.3),
    ("q", 0.5), ("q_vo", 0.45), ("q_hit", 0.3),
    ("e", 0.45), ("e_vo", 0.45), ("e_rush", 0.4),
    ("r", 0.55), ("r_chick", 0.45), ("r_peck", 0.25), ("r_peck_hit", 0.25), ("r_end", 0.35),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/raptor.rs: Orange Buff filling, a feather's hit, its death cry)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_q_hit", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("p_arm", "p_max", "q_n", "q_dmg", "q_ratio", "e_as", "r_dmg", "r_ratio")}
    for k in ("p_t", "e_t", "r_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_raptor.py")
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
