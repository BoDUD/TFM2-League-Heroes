"""Build the add-on's copy of Viktor from the main pack (Glorious Evolution by League's Hex Fragments).

    python addons/league_viktor/make_override.py [--check]

Rebuilds Viktor with tools/kit/build_viktor.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_viktor.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_viktor/override/league_viktor.data_champion and .../text/champion.i18n: the build with native=1 -
  * passive league_viktor:evolve (params: hex_unit, hex_epic, hex_takedown, hex_cost and W's w_arm, w_stun_at, w_stun,
    w_r, w_t) - it raises the evolution flags league_viktor_s1..s4 from his Hex Fragments, so the attack carries no
    level probe; and it stuns each enemy that stays in the armed Gravity Field (the field's landing calls
    league_viktor:field instead of the data's stun);
  * the attack's (Glorious Evolution) and skill2's (W -> E) tooltips point to description.league_viktor_addon.* with the
    add-on's wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Viktor changes (--check: compare only, for
CI).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_viktor")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_viktor as kit  # noqa: E402
import setup_viktor as setup  # noqa: E402

TEXT_ID = "league_viktor_addon"       # the texts' key (the hero's own id is league_viktor)
HERO = "league_viktor"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, R, E, SPi, Wh, M = setup.O, setup.A, setup.R, setup.E, setup.SPi, setup.Wh, setup.M
mag = setup.mag
TEXT = {
    "zh-hans": {
        "attack": "被动" + O + "光荣进化" + E + "：补到小兵、野怪各得" + A + "{hex_unit}" + E + "个海克斯碎片，参与击杀英雄得" + A + "{hex_takedown}" + E +
                  "个，每" + A + "{hex_cost}" + E + "个按顺序强化：E附带余波，Q护盾更强并" + SPi + Wh + "加速{q_ms}%" + E + "，Q、E和风暴首击" + R +
                  "减速{evo_slow}%" + E + "，风暴转移后变大、持续更久。",
        "skill2": "先在敌方英雄脚下放" + O + "重力场" + E + "：" + A + "{w_arm}秒" + E + "后生效，" + R + "减速{w_slow}%" + E + "，在场里待满" + A +
                  "{w_stack}秒" + E + "的敌人" + R + "晕眩{w_stun}秒" + E + "（每人一次）。再从目标处向后方射出海克斯射线，造成" +
                  mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "。",
    },
    "zh-hant": {
        "attack": "被動" + O + "榮光進化" + E + "：補到小兵、野怪各得" + A + "{hex_unit}" + E + "個海克斯碎片，參與擊殺英雄得" + A + "{hex_takedown}" + E +
                  "個，每" + A + "{hex_cost}" + E + "個依序強化：E附帶餘波，Q護盾更強並" + SPi + Wh + "加速{q_ms}%" + E + "，Q、E和風暴首擊" + R +
                  "緩速{evo_slow}%" + E + "，風暴轉移後變大、持續更久。",
        "skill2": "先在敵方英雄腳下放" + O + "萬有引力產生裝置" + E + "：" + A + "{w_arm}秒" + E + "後生效，" + R + "緩速{w_slow}%" + E +
                  "，在場內待滿" + A + "{w_stack}秒" + E + "的敵人" + R + "暈眩{w_stun}秒" + E + "（每人一次）。再從目標處向後方射出海克斯科技射線，造成" +
                  mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "。",
    },
    "en": {
        "attack": "Passive " + O + "Glorious Evolution" + E + ": " + A + "{hex_unit}" + E + " Hex Fragment for each minion or monster he kills, " + A +
                  "{hex_takedown}" + E + " for a champion takedown; every " + A + "{hex_cost}" + E + " evolves the next spell: Hextech Ray's aftershock, "
                  "Siphon Power's bigger shield and " + SPi + Wh + "{q_ms}% Move Speed" + E + ", Q, E and the storm's first strike " + R +
                  "slowing {evo_slow}%" + E + ", the storm growing and lasting longer when it moves on.",
        "skill2": "First a " + O + "Gravity Field" + E + " under an enemy champion arms after " + A + "{w_arm}s" + E + " and " + R +
                  "slows {w_slow}%" + E + "; an enemy that stays in it " + A + "{w_stack}s" + E + " is " + R + "stunned for {w_stun}s" + E +
                  " (once each). Then a Hextech Ray from the target on away from him deals " + mag("e_dmg", "e_ratio") + " " + M +
                  "magic damage" + E + ".",
    },
    "ko": {
        "attack": "기본 지속 효과 " + O + "영광스러운 진화" + E + ": 미니언·몬스터 처치 " + A + "{hex_unit}" + E + "개, 챔피언 관여 " + A + "{hex_takedown}" + E +
                  "개의 헥스 조각, " + A + "{hex_cost}" + E + "개마다 차례로 강화: E 여진, Q 보호막 강화와 " + SPi + Wh + "이동 속도 {q_ms}%" + E +
                  ", Q·E·폭풍 첫 타격 " + R + "{evo_slow}% 둔화" + E + ", 폭풍이 옮겨 가면 커지고 더 오래 유지.",
        "skill2": "먼저 적 챔피언 발밑에 " + O + "중력장" + E + ": " + A + "{w_arm}초" + E + " 뒤 작동해 " + R + "{w_slow}% 둔화" + E +
                  ", 안에 " + A + "{w_stack}초" + E + " 머문 적 " + R + "기절 {w_stun}초" + E + "(각자 한 번). 이어서 대상에서 뒤쪽으로 마법공학 광선이 " +
                  mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + ".",
    },
    "ja": {
        "attack": "パッシブ " + O + "グロリアス・エヴォリューション" + E + "：ミニオン・モンスター" + A + "{hex_unit}" + E + "個、キル関与" + A +
                  "{hex_takedown}" + E + "個のヘクスの欠片、" + A + "{hex_cost}" + E + "個毎に順に強化：Eに余波、Qのシールド強化と" + SPi + Wh +
                  "移動速度{q_ms}%" + E + "、Q・E・嵐の初撃が" + R + "{evo_slow}%スロウ" + E + "、嵐が移ると大きく長持ち。",
        "skill2": "まず敵チャンピオンの足元に" + O + "グラビティフィールド" + E + "：" + A + "{w_arm}秒" + E + "後に発動し" + R +
                  "{w_slow}%スロウ" + E + "、中に" + A + "{w_stack}秒" + E + "留まった敵を" + R + "{w_stun}秒スタン" + E + "（各1回）。続けて対象から奥へレイが" +
                  mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "。",
    },
}
HEX = ("hex_unit", "hex_epic", "hex_takedown", "hex_cost")


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def build():
    """[(path, text)] of the copy and its texts."""
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_viktor differs from build_viktor.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if (champion.get("passive", {}).get("passive_ref") != "league_viktor:evolve" or "league_viktor_pr_" in text
            or '"league_viktor:field"' not in text or '"Stun"' in text):
        sys.exit("the copy does not call the add-on (or still probes his level / stuns in data): update this script")
    for slot in TEXT["en"]:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = dict(setup.values(p), w_stack=setup.secs(p["w_stun_at"]), **{k: p[k] for k in HEX})
    texts = {lang: {k: (LEAD[lang] + t[k]).format(**values) for k in t} for lang, t in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(LEAD[lang] + TEXT[lang][k]) for lang in TEXT for k in TEXT[lang]
            if setup.shown_length(LEAD[lang] + TEXT[lang][k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    for lang in TEXT:
        print(lang, " ".join(f"{k}:{setup.shown_length(LEAD[lang] + TEXT[lang][k])}/{setup.TOOLTIP_MAX[lang]}"
                             for k in TEXT[lang]))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    return [(os.path.join(ADDON, "override", HERO + ".data_champion"), dumps_main(champion)),
            (os.path.join(ADDON, "text", "champion.i18n"), dumps_main(i18n))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="only compare the copy with the files (CI)")
    a = ap.parse_args()
    out = build()
    if a.check:
        bad = []
        for path, text in out:
            try:
                with open(lp(path), encoding="utf-8", newline="") as f:
                    have = f.read()
            except FileNotFoundError:
                have = None
            if have is None or have.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
                bad.append(os.path.relpath(path, ROOT))
        if bad:
            sys.exit("out of date (python addons/league_viktor/make_override.py): " + ", ".join(bad))
        print("league_viktor: the copy is up to date")
        return
    for path, text in out:
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(path)


if __name__ == "__main__":
    main()
