"""Build the add-on's copy of Nidalee from the main pack (Prowl's brush speed; the whole-body cougar and the targets need
nothing in the data).

    python addons/league_nidalee/make_override.py

Rebuilds Nidalee with tools/kit/build_nidalee.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_nidalee.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_nidalee/override/league_nidalee.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit plus passive league_nidalee:prowl (params: the brush speed numbers);
  * the attack's, skill's and R's tooltips point to description.league_nidalee_prowl.* with the add-on's wording, so the
    tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Nidalee changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_nidalee")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_nidalee as kit  # noqa: E402
import setup_nidalee as setup  # noqa: E402

TEXT_ID = "league_nidalee_prowl"      # the text's key (the hero's own id is league_nidalee)
HERO = "league_nidalee"
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("期间移速+{p_ms}%。", "期间移速+{p_ms}%；草丛里和离开后{brush_t}秒移速+{brush_ms}%（附近有敌方英雄+{brush_near_ms}%）。")],
                "skill": [("投出标枪", "向线上没被挡的英雄投出标枪")],
                "ult": [("扑向英雄", "扑向被捕猎或血量最低的英雄")]},
    "zh-hant": {"attack": [("期間跑速+{p_ms}%。", "期間跑速+{p_ms}%；草叢裡和離開後{brush_t}秒跑速+{brush_ms}%（附近有敵方英雄+{brush_near_ms}%）。")],
                "skill": [("擲出標槍", "向線上沒被擋的英雄擲出標槍")],
                "ult": [("撲向英雄", "撲向被狩獵或血量最低的英雄")]},
    "en": {"attack": [("(+{p_ms}% move speed).", "(+{p_ms}% move speed); in brush and {brush_t}s after it +{brush_ms}% move speed "
                                                  "(+{brush_near_ms}% with an enemy champion near).")],
           "skill": [("throws a javelin", "throws a javelin at a champion with a clear line")],
           "ult": [("pounces on a champion", "pounces on the hunted or the lowest champion")]},
    "ko": {"attack": [("(이동 속도 +{p_ms}%).", "(이동 속도 +{p_ms}%); 수풀 안과 나온 뒤 {brush_t}초 이동 속도 +{brush_ms}% (근처 적 챔피언 +{brush_near_ms}%).")],
           "skill": [("창을 던져", "막히지 않은 챔피언에게 창을 던져")],
           "ult": [("챔피언에게 도약해", "사냥 대상이나 체력이 가장 낮은 챔피언에게 도약해")]},
    "ja": {"attack": [("（移動速度+{p_ms}%）。", "（移動速度+{p_ms}%）；草むらの中と出て{brush_t}秒移動速度+{brush_ms}%（近くに敵チャンピオンで+{brush_near_ms}%）。")],
           "skill": [("槍を投げ", "遮られていないチャンピオンへ槍を投げ")],
           "ult": [("チャンピオンへ飛びかかり", "狩る相手か体力の最も低いチャンピオンへ飛びかかり")]},
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
        sys.exit("the main pack's league_nidalee differs from build_nidalee.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_nidalee:prowl":
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("attack", "skill", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = dict(setup.values(p), brush_ms=p["brush_ms"], brush_near_ms=p["brush_near_ms"],
                  brush_t=setup.secs(p["brush_t"]))
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, pairs in swaps.items():
            src = setup.TEXT[lang][slot]
            for old, new in pairs:
                if old not in src:
                    sys.exit(f"{lang}.{slot}: {old!r} is not in setup_nidalee.TEXT")
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
