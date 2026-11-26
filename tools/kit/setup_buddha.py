"""释迦的文本（五种语言）、sound_info 和 champion_view，数字取自 build_buddha.P。

    python tools/kit/setup_buddha.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_buddha（说明和技能名）、sound/sfx/ragnarok_buddha_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：释迦 / 釋迦 / Buddha / 釈迦 / 석가；技能名照终末的女武神和 Codex 的交付：六道棍·枪刃、观音盾、大圆寂刀·零，被动「未来视」
写在普攻说明里；图标照 Codex 的交付（assets/source/buddha/runtime/icons：staff、shield、nirvana；sight 那张是被动，不装）。
声音：Codex 的交付（buddha_packs/outputs/buddha_assets_done.zip）：15 条原创音效（棍的挥出和命中、枪刃的起手、前刺和命中、
未来视的聚焦、观音盾的展开、格挡和收回、撤步、涅槃剑的蓄势、出鞘、斩出和命中、倒地）和六句官方日语原声（中村悠一，宣传片
结尾那句只给试听，不用）。音频不进仓库，tools/kit/seed_buddha_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod
挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_buddha import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 99 格 = 30 个游戏像素、往前 9 格 = 3；
# 百科中心照雷电（1 倍待机的实心顶上方 23 格）：实心顶 -34 -> -11；选人卡用默认的 -12
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 4, "y": -36}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "释迦",
        "attack": "六道棍一击，造成" + AD + O + "物理伤害" + E + "。" + O + "未来视" + E + "：普攻和枪刃时看穿接下来的招（每" + A +
                  "{p_cd}秒" + E + "一次），" + A + "{p_t}秒" + E + "里普攻打不疼他。",
        "skill": "六道棍化作十二天斧（长戟）横扫：前方扇形的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "，" + R + "护甲降低{q_shred}%" +
                 E + "，持续" + A + "{q_shred_t}秒" + E + "。",
        "skill2": "看见要挨的打，六道棍化作七难即灭之盾：" + S + "护盾{e_sh}" + E + " + " + ratio("e_sh_ad") + "（" + A + "{e_t}秒" + E + "），" + A +
                  "{e_cc}秒" + E + "不受控制。盾收起时莲光绽开，身边的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R +
                  "减速{e_slow}%" + E + "。",
        "ult": "与零福的灵魂炼出大圆寂刀·零，天眼妙觉大涅槃斩（斩中前不受控制、受到的伤害降低" + A + "{r_dr}%" + E + "）一刀斩下：前方扇形的敌人受到" +
               phys("r_dmg", "r_ad") + "加目标最大生命" + O + "{r_thp}%" + E + "的" + O + "物理伤害" + E + "并" + R + "眩晕{r_stun}秒" + E + "。",
        "names": ("十二天斧", "七难即灭之盾", "大圆寂刀·零"),
    },
    "zh-hant": {
        "name": "釋迦",
        "attack": "六道棍一擊，造成" + AD + O + "物理傷害" + E + "。" + O + "未來視" + E + "：普攻和槍刃時看穿接下來的招（每" + A +
                  "{p_cd}秒" + E + "一次），" + A + "{p_t}秒" + E + "裡普攻打不疼他。",
        "skill": "六道棍化作十二天斧（長戟）橫掃：前方扇形的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "，" + R + "護甲降低{q_shred}%" +
                 E + "，持續" + A + "{q_shred_t}秒" + E + "。",
        "skill2": "看見要挨的打，六道棍化作七難即滅之盾：" + S + "護盾{e_sh}" + E + " + " + ratio("e_sh_ad") + "（" + A + "{e_t}秒" + E + "），" + A +
                  "{e_cc}秒" + E + "不受控制。盾收起時蓮光綻開，身邊的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R +
                  "減速{e_slow}%" + E + "。",
        "ult": "與零福的靈魂煉出大圓寂刀·零，天眼妙覺大涅槃斬（斬中前不受控制、受到的傷害降低" + A + "{r_dr}%" + E + "）一刀斬下：前方扇形的敵人受到" +
               phys("r_dmg", "r_ad") + "加目標最大生命" + O + "{r_thp}%" + E + "的" + O + "物理傷害" + E + "並" + R + "暈眩{r_stun}秒" + E + "。",
        "names": ("十二天斧", "七難即滅之盾", "大圓寂刀·零"),
    },
    "en": {
        "name": "Buddha",
        "attack": "A blow of the Six Realms Staff for " + AD + " " + O + "physical damage" + E + ". " + O + "Future Sight" + E +
                  ": on an attack or Spear Blade he reads the blows to come (once every " + A + "{p_cd}s" + E + "): for " + A +
                  "{p_t}s" + E + " basic attacks cannot hurt him.",
        "skill": "The staff becomes the Twelve Devas Axe, a long halberd, for one sweep: enemies in a cone take " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + " and lose " + R + "{q_shred}% armour" + E + " for " + A + "{q_shred_t}s" + E + ".",
        "skill2": "He sees the blow coming and the staff becomes the Shield of Ahimsa: a " + S + "{e_sh}" + E + " + " + ratio("e_sh_ad") + " " + S +
                  "shield" + E + " for " + A + "{e_t}s" + E + ", unstoppable for " + A + "{e_cc}s" + E + ". When it is lowered a lotus "
                  "blooms: enemies around him take " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + " and are " + R +
                  "slowed {e_slow}%" + E + ".",
        "ult": "Forges the Great Nirvana Sword Zero with Zerofuku's soul and cuts the Mahabali Nirvana (unstoppable and " + A + "{r_dr}%" + E + " less damage until it lands) and cuts: "
               "enemies in a cone take " + phys("r_dmg", "r_ad") + " plus " + O + "{r_thp}%" + E + " of their maximum health as " + O +
               "physical damage" + E + " and are " + R + "stunned for {r_stun}s" + E + ".",
        "names": ("Twelve Devas Axe", "Shield of Ahimsa", "Great Nirvana Sword Zero"),
    },
    "ko": {
        "name": "석가",
        "attack": "육도곤으로 쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "미래시" + E + ": 기본 공격이나 창날 때 다음 수를 꿰뚫어 보고(" +
                  A + "{p_cd}초" + E + "마다 한 번) " + A + "{p_t}초" + E + " 동안 기본 공격에 피해를 받지 않음.",
        "skill": "육도곤이 십이천부(긴 창도끼)로 변해 휩쓸어 앞쪽 부채꼴의 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", " + A +
                 "{q_shred_t}초" + E + " 동안 " + R + "방어력 {q_shred}% 감소" + E + ".",
        "skill2": "맞을 공격을 보고 육도곤이 칠난즉멸의 방패로 변함: " + S + "보호막 {e_sh}" + E + " + " + ratio("e_sh_ad") + "(" + A + "{e_t}초" + E +
                  "), " + A + "{e_cc}초" + E + " 저지 불가. 방패를 거둘 때 연꽃이 피어 주변 적에게 " + phys("e_dmg", "e_ad") + " " + O +
                  "물리 피해" + E + "와 " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "영복의 혼과 함께 대원적도·영을 벼려 천안묘각대열반참(베기 전까지 저지 불가, 받는 피해 " + A + "{r_dr}%" + E + " 감소) 내리벰: 앞쪽 부채꼴의 적에게 " +
               phys("r_dmg", "r_ad") + " + 최대 체력 " + O + "{r_thp}%" + E + "의 " + O + "물리 피해" + E + "와 " + R + "{r_stun}초 기절" +
               E + ".",
        "names": ("십이천부", "칠난즉멸의 방패", "대원적도·영"),
    },
    "ja": {
        "name": "釈迦",
        "attack": "六道棍の一撃で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "未来視" + E + "：通常攻撃や槍刃の時に次の手を見切り（" +
                  A + "{p_cd}秒" + E + "に一度）、" + A + "{p_t}秒" + E + "の間、通常攻撃のダメージを受けない。",
        "skill": "六道棍を十二天斧（長柄の斧）に変えて薙ぐ：前方扇形の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、" + A +
                 "{q_shred_t}秒" + E + "の間" + R + "物防{q_shred}%低下" + E + "。",
        "skill2": "受ける攻撃を見て六道棍が七難即滅の楯に変わる：" + S + "シールド{e_sh}" + E + " + " + ratio("e_sh_ad") + "（" + A + "{e_t}秒" + E + "）、" +
                  A + "{e_cc}秒" + E + "行動妨害無効。盾を収める時に蓮華が咲き、周囲の敵に" + phys("e_dmg", "e_ad") + "の" + O +
                  "物理ダメージ" + E + "と" + R + "{e_slow}%スロウ" + E + "。",
        "ult": "零福の魂と大円寂刀・零を鍛え、天眼妙覚大涅槃斬（斬るまで行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）斬り下ろす：前方扇形の敵に" +
               phys("r_dmg", "r_ad") + "＋最大体力" + O + "{r_thp}%" + E + "の" + O + "物理ダメージ" + E + "と" + R + "{r_stun}秒スタン" + E +
               "。",
        "names": ("十二天斧", "七難即滅の楯", "大円寂刀・零"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_buddha 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "staff", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "staff_hit", 0.45, 0.0)],
    f"{ID}_p": [(SFX + "focus", 0.35, 0.0)],
    f"{ID}_q_load": [(SFX + "vajra_load", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "vajra", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "vajra_hit", 0.5, 0.0)],
    f"{ID}_e_eye": [(SFX + "focus", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "shield_open", 0.55, 0.0)],
    f"{ID}_e_end": [(SFX + "shield_end", 0.5, 0.0)],
    f"{ID}_e_hit": [(SFX + "shield_block", 0.5, 0.0)],
    f"{ID}_r_load": [(SFX + "nirvana_load", 0.55, 0.0)],
    f"{ID}_r_show": [(SFX + "nirvana_ready", 0.6, 0.0)],
    f"{ID}_r": [(SFX + "nirvana", 0.65, 0.0)],
    f"{ID}_r_hit": [(SFX + "nirvana_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/buddha.rs）：死的时候身子着地（Codex 的 cues：0.846 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("question", "indifferent", "brief", "resolve", "resolve_short")},
}


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ad", "q_shred", "e_sh", "e_sh_ad", "e_dmg", "e_ad", "e_slow", "r_dr", "r_dmg",
                           "r_ad", "r_thp")}
    for k in ("p_cd", "p_t", "q_shred_t", "e_t", "e_cc", "r_stun"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "buddha", "tools/kit/seed_buddha_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
