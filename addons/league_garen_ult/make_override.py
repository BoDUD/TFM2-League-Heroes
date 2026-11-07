"""Build the add-on's copy of Garen from the main pack (R an execute on missing health, cast only for a kill).

    python addons/league_garen_ult/make_override.py [--check]

Garen has no kit script: his kit is the main pack's league/champion/league_garen.data_champion. This reads it, checks
that src/plan.rs's numbers are the kit's (R's FixedAttack damage / attack_ratio, its range, its start_timing + the
Delayed ticks to the blow), and writes addons/league_garen_ult/override/league_garen.data_champion and
.../text/champion.i18n: the same kit with -
  * R's FixedAttack without its 12% max-health share (the add-on adds R_MISSING% of the missing health at the blow);
  * R marking its target at the cast (an AddBuff of plan.rs's MARK, MARK_TICKS long) for the passive;
  * the passive league_garen_ult:verdict (it deals that share; the AI hook league_garen_ult:ult decides when R goes);
  * R's tooltip pointing to description.league_garen_ult.ult in the add-on's wording;
  * (0.2.0) E's seven spins each running league_garen_ult:spin_as on every unit the spin hits, right after the main
    pack's Attack (plan.rs's E_BASE / E_AD / E_SPINS checked against them): bonus attack speed adds damage, League's
    "a spin more every 25% bonus attack speed", and E's tooltip pointing to description.league_garen_ult.skill2.
Every other champion stays untouched. Run it again whenever the main pack's Garen changes (--check: compare only).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_garen_ult")
MOD_ID = "league_garen_ult"
HERO = "league_garen"
TEXT_KEY = "description." + MOD_ID + ".ult"
E_TEXT_KEY = "description." + MOD_ID + ".skill2"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
O, W, Y, E = "<#ff9028ff>", "<#f5f5f5ff>", "<#ffb900ff>", "<>"
TEXT = {
    "zh-hans": "【附加包】" + O + "德玛西亚正义" + E + "：召唤巨剑从天而降，对目标敌方英雄造成" + W + "{b}" + E + " + " + ADi + O + "{a}% 攻击力" + E +
               " + " + W + "{m}% 目标已损失生命值" + E + "的" + W + "真实伤害" + E + "。只在能斩杀射程内的英雄时释放。",
    "zh-hant": "【附加包】" + O + "德瑪西亞正義" + E + "：召喚巨劍從天而降，對目標敵方英雄造成" + W + "{b}" + E + " + " + ADi + O + "{a}% 攻擊力" + E +
               " + " + W + "{m}% 目標已損失生命值" + E + "的" + W + "真實傷害" + E + "。只在能斬殺射程內的英雄時施放。",
    "en": "[Add-on] " + O + "Demacian Justice" + E + ": Calls a giant sword down on the target enemy champion, dealing " + W + "{b}" + E +
          " + " + ADi + O + "{a}% AD" + E + " + " + W + "{m}% of its missing health" + E + " " + W + "true damage" + E +
          ". Cast only when it kills a champion in range.",
    "ko": "[확장] " + O + "데마시아의 정의" + E + ": 대상 적 챔피언에게 거대한 검을 내리꽂아 " + W + "{b}" + E + " + " + ADi + O + "공격력의 {a}%" + E +
          " + " + W + "대상 잃은 체력의 {m}%" + E + " " + W + "고정 피해" + E + "를 줍니다. 사거리 안의 챔피언을 처치할 수 있을 때만 사용합니다.",
    "ja": "【拡張】" + O + "デマーシアの正義" + E + "：対象の敵チャンピオンに巨大な剣を落とし、" + W + "{b}" + E + " + " + ADi + O + "攻撃力の{a}%" + E +
          " + " + W + "対象の減少体力の{m}%" + E + "の" + W + "確定ダメージ" + E + "を与える。射程内のチャンピオンを倒せる時にだけ使う。",
}
ARi = "<i#asset/base/ui/banpick/champion_stat_icon:armor_0>"
AR, G = "<#ffdd8eff>", "<#6aff55ff>"
# E (0.2.0): the main pack's Judgment, shortened to make room for the attack-speed rule
E_TEXT = {
    "zh-hans": "【附加包】" + O + "审判" + E + "：盖伦挥剑旋转" + Y + "3秒" + E + "，边转边走向身边的敌人，共转" + Y + "{n}" + E +
               "圈，每圈对周围敌人造成" + O + "{b}" + E + " + " + ADi + O + "{a}% 攻击力" + E + "的" + O + "物理伤害" + E +
               "，额外攻速每" + Y + "25%" + E + "多算" + Y + "1" + E + "圈。走向的敌人每圈多受" + Y + "25%" + E + "，第" + Y + "{n}" + E +
               "圈" + ARi + AR + "护甲" + E + "-" + Y + "25%" + E + "，持续" + Y + "6秒" + E + "。被动 " + O + "坚韧" + E + "：很高的" +
               G + "生命回复" + E + "。",
    "zh-hant": "【附加包】" + O + "審判" + E + "：蓋倫揮劍旋轉" + Y + "3秒" + E + "，邊轉邊走向身邊的敵人，共轉" + Y + "{n}" + E +
               "圈，每圈對周圍敵人造成" + O + "{b}" + E + " + " + ADi + O + "{a}% 攻擊力" + E + "的" + O + "物理傷害" + E +
               "，額外攻速每" + Y + "25%" + E + "多算" + Y + "1" + E + "圈。走向的敵人每圈多受" + Y + "25%" + E + "，第" + Y + "{n}" + E +
               "圈" + ARi + AR + "護甲" + E + "-" + Y + "25%" + E + "，持續" + Y + "6秒" + E + "。被動 " + O + "堅韌" + E + "：很高的" +
               G + "生命回復" + E + "。",
    "en": "[Add-on] " + O + "Judgment" + E + ": Garen spins for " + Y + "3s" + E + ", walking to the nearest enemies. Each of the " +
          Y + "{n}" + E + " spins deals " + O + "{b}" + E + " + " + ADi + O + "{a}% AD" + E + " " + O + "physical damage" + E +
          " to nearby enemies, " + Y + "25%" + E + " more to the one he walks to; every " + Y + "25%" + E +
          " bonus attack speed adds a spin's damage. The " + Y + "{n}th" + E + " spin lowers " + ARi + AR + "armor" + E + " by " +
          Y + "25%" + E + " for " + Y + "6s" + E + ". Passive " + O + "Perseverance" + E + ": very high " + G + "health regeneration" + E + ".",
    "ko": "[확장] " + O + "심판" + E + ": 가렌이 " + Y + "3초" + E + " 동안 회전하며 가까운 적에게 다가갑니다. " + Y + "{n}" + E +
          "번의 회전마다 주변 적에게 " + O + "{b}" + E + " + " + ADi + O + "공격력의 {a}%" + E + " " + O + "물리 피해" + E +
          "(다가가는 대상은 " + Y + "25%" + E + " 추가), 추가 공격 속도 " + Y + "25%" + E + "마다 회전 1번의 피해가 더해집니다. " + Y + "{n}" + E +
          "번째 회전은 " + ARi + AR + "방어력" + E + "을 " + Y + "6초" + E + " 동안 " + Y + "25%" + E + " 낮춥니다. 기본 지속 효과 " + O + "인내" + E +
          ": " + G + "체력 재생" + E + "이 매우 높습니다.",
    "ja": "【拡張】" + O + "審判" + E + "：ガレンは" + Y + "3秒" + E + "間回転し近くの敵へ歩み寄る。" + Y + "{n}" + E + "回の回転ごとに周囲の敵に" +
          O + "{b}" + E + " + " + ADi + O + "攻撃力の{a}%" + E + "の" + O + "物理ダメージ" + E + "（向かう敵には" + Y + "25%" + E +
          "増し）、追加攻撃速度" + Y + "25%" + E + "ごとに1回転分増える。" + Y + "{n}" + E + "回目は" + ARi + AR + "物理防御" + E + "を" + Y + "6秒" + E +
          "間" + Y + "25%" + E + "低下。自動効果 " + O + "忍耐" + E + "：高い" + G + "体力自動回復" + E + "。",
}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def walk(node):
    """Every dict in a JSON tree."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def plan_consts():
    src = open(lp(os.path.join(ADDON, "src", "plan.rs")), encoding="utf-8").read()
    out = {}
    for name in ("R_BASE", "R_AD", "R_MISSING", "R_RANGE", "R_LAND", "MARK_TICKS", "MARK_TO_LAND", "E_SPINS", "E_BASE",
                 "E_AD"):
        m = re.search(r"pub const " + name + r": usize = ([\d_]+);", src)
        out[name] = int(m.group(1).replace("_", ""))
    out["MARK"] = re.search(r'pub const MARK: &str = "([^"]+)";', src).group(1)
    return out


