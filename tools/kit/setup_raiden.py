"""雷电为右卫门的文本（五种语言）、sound_info 和 champion_view，数字取自 build_raiden.P。

    python tools/kit/setup_raiden.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_raiden（说明和技能名）、sound/sfx/ragnarok_raiden_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：雷电为右卫门 / 雷電為右衛門 / Raiden Tameemon / 雷電為右衛門 / 라이덴 타메에몬；技能名照相扑和终末的女武神：连掌（张手连出）、
四股、八咫乌，被动「肌肉解放」写在普攻说明里；图标照 Codex 的交付（assets/source/raiden/runtime/icons：palm、shiko、yatagarasu；
volund 那张是被动，不装）。
声音：Codex 的交付（raiden_packs/outputs/raiden_assets_done.zip）：13 条原创音效（掌风、命中、连掌两下和命中、四股起足、
落脚、余震、八咫乌的蓄劲、出掌、命中、肌肉解放、倒地）和六句官方日语原声（木村昴）。音频不进仓库，
tools/kit/seed_raiden_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_raiden import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 101 格 = 31 个游戏像素、往前 14 格 = 4；
# 百科中心照小次郎、波塞冬（1 倍待机的实心顶上方 22 格左右）：实心顶 -35 -> -12；选人卡用默认的 -12
VIEW = {"face": {"x": 4, "y": -31}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "雷电为右卫门",
        "attack": "一掌推出，造成" + AD + O + "物理伤害" + E + "。" + O + "肌肉解放" + E + "：每条命第一次放八咫乌前先放开压了一辈子的肌肉"
                  "（" + A + "{rel_t}秒" + E + "，不受控制、受到的伤害降低" + A + "{rel_dr}%" + E + "），之后攻击力" + A + "+{p_atk}%" + E +
                  "、护甲和魔抗" + A + "+{p_res}" + E + "、攻速" + A + "+{p_as}%" + E + "。",
        "skill": "连出两掌：第一掌造成" + phys("q1_dmg", "q1_ad") + O + "物理伤害" + E + "，第二掌造成" + phys("q2_dmg", "q2_ad") + O +
                 "物理伤害" + E + "，打得人" + R + "踉跄{q_stun}秒" + E + "并" + R + "减速{q_slow}%" + E + "。",
        "skill2": "抬脚跺地：身边的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "眩晕{e_stun}秒" + E +
                  "；地面余震让更大一圈的敌人" + R + "减速{e_slow}%" + E + "。",
        "ult": "蓄劲（不受控制、受到的伤害降低" + A + "{r_dr}%" + E + "）后一掌推出：前方扇形的敌人受到" + phys("r_dmg", "r_ad") + O +
               "物理伤害" + E + "并被" + R + "冲击波震飞{r_up}秒" + E + "。",
        "names": ("连掌", "四股", "八咫乌"),
    },
    "zh-hant": {
        "name": "雷電為右衛門",
        "attack": "一掌推出，造成" + AD + O + "物理傷害" + E + "。" + O + "肌肉解放" + E + "：每條命第一次放八咫烏前先放開壓了一輩子的肌肉"
                  "（" + A + "{rel_t}秒" + E + "，不受控制、受到的傷害降低" + A + "{rel_dr}%" + E + "），之後攻擊力" + A + "+{p_atk}%" + E +
                  "、護甲和魔抗" + A + "+{p_res}" + E + "、攻速" + A + "+{p_as}%" + E + "。",
        "skill": "連出兩掌：第一掌造成" + phys("q1_dmg", "q1_ad") + O + "物理傷害" + E + "，第二掌造成" + phys("q2_dmg", "q2_ad") + O +
                 "物理傷害" + E + "，打得人" + R + "踉蹌{q_stun}秒" + E + "並" + R + "減速{q_slow}%" + E + "。",
        "skill2": "抬腳跺地：身邊的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E +
                  "；地面餘震讓更大一圈的敵人" + R + "減速{e_slow}%" + E + "。",
        "ult": "蓄勁（不受控制、受到的傷害降低" + A + "{r_dr}%" + E + "）後一掌推出：前方扇形的敵人受到" + phys("r_dmg", "r_ad") + O +
               "物理傷害" + E + "並被" + R + "衝擊波震飛{r_up}秒" + E + "。",
        "names": ("連掌", "四股", "八咫烏"),
    },
    "en": {
        "name": "Raiden Tameemon",
        "attack": "An open-hand thrust for " + AD + " " + O + "physical damage" + E + ". " + O + "Muscle Release" + E + ": the first "
                  "Yatagarasu of each life begins by unbinding the muscles he held back all his life (" + A + "{rel_t}s" + E +
                  ", unstoppable, " + A + "{rel_dr}%" + E + " less damage); for the rest of the life " + A + "+{p_atk}%" + E +
                  " attack, " + A + "+{p_res}" + E + " armour and magic resistance, " + A + "+{p_as}%" + E + " attack speed.",
        "skill": "Two palm thrusts: the first for " + phys("q1_dmg", "q1_ad") + " " + O + "physical damage" + E + ", the second for " +
                 phys("q2_dmg", "q2_ad") + " " + O + "physical damage" + E + " that " + R + "staggers for {q_stun}s" + E +
                 " and " + R + "slows {q_slow}%" + E + ".",
        "skill2": "Lifts a leg and stamps: enemies around him take " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E +
                  " and are " + R + "stunned for {e_stun}s" + E + "; the aftershock " + R + "slows {e_slow}%" + E +
                  " a wider ring.",
        "ult": "Gathers his strength (unstoppable, " + A + "{r_dr}%" + E + " less damage) and thrusts one palm: enemies in a cone "
               "take " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + " and are " + R + "knocked up for {r_up}s" + E +
               " by the shockwave.",
        "names": ("Tsuppari", "Shiko", "Yatagarasu"),
    },
    "ko": {
        "name": "라이덴 타메에몬",
        "attack": "손바닥으로 밀어 " + AD + " " + O + "물리 피해" + E + ". " + O + "근육 해방" + E + ": 목숨마다 첫 야타가라스 전에 평생 "
                  "억눌러 온 근육을 풀고(" + A + "{rel_t}초" + E + ", 저지 불가, 받는 피해 " + A + "{rel_dr}%" + E + " 감소) 그 뒤로 "
                  "공격력 " + A + "+{p_atk}%" + E + ", 방어력과 마법 저항력 " + A + "+{p_res}" + E + ", 공격 속도 " + A + "+{p_as}%" + E + ".",
        "skill": "두 번 밀어치기: 첫 번째 " + phys("q1_dmg", "q1_ad") + " " + O + "물리 피해" + E + ", 두 번째 " + phys("q2_dmg", "q2_ad") +
                 " " + O + "물리 피해" + E + ", " + R + "{q_stun}초 기절" + E + "과 " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "다리를 들어 내리찍어 주변 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R + "{e_stun}초 기절" +
                  E + ", 여진이 더 넓은 범위를 " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "힘을 모은 뒤(저지 불가, 받는 피해 " + A + "{r_dr}%" + E + " 감소) 손바닥을 내질러 앞쪽 부채꼴의 적에게 " +
               phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_up}초 에어본" + E + ".",
        "names": ("연속 장타", "시코", "야타가라스"),
    },
    "ja": {
        "name": "雷電為右衛門",
        "attack": "張り手で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "筋肉解放" + E + "：命ごとに最初の八咫烏の前に、一生抑えてきた"
                  "筋肉を解き放つ（" + A + "{rel_t}秒" + E + "、行動妨害無効、被ダメージ" + A + "{rel_dr}%" + E + "軽減）。以後攻撃力" + A +
                  "+{p_atk}%" + E + "、物防・魔防" + A + "+{p_res}" + E + "、攻撃速度" + A + "+{p_as}%" + E + "。",
        "skill": "二連の突っ張り：一発目" + phys("q1_dmg", "q1_ad") + "、二発目" + phys("q2_dmg", "q2_ad") + "の" + O + "物理ダメージ" + E +
                 "、よろめかせ" + R + "{q_stun}秒スタン" + E + "と" + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "足を上げて四股を踏み、周囲の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{e_stun}秒スタン" +
                  E + "。余震でより広い範囲に" + R + "{e_slow}%スロウ" + E + "。",
        "ult": "力を溜め（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）掌を突き出す：前方扇形の敵に" + phys("r_dmg", "r_ad") + "の" +
               O + "物理ダメージ" + E + "と" + R + "衝撃波で{r_up}秒打ち上げ" + E + "。",
        "names": ("突っ張り", "四股", "八咫烏"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_raiden 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "palm_sweep", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "palm_hit", 0.45, 0.0)],
    f"{ID}_q1": [(SFX + "chain_first", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "palm_hit", 0.45, 0.0)],
    f"{ID}_q2": [(SFX + "chain_second", 0.5, 0.0)],
    f"{ID}_q_hit2": [(SFX + "chain_hit", 0.5, 0.0)],
    f"{ID}_e_lift": [(SFX + "foot_lift", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "shiko", 0.6, 0.0)],
    f"{ID}_e2": [(SFX + "ground", 0.55, 0.0)],
    f"{ID}_r1": [(SFX + "tension", 0.55, 0.0)],
    f"{ID}_r2": [(SFX + "yatagarasu", 0.65, 0.0)],
    f"{ID}_r_hit": [(SFX + "yatagarasu_hit", 0.6, 0.0)],
    f"{ID}_rel": [(SFX + "release", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/raiden.rs）：死的时候身子着地（Codex 的 cues：0.893 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.893)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("awake", "dream", "turn", "arena", "battle", "serious")},
}


def values(p):
    v = {k: p[k] for k in ("rel_dr", "p_atk", "p_res", "p_as", "q1_dmg", "q1_ad", "q2_dmg", "q2_ad", "q_slow", "e_dmg",
                           "e_ad", "e_slow", "r_dr", "r_dmg", "r_ad")}
    v["rel_t"] = secs(p["rel_dur"])
    for k in ("e_stun", "q_stun", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "raiden", "tools/kit/seed_raiden_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
