"""Build the add-on's copy of Rell from the main pack (Break the Mold per champion, Shattering Strike breaking shields,
Full Tilt toward).

    python addons/league_rell/make_override.py

Rebuilds Rell with tools/kit/build_rell.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_rell.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_rell/override/league_rell.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * every Break the Mold of the data (the champion-only hits of the attack, Q, Crash Down, Mount Up and Magnet Storm)
    calling league_rell:mold instead (stacks per champion, her share summed by the passive);
  * every Shattering Strike hit calling league_rell:shatter too (its shields broken);
  * Full Tilt's second half without the data's own 30% (the add-on adds it while they run toward enemies or each other);
  * passive = the add-on's league_rell:iron with the numbers of P;
  * the attack's, skill's and skill2's tooltips point to description.league_rell.attack / .skill / .skill2 with the
    add-on's wording (keys of the add-on's own id), so the tooltip in game shows whether the override took.
The whole body on foot needs no data: the add-on's display hook reads the main pack's own buff league_rell_foot.
Every other champion stays untouched. Run it again whenever the main pack's Rell changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_rell")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_rell as kit  # noqa: E402
import setup_rell as setup  # noqa: E402

MOD_ID = "league_rell"
HERO = "league_rell"
O, A, M, R, G, E = setup.O, setup.A, setup.M, setup.R, setup.G, setup.E
APi = setup.APi
mag = setup.mag
REFS = ("mold", "shatter")
SLOTS = ("attack", "skill", "skill2")
# lang -> the add-on's attack, skill and skill2 texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】骑枪突刺，附带" + M + "{p_dmg}+最大生命{p_hp}%魔法伤害" + E + "。" + O + "溃敌沉力" + E + "：每个英雄身上单独叠，最多" +
                  A + "5层" + E + "，每层削减其{p_shred}%护甲和魔抗，芮尔得到首层时它双抗的{p_shred}%。",
        "skill": "【附加包】前冲一刺，" + R + "打破护盾" + E + "，造成" + mag("q") + M + "魔法伤害" + E + "并" + R + "晕眩{q_stun}秒" + E + "。" +
                 O + "全速冲锋" + E + "：与身边一名队友加速{e_ms1}%，朝敌人或彼此跑时翻倍；下次普攻或裂阵爆炸。",
        "skill2": "【附加包】跃向敌方英雄砸下，造成" + mag("w") + M + "魔法伤害" + E + "并" + R + "击飞{w_up}秒" + E + "，获得" + setup.SHIELD +
                  "护盾，换成披甲步行作战" + A + "{w_foot}秒" + E + "。" + O + "驾临" + E + "：上马冲锋，" + R + "晕眩{w2_stun}秒" + E + "并掀飞目标。",
    },
    "zh-hant": {
        "attack": "【擴充包】騎槍突刺，附帶" + M + "{p_dmg}+最大生命{p_hp}%魔法傷害" + E + "。" + O + "破鑄者" + E + "：每個英雄身上單獨疊，最多" +
                  A + "5層" + E + "，每層削減其{p_shred}%護甲和魔抗，銳兒得到首層時它雙抗的{p_shred}%。",
        "skill": "【擴充包】前衝一刺，" + R + "打破護盾" + E + "，造成" + mag("q") + M + "魔法傷害" + E + "並" + R + "暈眩{q_stun}秒" + E + "。" +
                 O + "全速突進" + E + "：與身邊一名隊友加速{e_ms1}%，朝敵人或彼此跑時翻倍；下次普攻或鐵碎之擊爆炸。",
        "skill2": "【擴充包】躍向敵方英雄砸下，造成" + mag("w") + M + "魔法傷害" + E + "並" + R + "擊飛{w_up}秒" + E + "，獲得" + setup.SHIELD +
                  "護盾，換成披甲步行作戰" + A + "{w_foot}秒" + E + "。" + O + "起駕" + E + "：上馬衝鋒，" + R + "暈眩{w2_stun}秒" + E + "並掀飛目標。",
    },
    "en": {
        "attack": "[Add-on] Lance thrusts with " + M + "{p_dmg} + {p_hp}% max health magic damage" + E + ". " + O + "Break the Mold" + E +
                  ": stacks on each champion apart, up to " + A + "5" + E + ", each taking {p_shred}% of its armour and magic resist and "
                  "giving Rell {p_shred}% of what it had at the first stack.",
        "skill": "[Add-on] Thrusts forward, " + R + "breaking shields" + E + ", dealing " + mag("q") + " " + M + "magic damage" + E + " and " +
                 R + "stunning {q_stun}s" + E + ". " + O + "Full Tilt" + E + ": she and a nearby ally gain {e_ms1}% speed, doubled running "
                 "toward enemies or each other; her next attack or Shattering Strike explodes.",
        "skill2": "[Add-on] Leaps onto an enemy champion and crashes down for " + mag("w") + " " + M + "magic damage" + E + ", " + R +
                  "knocking up {w_up}s" + E + ", gaining a " + setup.SHIELD + " shield and fighting on foot in her armour for " + A +
                  "{w_foot}s" + E + ". " + O + "Mount Up" + E + ": charges on her horse, " + R + "stunning {w2_stun}s" + E + " and flinging the target.",
    },
    "ko": {
        "attack": "[확장] 창으로 찌르며 " + M + "{p_dmg} + 최대 체력 {p_hp}% 마법 피해" + E + ". " + O + "갑옷 파쇄" + E + ": 챔피언마다 따로 최대 " +
                  A + "5중첩" + E + ", 중첩당 방어력·마법 저항력 {p_shred}% 감소, 렐은 첫 중첩 때 값의 {p_shred}% 획득.",
        "skill": "[확장] 앞으로 찔러 " + R + "보호막을 깨고" + E + " " + mag("q") + "의 " + M + "마법 피해" + E + "와 " + R + "{q_stun}초 기절" + E + ". " +
                 O + "전속력" + E + ": 자신과 근처 아군 이동 속도 {e_ms1}%, 적이나 서로를 향하면 두 배; 다음 기본 공격이나 파열의 일격이 폭발.",
        "skill2": "[확장] 적 챔피언에게 뛰어올라 내려찍어 " + mag("w") + "의 " + M + "마법 피해" + E + "와 " + R + "{w_up}초 에어본" + E + ", " +
                  setup.SHIELD + " 보호막, " + A + "{w_foot}초" + E + " 갑옷을 입고 걸어서 싸움. " + O + "탑승" + E + ": 말을 타고 돌진해 " + R +
                  "{w2_stun}초 기절" + E + "시키고 대상을 날립니다.",
    },
    "ja": {
        "attack": "【拡張】騎槍で突き、" + M + "{p_dmg}+最大体力{p_hp}%の魔法ダメージ" + E + "。" + O + "革新の鬨" + E + "：チャンピオンごとに最大" +
                  A + "5スタック" + E + "、1スタックで物理防御・魔法防御{p_shred}%低下、レルは初回スタック時の値の{p_shred}%を得る。",
        "skill": "【拡張】前方へ突き" + R + "シールドを破壊" + E + "、" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_stun}秒スタン" + E + "。" +
                 O + "重槍突貫" + E + "：自身と近くの味方1人が移動速度{e_ms1}%、敵か互いへ向かうと2倍；次の通常攻撃か破鋼撃が爆発。",
        "skill2": "【拡張】敵チャンピオンへ跳んで叩きつけ" + mag("w") + "の" + M + "魔法ダメージ" + E + "と" + R + "{w_up}秒ノックアップ" + E + "、" +
                  setup.SHIELD + "のシールド、" + A + "{w_foot}秒" + E + "鎧をまとい徒歩で戦う。" + O + "騎馬" + E + "：馬で突撃し" + R +
                  "{w2_stun}秒スタン" + E + "、対象を弾く。",
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
        sys.exit("the main pack's league_rell differs from build_rell.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":iron":
        sys.exit("the copy has no league_rell:iron passive: update this script")
    text = json.dumps(champion)
    for ref in REFS:
        if f'"{MOD_ID}:{ref}"' not in text:
            sys.exit(f"the copy does not call {MOD_ID}:{ref}: update this script")
    if '"league_rell_p_steal"' in text:
        sys.exit("the copy still carries the data's own steal buff: update this script")
    for slot in SLOTS:
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
