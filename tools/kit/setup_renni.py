"""Renni's text (5 languages), sound_info files and the tft pack's shared files, numbers from build_renni.P.

    python tools/kit/setup_renni.py [--check]

Writes (in tft/, the Teamfight Tactics pack, mod_id tft) what setup_scar.py writes for Scar: mod.mod_info (VERSION, the
pack's description: setup_powder.DESC with every hero of HEROES, contains_code / mod_type native for tft.dll, the keys
sorted), text/champion.i18n (tft_renni in every language, description + skill_name), sound/sfx/tft_renni_*.sound_info,
mod.override_info (the text and champion_view merges and two entries a sound: its event -> our .sound_info, its clip ->
our audio, the custom-sound rule), style/champion_view (face, centre, banpick_center). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX
and the texts themselves.
Names: TFT set 13's own (CommunityDragon latest cdragon/tft/<locale>.json, TFT13_Chainsaw, 2026-10-29): zh_CN 荏妮 (the
user calls her 伦妮), zh_TW 雷尼, ja レニー, ko 레니, en Renni; Sludgerunner's Smash = 泥奔者重击 / 泥奔者猛擊 / スラッジランナーの襲撃 /
진창 주자의 강타. Shimmer Frenzy (微光狂热, after her trait Chem-Baron's Shimmer), the Chainsaw Charge (链锯冲撞) and the Saw
Guard (锯刃格挡) are our own (TFT has one ability; the user's pick, plan A 「泥奔者」). The texts are the rules she plays with
tft.dll (addons/tft/src/renni.rs): the shimmer shot under p_line% health, both heals by her maximum health.
Sounds: tools/lol/extract_renni.py's clips in tft/sound/sfx/tft_renni_sfx_*.wav (git-ignored) - her own set-13 TFT
sounds (the saw's two revs and grinds, the heave, the lift's grind, the slam's two hits, her voice on the heave), Vi's
Vault Breaker launch for the charge, Braum's Unbreakable for the guard, Dr. Mundo's Maximum Dosage and Heart Zapper heal
for the shimmer shot and the heals. A clip name never equals an event name (vo-clip-names rule): event tft_renni_<x>
plays clip tft_renni_sfx_<x>. package_mod moves the clips to sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_renni import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description (shared with the other tft heroes)
from setup_alune import load, save, secs, shown_length  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
CLIP = f"{ID}_sfx_"
# Powder 0.1, Norra 0.2, tft.dll 0.3, Alune 0.4, Silco 0.5, Maddie 0.6, Loris 0.7, Kobuko 0.8, Vander 0.9, Violet 0.10,
# Krug 0.11, Ao Shin 0.13, Scar 0.14, Renni 0.15
VERSION = "0.15.0"
ADi, APi, TOOLTIP_MAX = pack.ADi, pack.APi, pack.TOOLTIP_MAX
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view (game px from her soles' point, up negative): the face point by her eye (the design's eye row 22 of 77
# at PPU 2.0: 28 over the ground; 5 ahead of her standing column); the centre in her body; the ban/pick card by
# bp_card_audit.py's rule (-39 less the idle's top -27.3: her head 1 game px under the card's top)
VIEW = {"face": {"x": 5, "y": -28}, "center": {"x": 1, "y": -17}, "banpick_center": {"x": 2, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "荏妮",
        "attack": "链锯每次咬" + A + "3" + E + "下，每下造成" + ADi + O + "{a_pct}%" + E + O + "物理伤害" + E + "。" + O + "微光狂热" + E +
                  "：生命低于" + A + "{p_line}%" + E + "时注射微光（每" + A + "{p_cd}秒" + E + "一次），" + A + "{p_t}秒" + E + "内攻速+" +
                  A + "{p_as}%" + E + "，并回复" + HPi + O + "{p_heal}%" + E + "最大生命。",
        "skill": "冲向目标，在前方扇形里锯" + A + "{q_n}" + E + "次，每次造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R +
                 "减速{q_slow}%" + E + "，持续" + A + "{q_slow_t}秒" + E + "。",
        "skill2": "竖起链锯格挡：获得" + O + "{e_sh}" + E + "+" + ADi + O + "{e_sh_ad}%" + E + "护盾，持续" + A + "{e_t}秒" + E + "，期间减伤" +
                  A + "{e_dr}%" + E + "。",
        "ult": "把目标挑起举过头顶，造成" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并" + R + "击飞{r_up}秒" + E + "，期间回复" + HPi +
               O + "{r_heal}%" + E + "最大生命；再狠狠砸下，对前方周围敌人造成" + phys("r_s", "r_s_ad") + O + "物理伤害" + E + "。",
        "names": ("链锯冲撞", "锯刃格挡", "泥奔者重击"),
    },
    "zh-hant": {
        "name": "雷尼",
        "attack": "鏈鋸每次咬" + A + "3" + E + "下，每下造成" + ADi + O + "{a_pct}%" + E + O + "物理傷害" + E + "。" + O + "微光狂熱" + E +
                  "：生命低於" + A + "{p_line}%" + E + "時注射微光（每" + A + "{p_cd}秒" + E + "一次），" + A + "{p_t}秒" + E + "內攻速+" +
                  A + "{p_as}%" + E + "，並回復" + HPi + O + "{p_heal}%" + E + "最大生命。",
        "skill": "衝向目標，在前方扇形裡鋸" + A + "{q_n}" + E + "次，每次造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R +
                 "緩速{q_slow}%" + E + "，持續" + A + "{q_slow_t}秒" + E + "。",
        "skill2": "豎起鏈鋸格擋：獲得" + O + "{e_sh}" + E + "+" + ADi + O + "{e_sh_ad}%" + E + "護盾，持續" + A + "{e_t}秒" + E + "，期間減傷" +
                  A + "{e_dr}%" + E + "。",
        "ult": "把目標挑起舉過頭頂，造成" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並" + R + "擊飛{r_up}秒" + E + "，期間回復" + HPi +
               O + "{r_heal}%" + E + "最大生命；再狠狠砸下，對前方周圍敵人造成" + phys("r_s", "r_s_ad") + O + "物理傷害" + E + "。",
        "names": ("鏈鋸衝撞", "鋸刃格擋", "泥奔者猛擊"),
    },
    "en": {
        "name": "Renni",
        "attack": "Her saw bites " + A + "3" + E + " times, each for " + ADi + O + "{a_pct}%" + E + " " + O + "physical damage" + E + ". " +
                  O + "Shimmer Frenzy" + E + ": below " + A + "{p_line}%" + E + " health (once every " + A + "{p_cd}s" + E +
                  ") she shoots up Shimmer: " + A + "+{p_as}%" + E + " attack speed for " + A + "{p_t}s" + E + ", healing " + HPi +
                  O + "{p_heal}%" + E + " max health.",
        "skill": "Charges the target and grinds the cone in front of her " + A + "{q_n}" + E + " times, each for " +
                 phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + ", " + R + "slowing by {q_slow}%" + E + " for " + A +
                 "{q_slow_t}s" + E + ".",
        "skill2": "Raises her saw as a guard: a " + O + "{e_sh}" + E + " + " + ADi + O + "{e_sh_ad}%" + E + " shield for " + A +
                  "{e_t}s" + E + " and " + A + "{e_dr}%" + E + " less damage taken meanwhile.",
        "ult": "Hooks the target up overhead for " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + ", " + R +
               "airborne for {r_up}s" + E + ", healing " + HPi + O + "{r_heal}%" + E + " max health; then slams it down for " +
               phys("r_s", "r_s_ad") + " " + O + "physical damage" + E + " to the enemies there.",
        "names": ("Chainsaw Charge", "Saw Guard", "Sludgerunner's Smash"),
    },
    "ko": {
        "name": "레니",
        "attack": "전기톱이 " + A + "3" + E + "번 물어뜯어 각각 " + ADi + O + "{a_pct}%" + E + " " + O + "물리 피해" + E + ". " + O +
                  "시머 광란" + E + ": 체력 " + A + "{p_line}%" + E + " 미만에서 시머 주입(" + A + "{p_cd}초" + E + "마다 한 번), " + A +
                  "{p_t}초" + E + " 동안 공격 속도 +" + A + "{p_as}%" + E + ", 최대 체력의 " + HPi + O + "{p_heal}%" + E + " 회복.",
        "skill": "대상에게 돌진해 앞쪽 부채꼴을 " + A + "{q_n}" + E + "번 갈아 각각 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E +
                 "와 " + A + "{q_slow_t}초" + E + " 동안 " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "전기톱을 세워 막기: " + A + "{e_t}초" + E + " 동안 " + O + "{e_sh}" + E + " + " + ADi + O + "{e_sh_ad}%" + E + " 보호막, " +
                  "그동안 받는 피해 " + A + "{e_dr}%" + E + " 감소.",
        "ult": "대상을 머리 위로 들어 올려 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_up}초 에어본" + E +
               ", 그동안 최대 체력의 " + HPi + O + "{r_heal}%" + E + " 회복; 이어 내리찍어 그 주변 적에게 " + phys("r_s", "r_s_ad") + " " +
               O + "물리 피해" + E + ".",
        "names": ("전기톱 돌진", "톱날 방어", "진창 주자의 강타"),
    },
    "ja": {
        "name": "レニー",
        "attack": "チェーンソーが" + A + "3" + E + "回噛みつき、それぞれ" + ADi + O + "{a_pct}%" + E + "の" + O + "物理ダメージ" + E + "。" +
                  O + "シマー狂乱" + E + "：体力" + A + "{p_line}%" + E + "未満でシマーを注入（" + A + "{p_cd}秒" + E + "に1回）、" + A +
                  "{p_t}秒" + E + "間攻撃速度+" + A + "{p_as}%" + E + "、最大体力の" + HPi + O + "{p_heal}%" + E + "回復。",
        "skill": "対象へ突進し、前方の扇形を" + A + "{q_n}" + E + "回切り刻む。それぞれ" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" +
                 E + "と" + A + "{q_slow_t}秒" + E + "の" + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "チェーンソーを立てて防御：" + A + "{e_t}秒" + E + "間" + O + "{e_sh}" + E + "+" + ADi + O + "{e_sh_ad}%" + E +
                  "のシールド、その間被ダメージ" + A + "{e_dr}%" + E + "軽減。",
        "ult": "対象を頭上に持ち上げ、" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{r_up}秒のノックアップ" + E +
               "、その間最大体力の" + HPi + O + "{r_heal}%" + E + "回復。その後叩きつけ、周囲の敵に" + phys("r_s", "r_s_ad") + "の" + O +
               "物理ダメージ" + E + "。",
        "names": ("チェーンソーチャージ", "ソーガード", "スラッジランナーの襲撃"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_renni's sfx / tsfx) and tft.dll's
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_p": [(CLIP + "p", 0.5, 0.0)],
    f"{ID}_p_heal": [(CLIP + "p_heal", 0.45, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.5, 0.0)],
    f"{ID}_q_saw": [(CLIP + "q_saw", 0.45, 0.0)],
    f"{ID}_q_hit": [(CLIP + "q_hit", 0.4, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.5, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0)],
    f"{ID}_r_vo": [(CLIP + "r_vo", 0.6, 0.0)],
    f"{ID}_r_lift": [(CLIP + "r_lift", 0.5, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.6, 0.0)],
    f"{ID}_r_slam": [(CLIP + "r_slam", 0.6, 0.0)],
}
# the sounds tft.dll plays itself (addons/tft/src/renni.rs: the shimmer shot, the lift's heal)
DLL_SOUNDS = {f"{ID}_p", f"{ID}_p_heal"}


def values(p):
    v = {k: p[k] for k in ("a_pct", "p_line", "p_as", "p_heal", "q_n", "q_dmg", "q_ad", "q_slow", "e_sh", "e_sh_ad", "e_dr",
                           "r_dmg", "r_ad", "r_heal", "r_s", "r_s_ad")}
    for k in ("p_cd", "p_t", "q_slow_t", "e_t", "r_up"):
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
                print(f"warning: {c}.wav missing - run tools/lol/extract_renni.py")
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
    mi["last_updated"] = "2026-10-29"
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(len(SOUNDS), "sounds,", len(clips), "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
