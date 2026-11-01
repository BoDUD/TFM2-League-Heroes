"""The Ancient Krug's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_krug.P.

    python tools/kit/setup_krug.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_alune.py's way), text/champion.i18n (tft_krug in every language, description + skill_name),
sound/sfx/tft_krug_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: from Community Dragon's TFT data (C:/t/kr_work/cd, set 18's DA_Krug18): zh_CN 远古石甲虫 (the client's
zh_cn.json), zh_TW 石怪, en Krug, ja クルーグ, ko 돌거북; Rock and Roll = 岩之摇滚 / 撼地之石 / ロック＆リロール / 로큰롤 (set 18's
ability). Stone Shell, Ancient Landslide and the Shattered Rebirth are ours (the user's pick, plan A 「岩之摇滚」), named in
every language by what they do. The texts are the rules he plays with tft.dll (addons/tft/src/krug.rs): the rebirth.
Sounds: tools/lol/extract_krug.py's clips in tft/sound/sfx/tft_krug_sfx_*.wav (git-ignored) - the Rift's own Krug (its
stone fists, its death crumble, its spawn roar), Rammus (the Powerball roll and hit, the Defensive Ball Curl, the
Frenzying Taunt, the knock-up) and Malphite (the Granite Shield, Unstoppable Force's leap and landing, the Seismic
Shard). A clip name never equals an event name (vo-clip-names rule): event tft_krug_<x> plays clip tft_krug_sfx_<x>.
package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_krug import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.11.0"     # ... Kobuko 0.8, Vander 0.9, Violet 0.10 (its own branch), the Krug 0.11
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point at his small shell face low at his front
# (the design's eye at column 62, row 56 of 86 x 76 at PPU 2.0, 10 over the ground and 9.5 ahead of his standing column
# 43); the centre in his boulder-backed body; the ban/pick card by bp_card_audit.py's rule (y = -39 - top: his lo_idle
# reaches 30.5 over its centre -> -8)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": 7, "y": -15}, "center": {"x": 0, "y": -11}, "banpick_center": {"x": 0, "y": -8}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def phys(d, r, h, hp):
    """d + r% AD + h% of his maximum health, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E} + {O}{{{h}}}%{E}{hp}"


