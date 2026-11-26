"""尼古拉·特斯拉的文本（五种语言）、sound_info 和 champion_view，数字取自 build_tesla.P。

    python tools/kit/setup_tesla.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_tesla（说明和技能名）、sound/sfx/ragnarok_tesla_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：尼古拉·特斯拉 / 尼古拉·特斯拉 / Nikola Tesla / 니콜라 테슬라 / ニコラ・テスラ；技能名照终末的女武神和 Codex 的交付：特斯拉步、
神之监狱、双向电光拳；被动「等离子脉冲」写在普攻说明里。图标照 Codex 的交付（assets/source/tesla/runtime/icons：warp、zone、punch；
plasma 那张是普攻，图标位只有三个，不装）。
声音：Codex 的交付（tesla_packs/outputs/tesla_assets_done.zip）：用到 15 条原创音效（出拳和命中、反重力启动、掠行、离场、到达、
落地、监狱的蓄能、展开和运行、双拳的充能、两拳和命中、机甲着地）和八句官方日语原声（古川慎）；拳甲充电那条没用上。音频不进
仓库，tools/kit/seed_tesla_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_tesla import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"


def mag(d, r):
    """dd + 法强图标 rr%（魔法伤害的数字）。"""
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛在脚底上 102 格、往前 10 格（PPU 2.75：-37、4）；百科中心照 --centers 的规则（实心顶 -42.0 -> -15）；
# 选人卡 y = -39 - 头顶（-30.7）-> -8
VIEW = {"face": {"x": 4, "y": -37}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "尼古拉·特斯拉",
        "attack": "机甲重拳，造成" + AD + O + "物理伤害" + E + "。" + O + "等离子脉冲" + E + "：每一拳额外造成" + mag("p_dmg", "p_ap") +
                  M + "魔法伤害" + E + "。",
        "skill": "特斯拉步冲向目标，撞上的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%" + E +
                 "；众神的监狱还在时改为特斯拉跃迁（瞬移到目标身上），造成" + phys("q2_dmg", "q2_ad") + O + "物理伤害" + E + "并" + R + "眩晕{q2_stun}秒" +
                 E + "。",
        "skill2": "在目标那里展开众神的监狱（格玛特利亚领域），里面的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "减速{e_slow}%" +
                  E + "（" + A + "{e_t}秒" + E + "）；这段时间特斯拉步变成瞬移。",
        "ult": "等离子脉冲拳·交叉（不受控制、减伤" + A + "{r_dr}%" + E + "）：第一拳造成" + phys("r1_dmg", "r1_ad") + O + "物理伤害" + E + "并" +
               R + "眩晕{r1_stun}秒" + E + "；右臂跃迁到对手身后，第二拳打出一道电光，线上的敌人受到" + phys("r2_dmg", "r2_ad") + O + "物理伤害" + E +
               "并被" + R + "击飞{r_up}秒" + E + "。",
        "names": ("特斯拉步", "众神的监狱", "等离子脉冲拳·交叉"),
    },
    "zh-hant": {
        "name": "尼古拉·特斯拉",
        "attack": "機甲重拳，造成" + AD + O + "物理傷害" + E + "。" + O + "等離子脈衝" + E + "：每一拳額外造成" + mag("p_dmg", "p_ap") +
                  M + "魔法傷害" + E + "。",
        "skill": "特斯拉步衝向目標，撞上的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%" + E +
                 "；眾神的監獄還在時改為特斯拉躍遷（瞬移到目標身上），造成" + phys("q2_dmg", "q2_ad") + O + "物理傷害" + E + "並" + R + "暈眩{q2_stun}秒" +
                 E + "。",
        "skill2": "在目標那裡展開眾神的監獄（格瑪特利亞領域），裡面的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "減速{e_slow}%" +
                  E + "（" + A + "{e_t}秒" + E + "）；這段時間特斯拉步變成瞬移。",
        "ult": "等離子脈衝拳·交叉（不受控制、減傷" + A + "{r_dr}%" + E + "）：第一拳造成" + phys("r1_dmg", "r1_ad") + O + "物理傷害" + E + "並" +
               R + "暈眩{r1_stun}秒" + E + "；右臂躍遷到對手身後，第二拳打出一道電光，線上的敵人受到" + phys("r2_dmg", "r2_ad") + O + "物理傷害" + E +
               "並被" + R + "擊飛{r_up}秒" + E + "。",
        "names": ("特斯拉步", "眾神的監獄", "等離子脈衝拳·交叉"),
    },
    "en": {
        "name": "Nikola Tesla",
        "attack": "A mech punch: " + AD + " " + O + "physical damage" + E + ". " + O + "Plasma Pulse" + E + ": every punch deals " +
                  mag("p_dmg", "p_ap") + " more " + M + "magic damage" + E + ".",
        "skill": "Tesla Step dashes at the target: enemies he hits take " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E +
                 " and are " + R + "slowed {q_slow}%" + E + ". While the Prison of the Gods stands, Tesla Warp puts him on the target instead: " +
                 phys("q2_dmg", "q2_ad") + " " + O + "physical damage" + E + " and a " + R + "{q2_stun}s stun" + E + ".",
        "skill2": "He raises the Prison of the Gods, the Gematria Zone, where the target stands: enemies inside take " + phys("e_dmg", "e_ad") + " " + O +
                  "physical damage" + E + " and are " + R + "slowed {e_slow}%" + E + " for " + A + "{e_t}s" + E + "; meanwhile Tesla "
                  "Step is Tesla Warp.",
        "ult": "Plasma Pulse Punch Cross (unstoppable, " + A + "{r_dr}%" + E + " less damage): the first deals " + phys("r1_dmg", "r1_ad") + " " +
               O + "physical damage" + E + " and a " + R + "{r1_stun}s stun" + E + "; his right arm warps behind the foe and the second fires a bolt: enemies on its line take " +
               phys("r2_dmg", "r2_ad") + " " + O + "physical damage" + E + " and are " + R + "knocked up for {r_up}s" + E + ".",
        "names": ("Tesla Step", "Prison of the Gods", "Plasma Pulse Punch Cross"),
    },
    "ko": {
        "name": "니콜라 테슬라",
        "attack": "기갑 주먹으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "플라스마 펄스" + E + ": 주먹마다 " + mag("p_dmg", "p_ap") +
                  " " + M + "마법 피해" + E + " 추가.",
        "skill": "테슬라 스텝으로 대상에게 돌진해 부딪힌 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "와 " + R +
                 "{q_slow}% 둔화" + E + ". 신들의 감옥이 있는 동안에는 테슬라 워프로 대상에게 순간이동해 " + phys("q2_dmg", "q2_ad") + " " + O +
                 "물리 피해" + E + "와 " + R + "{q2_stun}초 기절" + E + ".",
        "skill2": "대상 위치에 신들의 감옥(게마트리아 존)을 펼쳐 안의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_slow}% 둔화" + E + "(" + A + "{e_t}초" + E + "). 그동안 테슬라 스텝이 순간이동이 됨.",
        "ult": "플라스마 펄스 펀치 크로스(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소): 첫 주먹은 " + phys("r1_dmg", "r1_ad") + " " + O + "물리 피해" +
               E + "와 " + R + "{r1_stun}초 기절" + E + ", 오른팔을 적 뒤로 워프시켜 둘째 주먹이 전광을 쏘아 일직선의 적에게 " + phys("r2_dmg", "r2_ad") + " " + O +
               "물리 피해" + E + "와 " + R + "{r_up}초 띄워 올림" + E + ".",
        "names": ("테슬라 스텝", "신들의 감옥", "플라스마 펄스 펀치 크로스"),
    },
    "ja": {
        "name": "ニコラ・テスラ",
        "attack": "機甲の拳で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "プラズマ・パルス" + E + "：拳ごとに" + mag("p_dmg", "p_ap") +
                  "の" + M + "魔法ダメージ" + E + "を追加。",
        "skill": "テスラ・ステップで対象へ突進し、ぶつかった敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                 "{q_slow}%スロウ" + E + "。神々の監獄がある間はテスラ・ワープで対象へ瞬間移動し" + phys("q2_dmg", "q2_ad") + "の" + O + "物理ダメージ" +
                 E + "と" + R + "{q2_stun}秒スタン" + E + "。",
        "skill2": "対象の位置に神々の監獄（ゲマトリア・ゾーン）を展開し、中の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_slow}%スロウ" + E + "（" + A + "{e_t}秒" + E + "）。その間テスラ・ステップは瞬間移動になる。",
        "ult": "プラズマパルスパンチ・クロス（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）：一撃目は" + phys("r1_dmg", "r1_ad") + "の" + O +
               "物理ダメージ" + E + "と" + R + "{r1_stun}秒スタン" + E + "、右腕を背後へワープさせた二撃目が電光を放ち一直線の敵に" + phys("r2_dmg", "r2_ad") +
               "の" + O + "物理ダメージ" + E + "と" + R + "{r_up}秒打ち上げ" + E + "。",
        "names": ("テスラ・ステップ", "神々の監獄", "プラズマパルスパンチ・クロス"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_tesla 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "punch", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "punch_hit", 0.45, 0.0)],
    f"{ID}_q_lift": [(SFX + "step_lift", 0.45, 0.0)],
    f"{ID}_q_slide": [(SFX + "step_slide", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "warp_depart", 0.5, 0.0)],
    f"{ID}_q_warp": [(SFX + "warp_arrive", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "punch_hit", 0.5, 0.0)],
    f"{ID}_q_land": [(SFX + "step_land", 0.45, 0.0)],
    f"{ID}_e_charge": [(SFX + "zone_charge", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "zone_deploy", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "zone_loop", 0.45, 0.0)],
    f"{ID}_r_load": [(SFX + "twin_charge", 0.55, 0.0)],
    f"{ID}_r1": [(SFX + "twin_first", 0.55, 0.0)],
    f"{ID}_r_hit1": [(SFX + "punch_hit", 0.55, 0.0)],
    f"{ID}_r2": [(SFX + "twin_second", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "twin_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/tesla.rs）：死的时候机甲着地（Codex 的 cues：0.846 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("open", "evolution", "punch", "twin", "zone", "god", "rally",
                                                       "keep_going")},
}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "q_dmg", "q_ad", "q_slow", "q2_dmg", "q2_ad", "e_dmg", "e_ad", "e_slow",
                           "r_dr", "r1_dmg", "r1_ad", "r2_dmg", "r2_ad")}
    for k in ("q2_stun", "e_t", "r1_stun", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "tesla", "tools/kit/seed_tesla_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
