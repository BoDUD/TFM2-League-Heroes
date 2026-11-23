#!/usr/bin/env python3
"""Generate 5-language texts, .sound_info files, mod.override_info, and mod.mod_info for baixi."""
import json
import os
import re
import sys

WS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOD_ID = "baixi"
MOD = os.path.join(WS, MOD_ID)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_baixi_kits import ALL_PARAMS  # noqa: E402

VERSION = "0.1.0"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
O = "<#ff9028ff>"
A = "<#ffb900ff>"
R = "<#ef5350ff>"
M = "<#a974ffff>"
S = "<#e8d44dff>"
G = "<#66bb6aff>"
E = "<>"
AD = ADi + O + "100%" + E


def phys(d, r):
    return f"{O}{{{d}}}{E}+{ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    return f"{M}{{{d}}}{E}+{APi}{M}{{{r}}}%{E}"


def shd_ap(d, r):
    return f"{S}{{{d}}}{E}+{APi}{S}{{{r}}}%{E}"


def shd_ad(d, r):
    return f"{S}{{{d}}}{E}+{ADi}{S}{{{r}}}%{E}"


def heal_ap(d, r):
    return f"{G}{{{d}}}{E}+{APi}{G}{{{r}}}%{E}"


def heal_ad(d, r):
    return f"{G}{{{d}}}{E}+{ADi}{G}{{{r}}}%{E}"


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def shown_len(s):
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def fmt_vals(h, p):
    v = dict(p)
    for k in list(v):
        if k.endswith(("_t", "_taunt", "_sil", "_bind", "_up", "_stun", "_invis", "_sh_t", "_slow_t")):
            v[k] = secs(p[k])
    return v