def rock(d, h, hp):
    """d + h% of his maximum health, physical."""
    return f"{O}{{{d}}}{E} + {O}{{{h}}}%{E}{hp}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "远古石甲虫",
        "attack": "岩拳砸地，造成" + AD + O + "物理伤害" + E + "。" + O + "碎岩重生" + E + "：每条命第一次受到致命伤害时碎成石堆" + A +
                  "{p_t}秒" + E + "，再以小石甲虫站起：生命" + A + "{p_hp}%" + E + "、攻速" + A + "+{p_as}%" + E + "，" + R +
                  "嘲讽" + E + "周围敌人" + A + "{p_taunt}秒" + E + "（至少隔" + A + "{p_cd}秒" + E + "）。",
        "skill": "获得" + mag("q_sh", "q_sh_ap") + "的护盾（" + A + "{q_sh_t}秒" + E + "），缩成石球滚向目标，造成" +
                 phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理伤害" + E + "并" + R + "击退" + E + "。",
        "skill2": "缩进巨石" + A + "{e_t}秒" + E + "：护甲" + A + "+{e_def}" + E + "、魔抗" + A + "+{e_mr}" + E + "；周围的敌人被" + R +
                  "嘲讽{e_taunt}秒" + E + "。",
        "ult": "一跃而起（不可选中、免疫控制），砸进敌方英雄身边：周围敌人受到" + phys("r_dmg", "r_ratio", "r_hp", "最大生命") + O +
               "物理伤害" + E + "并被" + R + "击飞{r_up}秒" + E + "；随后落石再造成" + rock("r_rock", "r_rock_hp", "最大生命") + O +
               "物理伤害" + E + "。",
        "names": ("岩之摇滚", "坚岩外壳", "远古崩落"),
    },
    "zh-hant": {
        "name": "石怪",
        "attack": "岩拳砸地，造成" + AD + O + "物理傷害" + E + "。" + O + "碎岩重生" + E + "：每條命第一次受到致命傷害時碎成石堆" + A +
                  "{p_t}秒" + E + "，再以小石怪站起：生命" + A + "{p_hp}%" + E + "、攻速" + A + "+{p_as}%" + E + "，" + R +
                  "嘲諷" + E + "周圍敵人" + A + "{p_taunt}秒" + E + "（至少隔" + A + "{p_cd}秒" + E + "）。",
        "skill": "獲得" + mag("q_sh", "q_sh_ap") + "的護盾（" + A + "{q_sh_t}秒" + E + "），縮成石球滾向目標，造成" +
                 phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理傷害" + E + "並" + R + "擊退" + E + "。",
        "skill2": "縮進巨石" + A + "{e_t}秒" + E + "：護甲" + A + "+{e_def}" + E + "、魔抗" + A + "+{e_mr}" + E + "；周圍的敵人被" + R +
                  "嘲諷{e_taunt}秒" + E + "。",
        "ult": "一躍而起（無法被選取、免疫控制），砸進敵方英雄身邊：周圍敵人受到" + phys("r_dmg", "r_ratio", "r_hp", "最大生命") + O +
               "物理傷害" + E + "並被" + R + "擊飛{r_up}秒" + E + "；隨後落石再造成" + rock("r_rock", "r_rock_hp", "最大生命") + O +
               "物理傷害" + E + "。",
        "names": ("撼地之石", "堅岩外殼", "遠古崩落"),
    },
    "en": {
        "name": "Krug",
        "attack": "A rock-fist slam for " + AD + " " + O + "physical damage" + E + ". " + O + "Shattered Rebirth" + E + ": the first "
                  "lethal blow each life shatters him to rubble for " + A + "{p_t}s" + E + "; he stands up again as a Mini Krug with " +
                  A + "{p_hp}%" + E + " health and " + A + "+{p_as}%" + E + " attack speed, " + R + "taunting" + E + " nearby enemies for " +
                  A + "{p_taunt}s" + E + " (at most every " + A + "{p_cd}s" + E + ").",
        "skill": "Gains a " + mag("q_sh", "q_sh_ap") + " shield (" + A + "{q_sh_t}s" + E + "), curls into a boulder and rolls into "
                 "the target: " + phys("q_dmg", "q_ratio", "q_hp", " max health") + " " + O + "physical damage" + E + " and a " +
                 R + "knock-back" + E + ".",
        "skill2": "Pulls into his boulder for " + A + "{e_t}s" + E + ": " + A + "+{e_def}" + E + " armor, " + A + "+{e_mr}" + E +
                  " magic resist; nearby enemies are " + R + "taunted for {e_taunt}s" + E + ".",
        "ult": "Springs up (untargetable, unstoppable) and crashes down by an enemy champion: nearby enemies take " +
               phys("r_dmg", "r_ratio", "r_hp", " max health") + " " + O + "physical damage" + E + " and are " + R +
               "knocked up for {r_up}s" + E + "; then falling rocks deal " + rock("r_rock", "r_rock_hp", " max health") + " " + O +
               "physical damage" + E + ".",
        "names": ("Rock and Roll", "Stone Shell", "Ancient Landslide"),
    },
    "ko": {
        "name": "돌거북",
        "attack": "바위 주먹 내려치기: " + AD + " 물리 피해. " + O + "부서진 부활" + E + ": 목숨마다 처음 치명적인 피해를 받으면 " + A +
                  "{p_t}초" + E + " 동안 돌무더기가 되었다가 작은 돌거북으로 일어선다: 체력 " + A + "{p_hp}%" + E + ", 공격 속도 " + A +
                  "+{p_as}%" + E + ", 주변 적 " + R + "{p_taunt}초 도발" + E + " (최소 " + A + "{p_cd}초" + E + " 간격).",
        "skill": mag("q_sh", "q_sh_ap") + " 보호막(" + A + "{q_sh_t}초" + E + ")을 얻고 바위로 몸을 말아 대상에게 굴러간다: " +
                 phys("q_dmg", "q_ratio", "q_hp", " 최대 체력") + " 물리 피해, " + R + "밀쳐내기" + E + ".",
        "skill2": A + "{e_t}초" + E + " 동안 바위 속에 웅크린다: 방어력 " + A + "+{e_def}" + E + ", 마법 저항력 " + A + "+{e_mr}" + E +
                  "; 주변 적 " + R + "{e_taunt}초 도발" + E + ".",
        "ult": "뛰어올라(대상 지정 불가, 저지 불가) 적 챔피언 곁으로 떨어진다: 주변 적에게 " + phys("r_dmg", "r_ratio", "r_hp", " 최대 체력") +
               " 물리 피해, " + R + "{r_up}초 에어본" + E + "; 이어서 낙석이 " + rock("r_rock", "r_rock_hp", " 최대 체력") + " 물리 피해.",
        "names": ("로큰롤", "단단한 바위 껍질", "고대의 산사태"),
    },
    "ja": {
        "name": "クルーグ",
        "attack": "岩の拳で叩きつけ" + AD + "の物理ダメージ。" + O + "砕岩の再生" + E + "：ライフごとに初めて致命傷を受けると" + A +
                  "{p_t}秒" + E + "瓦礫になり、小さなクルーグとして立ち上がる：体力" + A + "{p_hp}%" + E + "、攻撃速度" + A + "+{p_as}%" +
                  E + "、周囲の敵を" + R + "{p_taunt}秒挑発" + E + "（最短" + A + "{p_cd}秒" + E + "ごと）。",
        "skill": mag("q_sh", "q_sh_ap") + "のシールド（" + A + "{q_sh_t}秒" + E + "）を得て岩に丸まり対象へ転がる：" +
                 phys("q_dmg", "q_ratio", "q_hp", "最大体力") + "の物理ダメージと" + R + "ノックバック" + E + "。",
        "skill2": A + "{e_t}秒" + E + "岩に身を潜める：物理防御" + A + "+{e_def}" + E + "、魔法防御" + A + "+{e_mr}" + E + "。周囲の敵を" +
                  R + "{e_taunt}秒挑発" + E + "。",
        "ult": "跳び上がり（対象指定不可・CC無効）敵チャンピオンのそばへ落下：周囲の敵に" + phys("r_dmg", "r_ratio", "r_hp", "最大体力") +
               "の物理ダメージと" + R + "{r_up}秒のノックアップ" + E + "。続いて落石が" + rock("r_rock", "r_rock_hp", "最大体力") +
               "の物理ダメージ。",
        "names": ("ロック＆リロール", "堅岩の殻", "太古の地崩れ"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_krug's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.4, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_shield": [(CLIP + "q_shield", 0.4, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.5, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_taunt": [(CLIP + "e_taunt", 0.45, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.45, 0.0)],
    f"{ID}_r_slam": [(CLIP + "r_slam", 0.6, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.5, 0.0)],
    f"{ID}_r_rocks": [(CLIP + "r_rocks", 0.5, 0.0)],
    f"{ID}_p": [(CLIP + "p", 0.55, 0.0)],
    f"{ID}_p_up": [(CLIP + "p_up", 0.55, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/krug.rs: the shatter and the reforming)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_p_up"}


def values(p):
    v = {k: p[k] for k in ("p_hp", "p_as", "q_sh", "q_sh_ap", "q_dmg", "q_ratio", "q_hp", "e_def", "e_mr", "r_dmg",
                           "r_ratio", "r_hp", "r_rock", "r_rock_hp")}
    for k in ("p_t", "p_taunt", "p_cd", "q_sh_t", "e_t", "e_taunt", "r_up"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_krug.py")
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
