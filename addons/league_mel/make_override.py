"""Build the add-on's copy of Mel from the main pack (Overwhelm's execute, Rebuttal on incoming projectiles, the combos).

    python addons/league_mel/make_override.py

Rebuilds Mel with tools/kit/build_mel.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_mel.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_mel/override/league_mel.data_champion and .../text/champion.i18n: the build with native -
  * everything of the main pack's kit;
  * every Overwhelm stack also lays a plain m_mark buff on the champion and calls league_mel:overwhelm (the execute
    once the stacks are worth his health), and the attack no longer raises the main pack's barrier every w_cd ticks;
  * passive league_mel:reflect (the barrier when an enemy projectile flies at her, the copies sent back; params from P);
  * the attack's tooltip points to description.league_mel_addon.attack with the add-on's wording, so the tooltip in
    game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Mel changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_mel")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_mel as kit  # noqa: E402
import setup_mel as setup  # noqa: E402

TEXT_ID = "league_mel_addon"      # the text's key (the hero's own id is league_mel)
HERO = "league_mel"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, M, A, E, t, mag = setup.O, setup.M, setup.A, setup.E, setup.t, setup.mag
# the attack's whole text in the add-on (the execute and the projectile barrier)
ATTACK = {
    "zh-hans": "射出金色光弹。" + O + "灼灼之光" + E + "：放技能后下次普攻多射{p_n}枚光弹（最多{p_max}枚）；打中英雄叠" + O + "夺命残影" + E +
               "，残影的伤害够了直接处决。" + O + "灵魂折镜" + E + "：敌方弹体飞来时张开屏障" + t("{w_t}秒") + "（冷却" + t("{w_cd}秒") +
               "），免伤{w_red}%，把弹体反弹回去造成" + mag("w_back_dmg", "w_back_r") + "魔法伤害。",
    "zh-hant": "射出金色光彈。" + O + "炙灼耀輝" + E + "：施放技能後下次普攻多射{p_n}發射彈（最多{p_max}發）；打中英雄疊" + O + "奪目" + E +
               "，傷害足夠便直接處決。" + O + "叱返金身" + E + "：敵方射彈飛來時張開屏障" + t("{w_t}秒") + "（冷卻" + t("{w_cd}秒") +
               "），免傷{w_red}%，把射彈反彈回去造成" + mag("w_back_dmg", "w_back_r") + "魔法傷害。",
    "en": "A golden bolt. " + O + "Searing Brilliance" + E + ": each ability adds {p_n} bolts to her next attack (up to {p_max}); "
          "champion hits apply " + O + "Overwhelm" + E + ", executing once it is worth their health. " + O +
          "Rebuttal" + E + ": an enemy projectile flying at her raises a barrier for " + t("{w_t}s") + " (every " + t("{w_cd}s") +
          "): {w_red}% less damage, projectiles returned for " + mag("w_back_dmg", "w_back_r") + " magic damage.",
    "ko": "황금 투사체 발사. " + O + "이글거리는 광휘" + E + ": 스킬 후 다음 기본 공격에 투사체 {p_n}개 추가(최대 {p_max}개); 챔피언 적중 시 " +
          O + "압도" + E + ", 피해가 충분하면 처형. " + O + "반박" + E + ": 적 투사체가 날아오면 " + t("{w_t}초") + " 보호막(" +
          t("{w_cd}초") + "마다), 피해 {w_red}% 감소, 투사체를 되돌려 " + mag("w_back_dmg", "w_back_r") + " 마법 피해.",
    "ja": "黄金の弾を放つ。" + O + "灼熱の輝き" + E + "：スキル後の通常攻撃で弾が{p_n}発増える（最大{p_max}発）。チャンピオンに当たると" + O +
          "圧倒" + E + "、ダメージが足りればとどめ。" + O + "反駁" + E + "：敵の飛翔物が来ると" + t("{w_t}秒") + "障壁（" +
          t("{w_cd}秒") + "ごと）、被ダメージ{w_red}%減、跳ね返して" + mag("w_back_dmg", "w_back_r") + "の魔法ダメージ。",
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
        sys.exit("the main pack's league_mel differs from build_mel.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_mel:reflect":
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    v = {k: p[k] for k in ("p_n", "w_red", "w_back_dmg", "w_back_r")}
    v["p_max"] = 3 * p["p_n"]
    v["w_t"], v["w_cd"] = setup.secs(p["w_t"]), setup.secs(p["w_cd"])
    texts = {lang: {"attack": (LEAD[lang] + ATTACK[lang]).format(**v)} for lang in LEAD}
    long = {f"{lang}.attack": setup.shown_length(LEAD[lang] + ATTACK[lang]) for lang in LEAD
            if setup.shown_length(LEAD[lang] + ATTACK[lang]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
