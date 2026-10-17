"""Build the add-on's copy of Kalista from the main pack (the hop's way, the Oathsworn, Fate's Call's flight, Rend's execute).

    python addons/league_kalista/make_override.py

Rebuilds Kalista with tools/kit/build_kalista.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_kalista.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_kalista/override/league_kalista.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the spears and Rend, Pierce, Soul-Marked);
  * the hop after each spear played from the add-on's hop_f / hop_b and moved by it (the main pack's MoveBack only
    when neither flag is up: no enemy champion near);
  * R cast on an ally (the add-on's AI hook picks the Oathsworn), the flight left to the add-on (r_launch / r_landed);
  * passive = the add-on's league_kalista:oath with the numbers of P;
  * the attack's and the ult's tooltips point to description.league_kalista.attack / .ult with the add-on's wording
    (keys of the add-on's own id), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Kalista changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kalista")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_kalista as kit  # noqa: E402
import setup_kalista as setup  # noqa: E402

MOD_ID = "league_kalista"
HERO = "league_kalista"
O, A, W_, E = setup.O, setup.A, setup.W_, setup.E
phy = setup.phy
# lang -> the add-on's attack and ult texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】投矛，命中的敌人身上插一支矛（" + A + "{sp_t}秒" + E + "）。" + O + "武术姿态" + E + "：每次投矛后自己判断往前追（敌人残血或正在逃）"
                  "还是往后跳开。" + O + "哨兵" + E + "：有队友在目标身边时，额外造成目标" + W_ + "{w_hp}%最大生命值的真实伤害" + E + "。",
        "ult": "【附加包】开局和一名队友立下誓约（辅助优先）。把誓约者拉进身体保护" + A + "{r_hold}秒" + E + "，然后甩到最近的敌方英雄身边，落地击飞周围敌人" +
               A + "{r_up}秒" + E + "，造成" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "。",
    },
    "zh-hant": {
        "attack": "【附加包】投矛，命中的敵人身上插一支矛（" + A + "{sp_t}秒" + E + "）。" + O + "好戰突進" + E + "：每次投矛後自己判斷往前追（敵人殘血或正在逃）"
                  "還是往後跳開。" + O + "憎靈守衛" + E + "：有隊友在目標身邊時，額外造成目標" + W_ + "{w_hp}%最大生命的真實傷害" + E + "。",
        "ult": "【附加包】開局和一名隊友立下誓約（輔助優先）。把誓約者拉進身體保護" + A + "{r_hold}秒" + E + "，然後擲到最近的敵方英雄身邊，落地擊飛周圍敵人" +
               A + "{r_up}秒" + E + "，造成" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "。",
    },
    "en": {
        "attack": "[Add-on] Throws spears; each one stays in the enemy it hits for " + A + "{sp_t}s" + E + ". " + O + "Martial Poise" + E +
                  ": after each spear she hops forward (the enemy low or running away) or back on her own. " +
                  O + "Sentinel" + E + ": with an ally beside her target, deals " + W_ + "{w_hp}% of its max health as true damage" + E + ".",
        "ult": "[Add-on] She binds an ally at the start (a support first). Draws the Oathsworn into herself for " + A + "{r_hold}s" + E +
               ", then hurls them beside the nearest enemy champion; the landing knocks up nearby enemies for " + A + "{r_up}s" + E +
               " and deals " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E + ".",
    },
    "ko": {
        "attack": "[확장] 창을 던지며, 맞은 적에게 창이 " + A + "{sp_t}초" + E + " 꽂힙니다. " + O + "전투 태세" + E + ": 창을 던진 뒤 스스로 판단해 "
                  "앞으로(적의 체력이 낮거나 도망칠 때) 또는 뒤로 도약. " + O + "감시하는 혼" + E + ": 대상 곁에 아군이 있으면 "
                  "대상 최대 체력의 " + W_ + "{w_hp}% 고정 피해" + E + ".",
        "ult": "[확장] 시작할 때 아군 하나와 맹약(서포터 우선). 맹약자를 " + A + "{r_hold}초" + E + " 동안 몸에 거둔 뒤 가장 가까운 적 챔피언 곁으로 던집니다. "
               "착지하면 주변 적을 " + A + "{r_up}초" + E + " 띄워 올리고 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ".",
    },
    "ja": {
        "attack": "【拡張】槍を投げ、当たった敵に槍が" + A + "{sp_t}秒" + E + "刺さる。" + O + "戦の所作" + E + "：投擲のたびに自ら判断し、前へ（敵が瀕死か"
                  "逃げる時）か後ろへ跳ぶ。" + O + "執念の霊魂" + E + "：対象の傍に味方がいると最大体力の" + W_ + "{w_hp}%の確定ダメージ" + E + "。",
        "ult": "【拡張】開始時に味方一人と誓約（サポート優先）。誓約者を" + A + "{r_hold}秒" + E + "身に宿し、最も近い敵チャンピオンの傍へ投げ放つ。"
               "着地で周囲の敵を" + A + "{r_up}秒" + E + "打ち上げ、" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "。",
    },
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_kalista differs from build_kalista.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":oath":
        sys.exit("the copy has no league_kalista:oath passive: update this script")
    if '"league_kalista_hop_go"' not in json.dumps(champion):
        sys.exit("the copy does not hand the hop to the add-on: update this script")
    for slot in ("attack", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
