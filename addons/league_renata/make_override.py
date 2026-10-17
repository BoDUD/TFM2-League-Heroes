"""Build the add-on's copy of Renata from the main pack (Leverage popped by real allied hits, League's Bailout, a real
berserk).

    python addons/league_renata/make_override.py

Rebuilds Renata with tools/kit/build_renata.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_renata.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_renata/override/league_renata.data_champion and .../text/champion.i18n: the build with native=1 -
  * her shot marks champions but the data no longer pops the mark (the add-on pops it on an ally's real hit);
  * the data no longer casts Bailout (the add-on does: League's revive, drain and takedown);
  * Hostile Takeover's berserk keeps the data's disarm, silence and picture without the data's lash (the add-on walks
    them to their own allies and hits with their own attack);
  * passive = the add-on's league_renata:glasc with the numbers of P;
  * the attack's and ult's tooltips point to description.league_renata.attack / .ult with the add-on's wording, keys of
    the add-on's own id, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Renata changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_renata")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_renata as kit  # noqa: E402
import setup_renata as setup  # noqa: E402

MOD_ID = "league_renata"
HERO = "league_renata"
AP = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
# lang -> (the add-on's mark, the attack's text, the ult's text): the main pack's words with the add-on's Leverage,
# Bailout and berserk
NATIVE = {
    "zh-hans": ("【附加包】",
                "手枪普攻。<#ff9028ff>物尽其用<>：命中英雄时额外造成最大生命<#ffb900ff>{p_hp}%<><#f5f5f5ff>真实伤害<>并标记；队友打中它时"
                "引爆，造成<#a974ffff>{p_pop}<> + " + AP + "<#a974ffff>{p_pop_ap}%<><#a974ffff>魔法伤害<>。<#ff9028ff>及时救难<>：队友"
                "危急时自动施放，攻速+<#ffb900ff>{w_as}%<>、移速+<#ffb900ff>{w_ms}%<>，<#ffb900ff>{w_t}秒<>内受致命伤害时回满生命并"
                "逐渐流失，<#ffb900ff>{w_doom}秒<>内未参与击杀则阵亡。",
                "附近有2个以上敌方英雄，或敌方英雄被控制时，放出化学波：命中的敌方英雄狂暴<#ffb900ff>{r_t}秒<>，不能攻击我方、不能施法，"
                "走向身边的队友，用自己的攻击力打他。"),
    "zh-hant": ("【擴充包】",
                "手槍普攻。<#ff9028ff>唯利是圖<>：命中英雄時額外造成最大生命<#ffb900ff>{p_hp}%<><#f5f5f5ff>真實傷害<>並標記；隊友打中它時"
                "引爆，造成<#a974ffff>{p_pop}<> + " + AP + "<#a974ffff>{p_pop_ap}%<><#a974ffff>魔法傷害<>。<#ff9028ff>急難救助<>：隊友"
                "危急時自動施放，攻速+<#ffb900ff>{w_as}%<>、跑速+<#ffb900ff>{w_ms}%<>，<#ffb900ff>{w_t}秒<>內受致命傷害時回滿生命並"
                "逐漸流失，<#ffb900ff>{w_doom}秒<>內未參與擊殺則陣亡。",
                "附近有2個以上敵方英雄，或敵方英雄被控制時，放出化學波：命中的敵方英雄狂暴<#ffb900ff>{r_t}秒<>，不能攻擊我方、不能施法，"
                "走向身邊的隊友，用自己的攻擊力打他。"),
    "en": ("[Add-on] ",
           "Pistol attacks. <#ff9028ff>Leverage<>: hits on champions deal <#ffb900ff>{p_hp}%<> max health as <#f5f5f5ff>true "
           "damage<> and mark them; an ally's hit pops it for <#a974ffff>{p_pop}<> + " + AP + "<#a974ffff>{p_pop_ap}%<> "
           "<#a974ffff>magic damage<>. <#ff9028ff>Bailout<>: cast by itself on an ally in danger: +<#ffb900ff>{w_as}%<> "
           "attack speed, +<#ffb900ff>{w_ms}%<> move speed; a lethal hit within <#ffb900ff>{w_t}s<> restores full health "
           "instead, draining over <#ffb900ff>{w_doom}s<>: no takedown, they die.",
           "With 2+ enemy champions near, or one in crowd control, sends out a chemical wave: enemy champions hit go "
           "berserk for <#ffb900ff>{r_t}s<>, unable to attack her team or cast, walking to their nearest ally and hitting "
           "it with their own attack."),
    "ko": ("[확장] ",
           "권총 공격. <#ff9028ff>영향력<>: 챔피언 적중 시 최대 체력의 <#ffb900ff>{p_hp}%<> <#f5f5f5ff>고정 피해<>를 주고 표식을 남김. "
           "아군이 맞히면 터져 <#a974ffff>{p_pop}<> + " + AP + "<#a974ffff>{p_pop_ap}%<>의 <#a974ffff>마법 피해<>. "
           "<#ff9028ff>긴급 구제<>: 위급한 아군에게 자동 시전, 공격 속도 +<#ffb900ff>{w_as}%<>, 이동 속도 +<#ffb900ff>{w_ms}%<>, "
           "<#ffb900ff>{w_t}초<> 안에 치명상을 입으면 체력을 모두 회복한 뒤 잃고 <#ffb900ff>{w_doom}초<> 안에 처치 관여가 없으면 사망.",
           "근처에 적 챔피언이 2명 이상이거나 군중 제어된 적이 있으면 화학 파동 발사: 맞은 적 챔피언은 <#ffb900ff>{r_t}초<> 동안 "
           "광폭해져 우리 편을 공격하거나 스킬을 쓰지 못하고, 가장 가까운 자기 아군에게 걸어가 자신의 공격력으로 때림."),
    "ja": ("【拡張】",
           "拳銃で通常攻撃。<#ff9028ff>レバレッジ<>：チャンピオンに最大体力の<#ffb900ff>{p_hp}%<>の<#f5f5f5ff>確定ダメージ<>とマーク。"
           "味方が当てると爆発し<#a974ffff>{p_pop}<> + " + AP + "<#a974ffff>{p_pop_ap}%<>の<#a974ffff>魔法ダメージ<>。"
           "<#ff9028ff>緊急支援<>：危険な味方に自動発動、攻撃速度+<#ffb900ff>{w_as}%<>、移動速度+<#ffb900ff>{w_ms}%<>、"
           "<#ffb900ff>{w_t}秒<>内の致命傷で体力全回復し徐々に減少、<#ffb900ff>{w_doom}秒<>内にキルかアシストがなければ倒れる。",
           "敵チャンピオン2体以上が近いか行動妨害中の敵がいる時、化学波を放つ：命中した敵チャンピオンは<#ffb900ff>{r_t}秒<>狂乱し、"
           "こちらへの攻撃とスキルが不可、一番近い自分の味方へ歩いて自分の攻撃力で殴る。"),
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
        sys.exit("the main pack's league_renata differs from build_renata.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":glasc":
        sys.exit("the copy has no league_renata:glasc passive: update this script")
    text = json.dumps(champion)
    for gone in ("league_renata_p_probe", "league_renata_w_bolt", "\"ParabolicProjectile\", \"name\": \"league_renata_r_lash\""):
        if gone in text:
            sys.exit(f"the copy still carries {gone}: the main pack's native switch changed - update this script")
    for slot in ("attack", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), w_doom=setup.secs(p["w_doom"]))
    texts = {lang: {"attack": (mark + attack).format(**values), "ult": (mark + ult).format(**values)}
             for lang, (mark, attack, ult) in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in texts.items() for k, t in d.items()
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
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