TEXT = {
    "baixi_dianjing": {
        "zh-hans": {
            "name": "点睛",
            "names": ("采青", "狮被旋", "醒狮"),
            "attack": "狮头顶撞，造成" + AD + O + "物理伤害" + E + "。" + O + "鼓点" + E + "：每第3下变为狮咬，额外造成" + phys("p_dmg", "p_ad") + "并回复" + heal_ad("p_heal", "p_heal_ad") + "。",
            "skill": "跃扑咬住目标造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%({q_slow_t}秒)" + E + "，叼青菜回复" + heal_ad("q_heal", "q_heal_ad") + "。",
            "skill2": "抡起狮被旋转，对周围造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "，自身获" + shd_ad("e_sh", "e_sh_ad") + "护盾(" + A + "{e_sh_t}秒" + E + ")。",
            "ult": "狮眼点亮一声怒吼，周围敌人受" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并被" + R + "嘲讽{r_taunt}秒" + E + "；自身" + A + "{r_t}秒" + E + "减伤{r_dr}%、攻速+{r_as}%。",
        },
        "zh-hant": {
            "name": "點睛",
            "names": ("採青", "獅被旋", "醒獅"),
            "attack": "獅頭頂撞，造成" + AD + O + "物理傷害" + E + "。" + O + "鼓點" + E + "：每第3下變為獅咬，額外造成" + phys("p_dmg", "p_ad") + "並回復" + heal_ad("p_heal", "p_heal_ad") + "。",
            "skill": "躍撲咬住目標造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%({q_slow_t}秒)" + E + "，叼青菜回復" + heal_ad("q_heal", "q_heal_ad") + "。",
            "skill2": "掄起獅被旋轉，對周圍造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "，自身獲" + shd_ad("e_sh", "e_sh_ad") + "護盾(" + A + "{e_sh_t}秒" + E + ")。",
            "ult": "獅眼點亮一聲怒吼，周圍敵人受" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並被" + R + "嘲諷{r_taunt}秒" + E + "；自身" + A + "{r_t}秒" + E + "減傷{r_dr}%、攻速+{r_as}%。",
        },
        "en": {
            "name": "Dianjing",
            "names": ("Pluck the Greens", "Lion Cloak Spin", "Awakened Lion"),
            "attack": "Lion headbutt for " + AD + " physical damage. " + O + "Drumbeat" + E + ": every 3rd hit bites for +" + phys("p_dmg", "p_ad") + " and heals " + heal_ad("p_heal", "p_heal_ad") + ".",
            "skill": "Leaps onto target for " + phys("q_dmg", "q_ad") + " physical damage, " + R + "slows {q_slow}% ({q_slow_t}s)" + E + ", and heals " + heal_ad("q_heal", "q_heal_ad") + ".",
            "skill2": "Spins his lion cloak for " + phys("e_dmg", "e_ad") + " AoE physical damage and gains a " + shd_ad("e_sh", "e_sh_ad") + " shield (" + A + "{e_sh_t}s" + E + ").",
            "ult": "Roars with golden eyes: AoE " + phys("r_dmg", "r_ad") + " physical damage and " + R + "{r_taunt}s taunt" + E + "; gains {r_dr}% DR and +{r_as}% AS for " + A + "{r_t}s" + E + ".",
        },
        "ko": {
            "name": "점정",
            "names": ("채청", "사자망토 회전", "성사"),
            "attack": "사자탈 박치기(" + AD + "). " + O + "북장단" + E + ": 3번째 공격마다 추가로 " + phys("p_dmg", "p_ad") + " 피해 및 " + heal_ad("p_heal", "p_heal_ad") + " 회복.",
            "skill": "대상에 도약해 " + phys("q_dmg", "q_ad") + " 물리 피해, " + R + "{q_slow}% 둔화({q_slow_t}초)" + E + ", " + heal_ad("q_heal", "q_heal_ad") + " 회복.",
            "skill2": "사자망토 회전으로 주위에 " + phys("e_dmg", "e_ad") + " 피해 및 " + shd_ad("e_sh", "e_sh_ad") + " 보호막(" + A + "{e_sh_t}초" + E + ").",
            "ult": "포효로 주위 적에게 " + phys("r_dmg", "r_ad") + " 피해와 " + R + "{r_taunt}초 도발" + E + ". " + A + "{r_t}초" + E + " 피해 {r_dr}% 감소·공속 +{r_as}%.",
        },
        "ja": {
            "name": "点睛",
            "names": ("採青", "獅被旋", "醒獅"),
            "attack": "獅子頭の頭突き(" + AD + ")。" + O + "鼓点" + E + "：3回毎に獅咬となり+" + phys("p_dmg", "p_ad") + "ダメージと" + heal_ad("p_heal", "p_heal_ad") + "回復。",
            "skill": "飛びかかり" + phys("q_dmg", "q_ad") + "物理ダメージと" + R + "{q_slow}%スロウ({q_slow_t}秒)" + E + "、青菜で" + heal_ad("q_heal", "q_heal_ad") + "回復。",
            "skill2": "獅被を回し周囲に" + phys("e_dmg", "e_ad") + "物理ダメージ、自身に" + shd_ad("e_sh", "e_sh_ad") + "シールド(" + A + "{e_sh_t}秒" + E + ")。",
            "ult": "咆哮し周囲に" + phys("r_dmg", "r_ad") + "物理ダメージと" + R + "{r_taunt}秒挑発" + E + "。" + A + "{r_t}秒" + E + "被ダメ{r_dr}%軽減・AS+{r_as}%。",
        },
    },
    "baixi_sangeng": {
        "zh-hans": {
            "name": "三更",
            "names": ("过影", "隔幕", "灯灭"),
            "attack": "双刀斩击，造成" + AD + O + "物理伤害" + E + "。" + O + "影随形" + E + "：放技能后" + A + "{p_t}秒" + E + "内下次普攻连出影刃，额外造成" + phys("p_dmg", "p_ad") + "。",
            "skill": "化影穿过目标，对沿途敌人造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%({q_slow_t}秒)" + E + "。",
            "skill2": "退至皮影幕后" + A + "隐身{e_invis}秒" + E + "、移速+{e_ms}%；破隐第一击额外造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "。",
            "ult": "吹灭油灯闪至敌方英雄身后，隐身" + A + "{r_invis}秒" + E + "连斩三刀，每刀" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "，最后一刀" + R + "沉默{r_sil}秒" + E + "。",
        },
        "zh-hant": {
            "name": "三更",
            "names": ("過影", "隔幕", "燈滅"),
            "attack": "雙刀斬擊，造成" + AD + O + "物理傷害" + E + "。" + O + "影隨形" + E + "：放技能後" + A + "{p_t}秒" + E + "內下次普攻連出影刃，額外造成" + phys("p_dmg", "p_ad") + "。",
            "skill": "化影穿過目標，對沿途敵人造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%({q_slow_t}秒)" + E + "。",
            "skill2": "退至皮影幕後" + A + "隱身{e_invis}秒" + E + "、移速+{e_ms}%；破隱第一擊額外造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "。",
            "ult": "吹滅油燈閃至敵方英雄身後，隱身" + A + "{r_invis}秒" + E + "連斬三刀，每刀" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "，最後一刀" + R + "沉默{r_sil}秒" + E + "。",
        },
        "en": {
            "name": "Sangeng",
            "names": ("Shadow Pass", "Behind the Screen", "Lamp Out"),
            "attack": "Twin blades for " + AD + " physical damage. " + O + "Shadow Follow" + E + ": after a skill (" + A + "{p_t}s" + E + "), next attack strikes twice for +" + phys("p_dmg", "p_ad") + ".",
            "skill": "Dashes through the target as a shadow, dealing " + phys("q_dmg", "q_ad") + " physical damage and " + R + "slowing {q_slow}% ({q_slow_t}s)" + E + ".",
            "skill2": "Slips behind a lit puppet screen: " + A + "{e_invis}s stealth" + E + " & +{e_ms}% MS; first strike out deals +" + phys("e_dmg", "e_ad") + " physical damage.",
            "ult": "Snuffs the lamp and blinks behind target: invisible " + A + "{r_invis}s" + E + ", slashing 3 times for " + phys("r_dmg", "r_ad") + " each; 3rd hit " + R + "silences {r_sil}s" + E + ".",
        },
        "ko": {
            "name": "삼경",
            "names": ("과영", "격막", "등멸"),
            "attack": "쌍도 베기(" + AD + "). " + O + "그림자 추격" + E + ": 스킬 후 " + A + "{p_t}초" + E + " 내 다음 공격이 그림자 추가타 " + phys("p_dmg", "p_ad") + ".",
            "skill": "그림자가 되어 관통 돌진, 경로 적에게 " + phys("q_dmg", "q_ad") + " 피해 및 " + R + "{q_slow}% 둔화({q_slow_t}초)" + E + ".",
            "skill2": "막 뒤로 물러나 " + A + "{e_invis}초 은신" + E + "·이속 +{e_ms}%. 첫 공격에 " + phys("e_dmg", "e_ad") + " 추가 피해.",
            "ult": "등불을 끄고 적 뒤로 순간이동, " + A + "{r_invis}초" + E + " 은신 중 3연속 베기(회당 " + phys("r_dmg", "r_ad") + "), 마지막 타격 " + R + "{r_sil}초 침묵" + E + ".",
        },
        "ja": {
            "name": "三更",
            "names": ("過影", "隔幕", "灯滅"),
            "attack": "双刀斬り(" + AD + ")。" + O + "影随形" + E + "：スキル後" + A + "{p_t}秒" + E + "以内の次攻撃に影の追撃+" + phys("p_dmg", "p_ad") + "。",
            "skill": "影となって貫通突進し、" + phys("q_dmg", "q_ad") + "物理ダメージと" + R + "{q_slow}%スロウ({q_slow_t}秒)" + E + "。",
            "skill2": "幕の後ろへ退き" + A + "{e_invis}秒隠密" + E + "・MS+{e_ms}%。解除初撃に+" + phys("e_dmg", "e_ad") + "物理ダメージ。",
            "ult": "灯を消し敵背後へ閃撃、" + A + "{r_invis}秒" + E + "隠密しながら3連斬(各" + phys("r_dmg", "r_ad") + ")、3撃目で" + R + "{r_sil}秒沈黙" + E + "。",
        },
    },
    "baixi_maiya": {
        "zh-hans": {
            "name": "麦芽",
            "names": ("浇糖", "拉糖丝", "转糖"),
            "attack": "甩出糖滴造成" + AD + "。" + O + "甜头" + E + "：放技能后下次普攻附带热糖，额外" + mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "并" + R + "减速{p_slow}%({p_slow_t}秒)" + E + "。",
            "skill": "泼出热糖造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "，留热糖浆" + A + "{q_puddle_t}秒" + E + "持续烫伤并" + R + "减速{q_slow}%" + E + "。",
            "skill2": "甩出直线糖丝粘住首个敌人，造成" + mag("e_dmg", "e_ap") + M + "魔法伤害" + E + "并" + R + "定身{e_bind}秒" + E + "。",
            "ult": "拨转糖盘按" + A + "龙→凤→鱼" + E + "轮出：龙直线" + mag("rd_dmg", "rd_ap") + R + "击飞" + E + "；凤" + mag("rp_dmg", "rp_ap") + "并给队友" + shd_ap("rp_sh", "rp_sh_ap") + "盾；鱼" + mag("rf_dmg", "rf_ap") + R + "减速50%" + E + "。",
        },
        "zh-hant": {
            "name": "麥芽",
            "names": ("澆糖", "拉糖絲", "轉糖"),
            "attack": "甩出糖滴造成" + AD + "。" + O + "甜頭" + E + "：放技能後下次普攻附帶熱糖，額外" + mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "並" + R + "減速{p_slow}%({p_slow_t}秒)" + E + "。",
            "skill": "潑出熱糖造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "，留熱糖漿" + A + "{q_puddle_t}秒" + E + "持續燙傷並" + R + "減速{q_slow}%" + E + "。",
            "skill2": "甩出直線糖絲黏住首個敵人，造成" + mag("e_dmg", "e_ap") + M + "魔法傷害" + E + "並" + R + "定身{e_bind}秒" + E + "。",
            "ult": "撥轉糖盤按" + A + "龍→鳳→魚" + E + "輪出：龍直線" + mag("rd_dmg", "rd_ap") + R + "擊飛" + E + "；鳳" + mag("rp_dmg", "rp_ap") + "並給隊友" + shd_ap("rp_sh", "rp_sh_ap") + "盾；魚" + mag("rf_dmg", "rf_ap") + R + "減速50%" + E + "。",
        },
        "en": {
            "name": "Maiya",
            "names": ("Sugar Pour", "Sugar Thread", "Sugar Wheel"),
            "attack": "Flings a sugar drop (" + AD + "). " + O + "Sweet Spot" + E + ": after a skill, next attack adds " + mag("p_dmg", "p_ap") + " magic damage and " + R + "{p_slow}% slow ({p_slow_t}s)" + E + ".",
            "skill": "Pours molten sugar for " + mag("q_dmg", "q_ap") + " AoE magic damage, leaving a " + A + "{q_puddle_t}s" + E + " hot puddle that burns and " + R + "slows {q_slow}%" + E + ".",
            "skill2": "Whips a linear sugar thread hitting the first enemy for " + mag("e_dmg", "e_ap") + " magic damage and " + R + "{e_bind}s root" + E + ".",
            "ult": "Spins " + A + "Dragon -> Phoenix -> Fish" + E + ": Dragon line " + mag("rd_dmg", "rd_ap") + " + " + R + "knockup" + E + "; Phoenix " + mag("rp_dmg", "rp_ap") + " + ally " + shd_ap("rp_sh", "rp_sh_ap") + " shield; Fish " + mag("rf_dmg", "rf_ap") + " + " + R + "50% slow" + E + ".",
        },
        "ko": {
            "name": "맥아",
            "names": ("설탕 붓기", "설탕실", "돌림판"),
            "attack": "설탕 방울(" + AD + "). " + O + "단맛" + E + ": 스킬 후 다음 공격에 " + mag("p_dmg", "p_ap") + " 마법 피해와 " + R + "{p_slow}% 둔화({p_slow_t}초)" + E + ".",
            "skill": "뜨거운 설탕으로 " + mag("q_dmg", "q_ap") + " 마법 피해, " + A + "{q_puddle_t}초" + E + " 웅덩이 지속 피해 및 " + R + "{q_slow}% 둔화" + E + ".",
            "skill2": "직선 설탕실로 첫 적에게 " + mag("e_dmg", "e_ap") + " 마법 피해 및 " + R + "{e_bind}초 속박" + E + ".",
            "ult": A + "용→봉황→물고기" + E + " 순환: 용 직선 " + mag("rd_dmg", "rd_ap") + R + "에어본" + E + ", 봉황 " + mag("rp_dmg", "rp_ap") + "+아군 보호막, 물고기 " + mag("rf_dmg", "rf_ap") + R + "둔화" + E + ".",
        },
        "ja": {
            "name": "麦芽",
            "names": ("飴掛け", "飴糸", "飴回し"),
            "attack": "飴滴を飛ばす(" + AD + ")。" + O + "甘味" + E + "：スキル後の次攻撃に+" + mag("p_dmg", "p_ap") + "魔法ダメージと" + R + "{p_slow}%スロウ" + E + "。",
            "skill": "熱飴を撒き" + mag("q_dmg", "q_ap") + "魔法ダメージ、" + A + "{q_puddle_t}秒" + E + "飴溜まりで継続ダメージと" + R + "{q_slow}%スロウ" + E + "。",
            "skill2": "直線に飴糸を放ち最初の敵に" + mag("e_dmg", "e_ap") + "魔法ダメージと" + R + "{e_bind}秒スネア" + E + "。",
            "ult": A + "龍→鳳→魚" + E + "の順に召喚：龍" + mag("rd_dmg", "rd_ap") + R + "打上" + E + "、鳳" + mag("rp_dmg", "rp_ap") + "+味方シールド、魚" + mag("rf_dmg", "rf_ap") + R + "50%スロウ" + E + "。",
        },
    },
    "baixi_huoshu": {
        "zh-hans": {
            "name": "火树",
            "names": ("窜天猴", "地老鼠", "火树银花"),
            "attack": "点炮发射小炮造成" + AD + O + "物理伤害" + E + "。" + O + "连珠炮" + E + "：每第4下射出二踢脚，在目标周围炸开造成" + phys("p_dmg", "p_ad") + "范围伤害。",
            "skill": "连射三支追踪窜天猴，每支造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "。",
            "skill2": "向后一跳并在原地丢下地老鼠，" + A + "{e_t}秒" + E + "内每0.5秒造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "减速{e_slow}%" + E + "。",
            "ult": "点燃纸筒朝天齐射：目标区域" + A + "{r_t}秒" + E + "内每0.25秒炸一轮(" + phys("r_dmg", "r_ad") + ")，压轴大烟花再炸" + phys("r_fin_dmg", "r_fin_ad") + "。",
        },
        "zh-hant": {
            "name": "火樹",
            "names": ("竄天猴", "地老鼠", "火樹銀花"),
            "attack": "點炮發射小炮造成" + AD + O + "物理傷害" + E + "。" + O + "連珠炮" + E + "：每第4下射出二踢腳，在目標周圍炸開造成" + phys("p_dmg", "p_ad") + "範圍傷害。",
            "skill": "連射三支追蹤竄天猴，每支造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "。",
            "skill2": "向後一跳並在原地丟下地老鼠，" + A + "{e_t}秒" + E + "內每0.5秒造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "減速{e_slow}%" + E + "。",
            "ult": "點燃紙筒朝天齊射：目標區域" + A + "{r_t}秒" + E + "內每0.25秒炸一輪(" + phys("r_dmg", "r_ad") + ")，壓軸大煙花再炸" + phys("r_fin_dmg", "r_fin_ad") + "。",
        },
        "en": {
            "name": "Huoshu",
            "names": ("Sky Rockets", "Ground Spinner", "Blossoming Fireworks"),
            "attack": "Fires a paper cracker (" + AD + "). " + O + "Chain Crackers" + E + ": every 4th shot pops twice, splashing " + phys("p_dmg", "p_ad") + " AoE physical damage.",
            "skill": "Launches 3 homing sky rockets, each dealing " + phys("q_dmg", "q_ad") + " physical damage.",
            "skill2": "Hops back and drops a spinner lasting " + A + "{e_t}s" + E + ", dealing " + phys("e_dmg", "e_ad") + " every 0.5s and " + R + "slowing {e_slow}%" + E + ".",
            "ult": "Ignites all tubes: rains fireworks for " + A + "{r_t}s" + E + " (" + phys("r_dmg", "r_ad") + " every 0.25s) ending in a grand " + phys("r_fin_dmg", "r_fin_ad") + " burst.",
        },
        "ko": {
            "name": "화수",
            "names": ("불꽃 로켓", "땅쥐 폭죽", "화수은화"),
            "attack": "폭죽 발사(" + AD + "). " + O + "연발 폭죽" + E + ": 4번째 공격마다 2단 폭발로 주위에 " + phys("p_dmg", "p_ad") + " 범위 물리 피해.",
            "skill": "대상을 쫓는 로켓 3발을 연사, 발당 " + phys("q_dmg", "q_ad") + " 물리 피해.",
            "skill2": "뒤로 도약하며 " + A + "{e_t}초" + E + "간 회전 폭죽을 남겨 0.5초마다 " + phys("e_dmg", "e_ad") + " 피해 및 " + R + "{e_slow}% 둔화" + E + ".",
            "ult": "불꽃을 쏘아 올려 " + A + "{r_t}초" + E + "간 0.25초마다 " + phys("r_dmg", "r_ad") + " 폭격 후 마지막 대폭발 " + phys("r_fin_dmg", "r_fin_ad") + ".",
        },
        "ja": {
            "name": "火樹",
            "names": ("昇り龍花火", "ネズミ花火", "火樹銀花"),
            "attack": "小花火を発射(" + AD + ")。" + O + "連珠砲" + E + "：4発毎に二段爆竹となり周囲に" + phys("p_dmg", "p_ad") + "範囲物理ダメージ。",
            "skill": "追尾ロケット花火を3連射、各" + phys("q_dmg", "q_ad") + "物理ダメージ。",
            "skill2": "後方へ跳び足元に" + A + "{e_t}秒" + E + "ネズミ花火を設置、0.5秒毎に" + phys("e_dmg", "e_ad") + "ダメージと" + R + "{e_slow}%スロウ" + E + "。",
            "ult": "全筒点火し目標地点に" + A + "{r_t}秒" + E + "間0.25秒毎の連爆(" + phys("r_dmg", "r_ad") + ")、最後に大輪" + phys("r_fin_dmg", "r_fin_ad") + "。",
        },
    },
    "baixi_fumian": {
        "zh-hans": {
            "name": "拂面",
            "names": ("亮相", "甩袖", "变脸"),
            "attack": "扇风造成" + AD + "。" + O + "脸谱" + E + "：每次施法按" + A + "红→黑→金" + E + "换脸：红给队友" + shd_ap("p_sh", "p_sh_ap") + "盾，黑多" + R + "晕{p_stun}秒" + E + "，金回" + heal_ap("p_heal", "p_heal_ap") + "。",
            "skill": "开扇亮相，前方扇形造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "减速{q_slow}%({q_slow_t}秒)" + E + "，触发当前脸谱并变脸。",
            "skill2": "甩出水袖卷住首个敌方英雄拉至身前，造成" + mag("e_dmg", "e_ap") + M + "魔法伤害" + E + "并" + R + "眩晕{e_stun}秒" + E + "，触发当前脸谱并变脸。",
            "ult": "扬斗篷连变三脸：周围敌人受" + mag("r_dmg", "r_ap") + "并" + R + "眩晕{r_stun}秒" + E + "；队友得" + shd_ap("r_sh", "r_sh_ap") + "护盾并回复" + heal_ap("r_heal", "r_heal_ap") + "。",
        },
        "zh-hant": {
            "name": "拂面",
            "names": ("亮相", "甩袖", "變臉"),
            "attack": "扇風造成" + AD + "。" + O + "臉譜" + E + "：每次施法按" + A + "紅→黑→金" + E + "換臉：紅給隊友" + shd_ap("p_sh", "p_sh_ap") + "盾，黑多" + R + "暈{p_stun}秒" + E + "，金回" + heal_ap("p_heal", "p_heal_ap") + "。",
            "skill": "開扇亮相，前方扇形造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "減速{q_slow}%({q_slow_t}秒)" + E + "，觸發當前臉譜並變臉。",
            "skill2": "甩出水袖捲住首個敵方英雄拉至身前，造成" + mag("e_dmg", "e_ap") + M + "魔法傷害" + E + "並" + R + "暈眩{e_stun}秒" + E + "，觸發當前臉譜並變臉。",
            "ult": "揚斗篷連變三臉：周圍敵人受" + mag("r_dmg", "r_ap") + "並" + R + "暈眩{r_stun}秒" + E + "；隊友得" + shd_ap("r_sh", "r_sh_ap") + "護盾並回復" + heal_ap("r_heal", "r_heal_ap") + "。",
        },
        "en": {
            "name": "Fumian",
            "names": ("Grand Pose", "Silk Sleeve", "Face-Changing"),
            "attack": "Fan gust (" + AD + "). " + O + "Opera Masks" + E + ": each cast cycles " + A + "Red->Black->Gold" + E + ": Red shields allies " + shd_ap("p_sh", "p_sh_ap") + ", Black adds " + R + "{p_stun}s stun" + E + ", Gold heals " + heal_ap("p_heal", "p_heal_ap") + ".",
            "skill": "Snaps open his fan in a cone for " + mag("q_dmg", "q_ap") + " magic damage and " + R + "{q_slow}% slow ({q_slow_t}s)" + E + ", triggering and cycling his mask.",
            "skill2": "Whips a silk sleeve, pulling the first enemy champion in for " + mag("e_dmg", "e_ap") + " magic damage and " + R + "{e_stun}s stun" + E + ", cycling his mask.",
            "ult": "Flashes all 3 masks: enemies take " + mag("r_dmg", "r_ap") + " + " + R + "{r_stun}s stun" + E + "; allies gain " + shd_ap("r_sh", "r_sh_ap") + " shield and " + heal_ap("r_heal", "r_heal_ap") + " heal.",
        },
        "ko": {
            "name": "불면",
            "names": ("량상", "수수 휘두르기", "변검"),
            "attack": "부채바람(" + AD + "). " + O + "가면" + E + ": 스킬마다 " + A + "적→흑→금" + E + " 전환: 적 아군 보호막, 흑 " + R + "+{p_stun}초 기절" + E + ", 금 아군 회복.",
            "skill": "부채를 펼쳐 전방에 " + mag("q_dmg", "q_ap") + " 마법 피해 및 " + R + "{q_slow}% 둔화({q_slow_t}초)" + E + ", 가면 발동·전환.",
            "skill2": "긴 소매로 첫 적 챔피언을 끌어당겨 " + mag("e_dmg", "e_ap") + " 피해와 " + R + "{e_stun}초 기절" + E + ", 가면 발동·전환.",
            "ult": "세 가면을 연달아 펼쳐 주위 적 " + mag("r_dmg", "r_ap") + R + " {r_stun}초 기절" + E + ", 아군 보호막 " + shd_ap("r_sh", "r_sh_ap") + " 및 회복 " + heal_ap("r_heal", "r_heal_ap") + ".",
        },
        "ja": {
            "name": "払面",
            "names": ("見得", "水袖投げ", "変面"),
            "attack": "扇風(" + AD + ")。" + O + "臉譜" + E + "：スキル毎に" + A + "赤→黒→金" + E + "変面。赤は味方シールド、黒は" + R + "+{p_stun}秒スタン" + E + "、金は味方回復。",
            "skill": "扇を開き前方に" + mag("q_dmg", "q_ap") + "魔法ダメージと" + R + "{q_slow}%スロウ({q_slow_t}秒)" + E + "、臉譜発動＆変面。",
            "skill2": "水袖で最初の敵を引き寄せ" + mag("e_dmg", "e_ap") + "魔法ダメージと" + R + "{e_stun}秒スタン" + E + "、臉譜発動＆変面。",
            "ult": "三面連続変面：周囲の敵に" + mag("r_dmg", "r_ap") + "と" + R + "{r_stun}秒スタン" + E + "、味方に" + shd_ap("r_sh", "r_sh_ap") + "シールドと" + heal_ap("r_heal", "r_heal_ap") + "回復。",
        },
    },
}

