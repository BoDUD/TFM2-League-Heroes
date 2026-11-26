"""Lu Bu's text (5 languages), sound_info files and champion_view, numbers from build_lubu.P.

    python tools/kit/setup_lubu.py [--check]

Writes his keys in ragnarok/ (tools/kit/ragnarok_pack.py writes them and the pack's own files: mod.mod_info naming
every hero, the merges of mod.override_info): text/champion.i18n (ragnarok_lubu in every language, description +
skill_name), sound/sfx/ragnarok_lubu_*.sound_info and their override entries, style/champion_view (face, centre,
banpick_center). --check only prints each text's shown length against TOOLTIP_MAX and the texts themselves.

Names: Record of Ragnarok's own - 吕布奉先 / 呂布奉先 (ja, zh-hant) / Lu Bu / 여포 봉선; his halberd the Sky Piercer
(方天画戟), his technique Sky Eater (天喰); Sweep (横扫), Formation Breaker (破阵) and Shield Breaker (盾牌破坏者) name
Codex's four icons (assets/source/lubu/, the user's approved set).
Sounds: Codex's delivery (assets/source/lubu/README.md): 15 original SFX (the swings and hits apart, the charge, the
cut, its impact, the shield break) and ten lines of the official Japanese voice (Seki Tomokazu, the official
countdown and the Lu Bu vs Thor PV). Clips are git-ignored (tools/kit/seed_lubu_audio.py copies them from the
delivery into ragnarok/sound/sfx/); package_mod moves them to sound/bgm/ at install.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_lubu import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view (game px from his soles' point, up negative): set from the built sheet (tools/art/import_lubu.py
# prints the face point it measures on the 1x idle), the ban/pick card by bp_card_audit.py's rule
# 2026-11-20 at PPU 1.94 (85 % of the first size): eyes 50 rows over the soles = 26 game px; the encyclopedia centre by
# bp_card_audit --centers (-9); the ban/pick card by its rule, y = -39 - top (the plume's tip 26 over the centre)
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）；
# 放大后选人卡会挡 6 像素以上的腿：addons/ragnarok/src/hd.rs 的 UI_SIZES 把他在选人卡里缩小，这里按缩小后的头顶算
VIEW = {"face": {"x": 4, "y": -31}, "center": {"x": 0, "y": -17}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "吕布奉先",
        "attack": "方天画戟重击，造成" + AD + O + "物理伤害" + E + "。" + O + "盾牌破坏者" + E + "：无视" + A + "{p_pen}%" + E +
                  "护甲；对护盾的伤害提高" + A + "{p_shield}%" + E + "，打碎护盾时再造成" + ratio("p_break") + "物理伤害。",
        "skill": "方天画戟横扫前方扇形，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "，并减速" + A + "{q_slow}%" + E +
                 "，持续" + A + "{q_slow_t}秒" + E + "。",
        "skill2": "朝目标突刺冲阵，穿过路上的敌人，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R +
                  "击飞{e_air}秒" + E + "。",
        "ult": "举戟蓄力" + A + "{r_go}秒" + E + "（不受控制，受到的伤害降低" + A + "{r_dr}%" + E + "），随后朝目标斩出天喰：直线上的敌人受到" +
               phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并" + R + "眩晕{r_stun}秒" + E + "。",
        "names": ("横扫", "破阵", "天喰"),
    },
    "zh-hant": {
        "name": "呂布奉先",
        "attack": "方天畫戟重擊，造成" + AD + O + "物理傷害" + E + "。" + O + "盾牌破壞者" + E + "：無視" + A + "{p_pen}%" + E +
                  "護甲；對護盾的傷害提高" + A + "{p_shield}%" + E + "，擊碎護盾時再造成" + ratio("p_break") + "物理傷害。",
        "skill": "方天畫戟橫掃前方扇形，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "，並緩速" + A + "{q_slow}%" + E +
                 "，持續" + A + "{q_slow_t}秒" + E + "。",
        "skill2": "朝目標突刺衝陣，穿過路上的敵人，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R +
                  "擊飛{e_air}秒" + E + "。",
        "ult": "舉戟蓄力" + A + "{r_go}秒" + E + "（不受控制，受到的傷害降低" + A + "{r_dr}%" + E + "），隨後朝目標斬出天喰：直線上的敵人受到" +
               phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並" + R + "暈眩{r_stun}秒" + E + "。",
        "names": ("橫掃", "破陣", "天喰"),
    },
    "en": {
        "name": "Lu Bu",
        "attack": "Swings the Sky Piercer for " + AD + " " + O + "physical damage" + E + ". " + O + "Shield Breaker" + E +
                  ": ignores " + A + "{p_pen}%" + E + " armor; deals " + A + "{p_shield}%" + E + " more damage to shields, and "
                  "breaking a shield deals " + ratio("p_break") + " more physical damage.",
        "skill": "Sweeps the halberd through a cone in front, dealing " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + " and slowing by " + A + "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Charges through the enemy line toward the target: enemies in his path take " + phys("e_dmg", "e_ad") +
                  " " + O + "physical damage" + E + " and are " + R + "knocked up for {e_air}s" + E + ".",
        "ult": "Gathers himself for " + A + "{r_go}s" + E + " (unstoppable, taking " + A + "{r_dr}%" + E + " less damage), then "
               "cuts the sky toward the target: enemies on the line take " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + " and are " + R + "stunned for {r_stun}s" + E + ".",
        "names": ("Sweep", "Formation Breaker", "Sky Eater"),
    },
    "ko": {
        "name": "여포 봉선",
        "attack": "방천화극으로 내리쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "방패 파괴자" + E + ": 방어력 " + A +
                  "{p_pen}%" + E + " 무시; 보호막에 주는 피해 " + A + "{p_shield}%" + E + " 증가, 보호막을 깨면 " + ratio("p_break") +
                  " 물리 피해 추가.",
        "skill": "방천화극으로 전방 부채꼴을 휩쓸어 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "와 " + A +
                 "{q_slow_t}초" + E + " 동안 " + A + "{q_slow}%" + E + " 둔화.",
        "skill2": "대상을 향해 적진을 꿰뚫고 돌격: 경로의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_air}초 에어본" + E + ".",
        "ult": A + "{r_go}초" + E + " 동안 힘을 모은 뒤(군중 제어 면역, 받는 피해 " + A + "{r_dr}%" + E + " 감소) 대상 쪽으로 하늘을 "
               "베는 천식: 직선 위의 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_stun}초 기절" +
               E + ".",
        "names": ("휩쓸기", "파진", "천식"),
    },
    "ja": {
        "name": "呂布奉先",
        "attack": "方天画戟の一撃で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "シールドブレイカー" + E + "：物理防御の" +
                  A + "{p_pen}%" + E + "を無視、シールドへのダメージ+" + A + "{p_shield}%" + E + "、シールドを砕くと" +
                  ratio("p_break") + "の物理ダメージを追加。",
        "skill": "方天画戟で前方の扇状範囲を薙ぎ払い、" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + A +
                 "{q_slow_t}秒" + E + "間" + A + "{q_slow}%" + E + "のスロウ。",
        "skill2": "目標へ敵陣を突き破って突進：通り道の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_air}秒のノックアップ" + E + "。",
        "ult": A + "{r_go}秒" + E + "力を溜め（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）、目標の方向へ天喰を放つ：" +
               "直線上の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{r_stun}秒のスタン" + E + "。",
        "names": ("薙ぎ払い", "破陣", "天喰"),
    },
}

# sound event -> [(clip, volume, delay)]: every event the kit plays (build_lubu's sfx / tsfx) and ragnarok.dll's
SOUNDS = {
    f"{ID}_a": [(SFX + "attack_swing_2", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "attack_hit_1", 0.45, 0.0)],
    f"{ID}_q_swing": [(SFX + "skill_swing", 0.55, 0.0)],
    f"{ID}_q_hit": [(SFX + "skill_hit", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "skill2_thrust", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "skill2_hit", 0.45, 0.0)],
    f"{ID}_r": [(SFX + "ult_charge", 0.55, 0.0)],
    f"{ID}_r_vo": [(VO + "ult", 0.8, 0.0)],
    f"{ID}_r_slash": [(SFX + "ult_release", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "ult_impact", 0.55, 0.0)],
    # ragnarok.dll: the shattered shield, the voice lines (addons/ragnarok/src/lubu.rs)
    f"{ID}_p_break": [(SFX + "shield_break", 0.6, 0.0)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in
       ("select", "start", "taunt_strong", "taunt_gods", "challenge", "swing_call", "praise", "encounter", "power")},
}


def values(p):
    v = {k: p[k] for k in ("p_pen", "p_shield", "p_break", "q_dmg", "q_ad", "q_slow", "e_dmg", "e_ad", "r_dmg", "r_ad",
                           "r_dr")}
    for k in ("q_slow_t", "e_air", "r_go", "r_stun"):
        v[k] = secs(p[k])
    return v


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
    tx = texts(dict(P))
    bad = check_lengths(TEXT)
    if a.check:
        print_texts(tx)
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "lubu", "tools/kit/seed_lubu_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
