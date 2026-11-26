"""哈迪斯的文本（五种语言）、sound_info 和 champion_view，数字取自 build_hades.P。

    python tools/kit/setup_hades.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_hades（说明和技能名）、sound/sfx/ragnarok_hades_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：哈迪斯 / 黑帝斯 / Hades / 하데스 / ハデス；技能名照终末的女武神和 Codex 的交付：珀耳塞福涅·风压斩（ペルセポネ・ロアイ）、
冥府重砸、伊科尔·德斯莫斯；被动「伊科尔」写在普攻说明里。图标照 Codex 的交付（assets/source/hades/runtime/icons：wind、earth、
desmos；bident 那张是普攻，图标位只有三个，不装）。
声音：Codex 的交付（hades_packs/outputs/hades_assets_done.zip）：14 条原创音效（出刺和命中、风压斩的运枪、释放和命中、重砸的
抬枪、砸地和命中、碎石、伊科尔强化枪头、德斯莫斯的出刺和命中、双叉枪落地、倒地）和七句官方日语原声（置鮎龍太郎）。音频不进
仓库，tools/kit/seed_hades_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hades import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛在脚底上 101 格、往前 5 格（PPU 2.75：-37、2）；百科中心照 bp_card_audit.py --centers 的规则（实心顶 -39.3
# -> -12）；选人卡照它的规则 y = -39 - 头顶，量头不量枪：头发顶在 -28.7（-32 那几行是双叉枪的护环）-> -10
VIEW = {"face": {"x": 2, "y": -37}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "哈迪斯",
        "attack": "双叉枪直刺，造成" + AD + O + "物理伤害" + E + "。" + O + "伊科尔" + E + "：放完技能后" + A + "{p_t}秒" + E +
                  "内，下一次普攻额外造成" + phys("p_dmg", "p_ad") + O + "物理伤害" + E + "。",
        "skill": "冥府的铁锤：跳起来往下刺，落枪处地面炸开，周围的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R +
                 "减速{q_slow}%" + E + "（" + A + "{q_slow_t}秒" + E + "）；甩出的风刃再让前方一条线上的敌人受到" + phys("q2_dmg", "q2_ad") +
                 O + "物理伤害" + E + "。",
        "skill2": "大地崩碎者：滑着枪杆往下劈，砸进身前的地面，那一圈的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并被" + R +
                  "击飞{e_air}秒" + E + "。",
        "ult": "挖开胸口用神血把双叉枪锻成宿命之四血枪（伊科尔·德斯莫斯；不受控制、减伤" + A + "{r_dr}%" + E + "），血之引导曙光：朝目标直线突刺，穿过的敌人受到" +
               phys("r_dmg", "r_ad") + "加最大生命" + O + "{r_thp}%" + E + "的" + O + "物理伤害" + E + "并" + R + "眩晕{r_stun}秒" +
               E + "。",
        "names": ("冥府的铁锤", "大地崩碎者", "血之引导曙光"),
    },
    "zh-hant": {
        "name": "黑帝斯",
        "attack": "雙叉槍直刺，造成" + AD + O + "物理傷害" + E + "。" + O + "伊柯爾" + E + "：放完技能後" + A + "{p_t}秒" + E +
                  "內，下一次普攻額外造成" + phys("p_dmg", "p_ad") + O + "物理傷害" + E + "。",
        "skill": "冥府的鐵錘：跳起來往下刺，落槍處地面炸開，周圍的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R +
                 "減速{q_slow}%" + E + "（" + A + "{q_slow_t}秒" + E + "）；甩出的風刃再讓前方一條線上的敵人受到" + phys("q2_dmg", "q2_ad") +
                 O + "物理傷害" + E + "。",
        "skill2": "大地崩碎者：滑著槍桿往下劈，砸進身前的地面，那一圈的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並被" + R +
                  "擊飛{e_air}秒" + E + "。",
        "ult": "挖開胸口用神血把雙叉槍鍛成宿命之四血槍（伊柯爾·德斯莫斯；不受控制、減傷" + A + "{r_dr}%" + E + "），血之引導曙光：朝目標直線突刺，穿過的敵人受到" +
               phys("r_dmg", "r_ad") + "加最大生命" + O + "{r_thp}%" + E + "的" + O + "物理傷害" + E + "並" + R + "暈眩{r_stun}秒" +
               E + "。",
        "names": ("冥府的鐵錘", "大地崩碎者", "血之引導曙光"),
    },
    "en": {
        "name": "Hades",
        "attack": "A thrust of the bident: " + AD + " " + O + "physical damage" + E + ". " + O + "Ichor" + E + ": for " + A +
                  "{p_t}s" + E + " after a skill, his next attack deals " + phys("p_dmg", "p_ad") + " more " + O +
                  "physical damage" + E + ".",
        "skill": "Persephone Kallichore: he leaps and drives the bident down; the ground bursts: enemies around take " +
                 phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + " and are " + R + "slowed {q_slow}%" + E + " for " + A +
                 "{q_slow_t}s" + E + ", and the flung wind blade deals " + phys("q2_dmg", "q2_ad") + " " + O + "physical damage" + E +
                 " along a line ahead.",
        "skill2": "Persephone Titan: sliding his grip down the shaft he smashes the ground before him: enemies in the circle take " + phys("e_dmg", "e_ad") + " " +
                  O + "physical damage" + E + " and are " + R + "knocked up for {e_air}s" + E + ".",
        "ult": "He tears open his chest and forges the bident into the Ichor Desmos with his own blood (unstoppable, " + A + "{r_dr}%" + E + " less damage); Ichor Eos "
               "thrusts straight through his target: enemies on the way take " + phys("r_dmg", "r_ad") + " + " + O + "{r_thp}%" +
               E + " max health " + O + "physical damage" + E + " and are " + R + "stunned for {r_stun}s" + E + ".",
        "names": ("Persephone Kallichore", "Persephone Titan", "Ichor Eos"),
    },
    "ko": {
        "name": "하데스",
        "attack": "쌍지창으로 찔러 " + AD + " " + O + "물리 피해" + E + ". " + O + "이코르" + E + ": 스킬을 쓴 뒤 " + A + "{p_t}초" +
                  E + " 안에 다음 기본 공격이 " + phys("p_dmg", "p_ad") + " " + O + "물리 피해" + E + "를 더 줌.",
        "skill": "명부의 철퇴: 뛰어올라 창을 내리꽂아 땅이 터지며 주변 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E +
                 "와 " + R + "{q_slow}% 둔화" + E + "(" + A + "{q_slow_t}초" + E + "), 날아간 바람 칼날이 앞쪽 일직선의 적에게 " +
                 phys("q2_dmg", "q2_ad") + " " + O + "물리 피해" + E + ".",
        "skill2": "대지를 부순 자: 창대를 미끄러뜨리며 앞쪽 땅을 내리찍어 그 원 안의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_air}초 띄워 올림" + E + ".",
        "ult": "가슴을 갈라 신의 피로 쌍지창을 이코르 데스모스로 벼려(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소) 피가 이끈 서광: 대상을 향해 일직선으로 찔러 지나간 적에게 " +
               phys("r_dmg", "r_ad") + " + 최대 체력 " + O + "{r_thp}%" + E + " " + O + "물리 피해" + E + "와 " + R +
               "{r_stun}초 기절" + E + ".",
        "names": ("명부의 철퇴", "대지를 부순 자", "피가 이끈 서광"),
    },
    "ja": {
        "name": "ハデス",
        "attack": "二叉槍で突き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "イコル" + E + "：スキル使用後" + A + "{p_t}秒" + E +
                  "以内の次の通常攻撃が" + phys("p_dmg", "p_ad") + "の" + O + "物理ダメージ" + E + "を追加。",
        "skill": "冥府の鉄槌：跳んで槍を突き下ろし地面を爆ぜさせる：周囲の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" +
                 R + "{q_slow}%スロウ" + E + "（" + A + "{q_slow_t}秒" + E + "）、飛ばした風の刃が前方一直線に" + phys("q2_dmg", "q2_ad") +
                 "の" + O + "物理ダメージ" + E + "。",
        "skill2": "大地を砕きし者：柄を滑らせて振り下ろし前方の地面を叩き割り、円内の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_air}秒打ち上げ" + E + "。",
        "ult": "胸を裂き神の血で二叉槍を宿命の四血槍に鍛え（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）、血が導きし曙光：対象へ一直線に突き抜け、通った敵に" +
               phys("r_dmg", "r_ad") + "＋最大体力" + O + "{r_thp}%" + E + "の" + O + "物理ダメージ" + E + "と" + R + "{r_stun}秒スタン" +
               E + "。",
        "names": ("冥府の鉄槌", "大地を砕きし者", "血が導きし曙光"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_hades 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "thrust", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "thrust_hit", 0.45, 0.0)],
    f"{ID}_p_hit": [(SFX + "desmos_hit", 0.4, 0.0)],
    f"{ID}_q_load": [(SFX + "wind_prep", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "wind", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "wind_hit", 0.5, 0.0)],
    f"{ID}_e_lift": [(SFX + "slam_prep", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "slam", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "slam_hit", 0.5, 0.0)],
    f"{ID}_e_dust": [(SFX + "dust", 0.45, 0.0)],
    f"{ID}_r_load": [(SFX + "ichor", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "desmos", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "desmos_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/hades.rs）：死的时候双叉枪落地、身子着地（Codex 的 cues：0.353 / 0.846 秒）和配音
    f"{ID}_dead": [(SFX + "spear_fall", 0.45, 0.353), (SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("open", "brother", "eye", "earth", "thrust", "wind", "parry")},
}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ad", "q_dmg", "q_ad", "q2_dmg", "q2_ad", "q_slow", "e_dmg", "e_ad", "r_dr", "r_dmg", "r_ad", "r_thp")}
    for k in ("p_t", "q_slow_t", "e_air", "r_stun"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "hades", "tools/kit/seed_hades_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