# Sound event -> [(clip_stem, volume, delay)]
SOUNDS = {
    # Dianjing
    "baixi_dianjing_a":         [("baixi_dianjing_sfx_a", 0.45, 0.0)],
    "baixi_dianjing_bite":      [("baixi_dianjing_sfx_bite", 0.55, 0.0)],
    "baixi_dianjing_q":         [("baixi_dianjing_sfx_q", 0.50, 0.0)],
    "baixi_dianjing_q_hit":     [("baixi_dianjing_sfx_q_hit", 0.55, 0.0)],
    "baixi_dianjing_e":         [("baixi_dianjing_sfx_e", 0.50, 0.0)],
    "baixi_dianjing_r":         [("baixi_dianjing_sfx_r", 0.65, 0.0)],
    "baixi_dianjing_dead":      [("baixi_dianjing_sfx_dead", 0.50, 0.70)],
    # Sangeng
    "baixi_sangeng_a":          [("baixi_sangeng_sfx_a", 0.45, 0.0)],
    "baixi_sangeng_shadow":     [("baixi_sangeng_sfx_shadow", 0.50, 0.0)],
    "baixi_sangeng_q":          [("baixi_sangeng_sfx_q", 0.50, 0.0)],
    "baixi_sangeng_e":          [("baixi_sangeng_sfx_e", 0.50, 0.0)],
    "baixi_sangeng_r":          [("baixi_sangeng_sfx_r", 0.60, 0.0)],
    "baixi_sangeng_r_slash":    [("baixi_sangeng_sfx_r_slash", 0.55, 0.0)],
    "baixi_sangeng_dead":       [("baixi_sangeng_sfx_dead", 0.50, 0.70)],
    # Maiya
    "baixi_maiya_a":            [("baixi_maiya_sfx_a", 0.40, 0.0)],
    "baixi_maiya_q":            [("baixi_maiya_sfx_q", 0.50, 0.0)],
    "baixi_maiya_q_hit":        [("baixi_maiya_sfx_q_hit", 0.50, 0.0)],
    "baixi_maiya_e":            [("baixi_maiya_sfx_e", 0.50, 0.0)],
    "baixi_maiya_e_hit":        [("baixi_maiya_sfx_e_hit", 0.55, 0.0)],
    "baixi_maiya_r_dragon":     [("baixi_maiya_sfx_r_dragon", 0.65, 0.0)],
    "baixi_maiya_r_phoenix":    [("baixi_maiya_sfx_r_phoenix", 0.60, 0.0)],
    "baixi_maiya_r_fish":       [("baixi_maiya_sfx_r_fish", 0.65, 0.0)],
    "baixi_maiya_dead":         [("baixi_maiya_sfx_dead", 0.50, 0.70)],
    # Huoshu
    "baixi_huoshu_a":           [("baixi_huoshu_sfx_a", 0.45, 0.0)],
    "baixi_huoshu_twopop":      [("baixi_huoshu_sfx_twopop", 0.55, 0.0)],
    "baixi_huoshu_q":           [("baixi_huoshu_sfx_q", 0.55, 0.0)],
    "baixi_huoshu_e":           [("baixi_huoshu_sfx_e", 0.50, 0.0)],
    "baixi_huoshu_r":           [("baixi_huoshu_sfx_r", 0.60, 0.0)],
    "baixi_huoshu_r_boom":      [("baixi_huoshu_sfx_r_boom", 0.45, 0.0)],
    "baixi_huoshu_r_finale":    [("baixi_huoshu_sfx_r_finale", 0.65, 0.0)],
    "baixi_huoshu_dead":        [("baixi_huoshu_sfx_dead", 0.50, 0.70)],
    # Fumian
    "baixi_fumian_a":           [("baixi_fumian_sfx_a", 0.40, 0.0)],
    "baixi_fumian_q":           [("baixi_fumian_sfx_q", 0.50, 0.0)],
    "baixi_fumian_e":           [("baixi_fumian_sfx_e", 0.50, 0.0)],
    "baixi_fumian_e_hit":       [("baixi_fumian_sfx_e_hit", 0.55, 0.0)],
    "baixi_fumian_shift":       [("baixi_fumian_sfx_shift", 0.50, 0.0)],
    "baixi_fumian_r":           [("baixi_fumian_sfx_r", 0.65, 0.0)],
    "baixi_fumian_dead":        [("baixi_fumian_sfx_dead", 0.50, 0.70)],
}
# All 25 voice events
for _h in ("dianjing", "sangeng", "maiya", "huoshu", "fumian"):
    for _ev in ("start", "ult", "kill", "respawn", "dead"):
        SOUNDS[f"baixi_{_h}_v_{_ev}"] = [(f"baixi_{_h}_vo_{_ev}", 0.85, 0.0)]