def build():
    c = plan_consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    u = champion["ult"]
    eff = u["effect"]["effects"]
    delayed = [x for x in eff if x.get("type") == "Delayed"]
    if len(delayed) != 1:
        sys.exit("R is no longer one Delayed blow: update this script")
    blow = [x for x in delayed[0]["effects"] if x.get("type") == "FixedAttack"]
    if len(blow) != 1:
        sys.exit("R's blow is no longer one FixedAttack: update this script")
    checks = {"R_BASE": blow[0]["damage"], "R_AD": blow[0]["attack_ratio"], "R_RANGE": u["range"],
              "R_LAND": u["start_timing"] + delayed[0]["tick"], "MARK_TO_LAND": delayed[0]["tick"]}
    wrong = {k: (c[k], v) for k, v in checks.items() if c[k] != v}
    if wrong:
        sys.exit("src/plan.rs differs from the main pack's Garen (plan, kit): %s" % wrong)
    if u["casting_target"] != "EnemyChampion":
        sys.exit("R's casting target changed: update the AI hook")
    blow[0]["target_hp_ratio"] = 0
    eff.insert(0, {"type": "AddBuff", "buff_state": {"name": c["MARK"], "duration": {"Time": {"tick": c["MARK_TICKS"]}}}})
    champion["passive"] = {"passive_ref": MOD_ID + ":verdict", "params": {}}
    u["description"] = "#asset/base/text/champion?" + TEXT_KEY
    # E (0.2.0): the spins - the RangeEffects with an Attack in E (the dashes' hits sit in MoveToTarget end_effects)
    spins = [x for x in walk(champion["skill2"]) if x.get("type") == "RangeEffect"
             and any(y.get("type") == "Attack" for y in x.get("effects", []))]
    if len(spins) != c["E_SPINS"]:
        sys.exit("E has %d spins, plan.rs says %d: update this script" % (len(spins), c["E_SPINS"]))
    for x in spins:
        hit = [y for y in x["effects"] if y.get("type") == "Attack"]
        if len(hit) != 1 or (hit[0]["damage"], hit[0]["attack_ratio"]) != (c["E_BASE"], c["E_AD"]):
            sys.exit("an E spin's Attack differs from plan.rs (E_BASE, E_AD): %s" % hit)
        x["effects"].insert(x["effects"].index(hit[0]) + 1, {"type": "Native", "effect_ref": MOD_ID + ":spin_as"})
    champion["skill2"]["description"] = "#asset/base/text/champion?" + E_TEXT_KEY
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: TEXT[lang].format(b=c["R_BASE"], a=c["R_AD"], m=c["R_MISSING"]) for lang in main_text}
    e_texts = {lang: E_TEXT[lang].format(b=c["E_BASE"], a=c["E_AD"], n=c["E_SPINS"]) for lang in main_text}
    long = {lang: shown_length(t) for lang, t in list(texts.items()) + list(e_texts.items())
            if shown_length(t) > TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang], "skill2": e_texts[lang]}}} for lang in main_text}
    return champion, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    champion, text = build()
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps(text, ensure_ascii=False, indent=2) + "\n"}
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.exists(lp(p)) or open(lp(p), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for p, t in files.items():
        os.makedirs(lp(os.path.dirname(p)), exist_ok=True)
        with open(lp(p), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in files))


if __name__ == "__main__":
    main()
