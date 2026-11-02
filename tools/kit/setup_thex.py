"""T-Hex's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_thex.P.

    python tools/kit/setup_thex.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_brock.py writes for Brock: mod.mod_info (VERSION,
the pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the
keys sorted), text/champion.i18n (tft_thex in every language, description + skill_name), sound/sfx/tft_thex_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only its keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX and the
texts themselves.
Names: TFT set 16's own (CommunityDragon cdragon/tft/<locale>.json, TFT16_THex, 2026-11-02): zh_CN 海克斯霸龙, zh_TW 機械暴龍,
ja / en T-Hex, ko T-헥스; its ability Hextech Arsenal = 海克斯军械库 (zh_TW 海克斯科技軍火庫, ja ヘクステック アーセナル, ko 마법공학
무기고). Pilot Eject (驾驶员弹射, after TFT's HexMech trait: the pilot ejects as the mech falls), Gatling Barrage (加特林弹幕),
Homing Missiles (追踪导弹) and Rex Charge (霸龙冲撞) are ours (the user's pick, plan A 上单).
The texts are the rules it plays: the death burst and the laser's falloff in tft.dll (addons/tft/src/thex.rs), the rest
the data (the barrage and every fourth attack, the missiles, the charge and bite, the shield and the missile rain).
Sounds: tools/lol/extract_thex.py's clips in tft/sound/sfx/tft_thex_sfx_*.wav (git-ignored) - its own set-16 gatling,
crit, ability cast and shield, the HexMech pilot's jump-in and eject, Corki's missiles and carpet bomb, Renekton's and
Rengar's bite, Viktor's laser. A clip name never equals an event name (vo-clip-names rule): event tft_thex_<x> plays
clip tft_thex_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_thex import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15, Smeech 0.16, Sevika 0.17, Steb 0.18, Nomsy 0.19, Idas 0.20, Daeja 0.21,
# Shi Oh Yu 0.22, Sy'fen 0.23, Sohm 0.24, Terra 0.25, Zippy 0.26, the Blue Sentinel 0.27, the Brambleback 0.28, the Crimson
# Raptor 0.29, the Elder Dragon 0.30, Meepsie 0.31, Murk Wolf 0.32, the Scuttle Crab 0.33, Gromp 0.34, the encyclopedia
# centres 0.35 (PR #657), the log fixes 0.36 (PR #659), the Sentry 0.37, Brock 0.38, the Cinderling 0.39, T-Hex 0.40
VERSION = "0.40.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
AD = ADi + O + "100%" + E
# champion_view (game px from its soles' point, up negative): the face point on its near eye (ppu_restyle's face_to:
# hd/idle.png's eye (72, 12) from the pivot (55, 76) at PPU 1.9); the centre by League's rule (tools/art/
# bp_card_audit.py --centers, 2026-11-02: its solid top 40 px up -> -13); the ban/pick card by its rule (y = -39 - top:
# the lo_idle reaches 29.3 px over its centre -> -10)
VIEW = {"face": {"x": 9, "y": -34}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}}


def phys(d, r):
    """d + r% AD, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "海克斯霸龙",
        "attack": "每次攻击连射" + A + "{a_n}" + E + "发子弹，每发" + ADi + O + "{a_pct}%" + E + O + "物理伤害" + E + "；每第四次攻击最后一发额外" +
                  phys("a4_dmg", "a4_ratio") + "。" + O + "驾驶员弹射" + E + "：阵亡时机甲爆炸，周围敌人受到" + phys("p_dmg", "p_ratio") + O +
                  "物理伤害" + E + "，" + R + "击退并晕眩{p_stun}秒" + E + "。",
        "skill": "背部导弹舱翻开，向附近随机敌人发射" + A + "{q_n}" + E + "枚导弹，每枚造成" + phys("q_dmg", "q_ratio") + O + "物理伤害" + E + "。",
        "skill2": "冲向目标一口咬住，造成" + phys("e_dmg", "e_ratio") + O + "物理伤害" + E + "，" + R + "击退" + E + "并减速" + A + "{e_slow}%" + E +
                  "（" + A + "{e_slow_t}秒" + E + "）。",
        "ult": "获得" + phys("r_sh", "r_sh_ad") + "护盾（" + A + "{r_sh_t}秒" + E + "），导弹舱全开：每秒向目标射出贯穿激光，共" + A + "{r_n}" + E +
               "道，造成" + phys("r_dmg", "r_ratio") + O + "物理伤害" + E + "，每穿过一个敌人" + A + "-{r_fall}%" + E + "（最低" + A + "{r_min}%" + E +
               "）；每道激光伴随" + A + "{r_m}" + E + "枚导弹，每枚" + phys("r_mdmg", "r_mratio") + "。",
        "names": ("追踪导弹", "霸龙冲撞", "海克斯军械库"),
    },
    "zh-hant": {
        "name": "機械暴龍",
        "attack": "每次攻擊連射" + A + "{a_n}" + E + "發子彈，每發" + ADi + O + "{a_pct}%" + E + O + "物理傷害" + E + "；每第四次攻擊最後一發額外" +
                  phys("a4_dmg", "a4_ratio") + "。" + O + "駕駛員彈射" + E + "：陣亡時機甲爆炸，周圍敵軍受到" + phys("p_dmg", "p_ratio") + O +
                  "物理傷害" + E + "，" + R + "擊退並暈眩{p_stun}秒" + E + "。",
        "skill": "背部導彈艙翻開，向附近隨機敵軍發射" + A + "{q_n}" + E + "枚導彈，每枚造成" + phys("q_dmg", "q_ratio") + O + "物理傷害" + E + "。",
        "skill2": "衝向目標一口咬住，造成" + phys("e_dmg", "e_ratio") + O + "物理傷害" + E + "，" + R + "擊退" + E + "並緩速" + A + "{e_slow}%" + E +
                  "（" + A + "{e_slow_t}秒" + E + "）。",
        "ult": "獲得" + phys("r_sh", "r_sh_ad") + "護盾（" + A + "{r_sh_t}秒" + E + "），導彈艙全開：每秒向目標射出貫穿雷射，共" + A + "{r_n}" + E +
               "道，造成" + phys("r_dmg", "r_ratio") + O + "物理傷害" + E + "，每穿過一名敵軍" + A + "-{r_fall}%" + E + "（最低" + A + "{r_min}%" + E +
               "）；每道雷射伴隨" + A + "{r_m}" + E + "枚導彈，每枚" + phys("r_mdmg", "r_mratio") + "。",
        "names": ("追蹤導彈", "暴龍衝撞", "海克斯科技軍火庫"),
    },
    "en": {
        "name": "T-Hex",
        "attack": "Fires " + A + "{a_n}" + E + " bullets per attack, each " + ADi + O + "{a_pct}%" + E + " " + O + "physical damage" + E +
                  "; every fourth attack's last bullet adds " + phys("a4_dmg", "a4_ratio") + ". " + O + "Pilot Eject" + E + ": on death "
                  "the mech bursts, dealing " + phys("p_dmg", "p_ratio") + " " + O + "physical damage" + E + " nearby, " + R +
                  "knocking back and stunning for {p_stun}s" + E + ".",
        "skill": "Opens its back pods and fires " + A + "{q_n}" + E + " missiles at random nearby enemies, each dealing " +
                 phys("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ".",
        "skill2": "Charges the target and bites for " + phys("e_dmg", "e_ratio") + " " + O + "physical damage" + E + ", " + R +
                  "knocking it back" + E + " and slowing it by " + A + "{e_slow}%" + E + " for " + A + "{e_slow_t}s" + E + ".",
        "ult": "Gains a " + phys("r_sh", "r_sh_ad") + " shield for " + A + "{r_sh_t}s" + E + " and opens fire: " + A + "{r_n}" + E +
               " piercing lasers at the target, one a second, for " + phys("r_dmg", "r_ratio") + " " + O + "physical damage" + E + ", " +
               A + "{r_fall}%" + E + " less per enemy passed (" + A + "{r_min}%" + E + " minimum); each with " + A + "{r_m}" + E +
               " missiles of " + phys("r_mdmg", "r_mratio") + ".",
        "names": ("Homing Missiles", "Rex Charge", "Hextech Arsenal"),
    },
    "ko": {
        "name": "T-헥스",
        "attack": "공격마다 탄환 " + A + "{a_n}" + E + "발을 연사해 각각 " + ADi + O + "{a_pct}%" + E + " " + O + "물리 피해" + E + "; 네 번째 공격의 "
                  "마지막 탄환은 " + phys("a4_dmg", "a4_ratio") + " 추가. " + O + "조종사 탈출" + E + ": 사망 시 기체가 폭발해 주변 적에게 " +
                  phys("p_dmg", "p_ratio") + " " + O + "물리 피해" + E + ", " + R + "밀쳐내고 {p_stun}초 기절" + E + ".",
        "skill": "등의 미사일 포드를 열어 주변 무작위 적에게 미사일 " + A + "{q_n}" + E + "발, 각각 " + phys("q_dmg", "q_ratio") + " " + O +
                 "물리 피해" + E + ".",
        "skill2": "대상에게 돌진해 물어뜯어 " + phys("e_dmg", "e_ratio") + " " + O + "물리 피해" + E + ", " + R + "밀쳐내기" + E + ", " + A +
                  "{e_slow_t}초" + E + " 동안 " + A + "{e_slow}%" + E + " 둔화.",
        "ult": phys("r_sh", "r_sh_ad") + " 보호막(" + A + "{r_sh_t}초" + E + ")을 얻고 대상에게 매초 관통 레이저 " + A + "{r_n}" + E + "발: " +
               phys("r_dmg", "r_ratio") + " " + O + "물리 피해" + E + ", 적을 지날 때마다 " + A + "-{r_fall}%" + E + "(최소 " + A + "{r_min}%" + E +
               "); 레이저마다 미사일 " + A + "{r_m}" + E + "발, 각각 " + phys("r_mdmg", "r_mratio") + ".",
        "names": ("유도 미사일", "렉스 돌진", "마법공학 무기고"),
    },
    "ja": {
        "name": "T-Hex",
        "attack": "攻撃ごとに弾を" + A + "{a_n}" + E + "発連射し、各" + ADi + O + "{a_pct}%" + E + "の" + O + "物理ダメージ" + E + "。4回目の攻撃の"
                  "最後の弾は" + phys("a4_dmg", "a4_ratio") + "追加。" + O + "パイロット脱出" + E + "：倒れると機体が爆発し、周囲の敵に" +
                  phys("p_dmg", "p_ratio") + "の" + O + "物理ダメージ" + E + "、" + R + "ノックバックと{p_stun}秒スタン" + E + "。",
        "skill": "背中のミサイルポッドを開き、近くのランダムな敵にミサイルを" + A + "{q_n}" + E + "発、各" + phys("q_dmg", "q_ratio") + "の" + O +
                 "物理ダメージ" + E + "。",
        "skill2": "対象に突進して噛みつき" + phys("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "、" + R + "ノックバック" + E + "し" + A +
                  "{e_slow}%" + E + "スロウ（" + A + "{e_slow_t}秒" + E + "）。",
        "ult": phys("r_sh", "r_sh_ad") + "のシールド（" + A + "{r_sh_t}秒" + E + "）を得て、対象へ毎秒貫通レーザーを" + A + "{r_n}" + E + "本：" +
               phys("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、敵を貫くごとに" + A + "-{r_fall}%" + E + "（最低" + A + "{r_min}%" + E +
               "）。レーザーごとにミサイル" + A + "{r_m}" + E + "発、各" + phys("r_mdmg", "r_mratio") + "。",
        "names": ("ホーミングミサイル", "レックスチャージ", "ヘクステック アーセナル"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_thex's sfx) and tft.dll's
SOUNDS = {f"{ID}_{x}": [(CLIP + x, v, 0.0)] for x, v in (
    ("a", 0.35), ("a_crit", 0.45),
    ("q", 0.45), ("q_hit", 0.35),
    ("e", 0.45), ("e_hit", 0.45),
    ("r", 0.55), ("r_shield", 0.45), ("r_laser", 0.45), ("r_hit", 0.3),
    ("p_in", 0.45), ("p_eject", 0.55), ("d", 0.55))}
# the sounds tft.dll plays itself (addons/tft/src/thex.rs: the pilot jumping in each life, its eject and the burst)
DLL_SOUNDS = {f"{ID}_p_in", f"{ID}_p_eject", f"{ID}_d"}


def values(p):
    v = {k: p[k] for k in ("a_n", "a_pct", "a4_dmg", "a4_ratio", "p_dmg", "p_ratio", "q_n", "q_dmg", "q_ratio", "e_dmg",
                           "e_ratio", "e_slow", "r_sh", "r_sh_ad", "r_n", "r_dmg", "r_ratio", "r_fall", "r_min", "r_m",
                           "r_mdmg", "r_mratio")}
    for k in ("p_stun", "e_slow_t", "r_sh_t"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_thex.py")
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
