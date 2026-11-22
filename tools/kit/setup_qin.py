"""秦始皇的文本（五种语言）、sound_info 和 champion_view，数字取自 build_qin.P。

    python tools/kit/setup_qin.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_qin（说明和技能名）、sound/sfx/ragnarok_qin_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：秦始皇 / 秦始皇 / Qin Shi Huang / 진시황 / 始皇帝；技能名照终末的女武神和 Codex 的交付：波流龟气弹、神罗铠袖·承力天凤、
始皇勾践剑；被动「星」写在普攻说明里。图标照 Codex 的交付（assets/source/qin/runtime/icons：tortoise、phoenix、jian；claw 那张
是普攻，图标位只有三个，不装）。
声音：Codex 的交付（qin_packs/outputs/qin_assets_done.zip）：13 条原创音效（指爪的划出和命中、吸气、送出气弹、气弹破裂、
神罗铠袖的护势、承力、推回和命中、勾践剑的显形、斩出和命中、倒地）和七句官方日语原声（石川界人）。音频不进仓库，
tools/kit/seed_qin_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_qin import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛（眼罩下）在脚底上 100 格、往前 7 格（PPU 2.75：-36、2）；百科中心照 bp_card_audit.py --centers 的规则
# （实心顶 -40.0 -> -13）；选人卡照它的规则 y = -39 - 头顶（-30.0）-> -9
VIEW = {"face": {"x": 2, "y": -36}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -9}}

TEXT = {
    "zh-hans": {
        "name": "秦始皇",
        "attack": "金指爪抓击，造成" + AD + O + "物理伤害" + E + "。" + O + "星" + E + "：被他的技能打中的敌人露出破绽，" + A +
                  "{p_t}秒" + E + "内受到的伤害" + A + "+{p_amp}%" + E + "。",
        "skill": "吸一口气吐出气弹，追着目标飞去，炸开时造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R +
                 "眩晕{q_stun}秒" + E + "。",
        "skill2": "举起神罗铠袖（" + A + "{e_t}秒" + E + "内减伤" + A + "{e_dr}%" + E + "、不受控制），身边的友方英雄获得" + S +
                  "护盾{e_sh}" + E + " + " + ratio("e_sh_ad") + "；接着把力推回去，前方的敌人受到" + phys("e_dmg", "e_ad") + O +
                  "物理伤害" + E + "并" + R + "眩晕{e_stun}秒" + E + "。",
        "ult": "拔出始皇勾践剑（不受控制、减伤" + A + "{r_dr}%" + E + "）横斩，前方大扇形内的敌人受到" + phys("r_dmg", "r_ad") + O +
               "物理伤害" + E + "并被" + R + "击飞{r_up}秒" + E + "。",
        "names": ("波流龟气弹", "神罗铠袖·承力天凤", "始皇勾践剑"),
    },
    "zh-hant": {
        "name": "秦始皇",
        "attack": "金指爪抓擊，造成" + AD + O + "物理傷害" + E + "。" + O + "星" + E + "：被他的技能打中的敵人露出破綻，" + A +
                  "{p_t}秒" + E + "內受到的傷害" + A + "+{p_amp}%" + E + "。",
        "skill": "吸一口氣吐出氣彈，追著目標飛去，炸開時造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R +
                 "暈眩{q_stun}秒" + E + "。",
        "skill2": "舉起神羅鎧袖（" + A + "{e_t}秒" + E + "內減傷" + A + "{e_dr}%" + E + "、不受控制），身邊的友方英雄獲得" + S +
                  "護盾{e_sh}" + E + " + " + ratio("e_sh_ad") + "；接著把力推回去，前方的敵人受到" + phys("e_dmg", "e_ad") + O +
                  "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E + "。",
        "ult": "拔出始皇勾踐劍（不受控制、減傷" + A + "{r_dr}%" + E + "）橫斬，前方大扇形內的敵人受到" + phys("r_dmg", "r_ad") + O +
               "物理傷害" + E + "並被" + R + "擊飛{r_up}秒" + E + "。",
        "names": ("波流龜氣彈", "神羅鎧袖·承力天鳳", "始皇勾踐劍"),
    },
    "en": {
        "name": "Qin Shi Huang",
        "attack": "A strike of his golden claws: " + AD + " " + O + "physical damage" + E + ". " + O + "Stars" + E + ": enemies "
                  "his skills hit show their weak points and take " + A + "{p_amp}%" + E + " more damage for " + A + "{p_t}s" +
                  E + ".",
        "skill": "He breathes in and blows a qi bubble that chases the target and bursts: " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + " and a " + R + "{q_stun}s stun" + E + ".",
        "skill2": "He raises the Shinra Armor Sleeves (" + A + "{e_dr}%" + E + " less damage and unstoppable for " + A + "{e_t}s" +
                  E + "); allied champions around him gain a " + S + "{e_sh}" + E + " + " + ratio("e_sh_ad") + " " + S + "shield" +
                  E + ". Then he turns the force back: enemies in front take " + phys("e_dmg", "e_ad") + " " + O +
                  "physical damage" + E + " and are " + R + "stunned for {e_stun}s" + E + ".",
        "ult": "He draws the Goujian sword (unstoppable, " + A + "{r_dr}%" + E + " less damage) and cuts across: enemies in a "
               "wide cone take " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + " and are " + R +
               "knocked up for {r_up}s" + E + ".",
        "names": ("Turtle Qi Bubble", "Shinra Sleeves: Phoenix Reversal", "Goujian Sword of the First Emperor"),
    },
    "ko": {
        "name": "진시황",
        "attack": "금빛 손톱으로 할퀴어 " + AD + " " + O + "물리 피해" + E + ". " + O + "별" + E + ": 그의 스킬에 맞은 적은 약점이 드러나 " +
                  A + "{p_t}초" + E + " 동안 받는 피해 " + A + "+{p_amp}%" + E + ".",
        "skill": "숨을 들이쉬고 기탄을 뱉어 대상을 쫓아가 터지며 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "와 " + R +
                 "{q_stun}초 기절" + E + ".",
        "skill2": "신라개수를 들어(" + A + "{e_t}초" + E + " 동안 피해 " + A + "{e_dr}%" + E + " 감소, 저지 불가) 주변 아군 챔피언에게 " +
                  S + "보호막 {e_sh}" + E + " + " + ratio("e_sh_ad") + ". 이어 힘을 되돌려 앞쪽 적에게 " + phys("e_dmg", "e_ad") + " " +
                  O + "물리 피해" + E + "와 " + R + "{e_stun}초 기절" + E + ".",
        "ult": "시황 구천검을 뽑아(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소) 가로 베어 넓은 부채꼴의 적에게 " +
               phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_up}초 띄워 올림" + E + ".",
        "names": ("파류귀기탄", "신라개수·승력천봉", "시황 구천검"),
    },
    "ja": {
        "name": "始皇帝",
        "attack": "金の指爪で裂き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "星" + E + "：スキルが当たった敵は急所が露わになり" +
                  A + "{p_t}秒" + E + "被ダメージ" + A + "+{p_amp}%" + E + "。",
        "skill": "息を吸って気弾を吐き、追いかけて弾けた対象に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                 "{q_stun}秒スタン" + E + "。",
        "skill2": "神羅鎧袖を構え（" + A + "{e_t}秒" + E + "被ダメージ" + A + "{e_dr}%" + E + "軽減・行動妨害無効）周りの味方に" + S +
                  "シールド{e_sh}" + E + "＋" + ratio("e_sh_ad") + "。続けて力を押し返し、前方の敵に" + phys("e_dmg", "e_ad") + "の" +
                  O + "物理ダメージ" + E + "と" + R + "{e_stun}秒スタン" + E + "。",
        "ult": "始皇勾践剣を抜き（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）横に斬り、広い扇形の敵に" + phys("r_dmg", "r_ad") +
               "の" + O + "物理ダメージ" + E + "と" + R + "{r_up}秒打ち上げ" + E + "。",
        "names": ("波流亀気弾", "神羅鎧袖・承力天鳳", "始皇勾践剣"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_qin 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "claw", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "claw_hit", 0.45, 0.0)],
    f"{ID}_q_load": [(SFX + "breath", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "bubble", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "pop", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "guard", 0.5, 0.0)],
    f"{ID}_e_block": [(SFX + "receive", 0.5, 0.0)],
    f"{ID}_e_push": [(SFX + "counter", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "counter_hit", 0.5, 0.0)],
    f"{ID}_r_show": [(SFX + "jian_reveal", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "jian_cut", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "jian_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/qin.rs）：死的时候身子着地（Codex 的 cues：0.846 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("taunt", "entrance", "big_one", "armor", "counter", "hades",
                                                       "one_king")},
}


def values(p):
    v = {k: p[k] for k in ("p_amp", "q_dmg", "q_ad", "e_dr", "e_sh", "e_sh_ad", "e_dmg", "e_ad", "r_dr", "r_dmg", "r_ad")}
    for k in ("p_t", "q_stun", "e_t", "e_stun", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "qin", "tools/kit/seed_qin_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
