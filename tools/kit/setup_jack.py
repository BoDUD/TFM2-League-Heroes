"""开膛手杰克的文本（五种语言）、sound_info 和 champion_view，数字取自 build_jack.P。

    python tools/kit/setup_jack.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_jack（说明和技能名）、sound/sfx/ragnarok_jack_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：开膛手杰克 / 開膛手傑克 / Jack the Ripper / 切り裂きジャック / 잭 더 리퍼；技能名：飞刀扇、神器之伞、亲爱的神
（Dear GOD：原作他终结赫拉克勒斯那一招的名字，不是手套的名字；手套在原作里没有名字，是女武神赫萝克 Hlökk 变的），图标照 Codex
的交付（assets/source/jack/runtime/icons：fan、artifact（手套碰过的东西变成神器，伞也是）、dear_god；emotion 那张单片镜是
被动，不装）。被动「心之色」写在普攻说明里。2026-11-26 照原作改了 E、R（build_jack.py）：神器之伞转着挡、往后跳开，Dear GOD
按住伤口扣血、扑上去双手插进胸口。
声音：Codex 的交付（jack_packs/outputs/jack_assets_done.zip）：12 条原创音效（飞刀出手、命中，扇形飞刀出手、命中，开伞、
后撤、收伞，单片镜、手套触物、收招命中，短刀收回，倒地）和六句官方日语原声（杉田智和）。音频不进仓库，
tools/kit/seed_jack_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_jack import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧单片镜那只眼在脚底上约 99 格 = 30 个游戏像素、往前 6 格 = 2；
# 百科中心照小次郎、波塞冬（1 倍待机的实心顶上方 22 格左右）：帽檐宽，实心顶 -34 -> -11；选人卡用默认的 -12
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 2, "y": -36}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "开膛手杰克",
        "attack": "掷出飞刀，造成" + AD + O + "物理伤害" + E + "。" + O + "心之色" + E + "：他看得见人心的颜色，恐惧藏不住：对生命低于" + A +
                  "{p_hp}%" + E + "的敌方英雄，伤害" + A + "+{p_dmg}%" + E + "。",
        "skill": "掷出一扇飞刀，前方扇形里的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%" + E + "。",
        "skill2": "撑开被手套变成神器的伞转着挡：伞转着时普攻打不疼他、其余伤害降低" + A + "{e_dr}%" + E + "，随后往后跳开。",
        "ult": "按住伤口让血浸透手套（失去" + A + "{r_cost}%" + E + "最大生命），血也成了神器；装作倒下，再扑向对方，双手插进胸口：造成" +
               phys("r_dmg", "r_ad") + O + "物理伤害" + E + "。",
        "names": ("飞刀扇", "神器之伞", "亲爱的神"),
    },
    "zh-hant": {
        "name": "開膛手傑克",
        "attack": "擲出飛刀，造成" + AD + O + "物理傷害" + E + "。" + O + "心之色" + E + "：他看得見人心的顏色，恐懼藏不住：對生命低於" + A +
                  "{p_hp}%" + E + "的敵方英雄，傷害" + A + "+{p_dmg}%" + E + "。",
        "skill": "擲出一扇飛刀，前方扇形裡的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%" + E + "。",
        "skill2": "撐開被手套變成神器的傘轉著擋：傘轉著時普攻打不疼他、其餘傷害降低" + A + "{e_dr}%" + E + "，隨後往後跳開。",
        "ult": "按住傷口讓血浸透手套（失去" + A + "{r_cost}%" + E + "最大生命），血也成了神器；裝作倒下，再撲向對方，雙手插進胸口：造成" +
               phys("r_dmg", "r_ad") + O + "物理傷害" + E + "。",
        "names": ("飛刀扇", "神器之傘", "親愛的神"),
    },
    "en": {
        "name": "Jack the Ripper",
        "attack": "Throws a knife for " + AD + " " + O + "physical damage" + E + ". " + O + "Colours of the Heart" + E + ": he sees "
                  "the colour of every heart, and fear does not hide - " + A + "+{p_dmg}%" + E + " damage to enemy champions "
                  "below " + A + "{p_hp}%" + E + " health.",
        "skill": "Throws a fan of knives: enemies in a cone take " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E +
                 " and are " + R + "slowed {q_slow}%" + E + ".",
        "skill2": "Spins an umbrella his gloves made divine to parry: while it spins basic attacks cannot hurt him and the rest "
                  "deals " + A + "{e_dr}%" + E + " less; then he hops back.",
        "ult": "Presses his wound until the blood soaks his gloves (losing " + A + "{r_cost}%" + E + " max health) - the blood "
               "turns divine too. Feigning a fall, he lunges at the target and drives both hands into its chest for " +
               phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + ".",
        "names": ("Knife Fan", "Divine Umbrella", "Dear GOD"),
    },
    "ko": {
        "name": "잭 더 리퍼",
        "attack": "단검을 던져 " + AD + " " + O + "물리 피해" + E + ". " + O + "마음의 색" + E + ": 사람의 마음이 색으로 보인다. 체력이 " +
                  A + "{p_hp}%" + E + " 아래인 적 챔피언에게 피해 " + A + "+{p_dmg}%" + E + ".",
        "skill": "단검을 부채꼴로 던져 앞쪽 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "와 " + R + "{q_slow}% 둔화" +
                 E + ".",
        "skill2": "장갑으로 신기가 된 우산을 돌려 막음: 도는 동안 기본 공격 피해를 받지 않고 나머지 피해 " + A + "{e_dr}%" + E +
                  " 감소, 이어서 뒤로 뛰어 물러남.",
        "ult": "상처를 눌러 장갑을 피로 적신다(최대 체력 " + A + "{r_cost}%" + E + " 소모): 피도 신기가 된다. 쓰러지는 척하다 대상에게 "
               "달려들어 두 손을 가슴에 꽂는다: " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ".",
        "names": ("칼날 부채", "신기의 우산", "디어 갓"),
    },
    "ja": {
        "name": "切り裂きジャック",
        "attack": "ナイフを投げ" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "心の色" + E + "：人の心が色で見える。体力" + A +
                  "{p_hp}%" + E + "未満の敵チャンピオンへのダメージ" + A + "+{p_dmg}%" + E + "。",
        "skill": "ナイフを扇状に投げ、前方の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{q_slow}%スロウ" +
                 E + "。",
        "skill2": "手袋で神器となった傘を回して受け流す：回っている間は通常攻撃が効かず、他の被ダメージ" + A + "{e_dr}%" + E +
                  "軽減、続けて後ろへ跳ぶ。",
        "ult": "傷口を押さえ血で手袋を染める（最大体力の" + A + "{r_cost}%" + E + "を失う）：血も神器となる。倒れたふりから相手に飛びかかり、"
               "両手を胸に突き立てる：" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "。",
        "names": ("ナイフの扇", "神器の傘", "ディア・ゴッド"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_jack 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "knife_release", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "knife_hit", 0.45, 0.0)],
    # 扇形飞刀出手，收势时把刀收回（第 7 帧，出手后 0.22 秒）
    f"{ID}_q": [(SFX + "fan_release", 0.5, 0.0), (SFX + "metal_stow", 0.4, 0.22)],
    f"{ID}_q_hit": [(SFX + "fan_hit", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "umbrella", 0.5, 0.0)],
    # 伞面挡住的一下（第 4 帧火花）
    f"{ID}_e_block": [(SFX + "knife_hit", 0.4, 0.0)],
    f"{ID}_e_back": [(SFX + "cloak", 0.5, 0.0)],
    f"{ID}_e_close": [(SFX + "close", 0.45, 0.0)],
    # Dear GOD：手套染红（手套把东西变成神器的那一声），扑出去（披风）
    f"{ID}_r1": [(SFX + "artifact", 0.55, 0.0)],
    f"{ID}_r2": [(SFX + "cloak", 0.5, 0.0)],
    f"{ID}_r_hit": [(SFX + "ult_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/jack.rs）：死的时候披风和身子落地（Codex 的 cues：0.827 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.827)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)]
       for x in ("showtime", "delight", "reveal", "rule", "color", "etiquette")},
}


def values(p):
    return {k: p[k] for k in ("p_hp", "p_dmg", "q_dmg", "q_ad", "q_slow", "e_dr", "r_dmg", "r_ad", "r_cost")}


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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "jack", "tools/kit/seed_jack_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
