"""Build the add-on's copy of Milio from the main pack (Fired Up! burning on the next hit, Breath of Life only to save).

    python -X utf8 addons/league_milio/make_override.py

Rebuilds Milio with tools/kit/build_milio.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_milio.data_champion byte for byte (so the copy never drifts from the shipped kit) and that
src/rules.rs's R numbers are the kit's (R_CAST_RANGE = r_arm_range, R_RADIUS = r_r, R_REL = R_REL, ATTACK_RANGE =
atk_range), and writes addons/league_milio/override/league_milio.data_champion and .../text/champion.i18n:
  * the build with r_now=1 (R fires Breath of Life on the cast itself - the AI hook league_milio:ult decides when) and
    p_atk = p_ap = MARK (league_milio_fired marks the ally for Fired Up!'s burn, its picture unchanged; MARK % attack and
    ability power stay on it for balance, see below), plus NUMBERS;
  * passive league_milio:fired with PASSIVE as its params (the burn on the marked ally's next hit);
  * the native effect league_milio:cleanse first in R's circle (a real cleanse of the CC already on an ally);
  * league_milio_fired also on every ally a Cozy Campfire pulse heals (League's hearth applies Fired Up! each pulse);
  * the attack's (passive) and the ult's tooltips pointing to description.league_milio_fired.* with the add-on's
    wording in 5 languages (a lead that shows in game whether the override took).
Every other champion stays untouched. Run it again whenever the main pack's Milio changes.
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_milio")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_milio as kit  # noqa: E402
import setup_milio as setup  # noqa: E402

TEXT_ID = "league_milio_fired"      # the text's key (the hero's own id is league_milio)
HERO = "league_milio"
# the passive's params (src/rules.rs Params::default must match; tests::the_passive_params_match_make_override):
# League's burn 20-100 by level 1-18 (TFM2 levels 1-12), 1.5 s in 15-tick parts, at most 100 to monsters
PASSIVE = {"burn_hi": 100, "burn_lo": 20, "burn_p": 15, "burn_t": 90, "mon_cap": 100}
# the copy's own kit numbers on top of P (balance of the add-on version; empty = the main pack's)
NUMBERS = {}
# attack / ability power % the mark itself still gives for its p_t ticks. League's Fired Up! gives none, but with the
# burn alone the add-on's Milio fell to -2.12 / ... in the hooked classic-SDK simulation (scratchpad mi_hook.rs, kdm.py,
# lane 4 vs priest / monk / bard / pythoness / spirit_caller, seeds 1-12; main pack d9 +0.28): 15 -> -0.37, 20 -> +0.24,
# 30 -> +0.87 (the burn and R by health on top); 20 keeps him where the main pack's Milio is
MARK = 20
A, G, C, O, M, E = setup.A, setup.G, setup.C, setup.O, setup.M, setup.E
RH = setup.RH
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
BURN = M + "{burn_lo}-{burn_hi}" + E
ATTACK = {
    "zh-hans": "射出小火球。被动" + O + "热情洋溢！" + E + "：技能触及的友方（营火每跳也算）{mark_zh}下一次命中敌人时将其点燃，" + A + "{burn_t}秒" + E +
               "内造成" + BURN + "（随等级）" + M + "魔法伤害" + E + "{mark_end_zh}；米利欧获得" + A + "{p_ms}%" + E + "移速。",
    "zh-hant": "射出小火球。被動" + O + "爐火餘溫" + E + "：技能觸及的友軍（營火每跳也算）{mark_zt}下一次命中敵人時將其點燃，" + A + "{burn_t}秒" + E +
               "內造成" + BURN + "（隨等級）" + M + "魔法傷害" + E + "{mark_end_zt}；米里歐獲得" + A + "{p_ms}%" + E + "跑速。",
    "en": "Throws a small fireball. Passive " + O + "Fired Up!" + E + ": allies his spells touch (each campfire pulse too) {mark_en}set the "
          "enemy they hit next ablaze for " + BURN + " " + M + "magic damage" + E + " (by level) over " + A + "{burn_t}s" + E +
          "{mark_end_en}; Milio gains " + A + "{p_ms}%" + E + " move speed.",
    "ko": "작은 불덩이를 던집니다. 기본 지속 효과 " + O + "타오르는 힘" + E + ": 스킬이 닿은 아군(모닥불 매 회복 포함)이 {mark_ko}다음에 맞힌 적을 불태워 " + A +
          "{burn_t}초" + E + " 동안 " + BURN + "(레벨 비례) " + M + "마법 피해" + E + "{mark_end_ko}, 밀리오는 이동 속도 " + A + "{p_ms}%" + E + ".",
    "ja": "小さな火の玉を投げる。自動効果" + O + "ファイヤーアップ！" + E + "：スキルが触れた味方（焚き火の回復ごとにも）が{mark_ja}次に攻撃した敵を燃やし、" + A +
          "{burn_t}秒" + E + "で" + BURN + "（レベル比例）の" + M + "魔法ダメージ" + E + "{mark_end_ja}、ミリオは移動速度" + A + "{p_ms}%" + E + "。",
}
ULT = {
    "zh-hans": "周围友方英雄被控制、生命低于" + A + "30%" + E + "或" + A + "1秒" + E + "内被打掉三成（敌方英雄在旁）时，" + C + "解除" + E +
               "周围友方英雄的控制，恢复" + RH + "生命，" + C + "免疫控制{r_imm}秒" + E + "并获得" + A + "{r_ten}%" + E + "韧性（" + A + "{r_tt}秒" + E + "）。",
    "zh-hant": "周圍友方英雄被控場、生命低於" + A + "30%" + E + "或" + A + "1秒" + E + "內被打掉三成（敵方英雄在旁）時，" + C + "解除" + E +
               "周圍友方英雄的控場，恢復" + RH + "生命，" + C + "免疫控場{r_imm}秒" + E + "並獲得" + A + "{r_ten}%" + E + "韌性（" + A + "{r_tt}秒" + E + "）。",
    "en": "When an allied champion around him is crowd-controlled, below " + A + "30%" + E + " health or lost 30% within " + A + "1s" + E +
          " (an enemy champion close), allied champions around him are " + C + "cleansed" + E + ", heal " + RH + ", are " + C +
          "immune to crowd control for {r_imm}s" + E + " and gain " + A + "{r_ten}%" + E + " tenacity for " + A + "{r_tt}s" + E + ".",
    "ko": "주변 아군 챔피언이 군중 제어되거나 체력 " + A + "30%" + E + " 미만이거나 " + A + "1초" + E + " 안에 30%를 잃으면(적 챔피언 근처) 주변 아군 챔피언의 " +
          C + "군중 제어 해제" + E + ", " + RH + " 회복, " + C + "{r_imm}초 군중 제어 면역" + E + ", " + A + "{r_tt}초" + E + " 동안 강인함 " + A + "{r_ten}%" + E + ".",
    "ja": "周囲の味方チャンピオンが行動妨害を受けるか体力" + A + "30%" + E + "未満か" + A + "1秒" + E + "で30%失った時（敵チャンピオンが近い時）、周囲の味方の" + C +
          "行動妨害を解除" + E + "、" + RH + "回復、" + C + "{r_imm}秒行動妨害無効" + E + "、" + A + "{r_tt}秒" + E + "行動妨害耐性" + A + "{r_ten}%" + E + "。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rules_consts():
    """src/rules.rs's R numbers: {name: value}."""
    with open(lp(os.path.join(ADDON, "src", "rules.rs")), encoding="utf-8") as f:
        src = f.read()
    out = {}
    for name in ("R_CAST_RANGE", "R_RADIUS", "R_REL", "ATTACK_RANGE"):
        m = re.search(r"pub const %s: (?:f64|usize) = ([0-9_.]+);" % name, src)
        if not m:
            sys.exit("no %s in src/rules.rs: update this script" % name)
        out[name] = float(m.group(1).replace("_", ""))
    return out


