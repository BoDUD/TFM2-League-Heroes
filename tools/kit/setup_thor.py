"""Thor's text (5 languages), sound_info files and champion_view, numbers from build_thor.P.

    python tools/kit/setup_thor.py [--check]

Writes his keys in ragnarok/ (tools/kit/ragnarok_pack.py writes them and the pack's own files: mod.mod_info naming
every hero, the merges of mod.override_info): text/champion.i18n (ragnarok_thor in every language, description +
skill_name), sound/sfx/ragnarok_thor_*.sound_info and their override entries, style/champion_view (face, centre,
banpick_center). --check only prints each text's shown length against TOOLTIP_MAX and the texts themselves.

Names: Record of Ragnarok's - 索尔 / 索爾 / Thor / トール / 토르, his hammer Mjolnir; Thor's Hammer (雷神之锤, the
manga's トールハンマー), Returning Mjolnir (回旋雷槌), Awakened Thunder Hammer (觉醒雷槌, the manga's 覚醒雷槌) and
Mjolnir Awakening (雷槌觉醒) name Codex's four icons (assets/source/thor/).
Sounds: Codex's delivery (assets/source/thor/README.md): 16 original SFX (the swings and hits apart, the slam's
charge and its blow, the throw, the return and the catch apart, the awakening, the ult's charge / slam / impact, the
fall) and ten lines of the official Japanese voice (Hikaru Midorikawa: six from the official countdown, four from a
PV, which still carry its music), bound after Codex's audio_events.json. Clips are git-ignored
(tools/kit/seed_thor_audio.py copies them from the delivery into ragnarok/sound/sfx/); package_mod moves them to
sound/bgm/ at install.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_thor import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, HPi, AD, O, A, R, M, S, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view (game px from his soles' point, up negative), measured 2026-11-20 on the built sheet (idle moved 7 px
# back, import_thor.SHIFT): eyes on Codex's row 68.5, 47.5 rows over the soles = 29 game px, 10 px forward = 6; the
# encyclopedia centre by bp_card_audit's rule (his solid top is Mjolnir on his shoulder, 43 over the soles: -16); the
# ban/pick card by its rule, y = -39 - top (the hammer's top 34.7 over the frame centre: -4, the whole hammer shown)
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 7, "y": -35}, "center": {"x": 0, "y": -20}, "banpick_center": {"x": 0, "y": -14}}


def hp(k, colour=O):
    return f" + {HPi}{colour}{{{k}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "索尔",
        "attack": "雷槌重击，造成" + AD + O + "物理伤害" + E + "。" + O + "雷槌觉醒" + E + "：每放" + A + "{p_n}次" + E +
                  "技能，雷槌觉醒" + A + "{p_t}秒" + E + "：普攻再造成" + M + "{p_dmg}" + E + hp("p_hp", M) + M + "魔法伤害" +
                  E + "，雷神之锤改为" + R + "眩晕{q_stun}秒" + E + "。",
        "skill": "左臂蓄雷、双手举锤往后仰再砸下，" + A + "{q_hit}秒" + E + "后雷电在前方炸开：敌人受到" + phys("q_dmg", "q_ad") + hp("q_hp") + O +
                 "物理伤害" + E + "并被冲击波" + R + "击飞{q_stun0}秒" + E + "（觉醒时" + R + "{q_stun}秒" + E + "）。",
        "skill2": "双臂的铁手套「雅恩格利佩尔」（天界最强的防御）顶在身前" + A + "{e_win}秒" + E + "：普攻全部挡住，受到的技能伤害降低" +
                  A + "{e_dr}%" + E + "；举起时获得" + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E + S + "护盾" + E + A +
                  "{e_sh_t}秒" + E + "。",
        "ult": "雷槌觉醒" + A + "{r_awake}秒" + E + "并掷出，像回旋镖一样飞回：来回穿过的敌人受到" +
               phys("r_pdmg", "r_pad") + hp("r_php") + O + "物理伤害" + E + "、减速" + A + "{r_slow}%" + E + "；接住后把速度和离心力化作"
               "一击砸向前方：" + phys("r_dmg", "r_ad") + hp("r_hp") + O + "物理伤害" + E + "并" + R + "击飞{r_up}秒" + E +
               "。期间不受控制，伤害降低" + A + "{r_dr}%" + E + "。",
        "names": ("斗神之雷槌", "铁手套", "觉醒雷槌"),
    },
    "zh-hant": {
        "name": "索爾",
        "attack": "雷槌重擊，造成" + AD + O + "物理傷害" + E + "。" + O + "雷槌覺醒" + E + "：每施放" + A + "{p_n}次" + E +
                  "技能，雷槌覺醒" + A + "{p_t}秒" + E + "：普攻再造成" + M + "{p_dmg}" + E + hp("p_hp", M) + M + "魔法傷害" +
                  E + "，雷神之錘改為" + R + "暈眩{q_stun}秒" + E + "。",
        "skill": "左臂蓄雷、雙手舉錘往後仰再砸下，" + A + "{q_hit}秒" + E + "後雷電在前方炸開：敵人受到" + phys("q_dmg", "q_ad") + hp("q_hp") + O +
                 "物理傷害" + E + "並被衝擊波" + R + "擊飛{q_stun0}秒" + E + "（覺醒時" + R + "{q_stun}秒" + E + "）。",
        "skill2": "雙臂的鐵手套「雅恩格利佩爾」（天界最強的防禦）頂在身前" + A + "{e_win}秒" + E + "：普攻全部擋住，受到的技能傷害降低" +
                  A + "{e_dr}%" + E + "；舉起時獲得" + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E + S + "護盾" + E + A +
                  "{e_sh_t}秒" + E + "。",
        "ult": "雷槌覺醒" + A + "{r_awake}秒" + E + "並擲出，像迴旋鏢一樣飛回：來回穿過的敵人受到" +
               phys("r_pdmg", "r_pad") + hp("r_php") + O + "物理傷害" + E + "、緩速" + A + "{r_slow}%" + E + "；接住後把速度和離心力化作"
               "一擊砸向前方：" + phys("r_dmg", "r_ad") + hp("r_hp") + O + "物理傷害" + E + "並" + R + "擊飛{r_up}秒" + E +
               "。期間不受控制，傷害降低" + A + "{r_dr}%" + E + "。",
        "names": ("鬥神之雷槌", "鐵手套", "覺醒雷槌"),
    },
    "en": {
        "name": "Thor",
        "attack": "Strikes with Mjolnir for " + AD + " " + O + "physical damage" + E + ". " + O + "Mjolnir Awakening" + E +
                  ": every " + A + "{p_nth}" + E + " skill cast awakens Mjolnir for " + A + "{p_t}s" + E + ": his attacks add " +
                  M + "{p_dmg}" + E + hp("p_hp", M) + " " + M + "magic damage" + E + " and Thor's Hammer " + R +
                  "stuns for {q_stun}s" + E + ".",
        "skill": "Lightning in his left arm, both hands raise the hammer and bring it down: after " + A + "{q_hit}s" + E + " lightning bursts through the ground ahead, dealing " +
                 phys("q_dmg", "q_ad") + hp("q_hp") + " " + O + "physical damage" + E + " and the shockwave " + R + "knocks them up for {q_stun0}s" +
                 E + " (" + R + "{q_stun}s" + E + " awakened).",
        "skill2": "Raises Járngreipr, his iron gauntlets (heaven's strongest defence), for " + A + "{e_win}s" + E + ": "
                  "every basic attack is blocked and skill damage is reduced by " + A + "{e_dr}%" + E + "; raising them grants a " +
                  S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E + " " + S + "shield" + E + " for " + A + "{e_sh_t}s" + E + ".",
        "ult": "Mjolnir awakens for " + A + "{r_awake}s" + E + " and is hurled at the target, returning like a "
               "boomerang: enemies passed both ways take " + phys("r_pdmg", "r_pad") + hp("r_php") + " " + O + "physical damage" +
               E + " and are slowed by " + A + "{r_slow}%" + E + ". The catch turns its speed and spin into one blow ahead: " +
               phys("r_dmg", "r_ad") + hp("r_hp") + " " + O + "physical damage" + E + " and " + R + "knocked up for {r_up}s" + E +
               ". Unstoppable, taking " + A + "{r_dr}%" + E + " less damage.",
        "names": ("Thor's Hammer", "Járngreipr", "Geirröd Thor Hammer"),
    },
    "ko": {
        "name": "토르",
        "attack": "묠니르로 내리쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "묠니르 각성" + E + ": 스킬을 " + A + "{p_n}번" + E +
                  " 쓸 때마다 묠니르가 " + A + "{p_t}초" + E + " 각성: 기본 공격에 " + M + "{p_dmg}" + E + hp("p_hp", M) + " " + M +
                  "마법 피해" + E + " 추가, 토르 해머 " + R + "기절 {q_stun}초" + E + ".",
        "skill": "왼팔에 번개를 모아 두 손으로 망치를 내리쳐 " + A + "{q_hit}초" + E + " 뒤 번개가 앞쪽 땅에서 터진다: 적에게 " + phys("q_dmg", "q_ad") + hp("q_hp") +
                 " " + O + "물리 피해" + E + "와 충격파로 " + R + "{q_stun0}초 에어본" + E + "(각성 시 " + R + "{q_stun}초" + E + ").",
        "skill2": "강철 장갑 야른그레이프르(천계 최강의 방어)를 " + A + "{e_win}초" + E + " 동안 앞으로 세운다: 기본 공격을 모두 막고 "
                  "받는 스킬 피해 " + A + "{e_dr}%" + E + " 감소, 들어 올릴 때 " + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E +
                  " " + S + "보호막" + E + "(" + A + "{e_sh_t}초" + E + ").",
        "ult": "묠니르가 즉시 " + A + "{r_awake}초" + E + " 각성하고 대상에게 던져져 부메랑처럼 돌아온다: 오가며 지나친 적에게 " +
               phys("r_pdmg", "r_pad") + hp("r_php") + " " + O + "물리 피해" + E + "와 " + A + "{r_slow}%" + E + " 둔화. 받아낸 속도와 "
               "원심력을 일격으로 바꿔 앞쪽을 내리친다: " + phys("r_dmg", "r_ad") + hp("r_hp") + " " + O + "물리 피해" + E + "와 " + R +
               "{r_up}초 에어본" + E + ". 그동안 군중 제어 면역, 받는 피해 " + A + "{r_dr}%" + E + " 감소.",
        "names": ("토르 해머", "야른그레이프르", "게이르뢰드 토르 해머"),
    },
    "ja": {
        "name": "トール",
        "attack": "雷槌の一撃で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ミョルニル覚醒" + E + "：スキルを" + A + "{p_n}回" + E +
                  "使うごとにミョルニルが" + A + "{p_t}秒" + E + "覚醒：通常攻撃に" + M + "{p_dmg}" + E + hp("p_hp", M) + "の" + M +
                  "魔法ダメージ" + E + "を追加、トールハンマーは" + R + "{q_stun}秒のスタン" + E + "。",
        "skill": "左腕に雷を溜め両手で槌を振り下ろし、" + A + "{q_hit}秒" + E + "後に前方で雷が炸裂：敵に" + phys("q_dmg", "q_ad") + hp("q_hp") + "の" + O +
                 "物理ダメージ" + E + "と衝撃波で" + R + "{q_stun0}秒のノックアップ" + E + "（覚醒時" + R + "{q_stun}秒" + E + "）。",
        "skill2": "鉄手袋ヤールングレイプル（天界最強の防御）を" + A + "{e_win}秒" + E + "身の前に構える：通常攻撃を全て防ぎ、"
                  "スキルの被ダメージ" + A + "{e_dr}%" + E + "軽減。構えた時に" + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E +
                  "の" + S + "シールド" + E + "（" + A + "{e_sh_t}秒" + E + "）。",
        "ult": "ミョルニルが" + A + "{r_awake}秒" + E + "覚醒、投げるとブーメランのように戻る：往復で敵に" +
               phys("r_pdmg", "r_pad") + hp("r_php") + "の" + O + "物理ダメージ" + E + "と" + A + "{r_slow}%" + E + "スロウ。受け止めた"
               "勢いを一撃に変え前を叩く：" + phys("r_dmg", "r_ad") + hp("r_hp") + "の" + O + "物理ダメージ" + E + "と" +
               R + "{r_up}秒ノックアップ" + E + "。その間行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減。",
        "names": ("闘神の雷槌", "ヤールングレイプル", "覚醒雷槌"),
    },
}

# sound event -> [(clip, volume, delay)]: every event the kit plays (build_thor's sfx / tsfx) and ragnarok.dll's
SOUNDS = {
    f"{ID}_a": [(SFX + "attack_swing_2", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "attack_hit_1", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "skill_charge", 0.5, 0.0)],
    f"{ID}_q_slam": [(SFX + "skill_slam", 0.6, 0.0)],
    f"{ID}_q_hit": [(SFX + "attack_hit_3", 0.45, 0.0)],
    # 铁手套格挡：举起来挥一下，第 4 帧手套顶住时金属的一声（接锤那一声）
    f"{ID}_e": [(SFX + "attack_swing_2", 0.4, 0.0)],
    f"{ID}_e_block": [(SFX + "skill2_catch", 0.55, 0.0)],
    # 觉醒雷槌：扔出、折返、来回砸中、接住（原来 E 的那几声）
    f"{ID}_r_throw": [(SFX + "skill2_throw", 0.55, 0.0)],
    f"{ID}_r_pass": [(SFX + "attack_hit_2", 0.4, 0.0)],
    f"{ID}_r_turn": [(SFX + "skill2_return", 0.5, 0.0)],
    f"{ID}_r_catch": [(SFX + "skill2_catch", 0.55, 0.0)],
    f"{ID}_p_awake": [(SFX + "awakening", 0.6, 0.0)],
    f"{ID}_r": [(SFX + "ult_charge", 0.55, 0.0)],
    f"{ID}_r_vo": [(VO + "one_strike", 0.8, 0.0)],
    f"{ID}_r_slam": [(SFX + "ult_slam", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "ult_impact", 0.55, 0.0)],
    # ragnarok.dll (addons/ragnarok/src/thor.rs): the fall when he dies (his death frames lie down from 0.42 s to
    # 0.6 s), the voice lines
    f"{ID}_dead": [(SFX + "body_fall", 0.5, 0.5)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in
       ("worthy", "wake", "address", "smash_call", "praise", "weapon", "anticipation", "warning", "sleepy")},
}

NTH = {2: "second", 3: "third", 4: "fourth"}


def values(p):
    if not 0 < p["q_stun0"] < p["q_stun"]:
        sys.exit("the texts are for a slam that stuns, longer when awakened (0 < q_stun0 < q_stun)")
    v = {k: p[k] for k in ("p_n", "p_dmg", "p_hp", "q_dmg", "q_ad", "q_hp", "e_dr", "e_sh", "e_sh_ad", "r_pdmg", "r_pad",
                           "r_php", "r_slow", "r_dmg", "r_ad", "r_hp", "r_dr")}
    v["p_nth"] = NTH[p["p_n"]]
    for k in ("p_t", "q_hit", "q_stun", "q_stun0", "e_sh_t", "r_awake", "r_up"):
        v[k] = secs(p[k])
    v["e_win"] = secs(p["e_off"] - p["e_on"])
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "thor", "tools/kit/seed_thor_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
