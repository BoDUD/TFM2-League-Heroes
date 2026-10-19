"""Build the add-on's copy of Zoe from the main pack (a sleep broken by damage, Paddle Star by the real distance, Spell
Thief's shards).

    python addons/league_zoe/make_override.py

Rebuilds Zoe with tools/kit/build_zoe.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zoe.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zoe/override/league_zoe.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the stars, the bubble, Portal Jump with its star and missiles);
  * passive = the add-on's league_zoe:sparkles with the numbers of P it uses (passive.params);
  * Paddle Star deals the near share and marks what it hits (q_hit), her throw lights q_go: the add-on adds the rest by
    the distance flown;
  * the bubble marks the champion (e_mark) instead of the data's stun: the add-on puts him to sleep and wakes him on
    any damage; the data's doubled star on a sleeper is left out (the add-on doubles any first hit);
  * the skill, skill2 and ult tooltips point to description.league_zoe.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Zoe changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zoe")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zoe as kit  # noqa: E402
import setup_zoe as setup  # noqa: E402

MOD_ID = "league_zoe"
HERO = "league_zoe"
SLOTS = ("skill", "skill2", "ult")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag = setup.mag

TEXT = {
    "zh-hans": {
        "skill": "【扩展包】掷出一颗飞星，打中第一个敌人造成" + mag("q_dmg", "q_ratio") + "魔法伤害；按真实飞行距离越远越高，最远" + A +
                 "{q_far}%" + E + "。",
        "skill2": "【扩展包】踢出气泡，打中敌方英雄造成" + mag("e_dmg", "e_ratio") + "魔法伤害，" + R + "困倦" + E + "（减速{e_slow}%）" + A +
                  "{e_drowsy}秒" + E + "后" + R + "昏睡" + E + A + "{e_sleep_n}秒" + E + "；受到任何伤害就醒，那一下多受一次真实伤害（有封顶）。",
        "ult": "【扩展包】跳进传送门闪向敌方英雄，掷出飞星造成" + mag("r_dmg", "r_ratio") + "魔法伤害，再射{w_n}颗飞弹。" + O + "窃法巧手" + E +
               "：敌方英雄放大招时掉下法术碎片，她捡起来就射{w_n}颗飞弹，每颗" + mag("w_dmg", "w_ratio") + "，并加速{w_ms}%。",
    },
    "zh-hant": {
        "skill": "【擴充包】擲出一顆飛星，打中第一個敵人造成" + mag("q_dmg", "q_ratio") + "魔法傷害；按真實飛行距離越遠越高，最遠" + A +
                 "{q_far}%" + E + "。",
        "skill2": "【擴充包】踢出泡泡，打中敵方英雄造成" + mag("e_dmg", "e_ratio") + "魔法傷害，" + R + "睏倦" + E + "（緩速{e_slow}%）" + A +
                  "{e_drowsy}秒" + E + "後" + R + "沉睡" + E + A + "{e_sleep_n}秒" + E + "；受到任何傷害就醒，那一下多受一次真實傷害（有上限）。",
        "ult": "【擴充包】跳進傳送門閃向敵方英雄，擲出飛星造成" + mag("r_dmg", "r_ratio") + "魔法傷害，再射{w_n}顆飛彈。" + O + "法術竊盜" + E +
               "：敵方英雄放大招時掉下法術碎片，她撿起來就射{w_n}顆飛彈，每顆" + mag("w_dmg", "w_ratio") + "，並加速{w_ms}%。",
    },
    "en": {
        "skill": "[Add-on] Throws a star at the first enemy hit for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E +
                 ", more the farther it really flew, up to " + A + "{q_far}%" + E + ".",
        "skill2": "[Add-on] Kicks a bubble: the enemy champion hit takes " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  ", turns " + R + "drowsy" + E + " (slowed {e_slow}%) for " + A + "{e_drowsy}s" + E + ", then falls " + R + "asleep" +
                  E + " for " + A + "{e_sleep_n}s" + E + ". Any damage wakes him, and that hit lands again as true damage (capped).",
        "ult": "[Add-on] Jumps through a portal toward an enemy champion, throws a star for " + mag("r_dmg", "r_ratio") + " " + M +
               "magic damage" + E + " and {w_n} missiles. " + O + "Spell Thief" + E + ": an enemy champion's ult drops a spell shard; "
               "picking it up she throws {w_n} missiles, " + mag("w_dmg", "w_ratio") + " each, and gains {w_ms}% move speed.",
    },
    "ko": {
        "skill": "[확장] 별을 던져 처음 맞힌 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해. 실제로 멀리 날아갈수록 피해가 커져 최대 " + A +
                 "{q_far}%" + E + ".",
        "skill2": "[확장] 방울을 차서 맞힌 적 챔피언에게 " + mag("e_dmg", "e_ratio") + " 마법 피해, " + A + "{e_drowsy}초" + E + " " + R +
                  "졸음" + E + "({e_slow}% 둔화) 뒤 " + A + "{e_sleep_n}초" + E + " " + R + "수면" + E + ". 어떤 피해든 맞으면 깨어나고 그 피해를 "
                  "고정 피해로 한 번 더(상한 있음).",
        "ult": "[확장] 차원문을 넘어 적 챔피언 쪽으로 이동해 별을 던져 " + mag("r_dmg", "r_ratio") + " 마법 피해, 투사체 {w_n}개. " + O + "주문도둑" +
               E + ": 적 챔피언이 궁극기를 쓰면 주문 파편이 떨어지고, 주우면 투사체 {w_n}개(개당 " + mag("w_dmg", "w_ratio") +
               ")와 이동 속도 +{w_ms}%.",
    },
    "ja": {
        "skill": "【拡張】星を投げ、最初に当たった敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。実際に遠くまで飛ぶほど強く、最大" + A +
                 "{q_far}%" + E + "。",
        "skill2": "【拡張】泡を蹴り、当たった敵チャンピオンに" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、" + A + "{e_drowsy}秒" + E + R +
                  "まどろみ" + E + "（{e_slow}%スロウ）の後" + A + "{e_sleep_n}秒" + E + R + "睡眠" + E + "。どんなダメージでも目覚め、その一撃を"
                  "確定ダメージでもう一度（上限あり）。",
        "ult": "【拡張】ポータルを抜けて敵チャンピオンの方へ跳び、星を投げて" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、弾{w_n}発。" + O +
               "スペルシーフ" + E + "：敵チャンピオンがアルティメットを使うと呪文の欠片が落ち、拾うと弾{w_n}発（1発" +
               mag("w_dmg", "w_ratio") + "）と移動速度+{w_ms}%。",
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
        sys.exit("the main pack's league_zoe differs from build_zoe.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":sparkles":
        sys.exit("the copy has no league_zoe:sparkles passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values.update({k: p[k] for k in ("w_n",)})
    values["e_sleep_n"] = setup.secs(p["e_sleep_n"])
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in TEXT.items() for k, t in d.items()
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
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
