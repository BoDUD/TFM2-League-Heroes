"""Zeus's text (5 languages), sound_info files and champion_view, numbers from build_zeus.P.

    python tools/kit/setup_zeus.py [--check]

Writes his keys in ragnarok/ (tools/kit/ragnarok_pack.py writes them and the pack's own files: mod.mod_info naming
every hero, the merges of mod.override_info): text/champion.i18n (ragnarok_zeus in every language, description +
skill_name), sound/sfx/ragnarok_zeus_*.sound_info and their override entries, style/champion_view (face, centre,
banpick_center). --check only prints each text's shown length against TOOLTIP_MAX and the texts themselves.

Names: Record of Ragnarok's - 宙斯 / 宙斯 / Zeus / ゼウス / 제우스; Barrage (连拳), The Fist That Transcends Time
(超越时间之拳, the manga's 時を超える拳), Adamas (阿陀磨须, the manga's 阿陀磨須) and Muscle Expansion (肌肉膨胀) name
Codex's four icons (assets/source/zeus/).
Sounds: Codex's delivery (assets/source/zeus/README.md): 16 original SFX (three jab winds and hits, the barrage's wind
and hit, the time punch's charge / release / hit, the expansion, the compression, the release, the revert, the fall)
and six lines of the official Japanese voice (Wataru Takagi, the official countdown; the promotional slogan stays out
of the game, as Codex asked). Clips are git-ignored (tools/kit/seed_zeus_audio.py copies them from the delivery into
ragnarok/sound/sfx/); package_mod moves them to sound/bgm/ at install.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zeus import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view (game px from his soles' point, up negative), measured 2026-11-21 on the old man's idle (the body the
# cards show): eyes under the long white brows, 40 rows over the soles = 24 game px, 9 px forward = 5; the encyclopedia
# centre by bp_card_audit's rule (-6, the old man is short); the ban/pick card needs no value of its own (his top is
# 20 px over the frame centre, the rule starts at 28): base's -12
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 6, "y": -29}, "center": {"x": 0, "y": -6}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "宙斯",
        "attack": "快拳，造成" + AD + O + "物理伤害" + E + "。" + O + "肌肉膨胀" + E + "：老人状态打出" + A + "{p_n}拳" + E + "后，下一拳改为膨胀（" +
                  A + "{x_dur}秒" + E + "，不受控制），完成时震伤周围敌人" + phys("x_dmg", "x_ad") + O + "物理伤害" + E + "、减速" + A +
                  "{x_slow}%" + E + "；膨胀后攻击力+" + A + "{m_atk}%" + E + "、护甲和魔抗+" + A + "{m_def}%" + E + "。",
        "skill": "连打两拳，每拳" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "；膨胀时第二拳减速" + A + "{q_slow}%" + E + "，持续" + A +
                 "{q_slow_t}秒" + E + "，阿陀磨须时第二拳" + R + "眩晕{q_stun}秒" + E + "。",
        "skill2": "拳头快过时间，出拳之前伤害就已打到：" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "眩晕{e_stun}秒" + E +
                  "（阿陀磨须时" + R + "{e_stun_ad}秒" + E + "）。",
        "ult": "把膨胀的肌肉压缩" + A + "{r_go}秒" + E + "（老人状态先膨胀；不受控制，受到的伤害降低" + A + "{r_dr}%" + E + "），随后震飞周围"
               "敌人：" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并" + R + "击飞{r_up}秒" + E + "，以阿陀磨须作战" + A + "{r_t}秒" + E +
               "：攻击力+" + A + "{r_atk}%" + E + "、双抗+" + A + "{r_def}%" + E + "、攻速+" + A + "{r_as}%" + E + "、吸血" + A +
               "{r_vamp}%" + E + "。结束后变回老人。",
        "names": ("连拳", "超越时间之拳", "阿陀磨须"),
    },
    "zh-hant": {
        "name": "宙斯",
        "attack": "快拳，造成" + AD + O + "物理傷害" + E + "。" + O + "肌肉膨脹" + E + "：老人狀態打出" + A + "{p_n}拳" + E + "後，下一拳改為膨脹（" +
                  A + "{x_dur}秒" + E + "，不受控制），完成時震傷周圍敵人" + phys("x_dmg", "x_ad") + O + "物理傷害" + E + "、緩速" + A +
                  "{x_slow}%" + E + "；膨脹後攻擊力+" + A + "{m_atk}%" + E + "、護甲和魔抗+" + A + "{m_def}%" + E + "。",
        "skill": "連打兩拳，每拳" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "；膨脹時第二拳緩速" + A + "{q_slow}%" + E + "，持續" + A +
                 "{q_slow_t}秒" + E + "，阿陀磨須時第二拳" + R + "暈眩{q_stun}秒" + E + "。",
        "skill2": "拳頭快過時間，出拳之前傷害就已打到：" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E +
                  "（阿陀磨須時" + R + "{e_stun_ad}秒" + E + "）。",
        "ult": "把膨脹的肌肉壓縮" + A + "{r_go}秒" + E + "（老人狀態先膨脹；不受控制，受到的傷害降低" + A + "{r_dr}%" + E + "），隨後震飛周圍"
               "敵人：" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並" + R + "擊飛{r_up}秒" + E + "，以阿陀磨須作戰" + A + "{r_t}秒" + E +
               "：攻擊力+" + A + "{r_atk}%" + E + "、雙抗+" + A + "{r_def}%" + E + "、攻速+" + A + "{r_as}%" + E + "、吸血" + A +
               "{r_vamp}%" + E + "。結束後變回老人。",
        "names": ("連拳", "超越時間之拳", "阿陀磨須"),
    },
    "en": {
        "name": "Zeus",
        "attack": "A quick jab for " + AD + " " + O + "physical damage" + E + ". " + O + "Muscle Expansion" + E + ": after " + A +
                  "{p_n} punches" + E + " as the old man, his next one swells him up instead (" + A + "{x_dur}s" + E +
                  ", unstoppable), shaking nearby enemies for " + phys("x_dmg", "x_ad") + " " + O + "physical damage" + E +
                  " and slowing by " + A + "{x_slow}%" + E + "; swollen, he gains " + A + "{m_atk}%" + E + " attack and " + A +
                  "{m_def}%" + E + " armor and magic resistance.",
        "skill": "Two quick punches, each " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + "; swollen, the second "
                 "slows by " + A + "{q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ", as Adamas it " + R + "stuns for {q_stun}s" +
                 E + ".",
        "skill2": "A punch faster than time: the blow lands before he throws it, " + phys("e_dmg", "e_ad") + " " + O +
                  "physical damage" + E + " and a " + R + "{e_stun}s stun" + E + " (" + R + "{e_stun_ad}s" + E + " as Adamas).",
        "ult": "Presses his swollen muscles down for " + A + "{r_go}s" + E + " (the old man swells first; unstoppable, taking " +
               A + "{r_dr}%" + E + " less damage), then blasts nearby enemies for " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + ", " + R + "knocking them up for {r_up}s" + E + ", and fights as Adamas for " + A +
               "{r_t}s" + E + ": +" + A + "{r_atk}%" + E + " attack, +" + A + "{r_def}%" + E + " armor and magic resistance, +" + A +
               "{r_as}%" + E + " attack speed, " + A + "{r_vamp}%" + E + " lifesteal. Then he is old again.",
        "names": ("Barrage", "Fist That Transcends Time", "Adamas"),
    },
    "ko": {
        "name": "제우스",
        "attack": "빠른 잽으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "근육 팽창" + E + ": 노인 상태로 " + A + "{p_n}번" + E +
                  " 때리면 다음 주먹 대신 팽창(" + A + "{x_dur}초" + E + ", 군중 제어 면역)하고, 끝날 때 주변 적에게 " +
                  phys("x_dmg", "x_ad") + " " + O + "물리 피해" + E + "와 " + A + "{x_slow}%" + E + " 둔화; 팽창 후 공격력 +" + A +
                  "{m_atk}%" + E + ", 방어력·마법 저항력 +" + A + "{m_def}%" + E + ".",
        "skill": "두 번 연속 주먹, 각 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "; 팽창 상태면 두 번째 주먹이 " + A +
                 "{q_slow_t}초" + E + " 동안 " + A + "{q_slow}%" + E + " 둔화, 아다마스 상태면 " + R + "{q_stun}초 기절" + E + ".",
        "skill2": "시간보다 빠른 주먹: 주먹을 뻗기 전에 이미 맞는다. " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_stun}초 기절" + E + "(아다마스 " + R + "{e_stun_ad}초" + E + ").",
        "ult": "팽창한 근육을 " + A + "{r_go}초" + E + " 동안 압축(노인 상태면 먼저 팽창; 군중 제어 면역, 받는 피해 " + A + "{r_dr}%" + E +
               " 감소)한 뒤 주변 적을 날린다: " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_up}초 에어본" + E +
               ", " + A + "{r_t}초" + E + " 동안 아다마스: 공격력 +" + A + "{r_atk}%" + E + ", 방어·마저 +" + A + "{r_def}%" + E +
               ", 공격 속도 +" + A + "{r_as}%" + E + ", 생명력 흡수 " + A + "{r_vamp}%" + E + ". 끝나면 노인으로 돌아온다.",
        "names": ("연타", "시간을 넘어선 주먹", "아다마스"),
    },
    "ja": {
        "name": "ゼウス",
        "attack": "素早いジャブで" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "筋肉膨張" + E + "：老人の姿で" + A + "{p_n}発" + E +
                  "打つと次の一発の代わりに膨張（" + A + "{x_dur}秒" + E + "、行動妨害無効）、完了時に周囲の敵へ" + phys("x_dmg", "x_ad") +
                  "の" + O + "物理ダメージ" + E + "と" + A + "{x_slow}%" + E + "のスロウ。膨張後は攻撃力+" + A + "{m_atk}%" + E + "、防御と魔法防御+" +
                  A + "{m_def}%" + E + "。",
        "skill": "二連打、各" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "。膨張中は二発目が" + A + "{q_slow_t}秒" + E + "間" +
                 A + "{q_slow}%" + E + "のスロウ、阿陀磨須なら" + R + "{q_stun}秒のスタン" + E + "。",
        "skill2": "時を超える拳：拳を振るより先に当たっている。" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_stun}秒のスタン" + E + "（阿陀磨須なら" + R + "{e_stun_ad}秒" + E + "）。",
        "ult": "膨張した筋肉を" + A + "{r_go}秒" + E + "圧縮（老人なら先に膨張、行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）し、"
               "周囲の敵を吹き飛ばす：" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{r_up}秒のノックアップ" + E +
               "、" + A + "{r_t}秒" + E + "阿陀磨須で戦う：攻撃力+" + A + "{r_atk}%" + E + "、両防御+" + A + "{r_def}%" + E + "、攻撃速度+" +
               A + "{r_as}%" + E + "、吸血" + A + "{r_vamp}%" + E + "。終わると老人に戻る。",
        "names": ("連打", "時を超える拳", "阿陀磨須"),
    },
}

# sound event -> [(clip, volume, delay)]: every event the kit plays (build_zeus's sfx / tsfx) and ragnarok.dll's
SOUNDS = {
    f"{ID}_a": [(SFX + "jab_wind_2", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "jab_hit_1", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "barrage_wind", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "barrage_hit", 0.45, 0.0)],
    f"{ID}_e_charge": [(SFX + "time_charge", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "time_release", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "time_hit", 0.55, 0.0)],
    f"{ID}_x": [(SFX + "form_expand", 0.6, 0.0)],
    f"{ID}_x_burst": [(SFX + "form_release", 0.6, 0.0)],
    f"{ID}_r": [(SFX + "form_compress", 0.6, 0.0)],
    f"{ID}_r_burst": [(SFX + "form_release", 0.65, 0.0)],
    f"{ID}_v": [(SFX + "form_revert", 0.55, 0.0)],
    # ragnarok.dll (addons/ragnarok/src/zeus.rs): the fall when he dies (his death frames reach the ground on frame 6,
    # 0.66 s), the voice lines
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.66)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("greet", "eager", "fun", "taunt", "anticipation")},
}


def values(p):
    v = {k: p[k] for k in ("p_n", "x_dmg", "x_ad", "x_slow", "m_atk", "m_def", "q_dmg", "q_ad", "q_slow", "e_dmg", "e_ad",
                           "r_dr", "r_dmg", "r_ad", "r_atk", "r_def", "r_as", "r_vamp")}
    for k in ("x_dur", "q_slow_t", "q_stun", "e_stun", "e_stun_ad", "r_go", "r_up", "r_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "zeus", "tools/kit/seed_zeus_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
