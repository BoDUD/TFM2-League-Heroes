"""Sohm's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_sohm.P.

    python tools/kit/setup_sohm.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_daeja.py writes for Daeja: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_sohm in every language, description + skill_name), sound/sfx/tft_sohm_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 7's own (CommunityDragon cdragon/tft/<locale>.json, TFT7_AquaticDragon, 2026-10-30): zh_CN 索姆, zh_TW 頌沐,
ja ソーム, ko 솜, en Sohm; her ability Tideblossom = 潮涌, the Lagoon trait 碧波龙 (the passive 碧波之力). Water Bolt
(水泡弹), Tidecaller's Guard (海潮护佑) and Tidal Bloom (潮汐绽放) are our own (the user's pick, plan A 「潮汐之花」).
The texts are the rules she plays with tft.dll (addons/tft/src/sohm.rs): the tide stacks, the wave and its water flowers
that jump on when the flowered one falls, the shield on the weakest ally, the bloom on every flower.
Sounds: tools/lol/extract_sohm.py's clips in tft/sound/sfx/tft_sohm_sfx_*.wav (git-ignored) - her own set-7 TFT sounds
(the attack, the wave and its mark, the flower's jump, the crit for the bloom's cast and hits), Nami (the tide, the
guard, the bubble, the bloom's call and burst) and the Rift's drakes (the death). A clip name never equals an event name
(vo-clip-names rule): event tft_sohm_<x> plays clip tft_sohm_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sohm import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24
VERSION = "0.24.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from her feet's point, up negative): the face point on her eye (the design's eye at column 45.5,
# row 30.5 of 72 at PPU 1.8: 23 over the ground, 9 ahead of her middle column 29 - ppu_restyle's face_to); the centre in
# her coil; the ban/pick card by bp_card_audit.py's rule (-39 less the idle's top -29 with its float: the antler tips 1
# game px under the card's top)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 9, "y": -23}, "center": {"x": 0, "y": -11}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "索姆",
        "attack": "吐出水泡弹，造成" + AD + O + "物理伤害" + E + "。" + O + "碧波之力" + E + "：每次施放技能叠一层潮水（" + A + "{p_t}秒" +
                  E + "，最多" + A + "{p_max}" + E + "层），每层法强" + A + "+{p_ap}%" + E + "、攻速" + A + "+{p_as}%" + E + "。",
        "skill": "朝没开花的敌人冲出一道潮涌，沿途敌人受到" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "，目标头上开出水之花（" + A +
                 "{m_t}秒" + E + "）；带花的敌人倒下，花跳到附近的敌人。",
        "skill2": "给附近生命比例最低的队友套上" + mag("e_sh", "e_sh_ap") + "的水盾（" + A + "{e_sh_t}秒" + E + "），攻速" + A +
                  "+{e_as}%" + E + "。",
        "ult": "所有水之花一齐绽放，每朵花周围的敌人受到" + mag("r_dmg", "r_ratio") + M + "魔法伤害" + E + "，花随之散去；没有花时在目标身上绽放。",
        "names": ("潮涌", "海潮护佑", "潮汐绽放"),
    },
    "zh-hant": {
        "name": "頌沐",
        "attack": "吐出水泡彈，造成" + AD + O + "物理傷害" + E + "。" + O + "碧波之力" + E + "：每次施放技能疊一層潮水（" + A + "{p_t}秒" +
                  E + "，最多" + A + "{p_max}" + E + "層），每層法強" + A + "+{p_ap}%" + E + "、攻速" + A + "+{p_as}%" + E + "。",
        "skill": "朝沒開花的敵人衝出一道潮湧，沿途敵人受到" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "，目標頭上開出水之花（" + A +
                 "{m_t}秒" + E + "）；帶花的敵人倒下，花跳到附近的敵人。",
        "skill2": "給附近生命比例最低的隊友套上" + mag("e_sh", "e_sh_ap") + "的水盾（" + A + "{e_sh_t}秒" + E + "），攻速" + A +
                  "+{e_as}%" + E + "。",
        "ult": "所有水之花一齊綻放，每朵花周圍的敵人受到" + mag("r_dmg", "r_ratio") + M + "魔法傷害" + E + "，花隨之散去；沒有花時在目標身上綻放。",
        "names": ("潮湧", "海潮護佑", "潮汐綻放"),
    },
    "en": {
        "name": "Sohm",
        "attack": "Spits a water bolt for " + AD + " " + O + "physical damage" + E + ". " + O + "Lagoon Power" + E +
                  ": every cast adds a tide stack (" + A + "{p_t}s" + E + ", up to " + A + "{p_max}" + E + "): " + A + "+{p_ap}%" + E +
                  " ability power and " + A + "+{p_as}%" + E + " attack speed each.",
        "skill": "Sends a wave at an enemy without a flower: " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E +
                 " to every enemy on its way, and a water flower blooms over the target (" + A + "{m_t}s" + E + "). When a "
                 "flowered enemy falls, the flower jumps to a nearby enemy.",
        "skill2": "Wraps the nearby ally lowest on health in a " + mag("e_sh", "e_sh_ap") + " water shield (" + A + "{e_sh_t}s" + E +
                  ") and " + A + "+{e_as}%" + E + " attack speed.",
        "ult": "Every water flower bursts at once: " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " to enemies around "
               "each, and the flowers fade. With no flower out, one bursts on the target.",
        "names": ("Tideblossom", "Tidecaller's Guard", "Tidal Bloom"),
    },
    "ko": {
        "name": "솜",
        "attack": "물방울 탄을 뱉어 " + AD + " " + O + "물리 피해" + E + ". " + O + "석호의 힘" + E + ": 스킬을 쓸 때마다 조수 1중첩(" + A +
                  "{p_t}초" + E + ", 최대 " + A + "{p_max}" + E + "), 중첩당 주문력 " + A + "+{p_ap}%" + E + ", 공격 속도 " + A +
                  "+{p_as}%" + E + ".",
        "skill": "꽃이 없는 적에게 물결을 보내 경로의 적에게 " + mag("q_dmg", "q_ratio") + " " + M + "마법 피해" + E + ", 대상 머리 위에 물의 꽃(" +
                 A + "{m_t}초" + E + "). 꽃이 핀 적이 쓰러지면 꽃이 근처 적에게 옮겨 갑니다.",
        "skill2": "근처에서 체력 비율이 가장 낮은 아군에게 " + mag("e_sh", "e_sh_ap") + " 물보호막(" + A + "{e_sh_t}초" + E + ")과 공격 속도 " +
                  A + "+{e_as}%" + E + ".",
        "ult": "모든 물의 꽃이 한꺼번에 터져 각 꽃 주변 적에게 " + mag("r_dmg", "r_ratio") + " " + M + "마법 피해" + E + ", 꽃은 사라집니다. 꽃이 "
               "없으면 대상에게서 터집니다.",
        "names": ("조수의 꽃", "조수의 가호", "조수 개화"),
    },
    "ja": {
        "name": "ソーム",
        "attack": "水の弾を吐き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ラグーンの力" + E + "：スキルを使うたびに潮を1スタック（" + A +
                  "{p_t}秒" + E + "、最大" + A + "{p_max}" + E + "）、1スタックごとに魔力" + A + "+{p_ap}%" + E + "、攻撃速度" + A +
                  "+{p_as}%" + E + "。",
        "skill": "花のない敵へ潮の波を放ち、通り道の敵に" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "、対象の頭上に水の花（" +
                 A + "{m_t}秒" + E + "）。花のついた敵が倒れると花は近くの敵へ移る。",
        "skill2": "近くで体力の割合が最も低い味方に" + mag("e_sh", "e_sh_ap") + "の水のシールド（" + A + "{e_sh_t}秒" + E + "）と攻撃速度" +
                  A + "+{e_as}%" + E + "。",
        "ult": "すべての水の花が一斉に咲き、各花の周囲の敵に" + mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E + "、花は消える。花が"
               "なければ対象の上で咲く。",
        "names": ("潮の花", "潮の加護", "潮汐の開花"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_sohm's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.35), ("p", 0.3),
    ("q", 0.5), ("q_hit", 0.4), ("q_mark", 0.45), ("q_jump", 0.45), ("q_jump_hit", 0.45),
    ("e", 0.5), ("e_shield", 0.45),
    ("r", 0.5), ("r_cast", 0.5), ("r_bloom", 0.55), ("r_hit", 0.45),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/sohm.rs: the tide, the wave's hits, the mark, the flower's jump, the
# bubble, the bloom, its hits, her death cry)
DLL_SOUNDS = {f"{ID}_{x}" for x in ("p", "q_hit", "q_mark", "q_jump", "q_jump_hit", "e_shield", "r_bloom", "r_hit", "d")}


def values(p):
    v = {k: p[k] for k in ("p_max", "p_ap", "p_as", "q_dmg", "q_ratio", "e_sh", "e_sh_ap", "e_as", "r_dmg", "r_ratio")}
    for k in ("p_t", "m_t", "e_sh_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_sohm.py")
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
