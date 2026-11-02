"""The Mighty Mech's text (5 languages), sound_info files and the tft pack's shared files, numbers from
build_mightymech.P.

    python tools/kit/setup_mightymech.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_thex.py writes for T-Hex: mod.mod_info (VERSION, the
pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys
sorted), text/champion.i18n (tft_mightymech in every language, description + skill_name), sound/sfx/
tft_mightymech_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its event ->
our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center).
Only its keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length
against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 17's own (CommunityDragon cdragon/tft/<locale>.json, TFT17_Galio, 2026-11-03): zh_CN 超级机甲, zh_TW 超能機甲,
en The Mighty Mech, ja マイティーロボ, ko 거대 메크 로봇; its ability Gravity Matrix = 引力矩阵 (zh_TW 重力矩陣, ja グラビティマトリックス,
ko 중력 매트릭스). Voyager Escort (旅人护航, after TFT's Voyager trait), Piston Slash (活塞重斩), Mecha Leap (机甲飞跃) and Ultimate
Form: Super Blade (究极变形·超级战刃, after TFT's Mecha transform) are ours (the user's pick, plan A 辅助).
The texts are the rules it plays: the escort's shields, the shockwave on its armour and magic resistance and the leap's
target in tft.dll (addons/tft/src/mightymech.rs), the rest the data (the third swing, the stance, the taunt and the
heals, the transform and the slash).
Sounds: tools/lol/extract_mightymech.py's clips in tft/sound/sfx/tft_mightymech_sfx_*.wav (git-ignored) - its own
set-15 sword swing, shield, leap and slam, its set-17 Gravity Matrix and transform, the Mighty Mech trait's sword
ceremony, fanfare and ground hit. A clip name never equals an event name (vo-clip-names rule): event tft_mightymech_<x>
plays clip tft_mightymech_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_mightymech import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# ... the Rift Herald 0.40 (PR #663), T-Hex 0.41 (PR #664), the log fixes up to 0.46 (PR #674), Baron Nashor 0.48
# (PR #676, installed first), the Mighty Mech 0.49 (built on the Baron's branch, installed over it)
VERSION = "0.49.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from its soles' point, up negative): the face point on its yellow visor (ppu_restyle's
# face_to: hd/idle.png's visor (44, 33) from the pivot (33, 80) at PPU 2.0); the centre by League's rule (tools/art/
# bp_card_audit.py --centers tft, 2026-11-03: its solid top 38 px up -> -11); the ban/pick card by its rule (y = -39 - top:
# the lo_idle reaches 29.3 px over its centre -> -10)
VIEW = {"face": {"x": 6, "y": -24}, "center": {"x": 0, "y": -11}, "banpick_center": {"x": 0, "y": -10}}


def phys(d, r):
    """d + r% AD, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def ap(d, r):
    """d + r% AP (heals, shields)."""
    return f"{A}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "超级机甲",
        "attack": "每第三下" + O + "活塞重斩" + E + "额外造成" + phys("a3_dmg", "a3_ratio") + O + "物理伤害" + E + "并减速" + A + "{a3_slow}%" + E +
                  "。" + O + "旅人护航" + E + "：每次开战为生命最低的队友提供" + A + "{p_sh}" + E + "+最大生命" + A + "{p_sh_hp}%" + E +
                  "的护盾（" + A + "{p_t}秒" + E + "），自己双倍。",
        "skill": "张开刃翼" + A + "{q_t}秒" + E + "：受到伤害" + A + "-{q_red}%" + E + "，" + R + "嘲讽" + E + "附近敌人两次，每" + A + "{q_every}秒" +
                 E + "回复" + ap("q_hot", "q_hot_ap") + "；结束时冲击波造成" + O + "{q_dmg}" + E + " + 双抗" + O + "{q_arm}%" + E + O + "物理伤害" + E + "。",
        "skill2": "跃向正在冲击我方后排的敌人，落地造成" + phys("e_dmg", "e_ratio") + O + "物理伤害" + E + "，" + R + "击飞{e_up}秒" + E + "。",
        "ult": "究极变形：获得" + ap("r_sh", "r_sh_ap") + "护盾，双抗" + A + "+{r_def}%" + E + "（" + A + "{r_form}秒" + E + "）；剑核爆燃，向前劈出剑气，"
               "造成" + phys("r_dmg", "r_ratio") + O + "物理伤害" + E + "并" + R + "击飞{r_up}秒" + E + "。",
        "names": ("引力矩阵", "机甲飞跃", "究极变形·超级战刃"),
    },
    "zh-hant": {
        "name": "超能機甲",
        "attack": "每第三下" + O + "活塞重斬" + E + "額外造成" + phys("a3_dmg", "a3_ratio") + O + "物理傷害" + E + "並緩速" + A + "{a3_slow}%" + E +
                  "。" + O + "星際旅人護航" + E + "：每次開戰為生命最低的隊友提供" + A + "{p_sh}" + E + "+最大生命" + A + "{p_sh_hp}%" + E +
                  "的護盾（" + A + "{p_t}秒" + E + "），自己雙倍。",
        "skill": "張開刃翼" + A + "{q_t}秒" + E + "：受到傷害" + A + "-{q_red}%" + E + "，" + R + "嘲諷" + E + "附近敵軍兩次，每" + A + "{q_every}秒" +
                 E + "回復" + ap("q_hot", "q_hot_ap") + "；結束時衝擊波造成" + O + "{q_dmg}" + E + " + 雙抗" + O + "{q_arm}%" + E + O + "物理傷害" + E + "。",
        "skill2": "躍向正在衝擊我方後排的敵軍，落地造成" + phys("e_dmg", "e_ratio") + O + "物理傷害" + E + "，" + R + "擊飛{e_up}秒" + E + "。",
        "ult": "究極變形：獲得" + ap("r_sh", "r_sh_ap") + "護盾，雙抗" + A + "+{r_def}%" + E + "（" + A + "{r_form}秒" + E + "）；劍核爆燃，向前劈出劍氣，"
               "造成" + phys("r_dmg", "r_ratio") + O + "物理傷害" + E + "並" + R + "擊飛{r_up}秒" + E + "。",
        "names": ("重力矩陣", "機甲飛躍", "究極變形·超級戰刃"),
    },
    "en": {
        "name": "The Mighty Mech",
        "attack": "Every third swing, " + O + "Piston Slash" + E + " deals " + phys("a3_dmg", "a3_ratio") + " bonus " + O + "physical damage" + E +
                  " and slows by " + A + "{a3_slow}%" + E + ". " + O + "Voyager Escort" + E + ": as each fight starts, shields the lowest-health "
                  "ally for " + A + "{p_sh}" + E + " + " + A + "{p_sh_hp}%" + E + " of its max health (" + A + "{p_t}s" + E + "), itself double.",
        "skill": "Spreads its wings for " + A + "{q_t}s" + E + ": takes " + A + "{q_red}%" + E + " less damage, " + R + "taunts" + E + " nearby enemies "
                 "twice and heals " + ap("q_hot", "q_hot_ap") + " every " + A + "{q_every}s" + E + "; then a shockwave deals " + O + "{q_dmg}" + E +
                 " + " + O + "{q_arm}%" + E + " of its armor and magic resist as " + O + "physical damage" + E + ".",
        "skill2": "Leaps onto the enemy diving its back line, dealing " + phys("e_dmg", "e_ratio") + " " + O + "physical damage" + E +
                  " on landing and " + R + "knocking up for {e_up}s" + E + ".",
        "ult": "Transforms: gains a " + ap("r_sh", "r_sh_ap") + " shield and " + A + "+{r_def}%" + E + " armor and magic resist (" + A +
               "{r_form}s" + E + "); its blade blazes and cleaves forward for " + phys("r_dmg", "r_ratio") + " " + O + "physical damage" + E +
               ", " + R + "knocking up for {r_up}s" + E + ".",
        "names": ("Gravity Matrix", "Mecha Leap", "Ultimate Form: Super Blade"),
    },
    "ko": {
        "name": "거대 메크 로봇",
        "attack": "세 번째 공격마다 " + O + "피스톤 베기" + E + "로 " + phys("a3_dmg", "a3_ratio") + " 추가 " + O + "물리 피해" + E + ", " + A + "{a3_slow}%" +
                  E + " 둔화. " + O + "여행자 호위" + E + ": 전투가 시작될 때마다 체력이 가장 낮은 아군에게 " + A + "{p_sh}" + E + " + 최대 체력의 " + A +
                  "{p_sh_hp}%" + E + " 보호막(" + A + "{p_t}초" + E + "), 자신은 두 배.",
        "skill": A + "{q_t}초" + E + " 동안 날개를 펼쳐 받는 피해 " + A + "-{q_red}%" + E + ", 주변 적을 두 번 " + R + "도발" + E + ", " + A + "{q_every}초" +
                 E + "마다 " + ap("q_hot", "q_hot_ap") + " 회복; 끝날 때 충격파로 " + O + "{q_dmg}" + E + " + 방어력과 마법 저항력의 " + O + "{q_arm}%" + E +
                 " " + O + "물리 피해" + E + ".",
        "skill2": "아군 후열을 덮치는 적에게 도약해 착지 시 " + phys("e_dmg", "e_ratio") + " " + O + "물리 피해" + E + ", " + R + "{e_up}초 띄워 올림" +
                  E + ".",
        "ult": "변신: " + ap("r_sh", "r_sh_ap") + " 보호막과 방어력·마법 저항력 " + A + "+{r_def}%" + E + "(" + A + "{r_form}초" + E + "); 검의 핵이 "
               "타오르며 전방을 베어 " + phys("r_dmg", "r_ratio") + " " + O + "물리 피해" + E + ", " + R + "{r_up}초 띄워 올림" + E + ".",
        "names": ("중력 매트릭스", "메카 도약", "궁극 형태: 슈퍼 블레이드"),
    },
    "ja": {
        "name": "マイティーロボ",
        "attack": "3回目の攻撃ごとに" + O + "ピストンスラッシュ" + E + "で" + phys("a3_dmg", "a3_ratio") + "の追加" + O + "物理ダメージ" + E + "、" + A +
                  "{a3_slow}%" + E + "スロウ。" + O + "ボイジャーエスコート" + E + "：戦闘開始のたびに体力が最も低い味方に" + A + "{p_sh}" + E +
                  "+最大体力の" + A + "{p_sh_hp}%" + E + "のシールド（" + A + "{p_t}秒" + E + "）、自身は2倍。",
        "skill": "翼を広げて" + A + "{q_t}秒" + E + "間、被ダメージ" + A + "-{q_red}%" + E + "、周囲の敵を2回" + R + "挑発" + E + "し、" + A +
                 "{q_every}秒" + E + "ごとに" + ap("q_hot", "q_hot_ap") + "回復。終了時の衝撃波で" + O + "{q_dmg}" + E + "+物理・魔法防御の" + O +
                 "{q_arm}%" + E + "の" + O + "物理ダメージ" + E + "。",
        "skill2": "味方の後衛を狙う敵へ跳びかかり、着地で" + phys("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "、" + R + "{e_up}秒ノックアップ" +
                  E + "。",
        "ult": "変形：" + ap("r_sh", "r_sh_ap") + "のシールドと物理・魔法防御" + A + "+{r_def}%" + E + "（" + A + "{r_form}秒" + E + "）。剣の核が燃え、"
               "前方を斬り裂き" + phys("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、" + R + "{r_up}秒ノックアップ" + E + "。",
        "names": ("グラビティマトリックス", "メカリープ", "アルティメットフォーム：スーパーブレード"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_mightymech's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_hit", 0.35),
    ("q", 0.45), ("q_shield", 0.35), ("q_hit", 0.45),
    ("e", 0.45), ("e_hit", 0.5),
    ("r", 0.55), ("r_sword", 0.45), ("r_swing", 0.45), ("r_hit", 0.5),
    ("p", 0.4), ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/mightymech.rs: the escort, the shockwave, the leap's landing, the fall)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_q_hit", f"{ID}_e_hit", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("a3_dmg", "a3_ratio", "a3_slow", "p_sh", "p_sh_hp", "q_red", "q_hot", "q_hot_ap", "q_dmg", "q_arm",
                           "e_dmg", "e_ratio", "r_sh", "r_sh_ap", "r_def", "r_dmg", "r_ratio")}
    for k in ("p_t", "q_t", "q_every", "e_up", "r_form", "r_up"):
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
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--check", action="store_true")
    a = ap_.parse_args()
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_mightymech.py")
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
    mi["last_updated"] = "2026-11-03"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
