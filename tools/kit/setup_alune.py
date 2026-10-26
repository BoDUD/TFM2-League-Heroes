"""Alune's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_alune.P.

    python tools/kit/setup_alune.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft): mod.mod_info (VERSION, the pack's description:
setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys sorted,
setup_norra.py's way), text/champion.i18n
(tft_alune in every language, description + skill_name), sound/sfx/tft_alune_*.sound_info, mod.override_info (the text and
champion_view merges and two entries a sound: its event -> our .sound_info, its clip -> our audio, the custom-sound
rule), style/champion_view (face, centre, banpick_center). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX and the texts themselves.
Names: TFT set 18's own (CommunityDragon latest cdragon/tft/<locale>.json, DA_18_Alune): zh_CN 拉露恩, zh_TW 亞盧妮, ja
アルーン, ko 알룬, Moonfall = 月之降临 / 月隕 / 崩月 / 달빛 낙하. Moonlight (月华), Moon Descends (月曜降临) and the passive Moon
Phase (月相, in the attack's text) are our own (TFT has one ability; the user's pick, plan A 「月相」). The texts are the
rules she plays with tft.dll (addons/tft/src/alune.rs): Moonfall on the nearest enemies, the full moon's damage shared,
the ring's way back.
Sounds: tools/lol/extract_alune.py's clips in tft/sound/sfx/tft_alune_sfx_*.wav (git-ignored) - her own set-11 TFT
sounds (attack, Moonfall's cast and shards, her Chinese voice line on the ult) and Diana's Pale Cascade / Moonfall for
Moonlight and the full moon. A clip name never equals an event name (vo-clip-names rule): event tft_alune_<x> plays
clip tft_alune_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_alune import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with setup_norra.py)

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
VERSION = "0.4.0"      # Powder 0.1, Norra 0.2, the pack's own code (tft.dll) 0.3, Alune 0.4: the next free one at merge
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from her soles' point, up negative): the face point between her eyes (the design's eye rows 15-16
# of 90 at PPU 2: 37 over the ground, 2 ahead of her standing column 34); the centre in her body (she sits high on the
# crescent: league_aurora / league_nunu's -18); the ban/pick card at 85 % (league.dll UI_SIZES): her horns a game pixel
# under the canvas top, the crescent's foot on its bottom (bp_card_audit.py's math: top -28.9, bottom 10.2 -> -10)
VIEW = {"face": {"x": 2, "y": -37}, "center": {"x": 0, "y": -18}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "拉露恩",
        "attack": "把螺旋月环像飞盘一样甩出去，造成" + AD + O + "物理伤害" + E + "，月环飞回她手里，回程路上的敌人受到" + ADi + O +
                  "{a_back_r}%" + E + "物理伤害。" + O + "月相" + E + "：每放一次技能月亮长一档，最多" + A + "3" + E + "档；大招每档伤害+" +
                  A + "{r_ph}%" + E + "，砸完回到新月。",
        "skill": "月光碎片从天而降，落在离她最近的" + A + "{q_n}" + E + "个敌人身上，每枚造成" + mag("q_dmg", "q_ratio") +
                 "魔法伤害，并使魔抗降低" + A + "{q_shred}%" + E + "，持续" + A + "{q_shred_t}秒" + E + "。",
        "skill2": "月光洒在她和身边的友方英雄身上，攻击速度提高" + A + "{e_as}%" + E + "，持续" + A + "{e_t}秒" + E + "。",
        "ult": "敌方英雄脚下浮现月影，" + A + "{r_open}秒" + E + "后满月砸下：" + mag("r_dmg", "r_ratio") + "魔法伤害×" + A + "{r_split}%" +
               E + "由范围内的敌人平分（每人最多" + A + "{r_cap}%" + E + "），中心的敌人" + R + "眩晕" + E + A + "{r_stun}秒" + E + "。",
        "names": ("月之降临", "月华", "月曜降临"),
    },
    "zh-hant": {
        "name": "亞盧妮",
        "attack": "把螺旋月環像飛盤一樣甩出去，造成" + AD + O + "物理傷害" + E + "，月環飛回她手裡，回程路上的敵人受到" + ADi + O +
                  "{a_back_r}%" + E + "物理傷害。" + O + "月相" + E + "：每施放一次技能月亮長一階，最多" + A + "3" + E + "階；大招每階傷害+" +
                  A + "{r_ph}%" + E + "，砸完回到新月。",
        "skill": "月華碎片從天而降，落在離她最近的" + A + "{q_n}" + E + "名敵人身上，每塊造成" + mag("q_dmg", "q_ratio") +
                 "魔法傷害，並使魔抗降低" + A + "{q_shred}%" + E + "，持續" + A + "{q_shred_t}秒" + E + "。",
        "skill2": "月光灑在她和身邊的友方英雄身上，攻擊速度提高" + A + "{e_as}%" + E + "，持續" + A + "{e_t}秒" + E + "。",
        "ult": "敵方英雄腳下浮現月影，" + A + "{r_open}秒" + E + "後滿月砸下：" + mag("r_dmg", "r_ratio") + "魔法傷害×" + A + "{r_split}%" +
               E + "由範圍內的敵人平分（每人最多" + A + "{r_cap}%" + E + "），中心的敵人" + R + "暈眩" + E + A + "{r_stun}秒" + E + "。",
        "names": ("月隕", "月華", "月曜降臨"),
    },
    "en": {
        "name": "Alune",
        "attack": "Flings her spiral ring like a disc for " + AD + " " + O + "physical damage" + E + "; it flies back to her, "
                  "dealing " + ADi + O + "{a_back_r}%" + E + " physical damage to enemies on the way. " + O + "Moon Phase" + E +
                  ": each skill she casts grows the moon a phase, up to " + A + "3" + E + "; her ultimate deals " + A + "{r_ph}%" +
                  E + " more a phase, and the moon wanes to new.",
        "skill": "Moonshards rain on the " + A + "{q_n}" + E + " enemies nearest her, each dealing " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and lowering magic resistance by " + A + "{q_shred}%" +
                 E + " for " + A + "{q_shred_t}s" + E + ".",
        "skill2": "Moonlight falls on her and the allied champions near her: " + A + "{e_as}%" + E + " attack speed for " + A +
                  "{e_t}s" + E + ".",
        "ult": "The moon's shadow spreads under an enemy champion; " + A + "{r_open}s" + E + " later the full moon crashes down: " +
               A + "{r_split}%" + E + " of " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " split among the enemies in "
               "the area (at most " + A + "{r_cap}%" + E + " each), those in the middle " + R + "stunned" + E + " for " + A +
               "{r_stun}s" + E + ".",
        "names": ("Moonfall", "Moonlight", "Moon Descends"),
    },
    "ko": {
        "name": "알룬",
        "attack": "나선 고리를 원반처럼 던져 " + AD + " 물리 피해, 고리는 되돌아오며 길 위의 적에게 " + ADi + O + "{a_back_r}%" + E +
                  " 물리 피해. " + O + "달의 위상" + E + ": 스킬을 쓸 때마다 달이 한 단계 차오른다(최대 " + A + "3" + E + "단계). 궁극기는 단계마다 "
                  "피해 +" + A + "{r_ph}%" + E + ", 쓴 뒤 다시 초승달.",
        "skill": "가장 가까운 적 " + A + "{q_n}" + E + "명에게 달조각이 떨어져 각각 " + mag("q_dmg", "q_ratio") + " 마법 피해를 입히고 " + A +
                 "{q_shred_t}초" + E + " 동안 마법 저항력을 " + A + "{q_shred}%" + E + " 낮춘다.",
        "skill2": "자신과 주변 아군 챔피언에게 달빛이 내려 " + A + "{e_t}초" + E + " 동안 공격 속도 +" + A + "{e_as}%" + E + ".",
        "ult": "적 챔피언의 발밑에 달그림자가 드리우고 " + A + "{r_open}초" + E + " 뒤 보름달이 떨어진다: " + mag("r_dmg", "r_ratio") +
               " 마법 피해의 " + A + "{r_split}%" + E + "를 범위의 적이 나누어 받고(1명당 최대 " + A + "{r_cap}%" + E + "), 중심의 적은 " + A +
               "{r_stun}초" + E + " " + R + "기절" + E + ".",
        "names": ("달빛 낙하", "달빛 가호", "보름달 강림"),
    },
    "ja": {
        "name": "アルーン",
        "attack": "螺旋の輪を円盤のように投げ、" + AD + "の物理ダメージ。輪は戻ってきて途中の敵に" + ADi + O + "{a_back_r}%" + E +
                  "の物理ダメージ。" + O + "月相" + E + "：スキルを使うたびに月が満ちる（最大" + A + "3" + E + "段階）。アルティメットは1段階ごとに"
                  "ダメージ+" + A + "{r_ph}%" + E + "、使うと新月に戻る。",
        "skill": "最も近い敵" + A + "{q_n}" + E + "体に月の破片が降り、それぞれ" + mag("q_dmg", "q_ratio") +
                 "の魔法ダメージと" + A + "{q_shred_t}秒" + E + "の魔法防御-" + A + "{q_shred}%" + E + "。",
        "skill2": "自分と周りの味方チャンピオンに月光が降り、" + A + "{e_t}秒" + E + "間攻撃速度+" + A + "{e_as}%" + E + "。",
        "ult": "敵チャンピオンの足元に月の影が広がり、" + A + "{r_open}秒" + E + "後に満月が落ちる：" + mag("r_dmg", "r_ratio") +
               "の魔法ダメージの" + A + "{r_split}%" + E + "を範囲の敵で分け合い（1体あたり最大" + A + "{r_cap}%" + E + "）、中心の敵は" + A +
               "{r_stun}秒" + E + R + "スタン" + E + "。",
        "names": ("崩月", "月光の加護", "満月降臨"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_alune's sfx / tsfx)
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.35, 0.0)],
    f"{ID}_e_cast": [(CLIP + "e_cast", 0.45, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.25, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0), (CLIP + "r_vo", 0.6, 0.0)],
    f"{ID}_r_blast": [(CLIP + "r_blast", 0.55, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/alune.rs: a moonshard landing), not the kit's data
DLL_SOUNDS = {f"{ID}_q_hit"}


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_n", "q_dmg", "q_ratio", "q_shred", "e_as", "r_dmg", "r_ratio", "r_ph", "r_split", "r_cap",
                           "a_back_r")}
    for k in ("q_shred_t", "e_t", "r_open", "r_stun"):
        v[k] = secs(p[k])
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path, default=None):
    if default is not None and not os.path.isfile(lp(path)):
        return default
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def kit_sounds():
    """Every Sfx / TargetSfx name the kit plays."""
    kit = load(os.path.join(MOD, "champion", f"{ID}.data_champion"))
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
    walk(kit)
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_alune.py")
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
    mi["last_updated"] = "2026-10-26"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
