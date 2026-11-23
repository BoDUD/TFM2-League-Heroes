"""阿波罗的文本（五种语言）、sound_info 和 champion_view，数字取自 build_apollo.P。

    python tools/kit/setup_apollo.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_apollo（说明和技能名）、sound/sfx/ragnarok_apollo_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：阿波罗 / 阿波羅 / Apollo / 아폴론 / アポロン；技能名照 Codex 的交付（日轮拳、阿尔忒弥斯之丝、光之矢、银箭突进）；被动「日轮」
写在普攻说明里。图标照 Codex 的交付（assets/source/apollo/runtime/icons：threads、arrow、artemis；strike 那张是普攻，图标位只有
三个，不装）。
声音：Codex 的交付（apollo_packs/outputs/apollo_assets_done.zip）：用到 15 条原创音效（出拳和命中、光丝的汇聚、投出、收束和松开、
光弓成形、拉弦、放箭和命中、女神像显现、光索蓄力、银箭离弦和命中、着地）和三句官方日语原声（鈴村健一）；出拳预备那条没用上
（普攻的效果在打到那一拍才放，预备在它前面）。音频不进仓库，tools/kit/seed_apollo_audio.py 从交付复制到 ragnarok/sound/sfx/，
安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_apollo import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"

# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛在脚底上 99 格、往前 7 格（PPU 2.75：-36、3）；百科中心照 --centers 的规则（实心顶 -40.0 -> -13）；
# 选人卡 y = -39 - 头顶（-30.7）-> -8
VIEW = {"face": {"x": 3, "y": -36}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "阿波罗",
        "attack": "日轮拳，造成" + AD + O + "物理伤害" + E + "。" + O + "日轮" + E + "：每放一个技能，" + A + "{p_t}秒" + E +
                  "内下一拳额外造成" + phys("p_dmg", "p_ad") + O + "物理伤害" + E + "。",
        "skill": "投出阿尔忒弥斯之丝缠住目标，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "定身{q_bind}秒" + E +
                 "。",
        "skill2": "光弓成形，射出一支追着目标飞的光箭，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "。",
        "ult": "女神像拉开光索，把自己当作银箭射向目标（不受控制、减伤" + A + "{r_dr}%" + E + "），撞上的敌人受到" +
               phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并" + R + "眩晕{r_stun}秒" + E + "。",
        "names": ("阿尔忒弥斯之丝", "光之矢", "银箭突进"),
    },
    "zh-hant": {
        "name": "阿波羅",
        "attack": "日輪拳，造成" + AD + O + "物理傷害" + E + "。" + O + "日輪" + E + "：每放一個技能，" + A + "{p_t}秒" + E +
                  "內下一拳額外造成" + phys("p_dmg", "p_ad") + O + "物理傷害" + E + "。",
        "skill": "投出阿耳忒彌斯之絲纏住目標，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "定身{q_bind}秒" + E +
                 "。",
        "skill2": "光弓成形，射出一支追著目標飛的光箭，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "。",
        "ult": "女神像拉開光索，把自己當作銀箭射向目標（不受控制、減傷" + A + "{r_dr}%" + E + "），撞上的敵人受到" +
               phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並" + R + "暈眩{r_stun}秒" + E + "。",
        "names": ("阿耳忒彌斯之絲", "光之矢", "銀箭突進"),
    },
    "en": {
        "name": "Apollo",
        "attack": "A sun-wheel punch: " + AD + " " + O + "physical damage" + E + ". " + O + "Sun Wheel" + E + ": after each skill "
                  "his next punch within " + A + "{p_t}s" + E + " deals " + phys("p_dmg", "p_ad") + " more " + O +
                  "physical damage" + E + ".",
        "skill": "He casts Artemis's Thread round the target: " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E +
                 " and a " + R + "{q_bind}s root" + E + ".",
        "skill2": "A bow of light forms and looses a homing arrow: " + phys("e_dmg", "e_ad") + " " + O + "physical damage" +
                  E + ".",
        "ult": "Artemis's statue draws the cords of light and shoots him at the target as a silver arrow (unstoppable, " + A +
               "{r_dr}%" + E + " less damage): the enemy he strikes takes " + phys("r_dmg", "r_ad") + " " + O +
               "physical damage" + E + " and a " + R + "{r_stun}s stun" + E + ".",
        "names": ("Artemis's Thread", "Arrow of Light", "Silver Arrow"),
    },
    "ko": {
        "name": "아폴론",
        "attack": "일륜권으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "일륜" + E + ": 스킬을 쓰면 " + A + "{p_t}초" + E +
                  " 안의 다음 주먹이 " + phys("p_dmg", "p_ad") + " " + O + "물리 피해" + E + "를 추가로 줌.",
        "skill": "아르테미스의 실로 대상을 묶어 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + "와 " + R + "{q_bind}초 속박" +
                 E + ".",
        "skill2": "빛의 활을 만들어 대상을 쫓는 빛의 화살을 쏴 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + ".",
        "ult": "여신상이 빛의 줄을 당겨 자신을 은빛 화살로 쏘아 보냄(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소). 부딪힌 적에게 " +
               phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_stun}초 기절" + E + ".",
        "names": ("아르테미스의 실", "빛의 화살", "은빛 화살 돌진"),
    },
    "ja": {
        "name": "アポロン",
        "attack": "日輪の拳で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "日輪" + E + "：スキルを使うと" + A + "{p_t}秒" + E +
                  "以内の次の拳が" + phys("p_dmg", "p_ad") + "の" + O + "物理ダメージ" + E + "を追加。",
        "skill": "アルテミスの糸で対象を縛り、" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{q_bind}秒スネア" +
                 E + "。",
        "skill2": "光の弓を作り、対象を追う光の矢を放って" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "。",
        "ult": "女神像が光の綱を引き、自分を銀の矢として対象へ放つ（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）。"
               "当たった敵に" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{r_stun}秒スタン" + E + "。",
        "names": ("アルテミスの糸", "光の矢", "銀の矢"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_apollo 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "jab", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "jab_hit", 0.45, 0.0)],
    f"{ID}_q_charge": [(SFX + "thread_charge", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "thread_cast", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "thread_bind", 0.5, 0.0)],
    f"{ID}_q_fade": [(SFX + "thread_fade", 0.4, 0.0)],
    f"{ID}_e_form": [(SFX + "bow_form", 0.5, 0.0)],
    f"{ID}_e_draw": [(SFX + "bow_draw", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "arrow_fire", 0.5, 0.0)],
    f"{ID}_e_hit": [(SFX + "arrow_hit", 0.5, 0.0)],
    f"{ID}_r_show": [(SFX + "artemis_manifest", 0.55, 0.0)],
    f"{ID}_r_load": [(SFX + "artemis_tension", 0.5, 0.0)],
    f"{ID}_r": [(SFX + "sun_dash", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "sun_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/apollo.rs）：死的时候着地（Codex 的 cues：0.846 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("select", "challenge", "silver_arrow")},
}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ad", "q_dmg", "q_ad", "e_dmg", "e_ad", "r_dr", "r_dmg", "r_ad")}
    for k in ("p_t", "q_bind", "r_stun"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "apollo", "tools/kit/seed_apollo_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
