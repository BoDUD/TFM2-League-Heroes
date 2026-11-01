"""The Blue Sentinel's text (5 languages), sound_info files and the tft pack's shared files, numbers from
build_sentinel.P.

    python tools/kit/setup_sentinel.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_terra.py writes for Terra: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_sentinel in every language, description + skill_name),
sound/sfx/tft_sentinel_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon cdragon/tft/<locale>.json, DA_Sentinel18, 2026-10-31): zh_CN 苍蓝雕纹魔像,
zh_TW 守望者, ja センチネル, ko 파수꾼, en Sentinel; its ability Azure Shockwave = 蔚蓝冲击波 (zh_TW 蒼藍衝擊波, ja 蒼き衝撃波,
ko 하늘빛 충격파), Blue Buff = 蓝霸符 from the same text. Rock Fist (岩拳猛击), Twin Slam (双拳重砸) and Carved Skin (雕纹石肤)
are our own (the user's pick, plan A 「蔚蓝冲击波」).
The texts are the rules it plays with tft.dll (addons/tft/src/sentinel.rs): the fissure toward the most enemy
champions, the Mana Reave as the next ready skill sealed.
Sounds: tools/lol/extract_sentinel.py's clips in tft/sound/sfx/tft_sentinel_sfx_*.wav (git-ignored) - the Rift's own
Blue Sentinel (its fist, its roar, the spawn slam, the death), Malphite, Rammus, Ornn, Sona and Ryze for the rest. A
clip name never equals an event name (vo-clip-names rule): event tft_sentinel_<x> plays clip tft_sentinel_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sentinel import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26 (its own branch), the Blue Sentinel 0.27
VERSION = "0.27.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its feet's point, up negative): the face point on its one eye (the design's eye at column
# 62.5, row 22.5 of 68 at PPU 1.7: 27 over the ground, 7 ahead of its standing point, the design's middle column 50 -
# ppu_restyle's face_to); the centre in its body (the middle column, half its 40 px); the ban/pick card by
# bp_card_audit.py's rule (-39 less the highest idle frame's top over its centre, -28.7: its shoulder boulders 1 game px
# under the card's top)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 7, "y": -27}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}}


def magic(d, r, h):
    """base + AP ratio + its maximum health ratio, magic."""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E} + {HPi}{M}{{{h}}}%{E}"


def shield(d, r):
    return f"{O}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "苍蓝雕纹魔像",
        "attack": "巨拳砸下，造成" + AD + O + "物理伤害" + E + "。" + O + "蓝霸符" + E + "：每放一个技能，身边友军的技能剩余冷却立刻降到最多" + A +
                  "{p_keep}%" + E + "。",
        "skill": "双拳砸地，对周围敌人造成" + magic("q_dmg", "q_ap", "q_hp") + M + "魔法伤害" + E + "并减速" + R + "{q_slow}%" + E + "（" + A +
                 "{q_slow_t}秒" + E + "）。",
        "skill2": "符文亮起，获得" + shield("e_sh", "e_ap") + "护盾（" + A + "{e_sh_t}秒" + E + "），" + R + "嘲讽" + E + "周围敌人" + A +
                  "{e_taunt}秒" + E + "。",
        "ult": "获得" + shield("r_sh", "r_ap") + "护盾，猛砸地面，朝敌方英雄最多的方向裂开裂隙：" + R + "击飞" + E + "、" +
               magic("r_dmg", "r_ratio", "r_hp") + M + "魔法伤害" + E + "，" + R + "破法" + E + "（下一个技能晚" + A + "{r_reave}秒" + E + "）。",
        "names": ("双拳重砸", "雕纹石肤", "蔚蓝冲击波"),
    },
    "zh-hant": {
        "name": "守望者",
        "attack": "巨拳砸下，造成" + AD + O + "物理傷害" + E + "。" + O + "藍霸符" + E + "：每放一個技能，身邊友軍的技能剩餘冷卻立刻降到最多" + A +
                  "{p_keep}%" + E + "。",
        "skill": "雙拳砸地，對周圍敵人造成" + magic("q_dmg", "q_ap", "q_hp") + M + "魔法傷害" + E + "並緩速" + R + "{q_slow}%" + E + "（" + A +
                 "{q_slow_t}秒" + E + "）。",
        "skill2": "符文亮起，獲得" + shield("e_sh", "e_ap") + "護盾（" + A + "{e_sh_t}秒" + E + "），" + R + "嘲諷" + E + "周圍敵人" + A +
                  "{e_taunt}秒" + E + "。",
        "ult": "獲得" + shield("r_sh", "r_ap") + "護盾，猛砸地面，朝敵方英雄最多的方向裂開裂隙：" + R + "擊飛" + E + "、" +
               magic("r_dmg", "r_ratio", "r_hp") + M + "魔法傷害" + E + "，" + R + "破法" + E + "（下一個技能晚" + A + "{r_reave}秒" + E + "）。",
        "names": ("雙拳重砸", "雕紋石膚", "蒼藍衝擊波"),
    },
    "en": {
        "name": "Sentinel",
        "attack": "A stone fist slam for " + AD + " " + O + "physical damage" + E + ". " + O + "Blue Buff" + E +
                  ": each of its spells drops nearby allies' spell cooldowns at once to at most " + A + "{p_keep}%" + E + ".",
        "skill": "Slams both fists down, dealing " + magic("q_dmg", "q_ap", "q_hp") + " " + M + "magic damage" + E +
                 " to nearby enemies and slowing them " + R + "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Its runes flare: gains a " + shield("e_sh", "e_ap") + " shield for " + A + "{e_sh_t}s" + E + " and " + R + "taunts" +
                  E + " nearby enemies for " + A + "{e_taunt}s" + E + ".",
        "ult": "Gains a " + shield("r_sh", "r_ap") + " shield and slams a fissure toward the most enemy champions: " + R +
               "knock-up" + E + ", " + magic("r_dmg", "r_ratio", "r_hp") + " " + M + "magic damage" + E + " and " + R + "Mana Reave" + E +
               " (their next spell " + A + "{r_reave}s" + E + " late).",
        "names": ("Twin Slam", "Carved Skin", "Azure Shockwave"),
    },
    "ko": {
        "name": "파수꾼",
        "attack": "돌 주먹으로 내리쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "파란 버프" + E + ": 스킬을 쓸 때마다 주변 아군의 스킬 재사용 대기시간이 즉시 줄어듭니다(최대 " +
                  A + "{p_keep}%" + E + "까지).",
        "skill": "두 주먹으로 땅을 내리쳐 주변 적에게 " + magic("q_dmg", "q_ap", "q_hp") + " " + M + "마법 피해" + E + ", " + A + "{q_slow_t}초" +
                 E + " 동안 " + R + "{q_slow}%" + E + " 둔화.",
        "skill2": "문양이 빛나며 " + shield("e_sh", "e_ap") + "의 보호막(" + A + "{e_sh_t}초" + E + ")을 얻고 주변 적을 " + A + "{e_taunt}초" +
                  E + " 동안 " + R + "도발" + E + ".",
        "ult": shield("r_sh", "r_ap") + "의 보호막을 얻고 적 챔피언이 가장 많은 쪽으로 균열을 일으킵니다: " + R + "띄우기" + E + ", " +
               magic("r_dmg", "r_ratio", "r_hp") + " " + M + "마법 피해" + E + ", " + R + "마나 약탈" + E + "(다음 스킬 " + A + "{r_reave}초" + E +
               " 지연).",
        "names": ("쌍주먹 강타", "문양 석피", "하늘빛 충격파"),
    },
    "ja": {
        "name": "センチネル",
        "attack": "石の拳を振り下ろし" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ブルーバフ" + E + "：スキルを使うたび周囲の味方のスキルクールダウンを即座に短縮（最大" +
                  A + "{p_keep}%" + E + "まで）。",
        "skill": "両拳で地面を叩き、周囲の敵に" + magic("q_dmg", "q_ap", "q_hp") + "の" + M + "魔法ダメージ" + E + "、" + A + "{q_slow_t}秒" +
                 E + "間" + R + "{q_slow}%" + E + "スロウ。",
        "skill2": "紋様が輝き" + shield("e_sh", "e_ap") + "のシールド（" + A + "{e_sh_t}秒" + E + "）を得て、周囲の敵を" + A + "{e_taunt}秒" +
                  E + "間" + R + "挑発" + E + "。",
        "ult": shield("r_sh", "r_ap") + "のシールドを得て、敵チャンピオンが最も多い方向へ亀裂を走らせる：" + R + "ノックアップ" + E + "、" +
               magic("r_dmg", "r_ratio", "r_hp") + "の" + M + "魔法ダメージ" + E + "、" + R + "マナ枯渇" + E + "（次のスキルが" + A +
               "{r_reave}秒" + E + "遅れる）。",
        "names": ("双拳叩きつけ", "刻印の石肌", "蒼き衝撃波"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_sentinel's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.4), ("a_hit", 0.4),
    ("p", 0.3),
    ("q", 0.5), ("q_hit", 0.45),
    ("e", 0.45), ("e_taunt", 0.4),
    ("r", 0.55), ("r_vo", 0.5), ("r_shield", 0.4), ("r_crack", 0.5), ("r_hit", 0.35), ("r_reave", 0.35),
    ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/sentinel.rs: the fissure's hit, the reave, its crumbling)
DLL_SOUNDS = {f"{ID}_r_hit", f"{ID}_r_reave", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ap", "q_hp", "q_slow", "e_sh", "e_ap", "r_sh", "r_ap", "r_dmg", "r_ratio", "r_hp")}
    v["p_keep"] = round(100 * 100 / (100 + p["p_cdm"]))
    for k in ("q_slow_t", "e_taunt", "e_sh_t", "r_reave"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_sentinel.py")
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
    mi["last_updated"] = "2026-10-31"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
