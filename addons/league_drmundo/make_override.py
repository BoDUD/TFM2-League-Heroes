"""Build the add-on's copy of Dr. Mundo from the main pack (health-scaled Q / E / W / R, the passive's real block).

    python addons/league_drmundo/make_override.py

Rebuilds Dr. Mundo with tools/kit/build_drmundo.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_drmundo.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_drmundo/override/league_drmundo.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus what reads health in data: Q's champion part calls league_drmundo:saw
    (a share of current health) instead of the max-health share, E's swing calls league_drmundo:bonk, W calls
    league_drmundo:zap / zap_end (real grey health) instead of the hit sensor's heals, R calls league_drmundo:dose and
    is cast by the add-on's AI hook (real health) instead of the hit count; the passive's self check drops the tank
    when the add-on lays p_drop_n (the add-on clears the control itself);
  * passive league_drmundo:pleases (params: the cooldown, Q / E / W / R numbers, his base health for bonus health);
  * every slot's tooltip points to description.league_drmundo_addon.* with the add-on's wording, so the tooltips in
    game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Dr. Mundo changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_drmundo")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_drmundo as kit  # noqa: E402
import setup_drmundo as setup  # noqa: E402

TEXT_ID = "league_drmundo_addon"        # the text's key (the hero's own id is league_drmundo)
HERO = "league_drmundo"
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("首次被控后免控{p_imm}秒并丢下药罐", "挡下首个硬控（扣当前生命7%）并丢下药罐"),
                           ("额外造成", "按已损生命最多翻倍地额外造成")],
                "skill": [("额外造成其最大生命{q_thp}%真实伤害", "改为造成其当前生命{q_pct}%的魔法伤害")],
                "skill2": [("挨打时积攒灰色生命", "受到伤害的{w_store}%存为灰色生命")],
                "ult": [("被围攻时给自己注射：立即回复", "生命危急时注射：回复已损生命{r_miss}%与")]},
    "zh-hant": {"attack": [("首次被控後免控{p_imm}秒並丟下藥罐", "擋下首個硬控（扣目前生命7%）並丟下藥罐"),
                           ("額外造成", "依已損生命最多翻倍地額外造成")],
                "skill": [("額外造成其最大生命{q_thp}%真實傷害", "改為造成其目前生命{q_pct}%的魔法傷害")],
                "skill2": [("挨打時累積灰色生命", "受到傷害的{w_store}%存為灰色生命")],
                "ult": [("被圍攻時替自己注射：立即回復", "生命危急時注射：回復已損生命{r_miss}%與")]},
    "en": {"attack": [("after the first crowd control on him he is immune for {p_imm}s and drops",
                       "the first hard crowd control is shaken off (7% of current health) and he drops"),
                      ("an attack deals", "an attack deals, up to doubled by missing health,")],
           "skill": [("also takes {q_thp}% of its max health as true damage", "takes {q_pct}% of its current health as magic damage instead")],
           "skill2": [("storing grey health as he is hit", "storing {w_store}% of the damage taken as grey health")],
           "ult": [("Doses himself when cornered: heals", "Doses himself when his health runs low: heals {r_miss}% of his missing health and")]},
    "ko": {"attack": [("처음 군중 제어를 받으면 {p_imm}초 면역", "첫 강력한 군중 제어를 떨쳐냄 (현재 체력 7%)"),
                       ("기본 공격이", "잃은 체력에 따라 최대 2배로 기본 공격이")],
           "skill": [("최대 체력 {q_thp}% 고정 피해", "현재 체력 {q_pct}% 마법 피해")],
           "skill2": [("맞을 때 회색 체력 저장", "받은 피해의 {w_store}%를 회색 체력으로 저장")],
           "ult": [("포위되면 스스로 투약: 즉시", "체력이 위험하면 투약: 잃은 체력 {r_miss}%와")]},
    "ja": {"attack": [("最初の行動妨害の後{p_imm}秒無効", "最初の強い行動妨害を振り払い（現在体力7%）"),
                       ("通常攻撃が", "失った体力で最大2倍に通常攻撃が")],
           "skill": [("最大体力{q_thp}%の確定ダメージ", "現在体力{q_pct}%の魔法ダメージ")],
           "skill2": [("被弾でグレー体力を蓄積", "被ダメージの{w_store}%をグレー体力に")],
           "ult": [("囲まれると自ら投与：即", "体力が危ないと投与：失った体力{r_miss}%と")]},
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_drmundo differs from build_drmundo.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if any(f"league_drmundo:{x}" not in text for x in ("saw", "bonk", "zap", "zap_end", "dose")) or "passive" not in champion:
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("attack", "skill", "skill2", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = dict(setup.values(p), q_pct=p["q_pct"], w_store=p["w_store"], r_miss=p["r_miss"])
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, pairs in swaps.items():
            src = setup.TEXT[lang][slot]
            for old, new in pairs:
                if old not in src:
                    sys.exit(f"{lang}.{slot}: {old!r} is not in setup_drmundo.TEXT")
                src = src.replace(old, new)
            texts[lang][slot] = (LEAD[lang] + src).format(**values)
    long = {f"{lang}.{slot}": setup.shown_length(t) for lang, d in texts.items() for slot, t in d.items()
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
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
