"""Build the add-on's copy of Locke from the main pack (Silver Stake on missing health, Soul Ignition on current health,
Purgatory's execute and seals, takedown resets).

    python addons/league_locke/make_override.py [--draft] [--check]

Rebuilds Locke with tools/kit/build_locke.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_locke.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_locke/override/league_locke.data_champion and
.../text/champion.i18n: the build with native=1 (build_locke.py's docstring) -
  * passive = league_locke:exorcist (params build_locke.NATIVE_KEYS);
  * no takedown window (the add-on reads deaths and readies E itself); the attack marks `p_hit` (the add-on adds the
    missing-health part); W's `w_on` keeps its attack speed but neither burns nor heals (the add-on does, on current
    health); Purgatory's marks `r_mark` take no threshold checks (the add-on executes under r_exec% and keeps the seals);
  * every slot's tooltip (keys of the add-on's own id) says the League rules, so the tooltip in game shows whether the
    override took.
Every other champion stays untouched. Run it again whenever the main pack's Locke changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_locke")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_locke as kit  # noqa: E402
import setup_locke as setup  # noqa: E402

MOD_ID = "league_locke"
HERO = "league_locke"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")   # the add-on plays every slot (the W look), its tooltips say so
mag, t, n, cc, tr, APi = setup.mag, setup.t, setup.n, setup.cc, setup.tr, setup.APi
# the add-on's tag before each text; Ritual Nails and Ashen Pursuit keep the main pack's rules (the add-on reads their
# marks for the takedowns), so their texts are the main pack's
TAG = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
# lang -> the add-on's texts for every slot (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": n("圣银穿心") + "：攻击附带" + mag("p_dmg", "p_ap") + "魔法伤害，外加目标已损失生命{p_miss}%。" + n("灵焰仪式") +
                  "：灰猎无影落到敌方英雄身边时点燃（每" + t("{w_cd}秒") + "一次）：" + t("{w_t}秒") + "内攻速+{w_as}%、"
                  "移速+{w_ms}%（递减），" + t("每秒") + "受到当前生命{w_cost}%" + tr("真实伤害") + "，结束时回复其中{w_back}%。",
        "ult": "法器箱砸向敌方英雄：周围敌人受到" + mag("r_dmg", "r_ap") + "魔法伤害并" + cc("减速") + "{r_slow}%（递减）；"
               "英雄被标记" + t("{r_t}秒") + "，生命低于最大生命{r_exec}%即被" + tr("处决") + "，倒下处留下法器，捡起得一层封印"
               "（最多{seals}层，整局保留）：处决线+{r_exec_step}%，大招剩余冷却-{r_cap}%。",
    },
    "zh-hant": {
        "attack": n("銀樁咒殺") + "：攻擊附帶" + mag("p_dmg", "p_ap") + "魔法傷害，外加目標已損失生命{p_miss}%。" + n("燃魂回元") +
                  "：瞬影追命落到敵方英雄身邊時點燃（每" + t("{w_cd}秒") + "一次）：" + t("{w_t}秒") + "內攻速+{w_as}%、"
                  "移速+{w_ms}%（遞減），" + t("每秒") + "受到當前生命{w_cost}%" + tr("真實傷害") + "，結束時回復其中{w_back}%。",
        "ult": "法器箱砸向敵方英雄：周圍敵人受到" + mag("r_dmg", "r_ap") + "魔法傷害並" + cc("緩速") + "{r_slow}%（遞減）；"
               "英雄被標記" + t("{r_t}秒") + "，生命低於最大生命{r_exec}%即被" + tr("處決") + "，倒下處留下法器，撿起得一層封印"
               "（最多{seals}層，整局保留）：處決線+{r_exec_step}%，大招剩餘冷卻-{r_cap}%。",
    },
    "en": {
        "attack": n("Silver Stake") + ": attacks deal " + mag("p_dmg", "p_ap") + " bonus magic damage + {p_miss}% of the "
                  "target's missing health. " + n("Soul Ignition") + ": landing Ashen Pursuit by an enemy champion ignites him (" +
                  t("{w_cd}s") + " cooldown): " + t("{w_t}s") + " of +{w_as}% attack speed and +{w_ms}% decaying move speed; he "
                  "takes {w_cost}% current health as " + tr("true damage") + " " + t("each second") + ", then heals {w_back}% of it.",
        "ult": "Hurls his case at an enemy champion: " + mag("r_dmg", "r_ap") + " magic damage around it and a {r_slow}% "
               "decaying " + cc("slow") + "; champions there are marked for " + t("{r_t}s") + " and " + tr("executed") +
               " below {r_exec}% max health, leaving the artifact where they fall. Picking it up grants a seal (up to {seals}, "
               "kept all game): the line +{r_exec_step}%, the ult's remaining cooldown -{r_cap}%.",
    },
    "ko": {
        "attack": n("은빛 말뚝") + ": 공격 시 " + mag("p_dmg", "p_ap") + " 추가 마법 피해 + 대상이 잃은 체력의 {p_miss}%. " +
                  n("영혼 점화") + ": 잿빛 추격이 적 챔피언 곁에 착지하면 발동(" + t("{w_cd}초") + "마다): " + t("{w_t}초") +
                  " 동안 공격 속도 +{w_as}%, 이동 속도 +{w_ms}%(점차 감소), " + t("매초") + " 현재 체력 {w_cost}% " +
                  tr("고정 피해") + ", 끝나면 잃은 만큼의 {w_back}% 회복.",
        "ult": "법구 상자를 적 챔피언에게 던짐: 주변 적에게 " + mag("r_dmg", "r_ap") + " 마법 피해, {r_slow}% " + cc("둔화") +
               "(점차 감소); 챔피언은 " + t("{r_t}초") + " 동안 표식, 체력이 최대 체력의 {r_exec}% 미만이면 " + tr("처형") +
               "하고 그 자리에 법구를 남김. 주우면 봉인 1개(최대 {seals}개, 게임 내내 유지): 처형선 +{r_exec_step}%, 궁극기 남은 "
               "대기시간 -{r_cap}%.",
    },
    "ja": {
        "attack": n("シルバー・ステイク") + "：攻撃に" + mag("p_dmg", "p_ap") + "＋対象の減少体力{p_miss}%の魔法ダメージ。" +
                  n("ソウル・イグニッション") + "：灰塵の追撃で敵チャンピオンの側に着地で発動（" + t("{w_cd}秒") + "毎）：" +
                  t("{w_t}秒") + "間攻撃速度+{w_as}%、移動速度最大+{w_ms}%、" + t("毎秒") + "現在体力{w_cost}%の" +
                  tr("確定ダメージ") + "、終了時にその{w_back}%回復。",
        "ult": "ケースを敵チャンピオンに投げつけ、周囲の敵に" + mag("r_dmg", "r_ap") + "の魔法ダメージと{r_slow}%" + cc("スロウ") +
               "（減衰）；チャンピオンに" + t("{r_t}秒") + "の印、体力が最大体力の{r_exec}%未満なら" + tr("処刑") +
               "し聖具を残す。拾うと封印1つ（最大{seals}、ずっと残る）：処刑ライン+{r_exec_step}%、アルティメットの残りCD-{r_cap}%。",
    },
}
for _lang, _d in NATIVE.items():
    _d["skill"] = setup.TEXT[_lang]["skill"]
    _d["skill2"] = setup.TEXT[_lang]["skill2"]
    for _k in SLOTS:
        _d[_k] = TAG[_lang] + _d[_k]


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (p_miss: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":exorcist":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_locke differs from build_locke.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        # the add-on's own numbers, then setup_locke's (its durations in seconds win over the same keys in ticks)
        values = dict({k: p[k] for k in KEYS}, **setup.values(p))
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
        print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in NATIVE.items()
               for k, tx in d.items()})
    out[os.path.join(ADDON, "override", HERO + ".data_champion")] = dumps_main(champion)
    return out, champion


def main():
    draft = "--draft" in sys.argv[1:]
    out, champion = files(draft)
    if "--check" in sys.argv[1:]:
        stale = [os.path.relpath(path, ROOT) for path, text in out.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8", newline="").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in out.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, ROOT))
    print("(draft)" if draft else json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
