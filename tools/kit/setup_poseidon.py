"""波塞冬的文本（五种语言）、sound_info 和 champion_view，数字取自 build_poseidon.P。

    python tools/kit/setup_poseidon.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_poseidon（说明和技能名）、sound/sfx/ragnarok_poseidon_*.sound_info 和它们的
覆盖项、style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：终末的女武神里的叫法，波塞冬 / 波塞頓 / Poseidon / ポセイドン / 포세이돈；技能名照 Codex 的交接
（assets/source/poseidon/README.md）：怒涛连刺、暴雨斜刺、四十昼夜的大洪水，被动神无须依赖写在普攻说明里。
声音：Codex 的交付：17 条原创音效（普攻三组戟风和命中、暗流、连刺、斜刺的升势 / 坠刺 / 命中、大洪水的蓄势 / 戟影 /
命中、落戟、倒地）和九句官方日语原声（樱井孝宏）。音频不进仓库，tools/kit/seed_poseidon_audio.py 从交付复制到
ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_poseidon import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 47 格 = 28 个游戏像素、往前 4 格 = 2；
# 站高 58 格 = 35 个游戏像素，百科中心按 bp_card_audit 的规矩是 -8；选人卡用默认的 -12
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 2, "y": -34}, "center": {"x": 0, "y": -19}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "波塞冬",
        "attack": "三叉戟水平突刺，造成" + AD + O + "物理伤害" + E + "。" + O + "神无须依赖" + E + "：身边没有友方英雄时，攻击力" + A +
                  "+{p_atk}%" + E + "，受到的伤害降低" + A + "{p_dr}%" + E + "。",
        "skill": "踏前一步，朝前方连刺" + A + "{q_n}次" + E + "，每次对前方扇形里的敌人造成" + phys("q_dmg", "q_ad") + O + "物理伤害" +
                 E + "。",
        "skill2": "高举三叉戟斜刺而下，目标脚下的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并被" + R + "眩晕{e_stun}秒" +
                  E + "。",
        "ult": "蓄势" + A + "{r_go}秒" + E + "（受到的伤害降低" + A + "{r_dr}%" + E + "），戟影如洪水般围住目标连刺" + A + "{r_n}轮" + E +
               "，每轮对周围的敌人造成" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "，第一轮" + R + "定身{r_root}秒" + E + "。",
        "names": ("怒涛连刺", "暴雨斜刺", "四十昼夜的大洪水"),
    },
    "zh-hant": {
        "name": "波塞頓",
        "attack": "三叉戟水平突刺，造成" + AD + O + "物理傷害" + E + "。" + O + "神無須依賴" + E + "：身邊沒有友方英雄時，攻擊力" + A +
                  "+{p_atk}%" + E + "，受到的傷害降低" + A + "{p_dr}%" + E + "。",
        "skill": "踏前一步，朝前方連刺" + A + "{q_n}次" + E + "，每次對前方扇形裡的敵人造成" + phys("q_dmg", "q_ad") + O + "物理傷害" +
                 E + "。",
        "skill2": "高舉三叉戟斜刺而下，目標腳下的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並被" + R + "暈眩{e_stun}秒" +
                  E + "。",
        "ult": "蓄勢" + A + "{r_go}秒" + E + "（受到的傷害降低" + A + "{r_dr}%" + E + "），戟影如洪水般圍住目標連刺" + A + "{r_n}輪" + E +
               "，每輪對周圍的敵人造成" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "，第一輪" + R + "定身{r_root}秒" + E + "。",
        "names": ("怒濤連刺", "暴雨斜刺", "四十晝夜的大洪水"),
    },
    "en": {
        "name": "Poseidon",
        "attack": "A level trident thrust for " + AD + " " + O + "physical damage" + E + ". " + O + "A God Needs No One" + E +
                  ": with no allied champion near him he gains " + A + "{p_atk}%" + E + " attack and takes " + A + "{p_dr}%" + E +
                  " less damage.",
        "skill": "Steps in and thrusts " + A + "{q_n} times" + E + ", each dealing " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + " to enemies in a cone ahead.",
        "skill2": "Raises the trident and drives it down at a slant: enemies at the target's feet take " +
                  phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + " and are " + R + "stunned for {e_stun}s" + E + ".",
        "ult": "Gathers himself for " + A + "{r_go}s" + E + " (taking " + A + "{r_dr}%" + E + " less damage), then a flood of "
               "trident images rings the target for " + A + "{r_n} rounds" + E + " of thrusts, each dealing " + phys("r_dmg", "r_ad") +
               " " + O + "physical damage" + E + " around it; the first " + R + "roots for {r_root}s" + E + ".",
        "names": ("Raging Wave Thrusts", "Downpour Thrust", "Flood of Forty Days and Nights"),
    },
    "ko": {
        "name": "포세이돈",
        "attack": "삼지창 수평 찌르기로 " + AD + " " + O + "물리 피해" + E + ". " + O + "신은 기대지 않는다" + E + ": 주변에 아군 챔피언이 "
                  "없으면 공격력 " + A + "+{p_atk}%" + E + ", 받는 피해 " + A + "{p_dr}%" + E + " 감소.",
        "skill": "한 걸음 내디디며 앞쪽으로 " + A + "{q_n}번" + E + " 연속으로 찔러, 매번 앞쪽 부채꼴의 적에게 " + phys("q_dmg", "q_ad") +
                 " " + O + "물리 피해" + E + ".",
        "skill2": "삼지창을 들어 비스듬히 내리찍어, 대상 발밑의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_stun}초 기절" + E + ".",
        "ult": A + "{r_go}초" + E + " 동안 힘을 모은 뒤(받는 피해 " + A + "{r_dr}%" + E + " 감소) 삼지창의 그림자가 홍수처럼 대상을 에워싸 " +
               A + "{r_n}번" + E + " 찌르며, 매번 주변의 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ", 첫 번째는 " +
               R + "{r_root}초 속박" + E + ".",
        "names": ("성난 파도 연속 찌르기", "폭우 내려찍기", "사십 주야의 대홍수"),
    },
    "ja": {
        "name": "ポセイドン",
        "attack": "三叉槍の水平突きで" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "神は何者にも頼らず" + E + "：近くに味方チャンピオンが"
                  "いないと攻撃力" + A + "+{p_atk}%" + E + "、被ダメージ" + A + "{p_dr}%" + E + "軽減。",
        "skill": "一歩踏み込み前方へ" + A + "{q_n}回" + E + "連続で突き、毎回前方扇形の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" +
                 E + "。",
        "skill2": "三叉槍を掲げ斜めに突き下ろし、対象の足元の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_stun}秒スタン" + E + "。",
        "ult": A + "{r_go}秒" + E + "溜め（被ダメージ" + A + "{r_dr}%" + E + "軽減）、槍影が洪水のように対象を囲み" + A + "{r_n}回" + E +
               "突く。毎回周囲の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "、初撃で" + R + "{r_root}秒拘束" + E + "。",
        "names": ("怒濤連刺", "暴雨斜刺", "四十昼夜の大洪水"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_poseidon 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "thrust_wind_1", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "thrust_hit_1", 0.45, 0.0)],
    f"{ID}_q_step": [(SFX + "undertow", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "flurry_wind", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "flurry_hit", 0.5, 0.0)],
    f"{ID}_e_rise": [(SFX + "rain_rise", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "rain_drop", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "rain_hit", 0.55, 0.0)],
    f"{ID}_r_charge": [(SFX + "flood_charge", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "flood_barrage", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "flood_hit", 0.55, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/poseidon.rs）：死的时候三叉戟落地、身子着地（Codex 的 cues：0.33 秒、0.785 秒）和配音
    f"{ID}_dead": [(SFX + "trident_drop", 0.45, 0.33), (SFX + "body_fall", 0.5, 0.785)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)]
       for x in ("indifferent", "in_my_way", "no_mercy", "no_defiance", "watch_me", "dont_miss", "divine_independence",
                 "a_true_god", "alone")},
}


def values(p):
    v = {k: p[k] for k in ("p_atk", "p_dr", "q_n", "q_dmg", "q_ad", "e_dmg", "e_ad", "r_dr", "r_n", "r_dmg", "r_ad")}
    for k in ("e_stun", "r_go", "r_root"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "poseidon", "tools/kit/seed_poseidon_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
