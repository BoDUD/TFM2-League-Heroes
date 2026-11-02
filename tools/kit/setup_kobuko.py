"""Kobuko's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_kobuko.P.

    python tools/kit/setup_kobuko.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_alune.py's way), text/champion.i18n (tft_kobuko in every language, description + skill_name),
sound/sfx/tft_kobuko_*.sound_info, mod.override_info (the text and champion_view merges and two entries a sound: its
event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre,
banpick_center). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's
shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: zh_CN from the client's TFT data (C:/t/al_work/tft_zh.json): 可酷伯, Golden Claw Mantra = 金爪真言 (set 15's
ability), Game Over! = 游戏结束！ (set 14's), the Second Phase = 第二阶段 (set 14's passive); the other languages are ours
(the Riot client here has en_US and zh_MY string tables only, and the names are what our kit does), as is Tiger Pounce
(猛虎扑, the user's pick, plan A 「金爪宗师」). The texts are the rules he plays with tft.dll (addons/tft/src/kobuko.rs): the
rage at half health.
Sounds: tools/lol/extract_kobuko.py's clips in tft/sound/sfx/tft_kobuko_sfx_*.wav (git-ignored) - his own set-15 TFT
sounds (the palm, its hit, the golden shield, the crit palm, the stun, the mentor's knock-up and slam) and set 14's (the
second phase, the leap's wind-up, the big hit, his voice). A clip name never equals an event name (vo-clip-names
rule): event tft_kobuko_<x> plays clip tft_kobuko_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kobuko import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.8.0"      # Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from his soles' point, up negative): the face point at his eye (the design's eye at row 13 of
# 80, column 39 at PPU 2.0: 33 over the ground, 1 behind his standing column 41); the centre in his body; the ban/pick
# card by bp_card_audit.py's rule (y = -39 - top: his lo_idle reaches 32.7 over its centre -> -6)
# center: the encyclopedia card puts this point at a fixed spot - set by League's rule (tools/art/bp_card_audit.py --centers, 2026-11-01)
VIEW = {"face": {"x": -1, "y": -33}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -6}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def phys(d, r, h, hp):
    """d + r% AD + h% of his maximum health, physical."""
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E} + {O}{{{h}}}%{E}{hp}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "可酷伯",
        "attack": "猫爪掌，造成" + AD + O + "物理伤害" + E + "。" + O + "第二阶段" + E + "：每条命第一次生命低于" + A + "{p_hi}%" + E +
                  "时进入狂怒，直到阵亡：攻击速度" + A + "+{p_as}%" + E + "、生命偷取" + A + "{p_vamp}%" + E + "。",
        "skill": "获得" + mag("q_sh", "q_sh_ap") + "的护盾（" + A + "{q_sh_t}秒" + E + "）；" + A + "{q_t}秒" + E + "内下一次普攻变为金爪重掌，"
                 "造成" + phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理伤害" + E + "并" + R + "晕眩{q_stun}秒" + E + "。",
        "skill2": "扑向目标，落地时周围的敌人受到" + phys("e_dmg", "e_ratio", "e_hp", "最大生命") + O + "物理伤害" + E + "并被" + R +
                  "击飞{e_up}秒" + E + "。",
        "ult": "一跃冲天（期间不可选中、免疫控制），砸落在敌方英雄身上：目标受到" + phys("r_main", "r_main_ratio", "r_main_hp", "最大生命") +
               O + "物理伤害" + E + "，周围的敌人（含目标）再受到" + phys("r_dmg", "r_ratio", "r_hp", "最大生命") + O + "物理伤害" + E + "并被" +
               R + "击飞{r_up}秒" + E + "。",
        "names": ("金爪真言", "猛虎扑", "游戏结束！"),
    },
    "zh-hant": {
        "name": "可酷伯",
        "attack": "貓爪掌，造成" + AD + O + "物理傷害" + E + "。" + O + "第二階段" + E + "：每條命第一次生命低於" + A + "{p_hi}%" + E +
                  "時進入狂怒，直到陣亡：攻擊速度" + A + "+{p_as}%" + E + "、生命偷取" + A + "{p_vamp}%" + E + "。",
        "skill": "獲得" + mag("q_sh", "q_sh_ap") + "的護盾（" + A + "{q_sh_t}秒" + E + "）；" + A + "{q_t}秒" + E + "內下一次普攻變為金爪重掌，"
                 "造成" + phys("q_dmg", "q_ratio", "q_hp", "最大生命") + O + "物理傷害" + E + "並" + R + "暈眩{q_stun}秒" + E + "。",
        "skill2": "撲向目標，落地時周圍的敵人受到" + phys("e_dmg", "e_ratio", "e_hp", "最大生命") + O + "物理傷害" + E + "並被" + R +
                  "擊飛{e_up}秒" + E + "。",
        "ult": "一躍沖天（期間無法被選取、免疫控制），砸落在敵方英雄身上：目標受到" + phys("r_main", "r_main_ratio", "r_main_hp", "最大生命") +
               O + "物理傷害" + E + "，周圍的敵人（含目標）再受到" + phys("r_dmg", "r_ratio", "r_hp", "最大生命") + O + "物理傷害" + E + "並被" +
               R + "擊飛{r_up}秒" + E + "。",
        "names": ("金爪真言", "猛虎撲", "遊戲結束！"),
    },
    "en": {
        "name": "Kobuko",
        "attack": "A paw strike for " + AD + " " + O + "physical damage" + E + ". " + O + "Second Phase" + E + ": the first time "
                  "each life his health falls under " + A + "{p_hi}%" + E + " he is enraged until he dies: " + A + "+{p_as}%" + E +
                  " attack speed and " + A + "{p_vamp}%" + E + " life steal.",
        "skill": "Gains a " + mag("q_sh", "q_sh_ap") + " shield (" + A + "{q_sh_t}s" + E + "); within " + A + "{q_t}s" + E +
                 " his next attack is a Golden Claw: " + phys("q_dmg", "q_ratio", "q_hp", " max health") + " " + O +
                 "physical damage" + E + " and a " + R + "{q_stun}s stun" + E + ".",
        "skill2": "Pounces on the target: on landing, nearby enemies take " + phys("e_dmg", "e_ratio", "e_hp", " max health") +
                  " " + O + "physical damage" + E + " and are " + R + "knocked up for {e_up}s" + E + ".",
        "ult": "Springs out of sight (untargetable, unstoppable) and crashes down on an enemy champion: it takes " +
               phys("r_main", "r_main_ratio", "r_main_hp", " max health") + " " + O + "physical damage" + E + ", and nearby "
               "enemies (it too) " + phys("r_dmg", "r_ratio", "r_hp", " max health") + " and are " + R + "knocked up for {r_up}s" + E + ".",
        "names": ("Golden Claw Mantra", "Tiger Pounce", "Game Over!"),
    },
    "ko": {
        "name": "코부코",
        "attack": "고양이 발바닥 치기: " + AD + " 물리 피해. " + O + "2페이즈" + E + ": 목숨마다 처음으로 체력이 " + A + "{p_hi}%" + E +
                  " 아래로 떨어지면 죽을 때까지 격노: 공격 속도 " + A + "+{p_as}%" + E + ", 생명력 흡수 " + A + "{p_vamp}%" + E + ".",
        "skill": mag("q_sh", "q_sh_ap") + " 보호막(" + A + "{q_sh_t}초" + E + "). " + A + "{q_t}초" + E + " 안에 다음 기본 공격이 황금 발톱: " +
                 phys("q_dmg", "q_ratio", "q_hp", " 최대 체력") + " 물리 피해, " + R + "{q_stun}초 기절" + E + ".",
        "skill2": "대상에게 덮쳐 착지할 때 주변 적에게 " + phys("e_dmg", "e_ratio", "e_hp", " 최대 체력") + " 물리 피해, " + R +
                  "{e_up}초 에어본" + E + ".",
        "ult": "하늘 높이 뛰어올라(대상 지정 불가, 저지 불가) 적 챔피언 위로 떨어진다: 대상에게 " +
               phys("r_main", "r_main_ratio", "r_main_hp", " 최대 체력") + " 물리 피해, 주변 적(대상 포함)에게 " +
               phys("r_dmg", "r_ratio", "r_hp", " 최대 체력") + " 물리 피해, " + R + "{r_up}초 에어본" + E + ".",
        "names": ("황금 발톱 진언", "맹호 도약", "게임 오버!"),
    },
    "ja": {
        "name": "コブコ",
        "attack": "猫パンチで" + AD + "の物理ダメージ。" + O + "第二形態" + E + "：ライフごとに初めて体力が" + A + "{p_hi}%" + E +
                  "を下回ると、倒れるまで激昂：攻撃速度" + A + "+{p_as}%" + E + "、ライフスティール" + A + "{p_vamp}%" + E + "。",
        "skill": mag("q_sh", "q_sh_ap") + "のシールド（" + A + "{q_sh_t}秒" + E + "）。" + A + "{q_t}秒" + E + "以内の次の通常攻撃が金爪の一撃に："
                 + phys("q_dmg", "q_ratio", "q_hp", "最大体力") + "の物理ダメージと" + R + "{q_stun}秒のスタン" + E + "。",
        "skill2": "対象に飛びかかり、着地時に周囲の敵へ" + phys("e_dmg", "e_ratio", "e_hp", "最大体力") + "の物理ダメージと" + R +
                  "{e_up}秒のノックアップ" + E + "。",
        "ult": "空高く跳び（対象指定不可・CC無効）、敵チャンピオンの上に落下：対象に" + phys("r_main", "r_main_ratio", "r_main_hp", "最大体力") +
               "の物理ダメージ、周囲の敵（対象も）に" + phys("r_dmg", "r_ratio", "r_hp", "最大体力") + "の物理ダメージと" + R + "{r_up}秒のノックアップ" +
               E + "。",
        "names": ("金爪の真言", "猛虎の跳躍", "ゲームオーバー！"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_kobuko's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.45, 0.0)],
    f"{ID}_q_stun": [(CLIP + "q_stun", 0.35, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_hit": [(CLIP + "e_hit", 0.45, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.45, 0.0)],
    f"{ID}_vo": [(CLIP + "vo", 0.6, 0.0)],
    f"{ID}_r_slam": [(CLIP + "r_slam", 0.6, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.5, 0.0)],
    f"{ID}_p": [(CLIP + "p", 0.5, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/kobuko.rs: the rage)
DLL_SOUNDS = {f"{ID}_p"}


def values(p):
    v = {k: p[k] for k in ("p_hi", "p_as", "p_vamp", "q_sh", "q_sh_ap", "q_dmg", "q_ratio", "q_hp", "e_dmg", "e_ratio",
                           "e_hp", "r_main", "r_main_ratio", "r_main_hp", "r_dmg", "r_ratio", "r_hp")}
    for k in ("q_sh_t", "q_t", "q_stun", "e_up", "r_up"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_kobuko.py")
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
    mi["last_updated"] = "2026-10-27"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
