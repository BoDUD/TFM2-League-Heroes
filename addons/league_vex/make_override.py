"""Build the add-on's copy of Vex from the main pack (a real Gloom on each enemy, dashes marked, Shadow Surge's reset).

    python addons/league_vex/make_override.py

Rebuilds Vex with tools/kit/build_vex.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_vex.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_vex/override/league_vex.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the bolt, Personal Space in the attack, Mistral Bolt, Looming Darkness, Shadow
    Surge with its landing);
  * passive = the add-on's league_vex:gloom with the numbers of P it uses (passive.params);
  * her hits (but Looming Darkness's) mark what they strike (v_hit, 2 ticks): the add-on pops the Gloom on it; the
    data's stand-in (the caster flag g_win and its champion-only twins) is left out;
  * Doom's "ready" picture is the add-on's (it shortens the wait);
  * the attack's, skill2's and the ult's tooltips point to description.league_vex.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Vex changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_vex")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_vex as kit  # noqa: E402
import setup_vex as setup  # noqa: E402

MOD_ID = "league_vex"
HERO = "league_vex"
SLOTS = ("attack", "skill2", "ult")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag, sh = setup.mag, setup.sh

TEXT = {
    "zh-hans": {
        "attack": "【扩展包】射出暗影弹。" + O + "终焉暮气" + E + "：每" + A + "{p_cd}秒" + E + "下一个技能" + R + "恐惧" + E + "命中的敌人" + A +
                  "{p_fear}秒" + E + "；她身边突进的敌方英雄被施加" + O + "暮气" + E + "。" + O + "生人勿近" + E + "：敌方英雄靠近时改为获得" +
                  sh("w_sh", "w_sh_ratio") + "护盾并震伤周围" + mag("w_dmg", "w_ratio") + "。",
        "skill2": "【扩展包】影子飞到目标处扩散，造成" + mag("e_dmg", "e_ratio") + "魔法伤害、减速{e_slow}%，并施加" + O + "暮气" + E +
                  "：她再打中带暮气的敌人就引爆，造成" + mag("g_dmg", "g_ratio") + "魔法伤害，终焉的等待缩短{g_cut}%。",
        "ult": "【扩展包】射出飞弹标记一名敌方英雄，造成" + mag("r_dmg", "r_ratio") + "魔法伤害，随后冲向他再造成" + mag("r2_dmg", "r2_ratio") +
               "魔法伤害。被标记的英雄" + A + "{r_reset}秒" + E + "内阵亡就刷新愁煞。",
    },
    "zh-hant": {
        "attack": "【擴充包】射出暗影彈。" + O + "無望厄障" + E + "：每" + A + "{p_cd}秒" + E + "下一個技能" + R + "恐懼" + E + "命中的敵人" + A +
                  "{p_fear}秒" + E + "；她身邊突進的敵方英雄被施加" + O + "陰霾" + E + "。" + O + "個人舒適圈" + E + "：敵方英雄靠近時改為獲得" +
                  sh("w_sh", "w_sh_ratio") + "護盾並震傷周圍" + mag("w_dmg", "w_ratio") + "。",
        "skill2": "【擴充包】影子飛到目標處擴散，造成" + mag("e_dmg", "e_ratio") + "魔法傷害、緩速{e_slow}%，並施加" + O + "陰霾" + E +
                  "：她再打中帶陰霾的敵人就引爆，造成" + mag("g_dmg", "g_ratio") + "魔法傷害，無望的等待縮短{g_cut}%。",
        "ult": "【擴充包】射出飛彈標記一名敵方英雄，造成" + mag("r_dmg", "r_ratio") + "魔法傷害，隨後衝向他再造成" + mag("r2_dmg", "r2_ratio") +
               "魔法傷害。被標記的英雄" + A + "{r_reset}秒" + E + "內陣亡就刷新飛影急襲。",
    },
    "en": {
        "attack": "[Add-on] Fires a shadow bolt. " + O + "Doom" + E + ": every " + A + "{p_cd}s" + E + " her next spell " + R + "fears" + E +
                  " the enemies hit for " + A + "{p_fear}s" + E + "; enemy champions dashing near her get " + O + "Gloom" + E + ". " + O +
                  "Personal Space" + E + ": with an enemy champion close, she instead gains a " + sh("w_sh", "w_sh_ratio") +
                  " shield and blasts the enemies around her for " + mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + ".",
        "skill2": "[Add-on] Her Shadow flies to the target and spreads: " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  ", slowed {e_slow}%, and " + O + "Gloom" + E + ": her next hit on a Gloomed enemy pops it for " + mag("g_dmg", "g_ratio") +
                  " " + M + "magic damage" + E + " and takes {g_cut}% off Doom's wait.",
        "ult": "[Add-on] Fires a missile that marks an enemy champion for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               ", then surges toward it for " + mag("r2_dmg", "r2_ratio") + " more. If the champion dies within " + A + "{r_reset}s" + E +
               ", Shadow Surge is ready again.",
    },
    "ko": {
        "attack": "[확장] 그림자 탄을 쏜다. " + O + "파멸" + E + ": " + A + "{p_cd}초" + E + "마다 다음 스킬이 맞힌 적을 " + A + "{p_fear}초" + E + " " +
                  R + "공포" + E + "; 근처에서 돌진한 적 챔피언에게 " + O + "우울" + E + ". " + O + "거리 두기" + E + ": 적 챔피언이 가까우면 대신 " +
                  sh("w_sh", "w_sh_ratio") + " 보호막을 얻고 주변에 " + mag("w_dmg", "w_ratio") + " 마법 피해.",
        "skill2": "[확장] 그림자가 대상 위치로 날아가 퍼지며 " + mag("e_dmg", "e_ratio") + " 마법 피해, {e_slow}% 둔화, " + O + "우울" + E +
                  " 부여: 우울한 적을 다시 맞히면 터져 " + mag("g_dmg", "g_ratio") + " 마법 피해, 파멸 대기 {g_cut}% 단축.",
        "ult": "[확장] 투사체로 적 챔피언을 표식해 " + mag("r_dmg", "r_ratio") + " 마법 피해, 이어서 돌진해 " + mag("r2_dmg", "r2_ratio") +
               " 마법 피해. 표식된 챔피언이 " + A + "{r_reset}초" + E + " 안에 죽으면 그림자 파동 재사용 가능.",
    },
    "ja": {
        "attack": "【拡張】影の弾を撃つ。" + O + "フコウ" + E + "：" + A + "{p_cd}秒" + E + "ごとに次のスキルが当たった敵を" + A + "{p_fear}秒" + E +
                  R + "恐怖" + E + "；近くでダッシュした敵チャンピオンに" + O + "ユーウツ" + E + "。" + O + "パーソナルスペース" + E +
                  "：敵チャンピオンが近いと代わりに" + sh("w_sh", "w_sh_ratio") + "のシールドを得て周囲に" + mag("w_dmg", "w_ratio") + "。",
        "skill2": "【拡張】影が目標地点へ飛んで広がり、" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、{e_slow}%スロウ、" + O + "ユーウツ" + E +
                  "付与：ユーウツの敵に再び当てると弾けて" + mag("g_dmg", "g_ratio") + "の魔法ダメージ、フコウの待ちが{g_cut}%短縮。",
        "ult": "【拡張】弾で敵チャンピオンにマークをつけ" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、続いて突進して" +
               mag("r2_dmg", "r2_ratio") + "の魔法ダメージ。マークされたチャンピオンが" + A + "{r_reset}秒" + E + "以内に倒れると影法師が再使用可能。",
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
        sys.exit("the main pack's league_vex differs from build_vex.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":gloom":
        sys.exit("the copy has no league_vex:gloom passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values["g_cut"] = p["g_cut"]
    values["r_reset"] = setup.secs(p["r_reset"])
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
