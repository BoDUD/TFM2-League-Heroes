"""别西卜的文本（五种语言）、sound_info 和 champion_view，数字取自 build_beelzebub.P。

    python tools/kit/setup_beelzebub.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_beelzebub（说明和技能名）、sound/sfx/ragnarok_beelzebub_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：别西卜 / 別西卜 / Beelzebub / 벨제붑 / ベルゼブブ；技能名照终末的女武神和 Codex 的交付：暴食的堕天使（骸骨杖放的振动波）、
地狱之门（振动屏障）、虚神〈混沌〉；被动「振动」写在普攻说明里。图标照 Codex 的交付（assets/source/beelzebub/runtime/icons：wave、
guard、chaos；palm 那张是普攻，图标位只有三个，不装）。
声音：Codex 的交付（beelzebub_packs/outputs/beelzebub_assets_done.zip）：用到 14 条原创音效（振动掌的出手和命中、杖端蓄能、
主波释放、波纹增殖、振动波命中、屏障的展开、格挡和散去、混沌的黑核、爆发和命中、骸骨杖落地、倒地）和五句官方日语原声
（浪川大辅）；振动掌的起手、受击两条没用上。音频不进仓库，tools/kit/seed_beelzebub_audio.py 从交付复制到 ragnarok/sound/sfx/，
安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_beelzebub import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"


def mag(d, r):
    """dd + 法强图标 rr%（魔法伤害的数字）。"""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛在脚底上 103 格、往前 6 格（PPU 2.75：-37、2）；百科中心照 --centers 的规则（实心顶 -39.3 -> -12）；
# 选人卡 y = -39 - 头顶，量头不量杖：头发顶在 -29.3（-31.3 是骸骨杖的杖头）-> -10
VIEW = {"face": {"x": 2, "y": -37}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "别西卜",
        "attack": "振动掌，造成" + AD + O + "物理伤害" + E + "加" + mag("a_dmg", "a_ap") + M + "魔法伤害" + E + "。" + O + "恶魔的振翅" + E +
                  "：被他的技能打中的敌人" + A + "{p_t}秒" + E + "内魔抗" + A + "-{p_mr}%" + E + "。",
        "skill": "骸骨杖放出振动波，一条线上的敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "减速{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "展开振动屏障：" + S + "护盾{e_sh}" + E + " + " + APi + S + "{e_sh_ap}%" + E + "（" + A + "{e_t}秒" + E + "），" + A +
                  "{e_cc}秒" + E + "不受控制；随后屏障震开，身边的敌人受到" + mag("e_dmg", "e_ap") + M + "魔法伤害" + E + "并" + R +
                  "减速{e_slow}%" + E + "。",
        "ult": "压缩出虚神的黑核（不受控制、减伤" + A + "{r_dr}%" + E + "），把身边的敌人往里拉，再爆发：周围的敌人受到" +
               mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "并" + R + "眩晕{r_stun}秒" + E + "；他自己也被反噬，失去" + A + "{r_cost}%" + E + "最大生命。",
        "names": ("暴食的堕天使", "地狱之门扉", "虚神（卡俄斯）"),
    },
    "zh-hant": {
        "name": "別西卜",
        "attack": "振動掌，造成" + AD + O + "物理傷害" + E + "加" + mag("a_dmg", "a_ap") + M + "魔法傷害" + E + "。" + O + "惡魔的振翅" + E +
                  "：被他的技能打中的敵人" + A + "{p_t}秒" + E + "內魔抗" + A + "-{p_mr}%" + E + "。",
        "skill": "骸骨杖放出振動波，一條線上的敵人受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "減速{q_slow}%" + E +
                 "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "展開振動屏障：" + S + "護盾{e_sh}" + E + " + " + APi + S + "{e_sh_ap}%" + E + "（" + A + "{e_t}秒" + E + "），" + A +
                  "{e_cc}秒" + E + "不受控制；隨後屏障震開，身邊的敵人受到" + mag("e_dmg", "e_ap") + M + "魔法傷害" + E + "並" + R +
                  "減速{e_slow}%" + E + "。",
        "ult": "壓縮出虛神的黑核（不受控制、減傷" + A + "{r_dr}%" + E + "），把身邊的敵人往裡拉，再爆發：周圍的敵人受到" +
               mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "並" + R + "暈眩{r_stun}秒" + E + "；他自己也被反噬，失去" + A + "{r_cost}%" + E + "最大生命。",
        "names": ("暴食的墮天使", "地獄之門扉", "虛神（卡俄斯）"),
    },
    "en": {
        "name": "Beelzebub",
        "attack": "A vibrating palm: " + AD + " " + O + "physical damage" + E + " plus " + mag("a_dmg", "a_ap") + " " + M +
                  "magic damage" + E + ". " + O + "Palmyra, Devil's Beating Wings" + E + ": enemies his skills hit lose " + A + "{p_mr}%" + E +
                  " magic resist for " + A + "{p_t}s" + E + ".",
        "skill": "His bone staff sends out a vibration wave: enemies on a line take " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + " and are " + R + "slowed {q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "He raises a vibrating barrier: a " + S + "{e_sh}" + E + " + " + APi + S + "{e_sh_ap}%" + E + " " + S + "shield" + E +
                  " for " + A + "{e_t}s" + E + ", unstoppable for " + A + "{e_cc}s" + E + ". Then it shakes apart: enemies around "
                  "him take " + mag("e_dmg", "e_ap") + " " + M + "magic damage" + E + " and are " + R + "slowed {e_slow}%" + E + ".",
        "ult": "He compresses the black core of the False God (unstoppable, " + A + "{r_dr}%" + E + " less damage), pulls nearby "
               "enemies in and bursts: enemies around him take " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E +
               " and are " + R + "stunned for {r_stun}s" + E + "; it tears into him too, " + A + "{r_cost}%" + E + " of his max health.",
        "names": ("Fallen Angel of Gluttony", "Gates of Hell", "False God: Chaos"),
    },
    "ko": {
        "name": "벨제붑",
        "attack": "진동 장타로 " + AD + " " + O + "물리 피해" + E + " + " + mag("a_dmg", "a_ap") + " " + M + "마법 피해" + E + ". " + O +
                  "악마의 날갯짓" + E + ": 그의 스킬에 맞은 적은 " + A + "{p_t}초" + E + " 동안 마법 저항력 " + A + "-{p_mr}%" + E + ".",
        "skill": "해골 지팡이로 진동파를 쏘아 일직선의 적에게 " + mag("q_dmg", "q_ap") + " " + M + "마법 피해" + E + "와 " + R +
                 "{q_slow}% 둔화" + E + "(" + A + "{q_slow_t}초" + E + ").",
        "skill2": "진동 장벽을 펼쳐 " + S + "보호막 {e_sh}" + E + " + " + APi + S + "{e_sh_ap}%" + E + "(" + A + "{e_t}초" + E + "), " +
                  A + "{e_cc}초" + E + " 저지 불가. 이어 장벽이 흔들려 주변 적에게 " + mag("e_dmg", "e_ap") + " " + M + "마법 피해" + E +
                  "와 " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "허신의 검은 핵을 압축해(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소) 주변 적을 끌어당긴 뒤 폭발: 주변 적에게 " +
               mag("r_dmg", "r_ap") + " " + M + "마법 피해" + E + "와 " + R + "{r_stun}초 기절" + E + ". 자신도 반동으로 최대 체력 " + A + "{r_cost}%" + E + " 잃음.",
        "names": ("폭식의 타천사", "지옥의 문", "허신(카오스)"),
    },
    "ja": {
        "name": "ベルゼブブ",
        "attack": "振動の掌で" + AD + "の" + O + "物理ダメージ" + E + "＋" + mag("a_dmg", "a_ap") + "の" + M + "魔法ダメージ" + E + "。" + O +
                  "悪魔の羽ばたき" + E + "：スキルが当たった敵は" + A + "{p_t}秒" + E + "魔法防御" + A + "-{p_mr}%" + E + "。",
        "skill": "骸骨の杖から振動波を放ち、一直線の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R +
                 "{q_slow}%スロウ" + E + "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "振動の障壁を張り" + S + "シールド{e_sh}" + E + "＋" + APi + S + "{e_sh_ap}%" + E + "（" + A + "{e_t}秒" + E + "）、" + A +
                  "{e_cc}秒" + E + "行動妨害無効。続けて障壁が弾け、周りの敵に" + mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E +
                  "と" + R + "{e_slow}%スロウ" + E + "。",
        "ult": "虚神の黒核を圧縮し（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）周りの敵を引き寄せて炸裂：周囲の敵に" +
               mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{r_stun}秒スタン" + E + "。自身も反動で最大体力の" + A + "{r_cost}%" + E + "を失う。",
        "names": ("暴食の堕天使", "地獄の門扉", "虚神（カオス）"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_beelzebub 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "palm_cut", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "palm_hit", 0.45, 0.0)],
    f"{ID}_q_load": [(SFX + "wave_charge", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "wave", 0.5, 0.0)],
    f"{ID}_q_ripple": [(SFX + "ripples", 0.45, 0.0)],
    f"{ID}_q_hit": [(SFX + "wave_hit", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "guard_raise", 0.5, 0.0)],
    f"{ID}_e_block": [(SFX + "guard_block", 0.5, 0.0)],
    f"{ID}_e_hit": [(SFX + "wave_hit", 0.45, 0.0)],
    f"{ID}_e_fade": [(SFX + "guard_fade", 0.45, 0.0)],
    f"{ID}_r_load": [(SFX + "chaos_charge", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "chaos_burst", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "chaos_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/beelzebub.rs）：死的时候骸骨杖落地、身子着地（Codex 的 cues：0.501 / 0.846 秒）和配音
    f"{ID}_dead": [(SFX + "staff_land", 0.45, 0.501), (SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("interest", "taunt", "guard", "oath", "win")},
}


def values(p):
    v = {k: p[k] for k in ("a_dmg", "a_ap", "p_mr", "q_dmg", "q_ap", "q_slow", "e_sh", "e_sh_ap", "e_dmg", "e_ap",
                           "e_slow", "r_dr", "r_dmg", "r_ap", "r_cost")}
    for k in ("p_t", "q_slow_t", "e_t", "e_cc", "r_stun"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "beelzebub", "tools/kit/seed_beelzebub_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
