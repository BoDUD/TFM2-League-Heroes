"""Idas's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_idas.P.

    python tools/kit/setup_idas.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_nomsy.py writes for Nomsy: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_idas in every language, description + skill_name), sound/sfx/tft_idas_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_DragonGold, 2026-10-30): zh_CN 艾达丝, zh_TW 埃達斯,
ja イダス, ko 이다스, en Idas; her ability Golden Scales = 黄金龙鳞 / 黃金龍甲 / 黄金の鱗 / 황금 비늘 for the ult; her trait
Guardian (护卫 / 守護者 / ガーディアン / 수호자) for the passive's name (护卫之誓, Guardian's Vow). Golden Breath (黄金龙息) and
Dragon's Roar (龙威振翅) are our own (the user's pick, plan A 「黄金守护」). The texts are the rules she plays with tft.dll
(addons/tft/src/idas.rs): the vow's shields at low health on her and the nearest ally.
Sounds: tools/lol/extract_idas.py's clips in tft/sound/sfx/tft_idas_sfx_*.wav (git-ignored) - her own set-7 TFT sounds
(the golden breath's cast and its armour-melting hit, Golden Scales' cast, loop and burst, set 7's flame-breath hit),
Shyvana in dragon form (the claws, the heal), the Rift's drakes (the roars, the wing beat, the death) and the shields of
Lux, Janna and Rakan. A clip name never equals an event name (vo-clip-names rule): event tft_idas_<x> plays clip
tft_idas_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_idas import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20
VERSION = "0.20.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from her feet's point, up negative): the face point on her eye (the design's eye square
# (107, 23) of 127 x 98 at PPU 2.45: 31 over the ground, 18 ahead of her standing column 63 - ppu_restyle's face_to);
# the centre in her chest; the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -40: her crest 1 game
# px under the card's top)
VIEW = {"face": {"x": 18, "y": -31}, "center": {"x": 3, "y": -18}, "banpick_center": {"x": 3, "y": 1}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "艾达丝",
        "attack": "挥爪造成" + AD + O + "物理伤害" + E + "。" + O + "护卫之誓" + E + "：生命值低于" + A + "{p_low}%" + E +
                  "时，她和最近的一名友军各获得她最大生命值" + A + "{p_pct}%" + E + "的护盾（" + A + "{p_t}秒" + E + "），每" + A +
                  "{p_cd}秒" + E + "一次。",
        "skill": "向前喷出扇形金色龙息，造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "，护甲降低" + A + "{q_shred}%" + E +
                 "（" + A + "{q_shred_t}秒" + E + "）。",
        "skill2": "振翅一吼：附近的敌人" + R + "眩晕" + E + A + "{e_stun}秒" + E + "并减速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_slow_t}秒" + E + "）；她和附近友军获得" + mag("e_sh", "e_sh_ap") + "护盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "双翼裹身" + A + "{r_t}秒" + E + "，受到的伤害降低" + A + "{r_red}%" + E + "；然后回复" + mag("r_heal", "r_heal_ap") +
               "生命值，附近友军获得" + mag("r_sh", "r_sh_ap") + "护盾（" + A + "{r_sh_t}秒" + E + "），护盾在时攻速" + A +
               "+{r_as}%" + E + "。",
        "names": ("黄金龙息", "龙威振翅", "黄金龙鳞"),
    },
    "zh-hant": {
        "name": "埃達斯",
        "attack": "揮爪造成" + AD + O + "物理傷害" + E + "。" + O + "守護之誓" + E + "：生命值低於" + A + "{p_low}%" + E +
                  "時，她和最近的一名友軍各獲得她最大生命值" + A + "{p_pct}%" + E + "的護盾（" + A + "{p_t}秒" + E + "），每" + A +
                  "{p_cd}秒" + E + "一次。",
        "skill": "向前噴出扇形金色龍息，造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "，護甲降低" + A + "{q_shred}%" + E +
                 "（" + A + "{q_shred_t}秒" + E + "）。",
        "skill2": "振翅一吼：附近的敵人" + R + "暈眩" + E + A + "{e_stun}秒" + E + "並緩速" + A + "{e_slow}%" + E + "（" + A +
                  "{e_slow_t}秒" + E + "）；她和附近友軍獲得" + mag("e_sh", "e_sh_ap") + "護盾（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "雙翼裹身" + A + "{r_t}秒" + E + "，受到的傷害降低" + A + "{r_red}%" + E + "；接著回復" + mag("r_heal", "r_heal_ap") +
               "生命，附近友軍獲得" + mag("r_sh", "r_sh_ap") + "護盾（" + A + "{r_sh_t}秒" + E + "），護盾存在時攻速" + A +
               "+{r_as}%" + E + "。",
        "names": ("黃金龍息", "龍威振翅", "黃金龍甲"),
    },
    "en": {
        "name": "Idas",
        "attack": "Claws for " + AD + " " + O + "physical damage" + E + ". " + O + "Guardian's Vow" + E + ": under " + A +
                  "{p_low}%" + E + " health she and the nearest ally each get a shield of " + A + "{p_pct}%" + E +
                  " of her max health for " + A + "{p_t}s" + E + ", once every " + A + "{p_cd}s" + E + ".",
        "skill": "Breathes a cone of molten gold for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E +
                 ", cutting armor by " + A + "{q_shred}%" + E + " for " + A + "{q_shred_t}s" + E + ".",
        "skill2": "Beats her wings and roars: nearby enemies are " + R + "stunned" + E + " for " + A + "{e_stun}s" + E +
                  " and slowed " + A + "{e_slow}%" + E + " for " + A + "{e_slow_t}s" + E + "; she and nearby allies get a " +
                  mag("e_sh", "e_sh_ap") + " shield for " + A + "{e_sh_t}s" + E + ".",
        "ult": "Wraps herself in her wings for " + A + "{r_t}s" + E + ", taking " + A + "{r_red}%" + E +
               " less damage; then heals " + mag("r_heal", "r_heal_ap") + " and gives nearby allies a " +
               mag("r_sh", "r_sh_ap") + " shield for " + A + "{r_sh_t}s" + E + " and " + A + "{r_as}%" + E +
               " attack speed while it holds.",
        "names": ("Golden Breath", "Dragon's Roar", "Golden Scales"),
    },
    "ko": {
        "name": "이다스",
        "attack": "발톱으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "수호자의 맹세" + E + ": 체력 " + A + "{p_low}%" + E +
                  " 미만이 되면 자신과 가장 가까운 아군이 각각 자신의 최대 체력 " + A + "{p_pct}%" + E + "의 보호막(" + A +
                  "{p_t}초" + E + ") 획득, " + A + "{p_cd}초" + E + "마다 한 번.",
        "skill": "부채꼴로 녹은 황금을 뿜어 " + mag("q_dmg", "q_ratio") + " " + M + "마법 피해" + E + ", 방어력 " + A +
                 "{q_shred}%" + E + " 감소(" + A + "{q_shred_t}초" + E + ").",
        "skill2": "날개를 펄럭이며 포효: 근처 적 " + R + "기절" + E + " " + A + "{e_stun}초" + E + ", 이동 속도 " + A +
                  "{e_slow}%" + E + " 감소(" + A + "{e_slow_t}초" + E + "); 자신과 근처 아군에게 " + mag("e_sh", "e_sh_ap") +
                  " 보호막(" + A + "{e_sh_t}초" + E + ").",
        "ult": "날개로 몸을 감싸 " + A + "{r_t}초" + E + " 동안 받는 피해 " + A + "{r_red}%" + E + " 감소; 이후 " +
               mag("r_heal", "r_heal_ap") + " 회복, 근처 아군에게 " + mag("r_sh", "r_sh_ap") + " 보호막(" + A + "{r_sh_t}초" +
               E + "), 보호막이 있는 동안 공격 속도 " + A + "+{r_as}%" + E + ".",
        "names": ("황금 숨결", "용의 포효", "황금 비늘"),
    },
    "ja": {
        "name": "イダス",
        "attack": "爪で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ガーディアンの誓い" + E + "：体力" + A + "{p_low}%" + E +
                  "未満になると、自身と最も近い味方がそれぞれ自身の最大体力の" + A + "{p_pct}%" + E + "のシールドを得る（" + A +
                  "{p_t}秒" + E + "、" + A + "{p_cd}秒" + E + "に1回）。",
        "skill": "扇形に溶けた黄金のブレスを吐き" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "、物理防御" + A +
                 "{q_shred}%" + E + "低下（" + A + "{q_shred_t}秒" + E + "）。",
        "skill2": "翼を広げて咆哮：周囲の敵を" + A + "{e_stun}秒" + E + R + "スタン" + E + "させ" + A + "{e_slow}%" + E +
                  "スロウ（" + A + "{e_slow_t}秒" + E + "）；自身と周囲の味方に" + mag("e_sh", "e_sh_ap") + "のシールド（" + A +
                  "{e_sh_t}秒" + E + "）。",
        "ult": "翼で身を包み" + A + "{r_t}秒" + E + "被ダメージ" + A + "{r_red}%" + E + "軽減；その後" + mag("r_heal", "r_heal_ap") +
               "回復し、周囲の味方に" + mag("r_sh", "r_sh_ap") + "のシールド（" + A + "{r_sh_t}秒" + E + "）、シールド中は攻撃速度" +
               A + "+{r_as}%" + E + "。",
        "names": ("黄金のブレス", "竜の咆哮", "黄金の鱗"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_idas's sfx / tsfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.45),
    ("q", 0.5), ("q_hit", 0.4), ("q_shred", 0.35),
    ("e", 0.55), ("e_wing", 0.45), ("e_shield", 0.35),
    ("r", 0.5), ("r_loop", 0.35), ("r_hit", 0.55), ("r_roar", 0.55), ("r_heal", 0.4), ("r_shield", 0.35),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/idas.rs: the vow, her death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "d")}


def values(p):
    v = {k: p[k] for k in ("p_low", "p_pct", "q_dmg", "q_ratio", "q_shred", "e_slow", "e_sh", "e_sh_ap", "r_red",
                           "r_heal", "r_heal_ap", "r_sh", "r_sh_ap", "r_as")}
    for k in ("p_t", "p_cd", "q_shred_t", "e_stun", "e_slow_t", "e_sh_t", "r_t", "r_sh_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_idas.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # her sound keys rebuilt
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
    mi["contains_code"], mi["mod_type"] = True, "native"     # tft.dll (addons/tft): her rules the data cannot play
    mi["last_updated"] = "2026-10-30"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
