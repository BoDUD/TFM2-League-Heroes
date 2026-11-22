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
        "skill": "举锤砸地，" + A + "{q_hit}秒" + E + "后雷电在前方炸开：敌人受到" + phys("q_dmg", "q_ad") + hp("q_hp") + O +
                 "物理伤害" + E + "并" + R + "眩晕{q_stun0}秒" + E + "（觉醒时" + R + "{q_stun}秒" + E + "）。",
        "skill2": "朝目标方向掷出雷槌，雷槌飞回手中，来回穿过的敌人受到" + phys("e_dmg", "e_ad") + hp("e_hp") + O + "物理伤害" + E +
                  "并减速" + A + "{e_slow}%" + E + "，持续" + A + "{e_slow_t}秒" + E + "。雷槌回手前原地等待，接住时获得" + S + "{e_sh}" + E +
                  " + " + ADi + S + "{e_sh_ad}%" + E + S + "护盾" + E + A + "{e_sh_t}秒" + E + "。",
        "ult": "雷槌立即觉醒" + A + "{r_awake}秒" + E + "，蓄力" + A + "{r_go}秒" + E + "（不受控制，受到的伤害降低" + A + "{r_dr}%" + E +
               "）后砸下：前方的敌人受到" + phys("r_dmg", "r_ad") + hp("r_hp") + O + "物理伤害" + E + "并" + R + "击飞{r_up}秒" + E +
               "。",
        "names": ("雷神之锤", "回旋雷槌", "觉醒雷槌"),
    },
    "zh-hant": {
        "name": "索爾",
        "attack": "雷槌重擊，造成" + AD + O + "物理傷害" + E + "。" + O + "雷槌覺醒" + E + "：每施放" + A + "{p_n}次" + E +
                  "技能，雷槌覺醒" + A + "{p_t}秒" + E + "：普攻再造成" + M + "{p_dmg}" + E + hp("p_hp", M) + M + "魔法傷害" +
                  E + "，雷神之錘改為" + R + "暈眩{q_stun}秒" + E + "。",
        "skill": "舉錘砸地，" + A + "{q_hit}秒" + E + "後雷電在前方炸開：敵人受到" + phys("q_dmg", "q_ad") + hp("q_hp") + O +
                 "物理傷害" + E + "並" + R + "暈眩{q_stun0}秒" + E + "（覺醒時" + R + "{q_stun}秒" + E + "）。",
        "skill2": "朝目標方向擲出雷槌，雷槌飛回手中，來回穿過的敵人受到" + phys("e_dmg", "e_ad") + hp("e_hp") + O + "物理傷害" + E +
                  "並緩速" + A + "{e_slow}%" + E + "，持續" + A + "{e_slow_t}秒" + E + "。雷槌回手前原地等待，接住時獲得" + S + "{e_sh}" + E +
                  " + " + ADi + S + "{e_sh_ad}%" + E + S + "護盾" + E + A + "{e_sh_t}秒" + E + "。",
        "ult": "雷槌立即覺醒" + A + "{r_awake}秒" + E + "，蓄力" + A + "{r_go}秒" + E + "（不受控制，受到的傷害降低" + A + "{r_dr}%" + E +
               "）後砸下：前方的敵人受到" + phys("r_dmg", "r_ad") + hp("r_hp") + O + "物理傷害" + E + "並" + R + "擊飛{r_up}秒" + E +
               "。",
        "names": ("雷神之錘", "迴旋雷槌", "覺醒雷槌"),
    },
    "en": {
        "name": "Thor",
        "attack": "Strikes with Mjolnir for " + AD + " " + O + "physical damage" + E + ". " + O + "Mjolnir Awakening" + E +
                  ": every " + A + "{p_nth}" + E + " skill cast awakens Mjolnir for " + A + "{p_t}s" + E + ": his attacks add " +
                  M + "{p_dmg}" + E + hp("p_hp", M) + " " + M + "magic damage" + E + " and Thor's Hammer " + R +
                  "stuns for {q_stun}s" + E + ".",
        "skill": "Brings the hammer down: after " + A + "{q_hit}s" + E + " lightning bursts through the ground ahead, dealing " +
                 phys("q_dmg", "q_ad") + hp("q_hp") + " " + O + "physical damage" + E + " and " + R + "stunning for {q_stun0}s" +
                 E + " (" + R + "{q_stun}s" + E + " awakened).",
        "skill2": "Throws Mjolnir toward the target and it flies back to his hand, hitting every enemy it passes both ways "
                  "for " + phys("e_dmg", "e_ad") + hp("e_hp") + " " + O + "physical damage" + E + " and slowing by " + A +
                  "{e_slow}%" + E + " for " + A + "{e_slow_t}s" + E + ". He waits empty-handed until it returns; the catch "
                  "grants a " + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E + " " + S + "shield" + E + " for " + A +
                  "{e_sh_t}s" + E + ".",
        "ult": "Awakens Mjolnir at once for " + A + "{r_awake}s" + E + ", gathers himself for " + A + "{r_go}s" + E +
               " (unstoppable, taking " + A + "{r_dr}%" + E + " less damage), then smashes the ground ahead: enemies take " +
               phys("r_dmg", "r_ad") + hp("r_hp") + " " + O + "physical damage" + E + " and are " + R +
               "knocked up for {r_up}s" + E + ".",
        "names": ("Thor's Hammer", "Returning Mjolnir", "Awakened Thunder Hammer"),
    },
    "ko": {
        "name": "토르",
        "attack": "묠니르로 내리쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "묠니르 각성" + E + ": 스킬을 " + A + "{p_n}번" + E +
                  " 쓸 때마다 묠니르가 " + A + "{p_t}초" + E + " 각성: 기본 공격에 " + M + "{p_dmg}" + E + hp("p_hp", M) + " " + M +
                  "마법 피해" + E + " 추가, 토르 해머 " + R + "기절 {q_stun}초" + E + ".",
        "skill": "망치를 내리쳐 " + A + "{q_hit}초" + E + " 뒤 번개가 앞쪽 땅에서 터진다: 적에게 " + phys("q_dmg", "q_ad") + hp("q_hp") +
                 " " + O + "물리 피해" + E + "와 " + R + "{q_stun0}초 기절" + E + "(각성 시 " + R + "{q_stun}초" + E + ").",
        "skill2": "대상 방향으로 묠니르를 던지면 손으로 돌아온다: 오가며 지나친 적에게 " + phys("e_dmg", "e_ad") + hp("e_hp") + " " + O +
                  "물리 피해" + E + "와 " + A + "{e_slow_t}초" + E + " 동안 " + A + "{e_slow}%" + E + " 둔화. 돌아올 때까지 제자리에서 "
                  "기다리고, 받아내면 " + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E + " " + S + "보호막" + E + "(" + A +
                  "{e_sh_t}초" + E + ").",
        "ult": "묠니르가 즉시 " + A + "{r_awake}초" + E + " 각성하고 " + A + "{r_go}초" + E + " 동안 힘을 모은 뒤(군중 제어 면역, 받는 "
               "피해 " + A + "{r_dr}%" + E + " 감소) 앞쪽을 내리친다: 적에게 " + phys("r_dmg", "r_ad") + hp("r_hp") + " " + O +
               "물리 피해" + E + "와 " + R + "{r_up}초 에어본" + E + ".",
        "names": ("토르 해머", "돌아오는 묠니르", "각성 묠니르"),
    },
    "ja": {
        "name": "トール",
        "attack": "雷槌の一撃で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ミョルニル覚醒" + E + "：スキルを" + A + "{p_n}回" + E +
                  "使うごとにミョルニルが" + A + "{p_t}秒" + E + "覚醒：通常攻撃に" + M + "{p_dmg}" + E + hp("p_hp", M) + "の" + M +
                  "魔法ダメージ" + E + "を追加、トールハンマーは" + R + "{q_stun}秒のスタン" + E + "。",
        "skill": "槌を振り下ろし、" + A + "{q_hit}秒" + E + "後に前方で雷が炸裂：敵に" + phys("q_dmg", "q_ad") + hp("q_hp") + "の" + O +
                 "物理ダメージ" + E + "と" + R + "{q_stun0}秒のスタン" + E + "（覚醒時" + R + "{q_stun}秒" + E + "）。",
        "skill2": "目標の方向へミョルニルを投げ、手元へ戻ってくる：往復で通った敵に" + phys("e_dmg", "e_ad") + hp("e_hp") + "の" + O +
                  "物理ダメージ" + E + "と" + A + "{e_slow_t}秒" + E + "間" + A + "{e_slow}%" + E + "のスロウ。戻るまでその場で待ち、"
                  "受け止めると" + S + "{e_sh}" + E + " + " + ADi + S + "{e_sh_ad}%" + E + "の" + S + "シールド" + E + "（" + A +
                  "{e_sh_t}秒" + E + "）。",
        "ult": "ミョルニルが即座に" + A + "{r_awake}秒" + E + "覚醒、" + A + "{r_go}秒" + E + "力を溜め（行動妨害無効、被ダメージ" + A +
               "{r_dr}%" + E + "軽減）、前方を叩き潰す：敵に" + phys("r_dmg", "r_ad") + hp("r_hp") + "の" + O + "物理ダメージ" + E +
               "と" + R + "{r_up}秒のノックアップ" + E + "。",
        "names": ("トールハンマー", "回旋雷槌", "覚醒雷槌"),
    },
}

