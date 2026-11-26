"""冲田总司的文本（五种语言）、sound_info 和 champion_view，数字取自 build_okita.P。

    python tools/kit/setup_okita.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）。--check 只打印
每段说明的显示长度和全文。

名字：冲田总司 / 沖田總司 / Okita Soji / 오키타 소지 / 沖田総司；技能名照原作（漫画第十回合）：天然理心流奥义·三段突、鬼子、
天翔散段突；被动「剑之刻」（斯卡尔莫尔德变的刀的性质）写在普攻说明里。图标照 Codex 的交付（assets/source/okita/icons）。
声音：Codex 的交付（okita_packs/outputs/okita_final_assets.zip）：11 条原创音效和 6 句日语台词（Codex 用语音合成做的，
用户 2026-11-26 说要用）。音频不进仓库，tools/kit/seed_okita_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod
挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_okita import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"

# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则：待机第 1 帧的眼睛在脚底上 39 逻辑格、
# 往前 10 格（放大两倍、PPU 8/3：-29、8）；百科中心照 --centers 的规则（实心顶 -41.3 -> -14）；选人卡 y = -39 - 头顶（-31.3）-> -8
VIEW = {"face": {"x": 8, "y": -29}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "冲田总司",
        "attack": "一刀，造成" + AD + O + "物理伤害" + E + "。" + O + "剑之刻" + E + "：刀把他一生的剑技压进一刻，每放一个技能，" +
                  A + "{p_t}秒" + E + "内攻速提高" + A + "{p_as}%" + E + "。",
        "skill": "神速三刺，每刺对前方敌人造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "，第三刺再加" +
                 phys("q3_dmg", "q3_ad") + "。",
        "skill2": "变成鬼子：" + A + "{e_t}秒" + E + "内攻击力提高" + A + "{e_atk}%" + E + "、攻速提高" + A + "{e_as}%" + E +
                  "、移速提高" + A + "{e_ms}%" + E + "。",
        "ult": "极快地突进（不受控制），连刺三下，每刺" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "，第三刺再加目标" + A +
               "{r_thp}%" + E + "最大生命。",
        "names": ("三段突", "鬼子", "天翔散段突"),
    },
    "zh-hant": {
        "name": "沖田總司",
        "attack": "一刀，造成" + AD + O + "物理傷害" + E + "。" + O + "劍之刻" + E + "：刀把他一生的劍技壓進一刻，每放一個技能，" +
                  A + "{p_t}秒" + E + "內攻速提高" + A + "{p_as}%" + E + "。",
        "skill": "神速三刺，每刺對前方敵人造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "，第三刺再加" +
                 phys("q3_dmg", "q3_ad") + "。",
        "skill2": "變成鬼子：" + A + "{e_t}秒" + E + "內攻擊力提高" + A + "{e_atk}%" + E + "、攻速提高" + A + "{e_as}%" + E +
                  "、移速提高" + A + "{e_ms}%" + E + "。",
        "ult": "極快地突進（不受控制），連刺三下，每刺" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "，第三刺再加目標" + A +
               "{r_thp}%" + E + "最大生命。",
        "names": ("三段突", "鬼子", "天翔散段突"),
    },
    "en": {
        "name": "Okita Soji",
        "attack": "A cut: " + AD + " " + O + "physical damage" + E + ". " + O + "Sword Time" + E + ": his blade packs a life's "
                  "swordsmanship into one moment; after each skill he attacks " + A + "{p_as}%" + E + " faster for " + A +
                  "{p_t}s" + E + ".",
        "skill": "Sandanzuki, three godspeed thrusts, each dealing " + phys("q_dmg", "q_ad") + " " + O + "physical damage" +
                 E + " in front of him, the third " + phys("q3_dmg", "q3_ad") + " more.",
        "skill2": "Demon Child: for " + A + "{e_t}s" + E + " he gains " + A + "{e_atk}%" + E + " attack, " + A + "{e_as}%" +
                  E + " attack speed and " + A + "{e_ms}%" + E + " move speed.",
        "ult": "Tensho Sandanzuki: he lunges at blinding speed (unstoppable) and thrusts three times, each for " +
               phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + ", the third plus " + A + "{r_thp}%" + E +
               " of the target's max health.",
        "names": ("Sandanzuki", "Demon Child", "Tensho Sandanzuki"),
    },
    "ko": {
        "name": "오키타 소지",
        "attack": "한 칼에 " + AD + " " + O + "물리 피해" + E + ". " + O + "검의 시간" + E + ": 칼이 평생의 검술을 한순간에 담아, "
                  "스킬을 쓸 때마다 " + A + "{p_t}초" + E + " 동안 공격 속도 " + A + "{p_as}%" + E + " 증가.",
        "skill": "신속의 세 번 찌르기, 찌를 때마다 앞의 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E +
                 ", 세 번째는 " + phys("q3_dmg", "q3_ad") + " 추가.",
        "skill2": "귀자: " + A + "{e_t}초" + E + " 동안 공격력 " + A + "{e_atk}%" + E + ", 공격 속도 " + A + "{e_as}%" + E +
                  ", 이동 속도 " + A + "{e_ms}%" + E + " 증가.",
        "ult": "번개같이 돌진해(저지 불가) 세 번 찔러 각 " + phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + ", 세 번째는 "
               "대상 최대 체력의 " + A + "{r_thp}%" + E + " 추가.",
        "names": ("삼단 찌르기", "귀자", "천상산단돌"),
    },
    "ja": {
        "name": "沖田総司",
        "attack": "一太刀で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "剣の刻" + E + "：刀が一生の剣技を一瞬に凝縮し、"
                  "スキルを使うたび" + A + "{p_t}秒" + E + "攻撃速度" + A + "{p_as}%" + E + "上昇。",
        "skill": "神速の三連突き、一突きごとに前方の敵へ" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、三突き目は" +
                 phys("q3_dmg", "q3_ad") + "追加。",
        "skill2": "鬼子：" + A + "{e_t}秒" + E + "攻撃力" + A + "{e_atk}%" + E + "、攻撃速度" + A + "{e_as}%" + E + "、移動速度" +
                  A + "{e_ms}%" + E + "上昇。",
        "ult": "神速で踏み込み（行動妨害無効）三度突く、各" + phys("r_dmg", "r_ad") + "の" + O + "物理ダメージ" + E +
               "、三突き目は対象の最大体力の" + A + "{r_thp}%" + E + "追加。",
        "names": ("三段突き", "鬼子", "天翔散段突"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_okita 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "slash_release", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "sword_hit", 0.4, 0.0)],
    f"{ID}_q1": [(SFX + "thrust_1", 0.5, 0.0)],
    f"{ID}_q2": [(SFX + "thrust_2", 0.5, 0.0)],
    f"{ID}_q3": [(SFX + "thrust_3", 0.55, 0.0)],
    f"{ID}_q_hit": [(SFX + "sword_hit", 0.4, 0.0)],
    f"{ID}_e_charge": [(SFX + "oni_charge", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "oni_ignite", 0.55, 0.0)],
    f"{ID}_r_load": [(SFX + "ult_charge", 0.5, 0.0)],
    f"{ID}_r": [(SFX + "ult_release", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "finisher_hit", 0.55, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/okita.rs）：死的时候倒地（Codex 的 cues：0.835 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.835)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("select", "start", "challenge", "q", "e", "r")},
}


def values(p):
    v = {k: p[k] for k in ("p_as", "q_dmg", "q_ad", "q3_dmg", "q3_ad", "e_atk", "e_as", "e_ms", "r_dmg", "r_ad", "r_thp")}
    for k in ("p_t", "e_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "okita", "tools/kit/seed_okita_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
