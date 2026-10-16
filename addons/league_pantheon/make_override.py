"""Build the add-on's copy of Pantheon from the main pack (Aegis Assault's front, Comet Spear's execute, Grand Starfall's spot).

    python addons/league_pantheon/make_override.py

Rebuilds Pantheon with tools/kit/build_pantheon.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_pantheon.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_pantheon/override/league_pantheon.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (Mortal Will, the thrust and the throw, the vault, the shield, the fall);
  * E's shield without the data's all-round damage reduction (the add-on blocks the front);
  * Q's hits calling league_pantheon:spear (the bonus below 20% health);
  * R asking league_pantheon:starfall for the champion to fall on;
  * passive = the add-on's league_pantheon:will with the numbers of P;
  * the skills' tooltips point to description.league_pantheon.skill / .skill2 / .ult with the add-on's wording
    (keys of the add-on's own id), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Pantheon changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_pantheon")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_pantheon as kit  # noqa: E402
import setup_pantheon as setup  # noqa: E402

MOD_ID = "league_pantheon"
HERO = "league_pantheon"
O, A, M, R, E = setup.O, setup.A, setup.M, setup.R, setup.E
phy = setup.phy
# lang -> the add-on's skill, skill2 and ult texts
NATIVE = {
    "zh-hans": {
        "skill": "【附加包】近处向前突刺，远处蓄力后掷出长矛，对线上的敌人造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E +
                 "（掷出时第一个之后减半）；目标生命低于20%时伤害翻倍。强化：额外" + phy("q_emp", "q_emp_ratio") + "。",
        "skill2": "【附加包】跃向敌方英雄，造成其{w_hp}%最大生命的伤害并" + R + "晕眩{w_stun}秒" + E + "；强化：下次普攻连刺3下。" + O + "神佑枪阵" +
                  E + "：举盾" + A + "{e_t}秒" + E + "，免疫控制和正面伤害，连刺前方后盾击造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "。",
        "ult": "【附加包】下蹲" + A + "{r_ch}秒" + E + "后跃起，落向敌人最密集的战场：长矛先砸下造成" + phy("r_sp_dmg", "r_sp_ratio") + O +
               "物理伤害" + E + "并减速{r_slow}%，落地造成" + M + "{r_dmg}魔法伤害" + E + "（边缘减半），叠满被动。",
    },
    "zh-hant": {
        "skill": "【擴充包】近處向前突刺，遠處蓄力後擲出長矛，對線上的敵人造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E +
                 "（擲出時第一個之後減半）；目標生命低於20%時傷害翻倍。強化：額外" + phy("q_emp", "q_emp_ratio") + "。",
        "skill2": "【擴充包】躍向敵方英雄，造成其{w_hp}%最大生命的傷害並" + R + "暈眩{w_stun}秒" + E + "；強化：下次普攻連刺3下。" + O + "聖盾猛襲" +
                  E + "：舉盾" + A + "{e_t}秒" + E + "，免疫控制和正面傷害，連刺前方後盾擊造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "。",
        "ult": "【擴充包】蹲伏" + A + "{r_ch}秒" + E + "後躍起，落向敵人最密集的戰場：長矛先砸下造成" + phy("r_sp_dmg", "r_sp_ratio") + O +
               "物理傷害" + E + "並緩速{r_slow}%，落地造成" + M + "{r_dmg}魔法傷害" + E + "（邊緣減半），疊滿被動。",
    },
    "en": {
        "skill": "[Add-on] Thrusts at a near target, or charges and throws the spear at a far one, dealing " + phy("q_dmg", "q_ratio") +
                 " " + O + "physical damage" + E + " to enemies on the line (a throw: half after the first); double below 20% health. "
                 "Empowered: " + phy("q_emp", "q_emp_ratio") + " more.",
        "skill2": "[Add-on] Leaps at an enemy champion, dealing {w_hp}% of its max health and " + R + "stunning it {w_stun}s" + E +
                  "; empowered: his next attack strikes 3 times. " + O + "Aegis Assault" + E + ": raises the shield " + A + "{e_t}s" +
                  E + ", immune to crowd control and to damage from the front, stabbing ahead, then bashes for " +
                  phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + ".",
        "ult": "[Add-on] Crouches " + A + "{r_ch}s" + E + ", leaps and falls where the most enemies fight: his spear strikes first for " +
               phy("r_sp_dmg", "r_sp_ratio") + " " + O + "physical damage" + E + " and a {r_slow}% slow, then the landing deals " +
               M + "{r_dmg} magic damage" + E + " (half at the edge) and fills Mortal Will.",
    },
    "ko": {
        "skill": "[확장] 가까우면 앞으로 찌르고, 멀면 힘을 모아 창을 던져 선 위의 적에게 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" +
                 E + "(던질 때 첫 적 이후 절반); 체력 20% 미만이면 두 배. 강화: " + phy("q_emp", "q_emp_ratio") + " 추가.",
        "skill2": "[확장] 적 챔피언에게 도약해 최대 체력의 {w_hp}% 피해와 " + R + "{w_stun}초 기절" + E + "; 강화: 다음 기본 공격 3연타. " + O +
                  "방패 돌격" + E + ": " + A + "{e_t}초" + E + " 방패를 들어 군중 제어와 정면 피해 면역, 앞을 찌른 뒤 방패로 " +
                  phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + ".",
        "ult": "[확장] " + A + "{r_ch}초" + E + " 웅크렸다 도약해 적이 가장 많은 곳에 떨어집니다: 창이 먼저 " + phy("r_sp_dmg", "r_sp_ratio") +
               "의 " + O + "물리 피해" + E + "와 {r_slow}% 둔화, 착지 시 " + M + "{r_dmg} 마법 피해" + E + "(가장자리 절반), 패시브 최대.",
    },
    "ja": {
        "skill": "【拡張】近くなら前へ突き、遠ければ溜めて槍を投げ、線上の敵に" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E +
                 "（投擲は最初の敵以降半減）。体力20%未満なら2倍。強化：" + phy("q_emp", "q_emp_ratio") + "追加。",
        "skill2": "【拡張】敵チャンピオンへ跳び、最大体力の{w_hp}%のダメージと" + R + "{w_stun}秒スタン" + E + "。強化：次の通常攻撃が3連撃。" + O +
                  "イージスの猛攻" + E + "：" + A + "{e_t}秒" + E + "盾を構え、CCと正面のダメージを無効、前方を突いた後に盾で" +
                  phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "ult": "【拡張】" + A + "{r_ch}秒" + E + "身を屈めて跳び、敵が最も多い戦場へ落下：槍が先に" + phy("r_sp_dmg", "r_sp_ratio") + "の" + O +
               "物理ダメージ" + E + "と{r_slow}%スロウ、着地で" + M + "{r_dmg}の魔法ダメージ" + E + "（外側は半減）、パッシブ最大。",
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
        sys.exit("the main pack's league_pantheon differs from build_pantheon.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":will":
        sys.exit("the copy has no league_pantheon:will passive: update this script")
    text = json.dumps(champion)
    for ref in ("league_pantheon:spear", "league_pantheon:starfall"):
        if ref not in text:
            sys.exit(f"the copy does not call {ref}: update this script")
    if '"league_pantheon_e_red"' in text:
        sys.exit("the copy still reduces damage from every side: update this script")
    for slot in ("skill", "skill2", "ult"):
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
