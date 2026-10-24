"""Build the add-on's copy of Garen from the main pack (R an execute on missing health, cast only for a kill).

    python addons/league_garen_ult/make_override.py [--check]

Garen has no kit script: his kit is the main pack's league/champion/league_garen.data_champion. This reads it, checks
that src/plan.rs's numbers are the kit's (R's FixedAttack damage / attack_ratio, its range, its start_timing + the
Delayed ticks to the blow), and writes addons/league_garen_ult/override/league_garen.data_champion and
.../text/champion.i18n: the same kit with -
  * R's FixedAttack without its 12% max-health share (the add-on adds R_MISSING% of the missing health at the blow);
  * R marking its target at the cast (an AddBuff of plan.rs's MARK, MARK_TICKS long) for the passive;
  * the passive league_garen_ult:verdict (it deals that share; the AI hook league_garen_ult:ult decides when R goes);
  * R's tooltip pointing to description.league_garen_ult.ult in the add-on's wording.
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
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def plan_consts():
    src = open(lp(os.path.join(ADDON, "src", "plan.rs")), encoding="utf-8").read()
    out = {}
    for name in ("R_BASE", "R_AD", "R_MISSING", "R_RANGE", "R_LAND", "MARK_TICKS", "MARK_TO_LAND"):
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
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: TEXT[lang].format(b=c["R_BASE"], a=c["R_AD"], m=c["R_MISSING"]) for lang in main_text}
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text}
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
