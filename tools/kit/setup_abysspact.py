#!/usr/bin/env python3
"""Generate Abyss Pact (渊契) shared pack files:
- abysspact/text/champion.i18n (5 languages, strictly checked against TOOLTIP_MAX)
- abysspact/style/champion_view.champion_view
- abysspact/sound/sfx/*.sound_info (100% verified against .data_champion + addons/abysspact/src/*.rs)
- abysspact/mod.mod_info
- abysspact/mod.override_info (text, champion_view, skeleton unit sheet/anim, all sounds & clips)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "abysspact"
MOD = os.path.join(REPO, MOD_ID)
VERSION = "0.1.0"
NAME = "Abyss Pact · 渊契"

sys.path.insert(0, HERE)
import build_abysspact as B  # noqa: E402

TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
O = "<#ff9028ff>"
A = "<#ffb900ff>"
R = "<#ef5350ff>"
M = "<#a974ffff>"
S = "<#e8d44dff>"
E = "<>"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def ad(d, r):
    return f"{O}{d}{E}+{ADi}{O}{r}%{E}"


def ap(d, r):
    return f"{M}{d}{E}+{APi}{M}{r}%{E}"


# ---------------------------------------------------------------------------
# Sound event -> [(clip_basename, volume, delay)] mapping (never self-named!)
# ---------------------------------------------------------------------------
SOUNDS = {
    "abysspact_oathbreaker": {
        "a":          [("abysspact_oathbreaker_sfx_attack_swing", 0.45, 0.0)],
        "a_hit":      [("abysspact_oathbreaker_sfx_attack_hit", 0.50, 0.0)],
        "q_cast":     [("abysspact_oathbreaker_sfx_cleave_cast", 0.55, 0.0)],
        "q_hit":      [("abysspact_oathbreaker_sfx_cleave_hit", 0.55, 0.0)],
        "w_cast":     [("abysspact_oathbreaker_sfx_chain_release", 0.55, 0.0)],
        "w_pull":     [("abysspact_oathbreaker_sfx_chain_pull", 0.60, 0.0)],
        "r_plant":    [("abysspact_oathbreaker_sfx_ult_plant", 0.65, 0.0)],
        "r_erupt":    [("abysspact_oathbreaker_sfx_ult_eruption", 0.70, 0.0)],
        "oath_pulse": [("abysspact_oathbreaker_sfx_oath_pulse", 0.55, 0.0)],
        "v_start":    [("abysspact_oathbreaker_vo_start", 0.85, 0.0)],
        "v_ult":      [("abysspact_oathbreaker_vo_ult", 0.90, 0.0)],
        "v_kill":     [("abysspact_oathbreaker_vo_kill", 0.85, 0.0)],
        "v_respawn":  [("abysspact_oathbreaker_vo_respawn", 0.85, 0.0)],
        "v_dead":     [("abysspact_oathbreaker_vo_dead", 0.85, 0.0),
                       ("abysspact_oathbreaker_sfx_death_armor", 0.55, 0.1)],
    },
    "abysspact_faceless": {
        "a":           [("abysspact_faceless_sfx_attack_cross", 0.45, 0.0)],
        "a_hit":       [("abysspact_faceless_sfx_attack_hit", 0.50, 0.0)],
        "q_dash":      [("abysspact_faceless_sfx_dash_out", 0.55, 0.0)],
        "q_pass":      [("abysspact_faceless_sfx_dash_pass", 0.55, 0.0)],
        "w_hide":      [("abysspact_faceless_sfx_fade_hide", 0.55, 0.0)],
        "w_fear":      [("abysspact_faceless_sfx_fear_stinger", 0.60, 0.0)],
        "r_grasp":     [("abysspact_faceless_sfx_mask_grasp", 0.65, 0.0)],
        "r_return":    [("abysspact_faceless_sfx_mask_return", 0.60, 0.0)],
        "shroud_rise": [("abysspact_faceless_sfx_shroud_rise", 0.60, 0.0)],
        "mask_crack":  [("abysspact_faceless_sfx_mask_crack", 0.60, 0.0)],
        "v_start":     [("abysspact_faceless_vo_start", 0.85, 0.0)],
        "v_ult":       [("abysspact_faceless_vo_ult", 0.90, 0.0)],
        "v_kill":      [("abysspact_faceless_vo_kill", 0.85, 0.0)],
        "v_respawn":   [("abysspact_faceless_vo_respawn", 0.85, 0.0)],
        "v_dead":      [("abysspact_faceless_vo_dead", 0.85, 0.0),
                        ("abysspact_faceless_sfx_death_shards", 0.55, 0.1)],
    },
    "abysspact_whisperer": {
        "a":             [("abysspact_whisperer_sfx_bead_launch", 0.45, 0.0)],
        "a_hit":         [("abysspact_whisperer_sfx_bead_hit", 0.48, 0.0)],
        "q_cast":        [("abysspact_whisperer_sfx_whisper_cast", 0.55, 0.0)],
        "q_pass":        [("abysspact_whisperer_sfx_whisper_pass", 0.50, 0.0)],
        "w_open":        [("abysspact_whisperer_sfx_ground_eye_open", 0.58, 0.0)],
        "w_blink":       [("abysspact_whisperer_sfx_ground_eye_blink", 0.42, 0.0)],
        "r_open":        [("abysspact_whisperer_sfx_mouths_open", 0.65, 0.0)],
        "r_pulse":       [("abysspact_whisperer_sfx_mouths_pulse", 0.65, 0.0)],
        "madness_stack": [("abysspact_whisperer_sfx_madness_stack", 0.48, 0.0)],
        "madness_burst": [("abysspact_whisperer_sfx_madness_burst", 0.65, 0.0)],
        "v_start":       [("abysspact_whisperer_vo_start", 0.85, 0.0)],
        "v_ult":         [("abysspact_whisperer_vo_ult", 0.90, 0.0)],
        "v_kill":        [("abysspact_whisperer_vo_kill", 0.85, 0.0)],
        "v_respawn":     [("abysspact_whisperer_vo_respawn", 0.85, 0.0)],
        "v_dead":        [("abysspact_whisperer_vo_dead", 0.85, 0.0),
                          ("abysspact_whisperer_sfx_death_beads", 0.55, 0.1)],
    },
    "abysspact_bonebow": {
        "a":             [("abysspact_bonebow_sfx_arrow_release", 0.45, 0.0)],
        "a_hit":         [("abysspact_bonebow_sfx_arrow_hit", 0.48, 0.0)],
        "q_draw":        [("abysspact_bonebow_sfx_piercer_draw", 0.50, 0.0)],
        "q_release":     [("abysspact_bonebow_sfx_piercer_release", 0.55, 0.0)],
        "q_hit":         [("abysspact_bonebow_sfx_piercer_hit", 0.55, 0.0)],
        "funeral_burst": [("abysspact_bonebow_sfx_funeral_burst", 0.62, 0.0)],
        "r_launch":      [("abysspact_bonebow_sfx_army_launch", 0.62, 0.0)],
        "r_rain":        [("abysspact_bonebow_sfx_army_rain", 0.65, 0.0)],
        "skeleton_rise": [("abysspact_bonebow_sfx_skeleton_rise", 0.52, 0.0)],
        "v_start":       [("abysspact_bonebow_vo_start", 0.85, 0.0)],
        "v_ult":         [("abysspact_bonebow_vo_ult", 0.90, 0.0)],
        "v_kill":        [("abysspact_bonebow_vo_kill", 0.85, 0.0)],
        "v_respawn":     [("abysspact_bonebow_vo_respawn", 0.85, 0.0)],
        "v_dead":        [("abysspact_bonebow_vo_dead", 0.85, 0.0),
                          ("abysspact_bonebow_sfx_death_bones", 0.55, 0.1)],
    },
    "abysspact_corvus": {
        "a":          [("abysspact_corvus_sfx_vial_launch", 0.45, 0.0)],
        "a_hit":      [("abysspact_corvus_sfx_vial_break", 0.48, 0.0)],
        "q_cast":     [("abysspact_corvus_sfx_miasma_release", 0.55, 0.0)],
        "q_ring":     [("abysspact_corvus_sfx_miasma_ring", 0.55, 0.0)],
        "w_cast":     [("abysspact_corvus_sfx_raven_takeoff", 0.55, 0.0)],
        "w_wing":     [("abysspact_corvus_sfx_raven_wing", 0.50, 0.0)],
        "raven_peck": [("abysspact_corvus_sfx_raven_peck", 0.48, 0.0)],
        "r_cane":     [("abysspact_corvus_sfx_cane_tap", 0.60, 0.0)],
        "r_cast":     [("abysspact_corvus_sfx_quarantine", 0.68, 0.0)],
        "transmit":   [("abysspact_corvus_sfx_transmit", 0.45, 0.0)],
        "heal_lift":  [("abysspact_corvus_sfx_heal_lift", 0.45, 0.0)],
        "v_start":    [("abysspact_corvus_vo_start", 0.85, 0.0)],
        "v_ult":      [("abysspact_corvus_vo_ult", 0.90, 0.0)],
        "v_kill":     [("abysspact_corvus_vo_kill", 0.85, 0.0)],
        "v_respawn":  [("abysspact_corvus_vo_respawn", 0.85, 0.0)],
        "v_dead":     [("abysspact_corvus_vo_dead", 0.85, 0.0),
                       ("abysspact_corvus_sfx_death_censer", 0.55, 0.1)],
    },
}


def build_i18n():
    P = B.PARAMS
    po = P["oathbreaker"]
    pf = P["faceless"]
    pw = P["whisperer"]
    pb = P["bonebow"]
    pc = P["corvus"]

    desc = {"zh-hans": {}, "zh-hant": {}, "en": {}, "ja": {}, "ko": {}}
    skn = {"zh-hans": {}, "zh-hant": {}, "en": {}, "ja": {}, "ko": {}}

    def put(cid, lang, name, atk, s1, s2, ult, n1, n2, nu):
        desc[lang][cid] = {"name": name, "attack": atk, "skill": s1, "skill2": s2, "ult": ult}
        skn[lang][cid] = {"skill1": n1, "skill2": n2, "ult": nu}

    # --- 1. 断誓 Oathbreaker ---
    put("abysspact_oathbreaker", "zh-hans", "断誓",
        f"断剑劈砍造成{ADi}{O}100%{E}物理伤害。{O}血誓{E}：放技能烧{A}6%{E}当前生命，每损{A}10%{E}生命攻击+{A}4%{E}、攻速+{A}5%{E}。",
        f"横扫黑火月牙造成{ad(po['q_dmg'], po['q_ad'])}物理伤害并{R}减速{po['q_slow']}%{E}；命中英雄回血，斩中被链目标追加伤害。",
        f"甩出誓链勾中首个敌方英雄拽至身前，造成{ad(po['w_dmg'], po['w_ad'])}物理伤害并{R}定身{secs(po['w_bind'])}秒{E}。",
        f"盔甲裂开{A}{secs(po['r_t'])}秒{E}内不会阵亡，吸血{A}{po['r_vamp']}%{E}、普攻附带黑火；期间参与击杀回{A}25%{E}血，否则烧{A}15%{E}当前血。",
        "黑焰斩", "誓链", "断誓")
    put("abysspact_oathbreaker", "zh-hant", "斷誓",
        f"斷劍劈砍造成{ADi}{O}100%{E}物理傷害。{O}血誓{E}：放技能燒{A}6%{E}當前生命，每損{A}10%{E}生命攻擊+{A}4%{E}、攻速+{A}5%{E}。",
        f"橫掃黑火月牙造成{ad(po['q_dmg'], po['q_ad'])}物理傷害並{R}減速{po['q_slow']}%{E}；命中英雄回血，斬中被鏈目標追加傷害。",
        f"甩出誓鏈勾中首個敵方英雄拽至身前，造成{ad(po['w_dmg'], po['w_ad'])}物理傷害並{R}定身{secs(po['w_bind'])}秒{E}。",
        f"盔甲裂開{A}{secs(po['r_t'])}秒{E}內不會陣亡，吸血{A}{po['r_vamp']}%{E}、普攻附帶黑火；期間參與擊殺回{A}25%{E}血，否則燒{A}15%{E}當前血。",
        "黑焰斬", "誓鏈", "斷誓")
    put("abysspact_oathbreaker", "en", "Oathbreaker",
        f"Broken greatsword strike for {ADi}{O}100%{E} physical damage. {O}Blood Oath{E}: skills burn {A}6%{E} current HP; gain {A}+4%{E} AD and {A}+5%{E} AS per {A}10%{E} missing HP.",
        f"Sweep a black-flame crescent for {ad(po['q_dmg'], po['q_ad'])} physical damage and {R}{po['q_slow']}% slow{E}; heals on champion hits and deals bonus damage to chained foes.",
        f"Hurl a broken oath chain that hooks the first enemy champion, pulling them in for {ad(po['w_dmg'], po['w_ad'])} physical damage and {R}{secs(po['w_bind'])}s bind{E}.",
        f"Refuse death for {A}{secs(po['r_t'])}s{E} with {A}{po['r_vamp']}%{E} vamp and bonus black-flame hits. Takedown heals {A}25%{E} max HP at end; otherwise burn {A}15%{E} current HP.",
        "Blackflame Cleave", "Oath Chain", "Broken Oath")
    put("abysspact_oathbreaker", "ja", "断誓",
        f"断剣で{ADi}{O}100%{E}物理ダメージ。{O}血誓{E}：スキルで現在HP{A}6%{E}消費、減少HP{A}10%{E}毎に攻撃+{A}4%{E}・攻撃速度+{A}5%{E}。",
        f"黒炎の斬撃で{ad(po['q_dmg'], po['q_ad'])}物理ダメージと{R}{po['q_slow']}%スロウ{E}。英雄命中で回復、鎖対象に追加ダメージ。",
        f"誓いの鎖で最初の敵英雄を引き寄せ、{ad(po['w_dmg'], po['w_ad'])}物理ダメージと{R}{secs(po['w_bind'])}秒束縛{E}。",
        f"{A}{secs(po['r_t'])}秒{E}不死と吸血{A}{po['r_vamp']}%{E}、通常攻撃に黒炎付与。関与で終了時{A}25%{E}回復、未達成で現在HP{A}15%{E}消費。",
        "黒炎斬", "誓鎖", "断誓")
    put("abysspact_oathbreaker", "ko", "단서",
        f"부러진 대검으로 {ADi}{O}100%{E} 물리 피해. {O}혈서{E}: 스킬 사용 시 현재 체력 {A}6%{E} 소모, 잃은 체력 {A}10%{E}당 공격력+{A}4%{E}, 공속+{A}5%{E}.",
        f"검은 불꽃을 휘둘러 {ad(po['q_dmg'], po['q_ad'])} 물리 피해와 {R}{po['q_slow']}% 둔화{E}. 챔피언 적중 시 회복, 사슬 표적 추가 피해.",
        f"서약의 사슬로 첫 적 챔피언을 끌어당겨 {ad(po['w_dmg'], po['w_ad'])} 물리 피해와 {R}{secs(po['w_bind'])}초 속박{E}.",
        f"{A}{secs(po['r_t'])}초{E} 불사 및 흡혈 {A}{po['r_vamp']}%{E}, 기본 공격 흑염 추가. 처치 관여 시 최대 체력 {A}25%{E} 회복, 실패 시 현재 체력 {A}15%{E} 소모.",
        "흑염참", "서약 사슬", "단서")

    # --- 2. 无面 Faceless ---
    put("abysspact_faceless", "zh-hans", "无面",
        f"指刃划击造成{ADi}{O}100%{E}物理伤害。{O}夺面{E}：参与击杀英雄后戴上其面孔{A}10秒{E}，化身为目标并借用其攻击方式与强化爆发。",
        f"化作黑影穿过目标冲至其身后，对路径敌人造成{ad(pf['q_dmg'], pf['q_ad'])}物理伤害并{R}减速{pf['q_slow']}%{E}。",
        f"遁入黑雾{A}隐身{secs(pf['w_inv'])}秒{E}并提速；现身后的首击令目标直面空脸，追加伤害并{R}恐惧{secs(pf['w_fear'])}秒{E}。",
        f"按住敌方英雄撕下面孔造成{ad(pf['r_dmg'], pf['r_ad'])}物理伤害；目标生命低于{A}25%{E}时直接真实斩杀并立刻夺面。",
        "割影", "无相", "撕面")
    put("abysspact_faceless", "zh-hant", "無面",
        f"指刃劃擊造成{ADi}{O}100%{E}物理傷害。{O}奪面{E}：參與擊殺英雄後戴上其面孔{A}10秒{E}，化身為目標並借用其攻擊方式與強化爆發。",
        f"化作黑影穿過目標衝至其身後，對路徑敵人造成{ad(pf['q_dmg'], pf['q_ad'])}物理傷害並{R}減速{pf['q_slow']}%{E}。",
        f"遁入黑霧{A}隱身{secs(pf['w_inv'])}秒{E}並提速；現身後的首擊令目標直面空臉，追加傷害並{R}恐懼{secs(pf['w_fear'])}秒{E}。",
        f"按住敵方英雄撕下面孔造成{ad(pf['r_dmg'], pf['r_ad'])}物理傷害；目標生命低於{A}25%{E}時直接真實斬殺並立刻奪面。",
        "割影", "無相", "撕面")
    put("abysspact_faceless", "en", "Faceless",
        f"Claw slash for {ADi}{O}100%{E} physical damage. {O}Face Steal{E}: takedowns let him wear the victim's face for {A}10s{E}, assuming their form with boosted combat power.",
        f"Turn to shadow and dash through enemies for {ad(pf['q_dmg'], pf['q_ad'])} physical damage and a {R}{pf['q_slow']}% slow{E}.",
        f"Fade into dark mist, gaining {A}{secs(pf['w_inv'])}s stealth{E} and speed. His first strike out of stealth deals bonus damage and {R}fears for {secs(pf['w_fear'])}s{E}.",
        f"Grasp an enemy champion and rip off their face for {ad(pf['r_dmg'], pf['r_ad'])} physical damage; targets at or below {A}25%{E} HP are executed immediately and stolen.",
        "Shadow Slice", "Formless", "Face Rip")
    put("abysspact_faceless", "ja", "無面",
        f"指刃で{ADi}{O}100%{E}物理ダメージ。{O}奪面{E}：英雄撃破関与で{A}10秒{E}相手の姿に変身し、攻撃特性と強化を得る。",
        f"影となり敵を突き抜けて{ad(pf['q_dmg'], pf['q_ad'])}物理ダメージと{R}{pf['q_slow']}%スロウ{E}。",
        f"黒霧に{A}{secs(pf['w_inv'])}秒隠密{E}し加速。初撃に追加ダメージと{R}{secs(pf['w_fear'])}秒恐怖{E}。",
        f"敵英雄の顔を剥ぎ{ad(pf['r_dmg'], pf['r_ad'])}物理ダメージ。HP{A}25%{E}以下なら即座に確定処刑し奪面する。",
        "影割", "無相", "面剥ぎ")
    put("abysspact_faceless", "ko", "무면",
        f"손톱 칼날로 {ADi}{O}100%{E} 물리 피해. {O}탈면{E}: 적 챔피언 처치 관여 시 {A}10초{E}간 대상의 얼굴과 모습을 빼앗아 변신.",
        f"그림자가 되어 적을 관통하며 {ad(pf['q_dmg'], pf['q_ad'])} 물리 피해와 {R}{pf['q_slow']}% 둔화{E}.",
        f"검은 안개에 {A}{secs(pf['w_inv'])}초 은신{E} 및 가속. 은신 해제 첫 타격은 추가 피해와 {R}{secs(pf['w_fear'])}초 공포{E}.",
        f"적 챔피언의 얼굴을 찢어 {ad(pf['r_dmg'], pf['r_ad'])} 물리 피해. 체력 {A}25%{E} 이하는 즉시 고정 피해 처형 후 탈면.",
        "그림자 베기", "무상", "면박")

    # --- 3. 呓语 Whisperer ---
    put("abysspact_whisperer", "zh-hans", "呓语",
        f"弹射念珠造成{ADi}{O}100%{E}物理伤害。{O}疯狂{E}：技能叠加疯狂，满{A}3层{E}时{R}恐惧1.5秒{E}并爆开魔法伤害波及附近友军且继续传染。",
        f"推出直线穿透的紫色低语，对路径敌人造成{ap(pw['q_dmg'], pw['q_ap'])}魔法伤害并叠加{A}1层{E}疯狂。",
        f"在目标处睁开巨眼持续{A}{secs(pw['w_t'])}秒{E}，每秒造成{ap(pw['w_dmg'], pw['w_ap'])}魔法伤害、{R}减速{pw['w_slow']}%{E}并叠{A}1层{E}疯狂。",
        f"令目标地面裂开众口齐诵，造成{ap(pw['r_dmg'], pw['r_ap'])}魔法伤害，范围内敌人直接叠满{A}3层{E}疯狂当场连锁发狂。",
        "低语", "睁眼", "众口")
    put("abysspact_whisperer", "zh-hant", "囈語",
        f"彈射念珠造成{ADi}{O}100%{E}物理傷害。{O}瘋狂{E}：技能疊加瘋狂，滿{A}3層{E}時{R}恐懼1.5秒{E}並爆開魔法傷害波及附近友軍且繼續傳染。",
        f"推出直線穿透的紫色低語，對路徑敵人造成{ap(pw['q_dmg'], pw['q_ap'])}魔法傷害並疊加{A}1層{E}瘋狂。",
        f"在目標處睜開巨眼持續{A}{secs(pw['w_t'])}秒{E}，每秒造成{ap(pw['w_dmg'], pw['w_ap'])}魔法傷害、{R}減速{pw['w_slow']}%{E}並疊{A}1層{E}瘋狂。",
        f"令目標地面裂開眾口齊誦，造成{ap(pw['r_dmg'], pw['r_ap'])}魔法傷害，範圍內敵人直接疊滿{A}3層{E}瘋狂當場連鎖發狂。",
        "低語", "睜眼", "眾口")
    put("abysspact_whisperer", "en", "Whisperer",
        f"Flick a prayer bead for {ADi}{O}100%{E} physical damage. {O}Madness{E}: skills stack Madness; at {A}3 stacks{E} foes suffer {R}1.5s fear{E}, blast nearby allies for magic damage, and spread +1 stack.",
        f"Send a piercing purple whisper dealing {ap(pw['q_dmg'], pw['q_ap'])} magic damage and adding {A}1 Madness{E} stack.",
        f"Open a giant eye on the ground for {A}{secs(pw['w_t'])}s{E}, dealing {ap(pw['w_dmg'], pw['w_ap'])} magic damage/s, {R}{pw['w_slow']}% slow{E}, and {A}+1 Madness/s{E}.",
        f"Split the earth with chanting mouths for {ap(pw['r_dmg'], pw['r_ap'])} magic damage, instantly filling {A}3 Madness{E} on all foes inside to trigger chain eruptions.",
        "Whisper", "Open Eye", "Chorus of Mouths")
    put("abysspact_whisperer", "ja", "囈語",
        f"数珠を飛ばし{ADi}{O}100%{E}物理ダメージ。{O}狂気{E}：スキルで蓄積、{A}3層{E}で{R}1.5秒恐怖{E}し周囲の味方に魔法爆発＆狂気連鎖。",
        f"貫通する紫の囁きを放ち{ap(pw['q_dmg'], pw['q_ap'])}魔法ダメージと狂気{A}+1層{E}。",
        f"地面に巨眼を開き{A}{secs(pw['w_t'])}秒{E}間、毎秒{ap(pw['w_dmg'], pw['w_ap'])}魔法ダメージ、{R}{pw['w_slow']}%スロウ{E}、狂気{A}+1層{E}。",
        f"無数の口が裂け{ap(pw['r_dmg'], pw['r_ap'])}魔法ダメージを与え、範囲内の敵を即座に狂気{A}3層{E}にして連鎖発狂させる。",
        "低語", "開眼", "衆口")
    put("abysspact_whisperer", "ko", "잠꼬대",
        f"염주를 날려 {ADi}{O}100%{E} 물리 피해. {O}광기{E}: 스킬 적중 시 중첩, {A}3중첩{E} 시 {R}1.5초 공포{E}와 함께 주변 아군에게 마법 폭발 및 연쇄 전파.",
        f"관통하는 보라색 속삭임으로 {ap(pw['q_dmg'], pw['q_ap'])} 마법 피해와 광기 {A}1중첩{E}.",
        f"대상에 거대한 눈을 {A}{secs(pw['w_t'])}초{E}간 열어 매초 {ap(pw['w_dmg'], pw['w_ap'])} 마법 피해, {R}{pw['w_slow']}% 둔화{E}, 광기 {A}1중첩{E}.",
        f"지면에 수많은 입을 열어 {ap(pw['r_dmg'], pw['r_ap'])} 마법 피해와 동시에 모든 적에게 광기 {A}3중첩{E}을 채워 연쇄 폭주.",
        "속삭임", "개안", "중구")

    # --- 4. 骸弦 Bonebow ---
    put("abysspact_bonebow", "zh-hans", "骸弦",
        f"骨箭射击造成{ADi}{O}100%{E}物理伤害。{O}亡兵{E}：每第{A}4箭{E}在目标旁拉起1名骷髅兵作战{A}6秒{E}（继承{A}30%{E}攻击，常规上限{A}3名{E}）。",
        f"射出穿透骨箭造成{ad(pb['q_dmg'], pb['q_ad'])}物理伤害；每命中一名敌方英雄，就在其脚下拉起1名骷髅兵。",
        f"令场上所有骷髅兵冲向目标并自爆，每名造成{ad(40, 50)}范围物理伤害并{R}减速{pb['w_slow']}%{E}。",
        f"朝天射箭降下骨箭雨造成{ad(pb['r_dmg'], pb['r_ad'])}物理伤害并减速，同时爬出{A}5名{E}骷髅兵作战{A}8秒{E}（不占上限）。",
        "穿骨", "葬礼", "亡军")
    put("abysspact_bonebow", "zh-hant", "骸弦",
        f"骨箭射擊造成{ADi}{O}100%{E}物理傷害。{O}亡兵{E}：每第{A}4箭{E}在目標旁拉起1名骷髏兵作戰{A}6秒{E}（繼承{A}30%{E}攻擊，常規上限{A}3名{E}）。",
        f"射出穿透骨箭造成{ad(pb['q_dmg'], pb['q_ad'])}物理傷害；每命中一名敵方英雄，就在其腳下拉起1名骷髏兵。",
        f"令場上所有骷髏兵衝向目標並自爆，每名造成{ad(40, 50)}範圍物理傷害並{R}減速{pb['w_slow']}%{E}。",
        f"朝天射箭降下骨箭雨造成{ad(pb['r_dmg'], pb['r_ad'])}物理傷害並減速，同時爬出{A}5名{E}骷髏兵作戰{A}8秒{E}（不佔上限）。",
        "穿骨", "葬禮", "亡軍")
    put("abysspact_bonebow", "en", "Bonebow",
        f"Bone arrow for {ADi}{O}100%{E} physical damage. {O}Risen Dead{E}: every {A}4th arrow{E} raises a skeleton ({A}30%{E} AD, {A}6s{E}, cap {A}3{E}) beside the target.",
        f"Fire a piercing bone arrow for {ad(pb['q_dmg'], pb['q_ad'])} physical damage, raising a skeleton beside every enemy champion hit.",
        f"Command all living skeletons to rush her target and detonate for {ad(40, 50)} AoE physical damage each plus {R}{pb['w_slow']}% slow{E}.",
        f"Rain bone arrows for {ad(pb['r_dmg'], pb['r_ad'])} AoE physical damage and raise {A}5 uncapped skeletons{E} for {A}8s{E}.",
        "Bone Piercer", "Funeral", "Risen Army")
    put("abysspact_bonebow", "ja", "骸弦",
        f"骨矢で{ADi}{O}100%{E}物理ダメージ。{O}亡兵{E}：{A}4射目{E}毎に骸骨兵を召喚（攻撃{A}30%{E}、{A}6秒{E}、上限{A}3体{E}）。",
        f"貫通する骨矢で{ad(pb['q_dmg'], pb['q_ad'])}物理ダメージ。命中した敵英雄ごとに足元へ骸骨兵を召喚。",
        f"全骸骨兵を目標へ突撃自爆させ、各{ad(40, 50)}範囲物理ダメージと{R}{pb['w_slow']}%スロウ{E}。",
        f"骨矢の雨で{ad(pb['r_dmg'], pb['r_ad'])}物理ダメージを与え、上限外の骸骨兵{A}5体{E}を{A}8秒{E}召喚する。",
        "穿骨", "葬礼", "亡軍")
    put("abysspact_bonebow", "ko", "해현",
        f"뼈화살로 {ADi}{O}100%{E} 물리 피해. {O}망병{E}: {A}4발{E}마다 대상 옆에 해골병 소환(공격력 {A}30%{E}, {A}6초{E}, 최대 {A}3기{E}).",
        f"관통 뼈화살로 {ad(pb['q_dmg'], pb['q_ad'])} 물리 피해. 적중한 적 챔피언마다 해골병 1기 소환.",
        f"모든 해골병을 표적으로 돌진 자폭시켜 기당 {ad(40, 50)} 범위 물리 피해와 {R}{pb['w_slow']}% 둔화{E}.",
        f"뼈화살 비로 {ad(pb['r_dmg'], pb['r_ad'])} 범위 물리 피해와 함께 상한 외 해골병 {A}5기{E}를 {A}8초{E} 소환.",
        "천골", "장례", "망군")

    # --- 5. 鸦医 Corvus ---
    put("abysspact_corvus", "zh-hans", "鸦医",
        f"投掷药瓶造成{ADi}{O}100%{E}物理伤害。{O}传染{E}：技能种下{A}4秒{E}疫病（每秒{A}2%{E}最大血伤）并在敌间传染；队友靠近病人每秒回{A}1%–3%{E}血。",
        f"砸出大瘴气瓶，对范围内敌人造成{ap(pc['q_dmg'], pc['q_ap'])}魔法伤害、{R}减速{pc['q_slow']}%{E}并全部染上疫病。",
        f"派出肩头渡鸦守护队友{A}{secs(pc['w_t'])}秒{E}：赋予{S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E}护盾，渡鸦每秒啄击附近敌人并传染疫病。",
        f"划出持续{A}{secs(pc['r_t'])}秒{E}的隔离区：落地造成{ap(pc['r_init_dmg'], pc['r_init_ap'])}法伤并{R}眩晕{secs(pc['r_stun'])}秒{E}，圈内敌人持续染病减速，队友持续回血。",
        "瘴瓶", "渡鸦", "隔离区")
    put("abysspact_corvus", "zh-hant", "鴉醫",
        f"投擲藥瓶造成{ADi}{O}100%{E}物理傷害。{O}傳染{E}：技能種下{A}4秒{E}疫病（每秒{A}2%{E}最大血傷）並在敵間傳染；隊友靠近病人每秒回{A}1%–3%{E}血。",
        f"砸出大瘴氣瓶，對範圍內敵人造成{ap(pc['q_dmg'], pc['q_ap'])}魔法傷害、{R}減速{pc['q_slow']}%{E}並全部染上疫病。",
        f"派出肩頭渡鴉守護隊友{A}{secs(pc['w_t'])}秒{E}：賦予{S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E}護盾，渡鴉每秒啄擊附近敵人並傳染疫病。",
        f"劃出持續{A}{secs(pc['r_t'])}秒{E}的隔離區：落地造成{ap(pc['r_init_dmg'], pc['r_init_ap'])}法傷並{R}眩暈{secs(pc['r_stun'])}秒{E}，圈內敵人持續染病減速，隊友持續回血。",
        "瘴瓶", "渡鴉", "隔離區")
    put("abysspact_corvus", "en", "Corvus",
        f"Toss a vial for {ADi}{O}100%{E} physical damage. {O}Contagion{E}: skills inflict {A}4s Plague{E} ({A}2%{E} max HP/s) that jumps between foes; allies near sick foes heal {A}1–3%{E} max HP/s.",
        f"Lob a miasma flask for {ap(pc['q_dmg'], pc['q_ap'])} AoE magic damage, {R}{pc['q_slow']}% slow{E}, and Plague on all foes hit.",
        f"Send his raven to perch on an ally for {A}{secs(pc['w_t'])}s{E}, granting a {S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E} shield while pecking nearby enemies to spread Plague.",
        f"Draw a {A}{secs(pc['r_t'])}s{E} Quarantine zone: bursts for {ap(pc['r_init_dmg'], pc['r_init_ap'])} magic damage with {R}{secs(pc['r_stun'])}s stun{E}, plaguing & slowing foes while healing allies inside.",
        "Miasma Flask", "Plague Raven", "Quarantine")
    put("abysspact_corvus", "ja", "鴉医",
        f"薬瓶を投げ{ADi}{O}100%{E}物理ダメージ。{O}伝染{E}：スキルで{A}4秒{E}疫病（毎秒最大HP{A}2%{E}）を拡散し、病敵近くの味方を毎秒{A}1–3%{E}回復。",
        f"瘴気瓶を投げ範囲に{ap(pc['q_dmg'], pc['q_ap'])}魔法ダメージ、{R}{pc['q_slow']}%スロウ{E}と疫病を付与。",
        f"渡鴉を味方の肩に{A}{secs(pc['w_t'])}秒{E}送り{S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E}シールド付与。毎秒周囲の敵を啄み疫病拡散。",
        f"{A}{secs(pc['r_t'])}秒{E}の隔離区を展開：着弾で{ap(pc['r_init_dmg'], pc['r_init_ap'])}魔法ダメージと{R}{secs(pc['r_stun'])}秒スタン{E}。圏内の敵を疫病減速、味方を回復。",
        "瘴瓶", "渡鴉", "隔離区")
    put("abysspact_corvus", "ko", "까마귀 의사",
        f"약병을 던져 {ADi}{O}100%{E} 물리 피해. {O}전염{E}: 스킬로 {A}4초{E} 역병(초당 최대체력 {A}2%{E})을 퍼뜨리며 감염된 적 근처 아군 초당 {A}1~3%{E} 회복.",
        f"독기 병을 던져 범위에 {ap(pc['q_dmg'], pc['q_ap'])} 마법 피해, {R}{pc['q_slow']}% 둔화{E} 및 역병 감염.",
        f"어깨의 까마귀를 아군에게 {A}{secs(pc['w_t'])}초{E} 보내 {S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E} 보호막 부여. 매초 주변 적을 쪼아 역병 감염.",
        f"{A}{secs(pc['r_t'])}초{E} 격리 구역 선포: {ap(pc['r_init_dmg'], pc['r_init_ap'])} 마법 피해와 {R}{secs(pc['r_stun'])}초 기절{E}. 구역 내 적은 역병·둔화, 아군은 지속 회복.",
        "독기 병", "까마귀", "격리 구역")

    # Verify tooltip length limits strictly!
    bad = []
    for lang in TOOLTIP_MAX:
        for cid, d in desc[lang].items():
            for slot in ("attack", "skill", "skill2", "ult"):
                L = shown_length(d[slot])
                if L > TOOLTIP_MAX[lang]:
                    bad.append(f"{lang}/{cid}.{slot}: {L} > {TOOLTIP_MAX[lang]}")
    if bad:
        sys.exit("TOOLTIP LENGTH EXCEEDED:\n" + "\n".join(bad))

    i18n = {lang: {"description": desc[lang], "skill_name": skn[lang]} for lang in desc}
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)
    print(f"wrote text/champion.i18n (5 langs x 5 heroes, all under TOOLTIP_MAX!)")


def kit_sounds(cid):
    found = set()
    data = json.loads(open(lp(os.path.join(MOD, "champion", f"{cid}.data_champion")), "rb").read().decode("utf-8-sig"))

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx"):
                found.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    return found


def dll_sounds(cid, rs_name):
    src = open(lp(os.path.join(REPO, "addons", "abysspact", "src", f"{rs_name}.rs")), encoding="utf-8").read()
    found = set(re.findall(r'play_sfx\("([^"]+)"', src))
    # Voice cues played via Voice controller
    for cue in ("v_start", "v_ult", "v_kill", "v_respawn", "v_dead"):
        found.add(f"{cid}_{cue}")
    return found


def write_sounds_and_overrides():
    rs_map = {
        "abysspact_oathbreaker": "oathbreaker",
        "abysspact_faceless": "faceless",
        "abysspact_whisperer": "whisperer",
        "abysspact_bonebow": "bonebow",
        "abysspact_corvus": "corvus",
    }
    ov = {
        "asset/base/text/champion": {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"},
        "asset/base/style/champion_view": {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"},
        # Real summon unit sprite/anim overrides for sim.spawn_unit("abysspact_skeleton", ...)
        "asset/base/aseprite_resources/champions/abysspact_skeleton#sheet": {
            "remapping": f"asset/{MOD_ID}/champions/abysspact_skeleton#sheet", "type": "override"
        },
        "asset/base/aseprite_resources/champions/abysspact_skeleton#anim": {
            "remapping": f"asset/{MOD_ID}/champions/abysspact_skeleton#anim", "type": "override"
        },
    }
    sfx_dir = os.path.join(MOD, "sound", "sfx")
    # Clean stale .sound_info files first
    if os.path.isdir(lp(sfx_dir)):
        for fn in os.listdir(lp(sfx_dir)):
            if fn.endswith(".sound_info"):
                os.remove(lp(os.path.join(sfx_dir, fn)))

    all_sound_keys = set()
    for cid, rs_name in rs_map.items():
        played = kit_sounds(cid) | dll_sounds(cid, rs_name)
        defined = {f"{cid}_{k}": v for k, v in SOUNDS[cid].items()}
        missing = sorted(played - set(defined))
        unused = sorted(set(defined) - played)
        if missing or unused:
            sys.exit(f"SOUND MISMATCH for {cid}: missing={missing}, unused={unused}")
        for ev, plays in defined.items():
            for clip, vol, dly in plays:
                if clip == ev:
                    sys.exit(f"{ev} shares clip name")
                if not os.path.isfile(lp(os.path.join(sfx_dir, clip + ".mp3"))):
                    sys.exit(f"MISSING MP3 CLIP: {clip}.mp3")
                all_sound_keys.add(clip)
            save(os.path.join(sfx_dir, ev + ".sound_info"),
                 {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})
            all_sound_keys.add(ev)

    for key in sorted(all_sound_keys):
        ov[f"asset/base/sound/sfx/{key}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{key}", "type": "override"}

    save(os.path.join(MOD, "mod.override_info"), ov)
    print(f"wrote {sum(len(v) for v in SOUNDS.values())} .sound_info files and mod.override_info ({len(ov)} entries)")


def write_champion_view():
    entries = {
        "abysspact_oathbreaker": {"face": {"x": 3, "y": -32}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_faceless":    {"face": {"x": 2, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_whisperer":   {"face": {"x": 2, "y": -34}, "center": {"x": 0, "y": -16}, "banpick_center": {"x": 0, "y": -12}},
        "abysspact_bonebow":     {"face": {"x": 2, "y": -32}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_corvus":      {"face": {"x": 3, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
    }
    save(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": entries})
    print("wrote style/champion_view.champion_view")


def write_mod_info():
    desc = (
        "Abyss Pact (渊契) dark-fantasy original champion pack for Teamfight Manager 2: "
        "Oathbreaker (断誓 · Top melee cursed knight who burns blood for power and refuses death), "
        "Faceless (无面 · Jungle assassin who executes low-HP foes and steals their face & body), "
        "Whisperer (呓语 · Mid mage whose Madness stacks trigger chain-reaction fear explosions), "
        "Bonebow (骸弦 · Bot marksman who raises real skeleton soldiers and commands them to rush-detonate), "
        "and Corvus (鸦医 · Support plague doctor whose contagion jumps between foes while healing allies "
        "and sending his shoulder raven to guard teammates). "
        "Powered by abysspact.dll for dense HD PPU frames, real summon units, full-body Face-Steal, "
        "and Mandarin AI voice lines."
    )
    mi = {
        "author": "BoDUD",
        "contains_code": True,
        "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}],
        "description": desc,
        "last_updated": "2026-11-24",
        "mod_id": MOD_ID,
        "mod_type": "native",
        "name": NAME,
        "version": VERSION,
    }
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(f"wrote mod.mod_info ({MOD_ID} {VERSION})")


def main():
    build_i18n()
    write_champion_view()
    write_sounds_and_overrides()
    write_mod_info()
    print("ABYSS PACT PACK SETUP COMPLETE!")


if __name__ == "__main__":
    main()
