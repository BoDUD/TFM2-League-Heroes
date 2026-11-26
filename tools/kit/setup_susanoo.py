"""须佐之男命的文本（五种语言）、sound_info 和 champion_view，数字取自 build_susanoo.P。

    python tools/kit/setup_susanoo.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）。--check 只打印
每段说明的显示长度和全文。

名字：须佐之男 / 須佐之男 / Susanoo / 스사노오 / スサノヲ；技能名照原作（漫画第十回合）：奥义·天魔反、神罗八百万、无装剑；
被动「天魔反·无间」（不蓄力的天魔反）写在普攻说明里。图标照 Codex 的交付（assets/source/susanoo/icons）。
声音：Codex 的交付（susanoo_packs/output/sound，提交 890ad4437）：6 条原创刀声、剑压和命中音效；没有配音（官方还没有能确认是他的
日语原声），没有倒地声。音频不进仓库，tools/kit/seed_susanoo_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod
挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_susanoo import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX = f"{ID}_sfx_"
T = "<#ffffffff>"      # 真实伤害（白）

# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则：待机第 1 帧的眼睛在脚底上 48 逻辑格、
# 往前 5 格（放大两倍、PPU 8/3：-36、4）；百科中心照 --centers 的规则（实心顶 -41.3 -> -14）；选人卡 y = -39 - 头顶（-32.0）-> -7
VIEW = {"face": {"x": 4, "y": -36}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -7}}

TEXT = {
    "zh-hans": {
        "name": "须佐之男",
        "attack": "一刀，造成" + AD + O + "物理伤害" + E + "。" + O + "天魔反·无间" + E + "：每第三刀不蓄力地带出一道真空刃，一条"
                  "线上的敌人受到" + phys("p_dmg", "p_ad") + O + "物理伤害" + E + "。",
        "skill": "摆出天魔反的架势挥刀，月牙真空刃飞出，一条线上的敌人受到" + phys("q_dmg", "q_ad") + "，身前的敌人再受" +
                 phys("q2_dmg", "q2_ad") + O + "物理伤害" + E + "（越远越弱）。",
        "skill2": "摆出正眼构：普攻打不疼他、技能伤害降低" + A + "{e_sdr}%" + E + "；随后回敬一刀，前方敌人受到" +
                  phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "眩晕{e_stun}秒" + E + "。",
        "ult": "空手挥出看不见的剑（不受控制），只砍骨头：" + phys("r_dmg", "r_ad") + "加目标" + A + "{r_thp}%" + E + "最大生命的" +
               T + "真实伤害" + E + "，" + R + "{r_t}秒" + E + "内减速、攻击力降低；每挥一次自损" + A + "{r_cost}%" + E + "最大生命。",
        "names": ("天魔反", "神罗八百万", "无装剑"),
    },
    "zh-hant": {
        "name": "須佐之男",
        "attack": "一刀，造成" + AD + O + "物理傷害" + E + "。" + O + "天魔反·無間" + E + "：每第三刀不蓄力地帶出一道真空刃，一條"
                  "線上的敵人受到" + phys("p_dmg", "p_ad") + O + "物理傷害" + E + "。",
        "skill": "擺出天魔反的架勢揮刀，月牙真空刃飛出，一條線上的敵人受到" + phys("q_dmg", "q_ad") + "，身前的敵人再受" +
                 phys("q2_dmg", "q2_ad") + O + "物理傷害" + E + "（越遠越弱）。",
        "skill2": "擺出正眼構：普攻打不疼他、技能傷害降低" + A + "{e_sdr}%" + E + "；隨後回敬一刀，前方敵人受到" +
                  phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E + "。",
        "ult": "空手揮出看不見的劍（不受控制），只砍骨頭：" + phys("r_dmg", "r_ad") + "加目標" + A + "{r_thp}%" + E + "最大生命的" +
               T + "真實傷害" + E + "，" + R + "{r_t}秒" + E + "內緩速、攻擊力降低；每揮一次自損" + A + "{r_cost}%" + E + "最大生命。",
        "names": ("天魔反", "神羅八百萬", "無裝劍"),
    },
    "en": {
        "name": "Susanoo",
        "attack": "A cut: " + AD + " " + O + "physical damage" + E + ". " + O + "Ama no Magaeshi: Mugen" + E + ": every third "
                  "cut throws an uncharged vacuum blade, " + phys("p_dmg", "p_ad") + " " + O + "physical damage" + E +
                  " along a line.",
        "skill": "Ama no Magaeshi: from his strange stance he cuts the air into a crescent vacuum blade: " +
                 phys("q_dmg", "q_ad") + " along a line and " + phys("q2_dmg", "q2_ad") + " more to enemies close in front, " +
                 O + "physical damage" + E + " (weaker with distance).",
        "skill2": "Shinra Yaoyorozu: in a plain seigan stance basic attacks cannot hurt him and skills deal " + A + "{e_sdr}%" +
                  E + " less; then he answers: " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + " in front and a " +
                  R + "{e_stun}s stun" + E + ".",
        "ult": "Musoken: an unseen sword swung with empty hands (unstoppable) cuts only the bones: " + phys("r_dmg", "r_ad") +
               " plus " + A + "{r_thp}%" + E + " of max health as " + T + "true damage" + E + ", slowed and weakened for " + R +
               "{r_t}s" + E + "; each swing costs him " + A + "{r_cost}%" + E + " max health.",
        "names": ("Ama no Magaeshi", "Shinra Yaoyorozu", "Musoken"),
    },
    "ko": {
        "name": "스사노오",
        "attack": "한 칼에 " + AD + " " + O + "물리 피해" + E + ". " + O + "천마반·무간" + E + ": 세 번째 칼마다 모으지 않은 진공 "
                  "칼날이 날아가 한 줄의 적에게 " + phys("p_dmg", "p_ad") + " " + O + "물리 피해" + E + ".",
        "skill": "천마반의 자세로 베어 초승달 진공 칼날을 날림: 한 줄의 적에게 " + phys("q_dmg", "q_ad") + ", 앞의 가까운 적은 " +
                 phys("q2_dmg", "q2_ad") + " 추가 " + O + "물리 피해" + E + "(멀수록 약함).",
        "skill2": "정안 자세: 기본 공격 피해를 받지 않고 스킬 피해 " + A + "{e_sdr}%" + E + " 감소, 이어서 앞의 적에게 " +
                  phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R + "{e_stun}초 기절" + E + ".",
        "ult": "빈손으로 보이지 않는 검을 휘둘러(저지 불가) 뼈만 벰: " + phys("r_dmg", "r_ad") + " + 최대 체력 " + A +
               "{r_thp}%" + E + " " + T + "고정 피해" + E + ", " + R + "{r_t}초" + E + " 둔화와 공격력 감소. 휘두를 때마다 최대 체력 " +
               A + "{r_cost}%" + E + " 소모.",
        "names": ("천마반", "신라팔백만", "무장검"),
    },
    "ja": {
        "name": "スサノヲ",
        "attack": "一太刀で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "天魔反・無間" + E + "：三太刀ごとに溜めなしの真空"
                  "刃が飛び、一列の敵に" + phys("p_dmg", "p_ad") + "の" + O + "物理ダメージ" + E + "。",
        "skill": "天魔反の構えから斬り、三日月の真空刃を放つ：一列に" + phys("q_dmg", "q_ad") + "、目の前の敵には" +
                 phys("q2_dmg", "q2_ad") + "追加の" + O + "物理ダメージ" + E + "（遠いほど弱い）。",
        "skill2": "正眼の構え：通常攻撃が効かず、スキル被ダメージ" + A + "{e_sdr}%" + E + "軽減。続いて前方へ" +
                  phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{e_stun}秒スタン" + E + "。",
        "ult": "素手で見えない剣を振るい（行動妨害無効）骨だけを斬る：" + phys("r_dmg", "r_ad") + "＋最大体力の" + A + "{r_thp}%" +
               E + "の" + T + "確定ダメージ" + E + "、" + R + "{r_t}秒" + E + "鈍足と攻撃力低下。振るうたび最大体力" + A +
               "{r_cost}%" + E + "を失う。",
        "names": ("天魔反", "神羅八百万", "無装剣"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_susanoo 的 sfx / tsfx）放的每一个（ragnarok.dll 不放声音）
SOUNDS = {
    f"{ID}_a": [(SFX + "slash_release", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "sword_hit", 0.4, 0.0)],
    f"{ID}_p": [(SFX + "tenma_release", 0.35, 0.0)],
    f"{ID}_q_load": [(SFX + "tenma_charge", 0.5, 0.0)],
    f"{ID}_q": [(SFX + "tenma_release", 0.6, 0.0)],
    f"{ID}_q_hit": [(SFX + "sword_hit", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "stance_set", 0.5, 0.0)],
    f"{ID}_e_go": [(SFX + "slash_release", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "sword_hit", 0.5, 0.0)],
    f"{ID}_r_load": [(SFX + "stance_set", 0.4, 0.0)],
    f"{ID}_r": [(SFX + "muso_release", 0.65, 0.0)],
    f"{ID}_r_hit": [(SFX + "sword_hit", 0.55, 0.0)],
}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ad", "q_dmg", "q_ad", "q2_dmg", "q2_ad", "e_sdr", "e_dmg", "e_ad", "r_dmg", "r_ad",
                           "r_thp", "r_cost")}
    for k in ("e_stun", "r_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "susanoo", "tools/kit/seed_susanoo_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
