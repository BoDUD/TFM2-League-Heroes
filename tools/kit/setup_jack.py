"""开膛手杰克的文本（五种语言）、sound_info 和 champion_view，数字取自 build_jack.P。

    python tools/kit/setup_jack.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_jack（说明和技能名）、sound/sfx/ragnarok_jack_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：开膛手杰克 / 開膛手傑克 / Jack the Ripper / 切り裂きジャック / 잭 더 리퍼；技能名：飞刀扇、伦敦之雾、亲爱的神（他那副
手套的名字 Dear God），图标照 Codex 的交付（assets/source/jack/runtime/icons：fan、artifact（手套碰过的东西变成神器，
伞也是）、dear_god；emotion 那张单片镜是被动，不装）。被动「心之色」写在普攻说明里。
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
VIEW = {"face": {"x": 2, "y": -30}, "center": {"x": 0, "y": -11}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "开膛手杰克",
        "attack": "掷出飞刀，造成" + AD + O + "物理伤害" + E + "。" + O + "心之色" + E + "：他看得见人心的颜色，恐惧藏不住：对生命低于" + A +
                  "{p_hp}%" + E + "的敌方英雄，伤害" + A + "+{p_dmg}%" + E + "。",
        "skill": "掷出一扇飞刀，前方扇形里的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%" + E + "。",
        "skill2": "撑开被手套变成神器的伞，到收伞受到的伤害降低" + A + "{e_dr}%" + E + "；往后退进雾里，" + A + "隐身{e_inv}秒" + E +
                  "，之后" + A + "{e_as_t}秒" + E + "攻速" + A + "+{e_as}%" + E + "。",
        "ult": "单片镜后的眼睛看穿对方，手套碰过的刀成了神器飞出：造成" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "，之后" + A +
               "{r_t}秒" + E + "里对方受到的伤害增加" + A + "{r_amp}%" + E + "。",
        "names": ("飞刀扇", "伦敦之雾", "亲爱的神"),
    },
    "zh-hant": {
        "name": "開膛手傑克",
        "attack": "擲出飛刀，造成" + AD + O + "物理傷害" + E + "。" + O + "心之色" + E + "：他看得見人心的顏色，恐懼藏不住：對生命低於" + A +
                  "{p_hp}%" + E + "的敵方英雄，傷害" + A + "+{p_dmg}%" + E + "。",
        "skill": "擲出一扇飛刀，前方扇形裡的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%" + E + "。",
        "skill2": "撐開被手套變成神器的傘，到收傘受到的傷害降低" + A + "{e_dr}%" + E + "；往後退進霧裡，" + A + "隱身{e_inv}秒" + E +
                  "，之後" + A + "{e_as_t}秒" + E + "攻速" + A + "+{e_as}%" + E + "。",
        "ult": "單片鏡後的眼睛看穿對方，手套碰過的刀成了神器飛出：造成" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "，之後" + A +
               "{r_t}秒" + E + "裡對方受到的傷害增加" + A + "{r_amp}%" + E + "。",
        "names": ("飛刀扇", "倫敦之霧", "親愛的神"),
    },
    "en": {
        "name": "Jack the Ripper",
        "attack": "Throws a knife for " + AD + " " + O + "physical damage" + E + ". " + O + "Colours of the Heart" + E + ": he sees "
                  "the colour of every heart, and fear does not hide - " + A + "+{p_dmg}%" + E + " damage to enemy champions "
                  "below " + A + "{p_hp}%" + E + " health.",
        "skill": "Throws a fan of knives: enemies in a cone take " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E +
                 " and are " + R + "slowed {q_slow}%" + E + ".",
        "skill2": "Opens an umbrella his gloves made divine, " + A + "{e_dr}%" + E + " less damage until it closes, then steps "
                  "back into the fog: " + A + "invisible for {e_inv}s" + E + ", then " + A + "+{e_as}%" + E + " attack speed for " +
                  A + "{e_as_t}s" + E + ".",
        "ult": "The eye behind the monocle reads the target; a knife his gloves touched flies as a divine weapon for " +
               phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + ", and for " + A + "{r_t}s" + E + " the target "
               "takes " + A + "{r_amp}%" + E + " more damage from everyone.",
        "names": ("Knife Fan", "London Fog", "Dear God"),
    },
    "ko": {
        "name": "잭 더 리퍼",
        "attack": "단검을 던져 " + AD + " " + O + "물리 피해" + E + ". " + O + "마음의 색" + E + ": 사람의 마음이 색으로 보인다. 체력이 " +
                  A + "{p_hp}%" + E + " 아래인 적 챔피언에게 피해 " + A + "+{p_dmg}%" + E + ".",
        "skill": "단검을 부채꼴로 던져 앞쪽 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "와 " + R + "{q_slow}% 둔화" +
                 E + ".",
        "skill2": "장갑으로 신기가 된 우산을 펼쳐 접을 때까지 받는 피해 " + A + "{e_dr}%" + E + " 감소, 뒤로 물러나 안개 속으로: " + A +
                  "{e_inv}초 은신" + E + ", 이후 " + A + "{e_as_t}초" + E + " 동안 공격 속도 " + A + "+{e_as}%" + E + ".",
        "ult": "외알 안경 너머의 눈이 상대를 꿰뚫어 보고, 장갑이 닿은 칼이 신기가 되어 날아가 " + phys("r_dmg", "r_ad") + " " + O +
               "물리 피해" + E + ". 이후 " + A + "{r_t}초" + E + " 동안 상대가 받는 피해 " + A + "+{r_amp}%" + E + ".",
        "names": ("칼날 부채", "런던의 안개", "디어 갓"),
    },
    "ja": {
        "name": "切り裂きジャック",
        "attack": "ナイフを投げ" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "心の色" + E + "：人の心が色で見える。体力" + A +
                  "{p_hp}%" + E + "未満の敵チャンピオンへのダメージ" + A + "+{p_dmg}%" + E + "。",
        "skill": "ナイフを扇状に投げ、前方の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{q_slow}%スロウ" +
                 E + "。",
        "skill2": "手袋で神器となった傘を開き、閉じるまで被ダメージ" + A + "{e_dr}%" + E + "軽減。霧の中へ退き" + A + "{e_inv}秒透明化" +
                  E + "、その後" + A + "{e_as_t}秒" + E + "攻撃速度" + A + "+{e_as}%" + E + "。",
        "ult": "片眼鏡の奥の目が相手を見抜き、手袋が触れたナイフが神器となって飛ぶ：" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" +
               E + "、以後" + A + "{r_t}秒" + E + "相手の被ダメージ" + A + "+{r_amp}%" + E + "。",
        "names": ("ナイフの扇", "ロンドンの霧", "ディア・ゴッド"),
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
    f"{ID}_e_back": [(SFX + "cloak", 0.5, 0.0)],
    f"{ID}_e_close": [(SFX + "close", 0.45, 0.0)],
    f"{ID}_r1": [(SFX + "glint", 0.5, 0.0)],
    f"{ID}_r2": [(SFX + "artifact", 0.55, 0.0)],
    f"{ID}_r_hit": [(SFX + "ult_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/jack.rs）：死的时候披风和身子落地（Codex 的 cues：0.827 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.827)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)]
       for x in ("showtime", "delight", "reveal", "rule", "color", "etiquette")},
}


def values(p):
    v = {k: p[k] for k in ("p_hp", "p_dmg", "q_dmg", "q_ad", "q_slow", "e_dr", "e_as", "r_dmg", "r_ad", "r_amp")}
    for k in ("e_inv", "e_as_t", "r_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "jack", "tools/kit/seed_jack_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