def walk(node):
    """Every dict in the tree."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def add_buff_names(effects):
    return [e.get("buff_state", {}).get("name") for e in effects if isinstance(e, dict) and e.get("type") == "AddBuff"]


def main():
    p = dict(kit.P)
    if "r_now" not in p:
        sys.exit("build_milio.P has no r_now: the kit cannot build the add-on's R yet")
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_milio differs from build_milio.P: rebuild it first")
    c = rules_consts()
    want = {"R_CAST_RANGE": p["r_arm_range"], "R_RADIUS": p["r_r"], "R_REL": p["r_rel"], "ATTACK_RANGE": p["atk_range"]}
    off = {k: (c[k], v) for k, v in want.items() if abs(c[k] - v) > 1e-6}
    if off:
        sys.exit("src/rules.rs's R numbers are not the kit's (rules.rs, kit): %s" % off)

    q = dict(p, r_now=1, p_atk=MARK, p_ap=MARK, **NUMBERS)
    champion = kit.build(q)
    if json.dumps(champion["ult"]) == json.dumps(kit.build(p)["ult"]):
        sys.exit("r_now=1 left R as it was: update this script")
    fired = "league_milio_fired"
    # the mark: no stats on any league_milio_fired in the copy (E's hug and R's breath)
    for d in walk(champion):
        bs = d.get("buff_state")
        if isinstance(bs, dict) and bs.get("name") == fired and (bs.get("attack_mult", 0), bs.get("magic_power_mult", 0)) != (
                q["p_atk"], q["p_ap"]):
            sys.exit("a league_milio_fired with other stats than MARK in the copy: update this script")
    mark = next(copy.deepcopy(d) for d in walk(champion) if d.get("type") == "AddBuff"
                and d.get("buff_state", {}).get("name") == fired)
    # R's circle: the cleanse first
    breaths = [d for d in walk(champion["ult"]) if d.get("type") == "RangeEffect"
               and "league_milio_r_free" in add_buff_names(d.get("effects", []))]
    if len(breaths) != 1:
        sys.exit("R's circle (the RangeEffect adding league_milio_r_free) not found once: update this script")
    breaths[0]["effects"].insert(0, {"type": "Native", "effect_ref": "league_milio:cleanse"})
    # every campfire pulse: Fired Up! on the allies it heals
    pulses = [d for d in walk(champion["skill2"]) if d.get("name") == "league_milio_w_heal" and "applied_effects" in d]
    if not pulses:
        sys.exit("the campfire's heal zone (league_milio_w_heal) not found: update this script")
    for z in pulses:      # one per way the hug goes out (beside the enemy, round him, himself)
        z["applied_effects"].append({"casting_type": "Targeting", "effect": copy.deepcopy(mark)})
    champion["passive"] = {"passive_ref": "league_milio:fired", "params": dict(sorted(PASSIVE.items()))}
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"
    champion["ult"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.ult"

    values = setup.values(q)
    values.update({"burn_lo": PASSIVE["burn_lo"], "burn_hi": PASSIVE["burn_hi"], "burn_t": setup.secs(PASSIVE["burn_t"])})
    m = A + f"{MARK}%" + E
    t = A + setup.secs(q["p_t"])
    values.update({
        "mark_zh": f"获得{m}攻击力和法强，" if MARK else "", "mark_end_zh": f"（加成随之消失，最多{t}秒{E}）" if MARK else "",
        "mark_zt": f"獲得{m}攻擊力和魔攻，" if MARK else "", "mark_end_zt": f"（加成隨之消失，最多{t}秒{E}）" if MARK else "",
        "mark_en": f"gain {m} attack and ability power and " if MARK else "",
        "mark_end_en": f" (the bonus ends with that hit, {t}s{E} at most)" if MARK else "",
        "mark_ko": f"공격력과 주문력 {m} 증가, " if MARK else "", "mark_end_ko": f"(증가는 그 공격으로 끝, 최대 {t}초{E})" if MARK else "",
        "mark_ja": f"攻撃力と魔力{m}増加、" if MARK else "", "mark_end_ja": f"（増加はその攻撃で終了、最大{t}秒{E}）" if MARK else "",
    })
    texts = {lang: {"attack": (LEAD[lang] + ATTACK[lang]).format(**values), "ult": (LEAD[lang] + ULT[lang]).format(**values)}
             for lang in ATTACK}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in texts.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    for lang, d in texts.items():
        print(lang, " ".join(f"{k}:{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for k, t in d.items()))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