# sound event -> [(clip, volume, delay)]: every event the kit plays (build_thor's sfx / tsfx) and ragnarok.dll's
SOUNDS = {
    f"{ID}_a": [(SFX + "attack_swing_2", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "attack_hit_1", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "skill_charge", 0.5, 0.0)],
    f"{ID}_q_slam": [(SFX + "skill_slam", 0.6, 0.0)],
    f"{ID}_q_hit": [(SFX + "attack_hit_3", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "skill2_throw", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "attack_hit_2", 0.4, 0.0)],
    f"{ID}_e_turn": [(SFX + "skill2_return", 0.5, 0.0)],
    f"{ID}_e_catch": [(SFX + "skill2_catch", 0.55, 0.0)],
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
    v = {k: p[k] for k in ("p_n", "p_dmg", "p_hp", "q_dmg", "q_ad", "q_hp", "e_dmg", "e_ad", "e_hp", "e_slow", "e_sh",
                           "e_sh_ad", "r_dmg", "r_ad", "r_hp", "r_dr")}
    v["p_nth"] = NTH[p["p_n"]]
    for k in ("p_t", "q_hit", "q_stun", "q_stun0", "e_slow_t", "e_sh_t", "r_awake", "r_go", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "thor", "tools/kit/seed_thor_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
