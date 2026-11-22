"""湿婆的文本（五种语言）、sound_info 和 champion_view，数字取自 build_shiva.P。

    python tools/kit/setup_shiva.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_shiva（说明和技能名）、sound/sfx/ragnarok_shiva_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：湿婆 / 濕婆 / Shiva / シヴァ / 시바；技能名：四臂连击、舞步、轮回舞踊（终末的女武神里的 Tandava Karma），被动「节奏」写在普攻
说明里；图标照 Codex 的交付（assets/source/shiva/runtime/icons：fourarms、dance、tandava；rhythm 那张第三只眼是被动，不装）。
声音：Codex 的交付（shiva_packs/outputs/shiva_assets_done.zip）：14 条原创音效（拳风、命中、连击上下段、舞步、点燃的起势和点燃、
火拳、火焰命中、火步、高踢的抬腿、出腿、命中、倒地）和六句官方日语原声（铃木达央）。音频不进仓库，
tools/kit/seed_shiva_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_shiva import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 103 格 = 31 个游戏像素、往前 2 格 = 1；
# 百科中心照小次郎、波塞冬（1 倍待机的实心顶上方 22 格左右）：实心顶 -33（举起的手臂）-> -10；选人卡用默认的 -12
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 1, "y": -37}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "湿婆",
        "attack": "四臂一扫，造成" + AD + O + "物理伤害" + E + "；轮回舞踊里是火鞭，" + ADi + O + "{h_atk_all}%" + E + "。" + O + "节奏" + E +
                  "：每放一个技能记一拍（最多" + A + "{p_max}拍" + E + "），每拍攻击力" + A + "+{p_atk}%" + E + "、攻速" + A + "+{p_as}%" +
                  E + "；" + A + "{p_t}秒" + E + "没再放技能就散。",
        "skill": "四臂连击两下：前方扇形的敌人受到" + phys("q1_dmg", "q1_ad") + "、" + phys("q2_dmg", "q2_ad") + O + "物理伤害" + E +
                 "，第二下" + R + "减速{q_slow}%" + E + "；轮回舞踊里伤害" + A + "{h_mul}%" + E + "。",
        "skill2": "踏着舞步冲到目标身上，落脚时身边的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "减速{e_slow}%" +
                  E + "；轮回舞踊里是火步，伤害" + A + "{h_mul}%" + E + "。",
        "ult": "点燃心脏（不受控制、受到的伤害降低" + A + "{r_dr}%" + E + "），" + A + "{r_t}秒" + E + "轮回舞踊：攻击力" + A + "+{r_atk}%" +
               E + "、攻速" + A + "+{r_as}%" + E + "、移速" + A + "+{r_ms}%" + E + "；结束时一记高踢，前方扇形的敌人受到" +
               phys("r_end_dmg", "r_end_ad") + O + "物理伤害" + E + "并被" + R + "击飞" + E + "。",
        "names": ("四臂连击", "舞步", "轮回舞踊"),
    },
    "zh-hant": {
        "name": "濕婆",
        "attack": "四臂一掃，造成" + AD + O + "物理傷害" + E + "；輪迴舞踊裡是火鞭，" + ADi + O + "{h_atk_all}%" + E + "。" + O + "節奏" + E +
                  "：每放一個技能記一拍（最多" + A + "{p_max}拍" + E + "），每拍攻擊力" + A + "+{p_atk}%" + E + "、攻速" + A + "+{p_as}%" +
                  E + "；" + A + "{p_t}秒" + E + "沒再放技能就散。",
        "skill": "四臂連擊兩下：前方扇形的敵人受到" + phys("q1_dmg", "q1_ad") + "、" + phys("q2_dmg", "q2_ad") + O + "物理傷害" + E +
                 "，第二下" + R + "減速{q_slow}%" + E + "；輪迴舞踊裡傷害" + A + "{h_mul}%" + E + "。",
        "skill2": "踏著舞步衝到目標身上，落腳時身邊的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "減速{e_slow}%" +
                  E + "；輪迴舞踊裡是火步，傷害" + A + "{h_mul}%" + E + "。",
        "ult": "點燃心臟（不受控制、受到的傷害降低" + A + "{r_dr}%" + E + "），" + A + "{r_t}秒" + E + "輪迴舞踊：攻擊力" + A + "+{r_atk}%" +
               E + "、攻速" + A + "+{r_as}%" + E + "、移速" + A + "+{r_ms}%" + E + "；結束時一記高踢，前方扇形的敵人受到" +
               phys("r_end_dmg", "r_end_ad") + O + "物理傷害" + E + "並被" + R + "擊飛" + E + "。",
        "names": ("四臂連擊", "舞步", "輪迴舞踊"),
    },
    "en": {
        "name": "Shiva",
        "attack": "A four-armed sweep for " + AD + " " + O + "physical damage" + E + "; in Tandava Karma a whip of fire for " + ADi + O +
                  "{h_atk_all}%" + E + ". " + O + "Rhythm" + E + ": every skill is a beat (up to " + A + "{p_max}" + E + "), each " + A +
                  "+{p_atk}%" + E + " attack and " + A + "+{p_as}%" + E + " attack speed; the beats fade after " + A + "{p_t}s" + E +
                  " without a skill.",
        "skill": "Two strikes of his four arms: enemies in a cone take " + phys("q1_dmg", "q1_ad") + " and " + phys("q2_dmg", "q2_ad") +
                 " " + O + "physical damage" + E + ", the second " + R + "slowing {q_slow}%" + E + "; in Tandava Karma " + A +
                 "{h_mul}%" + E + " damage.",
        "skill2": "Dances onto the target; where he lands, enemies around him take " + phys("e_dmg", "e_ad") + " " + O +
                  "physical damage" + E + " and are " + R + "slowed {e_slow}%" + E + "; in Tandava Karma a step of fire for " + A +
                  "{h_mul}%" + E + " damage.",
        "ult": "Sets his heart alight (unstoppable, " + A + "{r_dr}%" + E + " less damage): Tandava Karma for " + A + "{r_t}s" + E +
               ", " + A + "+{r_atk}%" + E + " attack, " + A + "+{r_as}%" + E + " attack speed, " + A + "+{r_ms}%" + E +
               " move speed; at its end a high kick for " + phys("r_end_dmg", "r_end_ad") + " " + O + "physical damage" + E +
               " in a cone, " + R + "knocking up" + E + ".",
        "names": ("Four-Armed Flurry", "Dance Step", "Tandava Karma"),
    },
    "ko": {
        "name": "시바",
        "attack": "네 팔로 휩쓸어 " + AD + " " + O + "물리 피해" + E + ", 윤회무용 중에는 불의 채찍으로 " + ADi + O + "{h_atk_all}%" + E +
                  ". " + O + "리듬" + E + ": 스킬마다 한 박자(최대 " + A + "{p_max}박" + E + "), 박자마다 공격력 " + A + "+{p_atk}%" + E +
                  ", 공격 속도 " + A + "+{p_as}%" + E + ". " + A + "{p_t}초" + E + " 동안 스킬이 없으면 흩어짐.",
        "skill": "네 팔 연타 두 번: 앞쪽 부채꼴의 적에게 " + phys("q1_dmg", "q1_ad") + ", " + phys("q2_dmg", "q2_ad") + " " + O +
                 "물리 피해" + E + ", 두 번째는 " + R + "{q_slow}% 둔화" + E + ". 윤회무용 중 피해 " + A + "{h_mul}%" + E + ".",
        "skill2": "춤사위로 대상에게 돌진해 착지할 때 주변 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_slow}% 둔화" + E + ". 윤회무용 중에는 불꽃 걸음, 피해 " + A + "{h_mul}%" + E + ".",
        "ult": "심장에 불을 붙여(저지 불가, 받는 피해 " + A + "{r_dr}%" + E + " 감소) " + A + "{r_t}초" + E + " 동안 윤회무용: 공격력 " + A +
               "+{r_atk}%" + E + ", 공격 속도 " + A + "+{r_as}%" + E + ", 이동 속도 " + A + "+{r_ms}%" + E + ". 끝날 때 하이킥으로 앞쪽 "
               "부채꼴에 " + phys("r_end_dmg", "r_end_ad") + " " + O + "물리 피해" + E + "와 " + R + "에어본" + E + ".",
        "names": ("네 팔 연타", "춤사위", "윤회무용"),
    },
    "ja": {
        "name": "シヴァ",
        "attack": "四本の腕で薙ぎ払い" + AD + "の" + O + "物理ダメージ" + E + "、輪廻舞踊中は炎の鞭で" + ADi + O + "{h_atk_all}%" + E + "。" +
                  O + "リズム" + E + "：スキルごとに一拍（最大" + A + "{p_max}拍" + E + "）、一拍ごとに攻撃力" + A + "+{p_atk}%" + E +
                  "・攻撃速度" + A + "+{p_as}%" + E + "。" + A + "{p_t}秒" + E + "スキルがないと消える。",
        "skill": "四臂の二連撃：前方扇形の敵に" + phys("q1_dmg", "q1_ad") + "、" + phys("q2_dmg", "q2_ad") + "の" + O + "物理ダメージ" + E +
                 "、二撃目は" + R + "{q_slow}%スロウ" + E + "。輪廻舞踊中はダメージ" + A + "{h_mul}%" + E + "。",
        "skill2": "舞いながら対象に飛び込み、着地で周囲の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_slow}%スロウ" + E + "。輪廻舞踊中は炎の舞、ダメージ" + A + "{h_mul}%" + E + "。",
        "ult": "心臓に火を灯す（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）。" + A + "{r_t}秒" + E + "輪廻舞踊：攻撃力" + A +
               "+{r_atk}%" + E + "、攻撃速度" + A + "+{r_as}%" + E + "、移動速度" + A + "+{r_ms}%" + E + "。終わりに上段蹴りで前方扇形に" +
               phys("r_end_dmg", "r_end_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "打ち上げ" + E + "。",
        "names": ("四臂連撃", "舞踏", "輪廻舞踊"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_shiva 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "arm", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "arm_hit", 0.45, 0.0)],
    f"{ID}_ha": [(SFX + "fire_punch", 0.45, 0.0)],
    f"{ID}_ha_hit": [(SFX + "fire_hit", 0.45, 0.0)],
    f"{ID}_q1": [(SFX + "combo_up", 0.5, 0.0)],
    f"{ID}_q2": [(SFX + "combo_low", 0.5, 0.0)],
    f"{ID}_hq2": [(SFX + "fire_punch", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "step", 0.5, 0.0)],
    f"{ID}_he": [(SFX + "firestep", 0.55, 0.0)],
    f"{ID}_r1": [(SFX + "ignite_prep", 0.55, 0.0)],
    f"{ID}_r2": [(SFX + "ignite", 0.6, 0.0)],
    # 形态结束的高踢：抬腿在 h_ult 第 3 帧（0.258 秒），出腿在第 5 帧（0.423 秒）
    f"{ID}_r_end": [(SFX + "kick_load", 0.5, 0.258), (SFX + "kick", 0.55, 0.423)],
    f"{ID}_r_end_hit": [(SFX + "finish", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/shiva.rs）：死的时候身子着地（Codex 的 cues：0.846 秒，两种形态一样）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("entry", "excite", "challenge", "rally", "festival", "dance")},
}


def values(p):
    v = {k: p[k] for k in ("p_max", "p_atk", "p_as", "q1_dmg", "q1_ad", "q2_dmg", "q2_ad", "q_slow", "h_mul", "e_dmg", "e_ad",
                           "e_slow", "r_dr", "r_atk", "r_as", "r_ms", "r_end_dmg", "r_end_ad")}
    v["h_atk_all"] = 100 + p["h_atk"]
    for k in ("p_t", "r_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "shiva", "tools/kit/seed_shiva_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
