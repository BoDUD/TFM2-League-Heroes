"""零福／波旬的文本（五种语言）、sound_info 和 champion_view，数字取自 build_zerofuku.P。

    python tools/kit/setup_zerofuku.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_zerofuku（说明和技能名）、sound/sfx/ragnarok_zerofuku_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：零福 / 零福 / Zerofuku / 제로후쿠 / 零福（波旬是他破茧以后的形态，写在大招里）；技能名照终末的女武神和 Codex 的交付，
一个技能位两个形态各一个名字：斧爻（日文读音就是「不幸」）／魔钻、怨气冲击／魔刃碎击、破茧／魔臂横断；被动「不幸」「吞噬」
写在普攻说明里。图标照 Codex 的交付（assets/source/zerofuku/runtime/icons：cleaver、misfortune、cocoon；drill 那张是波旬的 Q，
图标位只有三个，不装）。
声音：Codex 的交付（zerofuku_packs/outputs/zerofuku_assets_done.zip）：18 条原创音效（斧爻的横砍和命中、吸聚不幸、重斧落下和
落地、怨气涌出和命中、合茧、破茧、臂刃的斩击和命中、魔钻的蓄力、钻出和命中、魔刃砸下、魔臂横断和命中、倒地）和六句官方日语
原声（零福四句，村瀬歩；波旬两句，稻田彻）。音频不进仓库，tools/kit/seed_zerofuku_audio.py 从交付复制到 ragnarok/sound/sfx/，
安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zerofuku import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 102 格 = 31 个游戏像素、往前 16 格 = 5；
# 百科中心照雷电（1 倍待机的实心顶上方 23 格）：实心顶 -35 -> -12；选人卡用默认的 -12
VIEW = {"face": {"x": 5, "y": -31}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "零福",
        "attack": "零福斧爻横砍、波旬臂刃横斩，造成" + AD + O + "物理伤害" + E + "。" + O + "不幸" + E + "：零福打中的敌人" + A +
                  "{p_t}秒" + E + "里受到的伤害" + A + "+{p_amp}%" + E + "。" + O + "吞噬" + E + "：波旬" + A + "吸血{h_vamp}%" + E + "。",
        "skill": "零福：斧爻吸了不幸变大后落下，前方的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R +
                 "减速{q_slow}%" + E + "，挂上不幸。波旬：前臂化成魔钻直线冲过去，路上的敌人受到" + phys("q2_dmg", "q2_ad") + O +
                 "物理伤害" + E + "并被" + R + "击飞" + E + "。",
        "skill2": "零福：怨气从脚下往前涌，一条线上的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并被" + R + "击飞" + E +
                  "。波旬：单臂化刃从上砸下，前方的敌人受到" + phys("e2_dmg", "e2_ad") + O + "物理伤害" + E + "并" + R +
                  "眩晕{e2_stun}秒" + E + "。",
        "ult": "零福被暗茧吞没（不受控制、减伤" + A + "{r_dr}%" + E + "），波旬破茧而出：回复" + phys("r_heal", "r_heal_ad") +
               "生命，这条命攻击力" + A + "+{h_atk}%" + E + "、攻速" + A + "+{h_as}%" + E + "、移速" + A + "+{h_ms}%" + E + "、双抗" + A +
               "+{h_res}" + E + "。再放是魔臂横断：前方的敌人受到" + phys("r2_dmg", "r2_ad") + "加最大生命" + O + "{r2_thp}%" + E +
               "的" + O + "物理伤害" + E + "并被" + R + "击飞" + E + "。",
        "names": ("斧爻／魔钻", "怨气冲击／魔刃碎击", "破茧／魔臂横断"),
    },
    "zh-hant": {
        "name": "零福",
        "attack": "零福斧爻橫砍、波旬臂刃橫斬，造成" + AD + O + "物理傷害" + E + "。" + O + "不幸" + E + "：零福打中的敵人" + A +
                  "{p_t}秒" + E + "裡受到的傷害" + A + "+{p_amp}%" + E + "。" + O + "吞噬" + E + "：波旬" + A + "吸血{h_vamp}%" + E + "。",
        "skill": "零福：斧爻吸了不幸變大後落下，前方的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R +
                 "減速{q_slow}%" + E + "，掛上不幸。波旬：前臂化成魔鑽直線衝過去，路上的敵人受到" + phys("q2_dmg", "q2_ad") + O +
                 "物理傷害" + E + "並被" + R + "擊飛" + E + "。",
        "skill2": "零福：怨氣從腳下往前湧，一條線上的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並被" + R + "擊飛" + E +
                  "。波旬：單臂化刃從上砸下，前方的敵人受到" + phys("e2_dmg", "e2_ad") + O + "物理傷害" + E + "並" + R +
                  "暈眩{e2_stun}秒" + E + "。",
        "ult": "零福被暗繭吞沒（不受控制、減傷" + A + "{r_dr}%" + E + "），波旬破繭而出：回復" + phys("r_heal", "r_heal_ad") +
               "生命，這條命攻擊力" + A + "+{h_atk}%" + E + "、攻速" + A + "+{h_as}%" + E + "、移速" + A + "+{h_ms}%" + E + "、雙抗" + A +
               "+{h_res}" + E + "。再放是魔臂橫斷：前方的敵人受到" + phys("r2_dmg", "r2_ad") + "加最大生命" + O + "{r2_thp}%" + E +
               "的" + O + "物理傷害" + E + "並被" + R + "擊飛" + E + "。",
        "names": ("斧爻／魔鑽", "怨氣衝擊／魔刃碎擊", "破繭／魔臂橫斷"),
    },
    "en": {
        "name": "Zerofuku",
        "attack": "Zerofuku hews with the Misery Cleaver, Hajun with his arm blade: " + AD + " " + O + "physical damage" + E +
                  ". " + O + "Misfortune" + E + ": enemies Zerofuku hits take " + A + "{p_amp}%" + E + " more damage for " + A +
                  "{p_t}s" + E + ". " + O + "Devour" + E + ": Hajun has " + A + "{h_vamp}% life steal" + E + ".",
        "skill": "Zerofuku: the cleaver drinks misfortune, grows and falls: enemies in front take " + phys("q_dmg", "q_ad") + " " +
                 O + "physical damage" + E + ", are " + R + "slowed {q_slow}%" + E + " and gain Misfortune. Hajun: his forearm "
                 "turns into a drill and he charges through: enemies on the way take " + phys("q2_dmg", "q2_ad") + " " + O +
                 "physical damage" + E + " and are " + R + "knocked up" + E + ".",
        "skill2": "Zerofuku: grudge surges from his feet: enemies on a line take " + phys("e_dmg", "e_ad") + " " + O +
                  "physical damage" + E + " and are " + R + "knocked up" + E + ". Hajun: an arm becomes a heavy blade and crushes "
                  "down: enemies in front take " + phys("e2_dmg", "e2_ad") + " " + O + "physical damage" + E + " and are " + R +
                  "stunned for {e2_stun}s" + E + ".",
        "ult": "Zerofuku is swallowed by a dark cocoon (unstoppable, " + A + "{r_dr}%" + E + " less damage) and Hajun breaks "
               "out: heals " + phys("r_heal", "r_heal_ad") + ", and for this life " + A + "+{h_atk}%" + E + " attack, " + A +
               "+{h_as}%" + E + " attack speed, " + A + "+{h_ms}%" + E + " speed, " + A + "+{h_res}" + E + " armour and magic "
               "resist. Again as Hajun, Demon Sever: enemies in a cone take " + phys("r2_dmg", "r2_ad") + " + " + O +
               "{r2_thp}%" + E + " max health " + O + "physical damage" + E + " and are " + R + "knocked up" + E + ".",
        "names": ("Misery Cleaver / Demon Drill", "Grudge Surge / Demon Crush", "Cocoon / Demon Sever"),
    },
    "ko": {
        "name": "제로후쿠",
        "attack": "제로후쿠는 부효로, 파순은 팔날로 베어 " + AD + " " + O + "물리 피해" + E + ". " + O + "불행" + E +
                  ": 제로후쿠에게 맞은 적은 " + A + "{p_t}초" + E + " 동안 받는 피해 " + A + "+{p_amp}%" + E + ". " + O + "탐식" + E +
                  ": 파순은 " + A + "생명력 흡수 {h_vamp}%" + E + ".",
        "skill": "제로후쿠: 불행을 빨아 커진 부효를 내려쳐 앞쪽 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", " +
                 R + "{q_slow}% 둔화" + E + ", 불행. 파순: 팔이 마찬이 되어 돌진, 지나간 적에게 " + phys("q2_dmg", "q2_ad") + " " +
                 O + "물리 피해" + E + "와 " + R + "띄워 올림" + E + ".",
        "skill2": "제로후쿠: 발밑에서 원한이 솟아 일직선의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "띄워 올림" + E + ". 파순: 팔날로 내리찍어 앞쪽 적에게 " + phys("e2_dmg", "e2_ad") + " " + O + "물리 피해" + E +
                  "와 " + R + "{e2_stun}초 기절" + E + ".",
        "ult": "검은 고치에 삼켜진 뒤(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소) 파순이 깨어남: " + phys("r_heal", "r_heal_ad") +
               " 회복, 이번 목숨 동안 공격력 " + A + "+{h_atk}%" + E + ", 공속 " + A + "+{h_as}%" + E + ", 이속 " + A + "+{h_ms}%" +
               E + ", 방어·마저 " + A + "+{h_res}" + E + ". 파순이 다시 쓰면 마비 횡단: 부채꼴 적에게 " + phys("r2_dmg", "r2_ad") +
               " + 최대 체력 " + O + "{r2_thp}%" + E + " " + O + "물리 피해" + E + "와 " + R + "띄워 올림" + E + ".",
        "names": ("부효 / 마찬", "원한 충격 / 마인 쇄격", "파견 / 마비 횡단"),
    },
    "ja": {
        "name": "零福",
        "attack": "零福は斧爻、波旬は腕刃で斬り" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "不幸" + E + "：零福が当てた敵は" + A +
                  "{p_t}秒" + E + "被ダメージ" + A + "+{p_amp}%" + E + "。" + O + "呑噬" + E + "：波旬は" + A + "吸血{h_vamp}%" + E + "。",
        "skill": "零福：不幸を吸って大きくなった斧爻を振り下ろし、前方の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E +
                 "と" + R + "{q_slow}%スロウ" + E + "、不幸を付与。波旬：前腕を魔鑽に変えて突進し、通った敵に" +
                 phys("q2_dmg", "q2_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "打ち上げ" + E + "。",
        "skill2": "零福：足元から怨念が湧き、一直線の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "打ち上げ" + E + "。波旬：腕刃で叩き斬り、前方の敵に" + phys("e2_dmg", "e2_ad") + "の" + O + "物理ダメージ" + E +
                  "と" + R + "{e2_stun}秒スタン" + E + "。",
        "ult": "闇の繭に呑まれ（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）波旬が羽化：" + phys("r_heal", "r_heal_ad") +
               "回復、この命の間攻撃" + A + "+{h_atk}%" + E + "・攻速" + A + "+{h_as}%" + E + "・移速" + A + "+{h_ms}%" + E + "・両防御" +
               A + "+{h_res}" + E + "。再使用で魔臂横断：扇形の敵に" + phys("r2_dmg", "r2_ad") + "＋最大体力" + O + "{r2_thp}%" + E +
               "の" + O + "物理ダメージ" + E + "と" + R + "打ち上げ" + E + "。",
        "names": ("斧爻／魔鑽", "怨念衝撃／魔刃砕撃", "破繭／魔臂横断"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_zerofuku 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "chop", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "chop_hit", 0.45, 0.0)],
    f"{ID}_ha": [(SFX + "armblade", 0.45, 0.0)],
    f"{ID}_ha_hit": [(SFX + "armblade_hit", 0.45, 0.0)],
    f"{ID}_q_load": [(SFX + "misfortune", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "cleaver_heavy", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "cleaver_land", 0.5, 0.0)],
    f"{ID}_hq_load": [(SFX + "drill_spool", 0.45, 0.0)],
    f"{ID}_hq": [(SFX + "drill", 0.5, 0.0)],
    f"{ID}_hq_hit": [(SFX + "drill_hit", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "ground", 0.5, 0.0)],
    f"{ID}_e_hit": [(SFX + "ground_hit", 0.5, 0.0)],
    f"{ID}_he": [(SFX + "demon_crush", 0.55, 0.0)],
    f"{ID}_he_hit": [(SFX + "demon_hit", 0.5, 0.0)],
    f"{ID}_r_shell": [(SFX + "shell_rise", 0.55, 0.0)],
    f"{ID}_r_open": [(SFX + "shell_open", 0.6, 0.0)],
    f"{ID}_r2": [(SFX + "demon_finish", 0.6, 0.0)],
    f"{ID}_r2_hit": [(SFX + "demon_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/zerofuku.rs）：死的时候身子着地（Codex 的 cues：0.846 秒，两种形态一样）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + clip, 0.8, 0.0)] for x, clip in (
        ("arrival", "zero_arrival"), ("threat", "zero_threat"), ("why", "zero_why"), ("outburst", "zero_outburst"),
        ("h_why", "hajun_why"), ("h_challenge", "hajun_challenge"))},
}


def values(p):
    v = {k: p[k] for k in ("p_amp", "h_vamp", "q_dmg", "q_ad", "q_slow", "q2_dmg", "q2_ad", "e_dmg", "e_ad", "e2_dmg",
                           "e2_ad", "r_dr", "r_heal", "r_heal_ad", "h_atk", "h_as", "h_ms", "h_res", "r2_dmg", "r2_ad",
                           "r2_thp")}
    for k in ("p_t", "e2_stun"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "zerofuku", "tools/kit/seed_zerofuku_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
