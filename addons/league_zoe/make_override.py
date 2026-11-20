"""Build the add-on's copy of Zoe from the main pack (Paddle Star thrown out and redirected, by the distance flown; Spell
Thief from the shards only; a sleep that any damage breaks; the bubble farther over a wall).

    python addons/league_zoe/make_override.py

Rebuilds Zoe with tools/kit/build_zoe.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zoe.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zoe/override/league_zoe.data_champion and .../text/champion.i18n: the build with native=1 -
  * the main pack's kit but for these (the attack, the bubble, Portal Jump with its star);
  * passive = the add-on's league_zoe:sparkles with the numbers of P it uses (passive.params);
  * Paddle Star throws no data star: the cast marks the target (q_aim), the release lights q_go, and the add-on throws
    the star out q_out and redirects it at the target (League's recast), its damage by the whole distance flown;
  * the bubble marks the unit it hits (e_mark; minions and monsters stop it too) and its release lights e_go; its sleep
    (a stun, as in the main pack) lasts e_sleep_n: the add-on shows the Zz while it holds and wakes him on any damage
    (that hit again as true damage, up to e_cap + e_cap_ratio% AP); the cast marks the champion aimed at (e_aim) and a
    wall on the line lights e_far, picking the e_wall longer bubble;
  * Portal Jump no longer fires Spell Thief (no toss, missiles or haste: League's R does not trigger it); the add-on's
    shards do;
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
        "skill": "【扩展包】掷出一颗飞星，先往身后（被挡就往旁边）飞一段，再拐回来砸向目标，打中第一个敌人造成" + mag("q_dmg", "q_ratio") +
                 "魔法伤害；两段一共飞得越远伤害越高，最远" + A + "{q_far}%" + E + "。",
        "skill2": "【扩展包】踢出气泡（飞过墙会飞得更远），打中第一个敌人造成" + mag("e_dmg", "e_ratio") + "魔法伤害，" + R + "困倦" + E + "（减速{e_slow}%）" + A +
                  "{e_drowsy}秒" + E + "后" + R + "睡眠" + E + A + "{e_sleep_n}秒" + E + "；受到任何伤害就醒，那一下多受一次真实伤害（有封顶）。",
        "ult": "【扩展包】跳进传送门闪向敌方英雄，掷出飞星造成" + mag("r_dmg", "r_ratio") + "魔法伤害，" + A + "{r_back}秒" + E + "后跳回原地。" + O +
               "窃法巧手" + E + "：敌方放大招掉下碎片，捡起就按局面放一个召唤师技能（闪现、点燃、虚弱、治疗、屏障、疾步、净化），射{w_n}颗飞弹，每颗" + mag("w_dmg", "w_ratio") +
               "，加速{w_ms}%。",
    },
    "zh-hant": {
        "skill": "【擴充包】擲出一顆飛星，先往身後（被擋就往旁邊）飛一段，再拐回來砸向目標，打中第一個敵人造成" + mag("q_dmg", "q_ratio") +
                 "魔法傷害；兩段一共飛得越遠傷害越高，最遠" + A + "{q_far}%" + E + "。",
        "skill2": "【擴充包】踢出泡泡（飛過牆會飛得更遠），打中第一個敵人造成" + mag("e_dmg", "e_ratio") + "魔法傷害，" + R + "睏倦" + E + "（緩速{e_slow}%）" + A +
                  "{e_drowsy}秒" + E + "後" + R + "睡眠" + E + A + "{e_sleep_n}秒" + E + "；受到任何傷害就醒，那一下多受一次真實傷害（有上限）。",
        "ult": "【擴充包】跳進傳送門閃向敵方英雄，擲出飛星造成" + mag("r_dmg", "r_ratio") + "魔法傷害，" + A + "{r_back}秒" + E + "後跳回原地。" + O +
               "法術竊盜" + E + "：敵方放大招掉下碎片，撿起就按局面放一個召喚師技能（閃現、點燃、虛弱、治療、屏障、疾步、淨化），射{w_n}顆飛彈，每顆" + mag("w_dmg", "w_ratio") +
               "，加速{w_ms}%。",
    },
    "en": {
        "skill": "[Add-on] Throws a star out behind her (to a side if that way is blocked), then turns it at the target: the first "
                 "enemy hit takes " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + ", more the farther it flew in all, up to " +
                 A + "{q_far}%" + E + ".",
        "skill2": "[Add-on] Kicks a bubble (it flies farther over a wall): the first enemy hit takes " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  ", turns " + R + "drowsy" + E + " (slowed {e_slow}%) for " + A + "{e_drowsy}s" + E + ", then falls " + R + "asleep" +
                  E + " for " + A + "{e_sleep_n}s" + E + ". Any damage wakes him, and that hit lands again as true damage (capped).",
        "ult": "[Add-on] Jumps through a portal toward an enemy champion and throws a star for " + mag("r_dmg", "r_ratio") + " " + M +
               "magic damage" + E + "; after " + A + "{r_back}s" + E + " she pops back. " + O + "Spell Thief" + E + ": an enemy ult "
               "drops a shard; picked up: a summoner spell picked by the fight (Flash, Ignite, Exhaust, Heal, Barrier, Ghost, "
               "Cleanse), {w_n} missiles, " +
               mag("w_dmg", "w_ratio") + " each, +{w_ms}% move speed.",
    },
    "ko": {
        "skill": "[확장] 별을 뒤쪽(막히면 옆)으로 던졌다가 대상 쪽으로 꺾어, 처음 맞힌 적에게 " + mag("q_dmg", "q_ratio") +
                 " 마법 피해. 모두 합쳐 멀리 날아갈수록 피해가 커져 최대 " + A + "{q_far}%" + E + ".",
        "skill2": "[확장] 방울을 차서(벽을 넘으면 더 멀리) 처음 맞힌 적에게 " + mag("e_dmg", "e_ratio") + " 마법 피해, " + A + "{e_drowsy}초" + E + " " + R +
                  "졸음" + E + "({e_slow}% 둔화) 뒤 " + A + "{e_sleep_n}초" + E + " " + R + "수면" + E + ". 어떤 피해든 맞으면 깨어나고 그 피해를 "
                  "고정 피해로 한 번 더(상한 있음).",
        "ult": "[확장] 차원문을 넘어 적 챔피언 쪽으로 이동해 별을 던져 " + mag("r_dmg", "r_ratio") + " 마법 피해, " + A + "{r_back}초" + E +
               " 뒤 제자리로. " + O + "주문도둑" + E + ": 적 궁극기가 떨군 파편을 주우면 상황에 맞는 소환사 주문(점멸·점화·탈진·회복·방어막·유체화·정화), 투사체 {w_n}개(개당 " +
               mag("w_dmg", "w_ratio") + "), 이동 속도 +{w_ms}%.",
    },
    "ja": {
        "skill": "【拡張】星を背後（塞がれていれば横）へ投げ、向きを変えて対象へ。最初に当たった敵に" + mag("q_dmg", "q_ratio") +
                 "の魔法ダメージ。合わせて遠くまで飛ぶほど強く、最大" + A + "{q_far}%" + E + "。",
        "skill2": "【拡張】泡を蹴り（壁を越えると遠くまで）、最初に当たった敵に" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、" + A + "{e_drowsy}秒" + E + R +
                  "まどろみ" + E + "（{e_slow}%スロウ）の後" + A + "{e_sleep_n}秒" + E + R + "睡眠" + E + "。どんなダメージでも目覚め、その一撃を"
                  "確定ダメージでもう一度（上限あり）。",
        "ult": "【拡張】ポータルを抜けて敵チャンピオンの方へ跳び、星を投げて" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、" + A + "{r_back}秒" + E +
               "後に元の場所へ。" + O + "スペルシーフ" + E + "：敵のアルティメットで落ちる欠片を拾うと状況に合うサモナースペルと弾{w_n}発（1発" +
               mag("w_dmg", "w_ratio") + "）、移動速度+{w_ms}%。",
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
    # 副本的大招不射飞弹，门口那颗飞星接过它们的伤害（build_zoe.P 的 r_dmg_n / r_ratio_n）
    values.update(r_dmg=p["r_dmg_n"], r_ratio=p["r_ratio_n"])
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