def main():
    i18n = {}
    bad = False
    for h, p in ALL_PARAMS.items():
        cid = f"baixi_{h}"
        vals = fmt_vals(h, p)
        for lang, t in TEXT[cid].items():
            d = {"name": t["name"]}
            for k in ("attack", "skill", "skill2", "ult"):
                rendered = t[k].format(**vals)
                d[k] = rendered
                n = shown_len(rendered)
                if n > TOOLTIP_MAX[lang]:
                    print(f"TOO LONG {cid}.{lang}.{k}: {n}/{TOOLTIP_MAX[lang]} -> {rendered}")
                    bad = True
            i18n.setdefault(lang, {}).setdefault("description", {})[cid] = d
            i18n[lang].setdefault("skill_name", {})[cid] = dict(zip(("skill1", "skill2", "ult"), t["names"]))
    if bad:
        sys.exit("Tooltip length exceeded TOOLTIP_MAX!")
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    # Sound info files & mod.override_info
    clips = set()
    for ev, plays in SOUNDS.items():
        save(os.path.join(MOD, "sound", "sfx", f"{ev}.sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})
        for c, _, _ in plays:
            clips.add(c)

    ov = {
        "asset/base/text/champion": {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"},
        "asset/base/style/champion_view": {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"},
    }
    for name in sorted(set(SOUNDS) | clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    mod_info = {
        "author": "Baixi Team",
        "contains_code": True,
        "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}],
        "description": (
            "Original Chinese folk-craft Q-pixel hero pack 'Baixi' (百戏) for Teamfight Manager 2: "
            "Dianjing (醒狮·点睛, Top Fighter), Sangeng (皮影·三更, Jungle Assassin), "
            "Maiya (糖画·麦芽, Mid Mage), Huoshu (烟花·火树, Bot Marksman), "
            "Fumian (变脸·拂面, Support). Includes custom 2.75 PPU HD frames, Fumian's 3-mask live display hook, "
            "Maiya's overhead Dragon/Phoenix/Fish wheel indicators, AI Mandarin voice lines, and balanced 5v5 kits."
        ),
        "last_updated": "2026-11-24",
        "mod_id": MOD_ID,
        "mod_type": "native",
        "name": "Baixi Original Heroes (百戏原创英雄)",
        "version": VERSION,
    }
    save(os.path.join(MOD, "mod.mod_info"), mod_info)
    print(f"setup_baixi done: 5 heroes x 5 langs, {len(SOUNDS)} sound_info, {len(clips)} clips, mod.mod_info & mod.override_info")


if __name__ == "__main__":
    main()
