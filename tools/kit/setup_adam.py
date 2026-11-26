"""亚当的文本（五种语言）、sound_info 和 champion_view，数字取自 build_adam.P。

    python tools/kit/setup_adam.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_adam（说明和技能名）、sound/sfx/ragnarok_adam_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：终末的女武神里的叫法，亚当 / 亞當 / Adam / アダム / 아담；技能名对应 Codex 的四张图标（assets/source/adam/）：
眼睛是神虚视（被动的记录写在普攻说明里），后仰躲拳是神虚视（Q），指虎和模仿标记是模仿反击，打碎钟面的是超越时间之拳。
声音：Codex 的交付（assets/source/adam/README.md）：16 条原创音效（普攻三组拳风和命中、睁眼、闪避、模仿标记、反击的
拳风和命中、时间之拳的蓄势 / 释放 / 命中、眼睛吃力、倒地）和七句官方日语原声（齐藤壮马）。音频不进仓库，
tools/kit/seed_adam_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_adam import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上 42 格 = 25 个游戏像素、往前 4 格 = 2；
# 头顶离脚底 54 格 = 33 个游戏像素，百科中心按 bp_card_audit 的规矩是 -6（和宙斯老人一样矮）；选人卡用默认的 -12
# 2026-11-22 整包放大 1.2 倍（「放大到联盟大小」，import 的 PPU 除以 1.2）以后重定：头像点乘 1.2；百科中心照
# bp_card_audit.py --centers 的规则（和联盟一样）；选人卡照它的规则 y = -39 - 头顶（量头，不量头顶上的刀、叉、锤、翎子）
VIEW = {"face": {"x": 2, "y": -30}, "center": {"x": 0, "y": -9}, "banpick_center": {"x": 0, "y": -11}}

TEXT = {
    "zh-hans": {
        "name": "亚当",
        "attack": "快拳，造成" + AD + O + "物理伤害" + E + "。" + O + "神虚视" + E + "读过一招就记下来（" + A + "{q_rec}秒" + E +
                  "），有记录时" + O + "模仿反击" + E + "会复刻那一招。",
        "skill": "睁开神虚视读出对手的动作，闪身躲开：" + A + "{q_t}秒" + E + "内普攻全部落空，受到的技能伤害降低" + A + "{q_sdr}%" +
                 E + "，并记下一招。",
        "skill2": "照着宙斯的黄昏流星群反击，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "。有记录时复刻那一招：再加" + O + "{e_cdmg}" + E +
                  "和目标" + A + "{e_hp}%" + E + "最大生命值的物理伤害，并" + R + "眩晕{e_stun}秒" + E + "，用掉记录。",
        "ult": "从宙斯那里学来的拳：蓄势" + A + "{r_go}秒" + E + "（不受控制，受到的伤害降低" + A + "{r_dr}%" + E +
               "），然后朝目标打出一道拳劲，路上的敌人受到" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并被" + R +
               "击飞{r_up}秒" + E + "。",
        "names": ("神虚视", "复刻·黄昏流星群", "超越时间之拳"),
    },
    "zh-hant": {
        "name": "亞當",
        "attack": "快拳，造成" + AD + O + "物理傷害" + E + "。" + O + "神虛視" + E + "讀過一招就記下來（" + A + "{q_rec}秒" + E +
                  "），有記錄時" + O + "模仿反擊" + E + "會複刻那一招。",
        "skill": "睜開神虛視讀出對手的動作，閃身躲開：" + A + "{q_t}秒" + E + "內普攻全部落空，受到的技能傷害降低" + A + "{q_sdr}%" +
                 E + "，並記下一招。",
        "skill2": "照著宙斯的黃昏流星群反擊，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "。有記錄時複刻那一招：再加" + O + "{e_cdmg}" + E +
                  "和目標" + A + "{e_hp}%" + E + "最大生命值的物理傷害，並" + R + "暈眩{e_stun}秒" + E + "，用掉記錄。",
        "ult": "從宙斯那裡學來的拳：蓄勢" + A + "{r_go}秒" + E + "（不受控制，受到的傷害降低" + A + "{r_dr}%" + E +
               "），然後朝目標打出一道拳勁，路上的敵人受到" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並被" + R +
               "擊飛{r_up}秒" + E + "。",
        "names": ("神虛視", "復刻·黃昏流星群", "超越時間之拳"),
    },
    "en": {
        "name": "Adam",
        "attack": "A quick jab for " + AD + " " + O + "physical damage" + E + ". " + O + "God Reader" + E +
                  " remembers a move it has read (" + A + "{q_rec}s" + E + "); with one remembered, " + O + "Mimic Counter" +
                  E + " copies it.",
        "skill": "Opens his God Reader eyes and slips aside: for " + A + "{q_t}s" + E + " basic attacks miss him and skills "
                 "deal " + A + "{q_sdr}%" + E + " less damage; he remembers a move.",
        "skill2": "A counter with Zeus's own Meteor Jab for " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + ". With a remembered move "
                  "he copies it: " + O + "{e_cdmg}" + E + " more plus " + A + "{e_hp}%" + E + " of the target's max health and a " +
                  R + "{e_stun}s stun" + E + ", using the move up.",
        "ult": "The punch he copied from Zeus: winds up for " + A + "{r_go}s" + E + " (unstoppable, taking " + A + "{r_dr}%" + E +
               " less damage), then drives a blast at the target that deals " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + " to enemies in its path and " + R + "knocks them up for {r_up}s" + E + ".",
        "names": ("Eyes of the Lord", "Copied Meteor Jab", "Fist That Transcends Time"),
    },
    "ko": {
        "name": "아담",
        "attack": "빠른 잽으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "신허시" + E + "로 읽은 기술은 " + A + "{q_rec}초" + E +
                  " 동안 기억하며, 기억이 있으면 " + O + "모방 반격" + E + "이 그 기술을 따라 한다.",
        "skill": "신허시로 상대의 움직임을 읽고 피한다: " + A + "{q_t}초" + E + " 동안 기본 공격이 모두 빗나가고 받는 스킬 피해 " + A +
                 "{q_sdr}%" + E + " 감소, 기술 하나를 기억한다.",
        "skill2": "제우스의 황혼유성군을 따라 반격해 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + ". 기억한 기술이 있으면 따라 해서 " + O +
                  "{e_cdmg}" + E + "와 대상 최대 체력의 " + A + "{e_hp}%" + E + " 피해를 더하고 " + R + "{e_stun}초 기절" + E +
                  "시키며 기억을 쓴다.",
        "ult": "제우스에게서 배운 주먹: " + A + "{r_go}초" + E + " 동안 힘을 모은 뒤(군중 제어 면역, 받는 피해 " + A + "{r_dr}%" + E +
               " 감소) 대상을 향해 주먹 기운을 날려 경로의 적에게 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R +
               "{r_up}초 에어본" + E + ".",
        "names": ("신허시", "복제·황혼유성군", "시간을 넘어선 주먹"),
    },
    "ja": {
        "name": "アダム",
        "attack": "素早いジャブで" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "神虚視" + E + "で読んだ技を" + A + "{q_rec}秒" +
                  E + "覚え、覚えていれば" + O + "模倣カウンター" + E + "がその技を写す。",
        "skill": "神虚視で相手の動きを読みかわす：" + A + "{q_t}秒" + E + "間通常攻撃はすべて外れ、受けるスキルダメージ" + A +
                 "{q_sdr}%" + E + "軽減、技をひとつ覚える。",
        "skill2": "ゼウスの黄昏流星群を写したカウンターで" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "。覚えた技があれば写して" + O +
                  "{e_cdmg}" + E + "と対象の最大体力" + A + "{e_hp}%" + E + "を上乗せし" + R + "{e_stun}秒スタン" + E + "、記憶を使う。",
        "ult": "ゼウスから写した拳：" + A + "{r_go}秒" + E + "溜め（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E +
               "軽減）、標的へ拳圧を放ち、通り道の敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
               "{r_up}秒のノックアップ" + E + "。",
        "names": ("神虚視", "模倣・黄昏流星群", "時を超える拳"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_adam 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "jab_wind_1", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "jab_hit_1", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "eyes_on", 0.5, 0.0)],
    f"{ID}_q_dodge": [(SFX + "dodge", 0.5, 0.0)],
    f"{ID}_q_strain": [(SFX + "eye_strain", 0.35, 0.0)],
    f"{ID}_e_mark": [(SFX + "copy_ready", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "counter_wind", 0.5, 0.0)],
    f"{ID}_e_hit": [(SFX + "counter_hit", 0.55, 0.0)],
    f"{ID}_r_charge": [(SFX + "time_charge", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "time_release", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "time_hit", 0.55, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/adam.rs）：死的时候的倒地声（死亡动作第 6 帧 0.62 秒着地）和配音
    f"{ID}_dead": [(SFX + "body_fall", 0.5, 0.62)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)]
       for x in ("introduce", "recognized", "first_human", "duel_resolve", "unfazed", "full_force", "protect")},
}


def values(p):
    v = {k: p[k] for k in ("q_sdr", "e_dmg", "e_ad", "e_cdmg", "e_hp", "r_dr", "r_dmg", "r_ad")}
    for k in ("q_rec", "q_t", "e_stun", "r_go", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "adam", "tools/kit/seed_adam_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
