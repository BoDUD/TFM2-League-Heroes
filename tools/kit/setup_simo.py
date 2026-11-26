"""西蒙·海耶的文本（五种语言）、sound_info 和 champion_view，数字取自 build_simo.P。

    python tools/kit/setup_simo.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）。--check 只打印
每段说明的显示长度和全文。

名字：西蒙·海耶 / 西蒙·海耶 / Simo Häyhä / 시모 해위해 / シモ・ヘイヘ；技能名照原作（漫画第十一回合）：对神狙击术（万花缭乱、
天穿白鸟、精灵的气息三发轮流）、雪中隐踪（原作里他每开一枪就换个地方、落雪盖住脚印，没有招式名）、天空的残光；被动「死神的契约」
写在普攻说明里。图标照 Codex 的交付（assets/source/simo/icons：skill、skill2、ult；passive 那张图标位放不下）。
声音：Codex 的交付（simo_packs/outputs/simo_final_assets.zip）：用到 10 条原创音效（冷息那条没用上）和 6 句日语台词（Codex 用语音
合成做的，用户 2026-11-26：「不对 音效要用 选错了」，要用）。音频不进仓库，tools/kit/seed_simo_audio.py 从交付复制到
ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_simo import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"

# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则：待机第 1 帧的眼睛在脚底上 41 逻辑格、
# 往前 9 格（放大两倍、PPU 8/3：-31、7）；百科中心照 --centers 的规则（实心顶 -41.3 -> -14）；选人卡 y = -39 - 头顶（-31.3）-> -8
VIEW = {"face": {"x": 7, "y": -31}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "西蒙·海耶",
        "attack": "莫辛-纳甘一枪，造成" + AD + O + "物理伤害" + E + "。" + O + "死神的契约" + E + "：技能射出的是器官换来的"
                  "弑神弹，每发先付" + A + "{p_cost}%" + E + "最大生命（不会因此阵亡）。",
        "skill": "对神狙击术，三发轮流：万花缭乱半空炸开，扇形内" + phys("q1_dmg", "q1_ad") + "；天穿白鸟穿透一列，" +
                 phys("q2_dmg", "q2_ad") + "；精灵的气息神速一枪，" + phys("q3_dmg", "q3_ad") + O + "物理伤害" + E + "。",
        "skill2": "扬起雪幕往后一跃，" + A + "隐身{e_inv}秒" + E + "，移速提高" + A + "{e_ms}%" + E + "（落雪盖住脚印）。",
        "ult": "最快最强的一发，造成" + phys("r_dmg", "r_ad") + "加目标" + A + "{r_thp}%" + E + "最大生命的" + O + "物理伤害" +
               E + "。",
        "names": ("对神狙击术", "雪中隐踪", "天空的残光"),
    },
    "zh-hant": {
        "name": "西蒙·海耶",
        "attack": "莫辛-納干一槍，造成" + AD + O + "物理傷害" + E + "。" + O + "死神的契約" + E + "：技能射出的是器官換來的"
                  "弒神彈，每發先付" + A + "{p_cost}%" + E + "最大生命（不會因此陣亡）。",
        "skill": "對神狙擊術，三發輪流：萬花繚亂半空炸開，扇形內" + phys("q1_dmg", "q1_ad") + "；天穿白鳥貫穿一列，" +
                 phys("q2_dmg", "q2_ad") + "；精靈的氣息神速一槍，" + phys("q3_dmg", "q3_ad") + O + "物理傷害" + E + "。",
        "skill2": "揚起雪幕往後一躍，" + A + "隱身{e_inv}秒" + E + "，移速提高" + A + "{e_ms}%" + E + "（落雪蓋住腳印）。",
        "ult": "最快最強的一發，造成" + phys("r_dmg", "r_ad") + "加目標" + A + "{r_thp}%" + E + "最大生命的" + O + "物理傷害" +
               E + "。",
        "names": ("對神狙擊術", "雪中隱蹤", "天空的殘光"),
    },
    "en": {
        "name": "Simo Häyhä",
        "attack": "A Mosin-Nagant shot: " + AD + " " + O + "physical damage" + E + ". " + O + "Reaper's Contract" + E +
                  ": his skills fire his organs as god-killing rounds, each costing " + A + "{p_cost}%" + E +
                  " of his max health (never fatal).",
        "skill": "Sniping Against the Gods, three rounds in turn: Ilmatar bursts mid-air over a wide cone for " +
                 phys("q1_dmg", "q1_ad") + "; Lemminkäinen pierces a line for " + phys("q2_dmg", "q2_ad") +
                 "; Mielikki, a 0.5 s shot, deals " + phys("q3_dmg", "q3_ad") + " " + O + "physical damage" + E + ".",
        "skill2": "He raises a veil of snow and leaps back, " + A + "invisible for {e_inv}s" + E + " with " + A + "{e_ms}%" +
                  E + " more move speed: the snow covers his tracks.",
        "ult": "His fastest, strongest round: " + phys("r_dmg", "r_ad") + " plus " + A + "{r_thp}%" + E +
               " of the target's max health as " + O + "physical damage" + E + ".",
        "names": ("Sniping Against the Gods", "Snow Stealth", "Ukonvasara"),
    },
    "ko": {
        "name": "시모 해위해",
        "attack": "모신나강 사격으로 " + AD + " " + O + "물리 피해" + E + ". " + O + "사신의 계약" + E + ": 스킬은 장기를 바꾼 "
                  "신살의 탄환, 한 발마다 최대 체력의 " + A + "{p_cost}%" + E + "를 치름(죽지는 않음).",
        "skill": "대신 저격술, 세 발을 차례로: 만화요란은 공중에서 터져 부채꼴에 " + phys("q1_dmg", "q1_ad") + ", 천천백조는 한 "
                 "줄을 꿰뚫어 " + phys("q2_dmg", "q2_ad") + ", 정령의 숨결은 신속의 한 발로 " + phys("q3_dmg", "q3_ad") + " " +
                 O + "물리 피해" + E + ".",
        "skill2": "눈의 장막을 일으키며 뒤로 뛰어 " + A + "{e_inv}초 은신" + E + ", 이동 속도 " + A + "{e_ms}%" + E +
                  " 증가(눈이 발자국을 덮음).",
        "ult": "가장 빠르고 강한 한 발: " + phys("r_dmg", "r_ad") + " + 대상 최대 체력의 " + A + "{r_thp}%" + E + " " + O +
               "물리 피해" + E + ".",
        "names": ("대신 저격술", "설중 잠행", "천공의 잔광"),
    },
    "ja": {
        "name": "シモ・ヘイヘ",
        "attack": "モシン・ナガンの一撃で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "死神の契り" + E + "：スキルは臓器を"
                  "変えた神殺しの弾、一発ごとに最大体力の" + A + "{p_cost}%" + E + "を払う（死にはしない）。",
        "skill": "対神狙撃術、三発を順に：万花繚乱は空中で炸裂し扇状に" + phys("q1_dmg", "q1_ad") + "、天穿つ白鳥は一列を貫き" +
                 phys("q2_dmg", "q2_ad") + "、精霊の息吹は神速の一発で" + phys("q3_dmg", "q3_ad") + "の" + O + "物理ダメージ" +
                 E + "。",
        "skill2": "雪の幕を上げて後ろへ跳び、" + A + "{e_inv}秒透明" + E + "、移動速度" + A + "{e_ms}%" + E + "上昇（雪が足跡を"
                  "消す）。",
        "ult": "最速最強の一発で" + phys("r_dmg", "r_ad") + "＋対象の最大体力の" + A + "{r_thp}%" + E + "の" + O +
               "物理ダメージ" + E + "。",
        "names": ("対神狙撃術", "雪中潜伏", "天空の残光"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_simo 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "shot_release", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "shot_hit", 0.4, 0.0)],
    f"{ID}_q_load": [(SFX + "precision_charge", 0.45, 0.0)],
    f"{ID}_q1": [(SFX + "precision_release", 0.55, 0.0)],
    f"{ID}_q2": [(SFX + "precision_release", 0.6, 0.0)],
    f"{ID}_q3": [(SFX + "precision_release", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "shot_hit", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "snow_veil", 0.45, 0.0)],
    f"{ID}_e_step": [(SFX + "snow_step", 0.45, 0.0)],
    f"{ID}_r_load": [(SFX + "white_charge", 0.5, 0.0)],
    f"{ID}_r": [(SFX + "white_release", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "white_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/simo.rs）：死的时候倒在雪里（Codex 的 cues：0.875 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.875)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("select", "start", "challenge", "q", "e", "r")},
}


def values(p):
    v = {k: p[k] for k in ("p_cost", "q1_dmg", "q1_ad", "q2_dmg", "q2_ad", "q3_dmg", "q3_ad", "e_ms", "r_dmg", "r_ad",
                           "r_thp")}
    v["e_inv"] = secs(p["e_inv"])
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "simo", "tools/kit/seed_simo_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
