"""Build the add-on's copy of Aurora from the main pack (Across the Veil at her real low health, League's rift border).

    python addons/league_aurora/make_override.py

Rebuilds Aurora with tools/kit/build_aurora.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_aurora.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_aurora/override/league_aurora.data_champion and
.../text/champion.i18n: the build with native=1 -
  * Across the Veil's hop (in the attack and The Weirding) reads the flag `league_aurora_low` as well as an enemy
    champion within w_near (the main pack's stand-in reads the champion alone);
  * passive = league_aurora:veil (params: w_low and the rift's r_t, r_edge, r_edge_t, r_wrap_t), which raises the flag
    every tick she is under w_low% health and keeps Between Worlds' rift by League's rules (src/rift.rs): the data's
    zone that slows everyone in it is gone, the line on the shockwave's centre calls league_aurora:rift instead;
  * Spirit Abjuration counts on each enemy (league_aurora:mark_<source>) and Twofold Hex's return hits by missing
    health (league_aurora:hex_back), src/spirit.rs;
  * the attack's, Q's and the ult's tooltips (keys of the add-on's own id) say what the add-on does, so the tooltips in
    game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Aurora changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_aurora")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_aurora as kit  # noqa: E402
import setup_aurora as setup  # noqa: E402

MOD_ID = "league_aurora"
HERO = "league_aurora"
mag, t, n, hl, cc = setup.mag, setup.t, setup.n, setup.hl, setup.cc
# 语言 -> 附加包的普攻、Q、大招说明（主包的说明加上附加包做的事：被动按敌人分别叠层、残血后跳和击杀刷新、
# Q 回程按已损失生命加伤、领域的边界和提前关）
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】" + n("驱灵奇术") + "：每个敌人分别叠层，第三层造成{p_hp_pct}% + 每100" + setup.APi + "{p_hp_ap_pct}%最大生命" +
                  "魔法伤害，抽出灵物，" + t("{sp_t}秒") + "内每秒" + hl("回复") + "{sp0}–{sp1} + {sp_ap}%法强。" + n("灵纱洞开") + "：生命低于{w_low}%被贴身时后跳，" +
                  "隐身" + t("{w_inv}秒") + "、加速{w_ms}%（" + t("{w_cd}秒") + "，参与击杀刷新）。",
        "skill": "【附加包】放出咒弹穿过敌人，造成" + mag("q_dmg", "q_ratio") + "魔法伤害并留下诅咒；" + t("{q_hold}秒") + "后抽回，回程造成" +
                 mag("q2_dmg", "q2_ratio") + "魔法伤害，按目标已损失生命最多+{q2_miss}%，对小兵{q2_minion}%、野怪{q2_monster}%。",
        "ult": "【附加包】朝敌方英雄跃出一小段，加速{r_ms}%；前方的冲击波造成" + mag("r_dmg", "r_ratio") + "魔法伤害并" + cc("减速") +
               "{r_slow1}%，" + t("{r_grow}秒") + "后成为领域（" + t("{r_t1}/{r_t2}/{r_t3}秒") + "）：敌人碰到边界被" + cc("减速") + "{r_edge}%，她碰到边界穿到对面；" +
               "里面没有敌人就提前关闭。",
    },
    "zh-hant": {
        "attack": "【附加包】" + n("精靈附體") + "：每個敵人分別疊層，第三層造成{p_hp_pct}% + 每100" + setup.APi + "{p_hp_ap_pct}%最大生命" +
                  "魔法傷害，抽出精靈，" + t("{sp_t}秒") + "內每秒" + hl("回復") + "{sp0}–{sp1} + {sp_ap}%法強。" + n("跨越兩界") + "：生命低於{w_low}%被貼身時後跳，" +
                  "隱形" + t("{w_inv}秒") + "、加速{w_ms}%（" + t("{w_cd}秒") + "，參與擊殺刷新）。",
        "skill": "【附加包】放出咒彈穿過敵人，造成" + mag("q_dmg", "q_ratio") + "魔法傷害並留下詛咒；" + t("{q_hold}秒") + "後抽回，回程造成" +
                 mag("q2_dmg", "q2_ratio") + "魔法傷害，按目標已損失生命最多+{q2_miss}%，對小兵{q2_minion}%、野怪{q2_monster}%。",
        "ult": "【附加包】朝敵方英雄躍出一小段，加速{r_ms}%；前方的衝擊波造成" + mag("r_dmg", "r_ratio") + "魔法傷害並" + cc("緩速") +
               "{r_slow1}%，" + t("{r_grow}秒") + "後成為領域（" + t("{r_t1}/{r_t2}/{r_t3}秒") + "）：敵人碰到邊界被" + cc("緩速") + "{r_edge}%，她碰到邊界穿到對面；" +
               "裡面沒有敵人就提前關閉。",
    },
    "en": {
        "attack": "[Add-on] " + n("Spirit Abjuration") + ": stacks on each enemy; the third deals {p_hp_pct}% (+" +
                  "{p_hp_ap_pct}% per 100 " + setup.APi + ") of his max health as magic damage and draws a spirit that " + hl("heals") +
                  " her {sp0}-{sp1} + {sp_ap}% AP a second for " + t("{sp_t}s") + ". " + n("Across the Veil") + ": under {w_low}% health "
                  "with an enemy on her, she hops back, invisible " + t("{w_inv}s") + ", {w_ms}% faster (every " + t("{w_cd}s") +
                  ", reset by a takedown).",
        "skill": "[Add-on] A hex flies through her enemies for " + mag("q_dmg", "q_ratio") + " magic damage, cursing them; " +
                 t("{q_hold}s") + " later it is drawn back for " + mag("q2_dmg", "q2_ratio") + " magic damage, up to {q2_miss}% more by "
                 "the target's missing health ({q2_minion}% to minions, {q2_monster}% to monsters).",
        "ult": "[Add-on] Leaps a short way toward an enemy champion, {r_ms}% faster; a shockwave in front of her deals " +
               mag("r_dmg", "r_ratio") + " magic damage and " + cc("slows") + " {r_slow1}%, and " + t("{r_grow}s") + " later becomes a rift (" +
               t("{r_t1}/{r_t2}/{r_t3}s") + "): enemies touching its border are " + cc("slowed") + " {r_edge}%, and when she touches it she "
               "crosses to the far side. It closes early once no enemy is left in it.",
    },
    "ko": {
        "attack": "[확장] 영혼 빛. " + n("영혼 방호술") + ": 적마다 따로 쌓여 세 번째에 최대 체력의 {p_hp_pct}% + " + setup.APi + "100당 {p_hp_ap_pct}% 마법 피해, " +
                  "영혼이 " + t("{sp_t}초") + " 동안 매초 {sp0}–{sp1} + 주문력 {sp_ap}% " + hl("회복") + ". " + n("장막 너머로") +
                  ": 체력 {w_low}% 미만에 적이 붙으면 뒤로 뛰어 " + t("{w_inv}초") + " 투명, 이동 속도 +{w_ms}% (" + t("{w_cd}초") + "마다, 처치 관여 시 초기화).",
        "skill": "[확장] 주문 탄이 적을 꿰뚫어 " + mag("q_dmg", "q_ratio") + " 마법 피해와 저주; " + t("{q_hold}초") + " 뒤 끌어당겨 " +
                 mag("q2_dmg", "q2_ratio") + " 마법 피해, 대상의 잃은 체력에 따라 최대 +{q2_miss}% (미니언 {q2_minion}%, 몬스터 {q2_monster}%).",
        "ult": "[확장] 적 챔피언 쪽으로 짧게 도약하며 이동 속도 +{r_ms}%; 앞쪽 충격파가 " + mag("r_dmg", "r_ratio") + " 마법 피해와 {r_slow1}% " +
               cc("둔화") + ", " + t("{r_grow}초") + " 뒤 영역(" + t("{r_t1}/{r_t2}/{r_t3}초") + "): 경계에 닿은 적은 {r_edge}% " + cc("둔화") +
               ", 그녀는 경계에 닿으면 반대편으로 건너간다. 안에 적이 없으면 일찍 닫힌다.",
    },
    "ja": {
        "attack": "【拡張】霊光。" + n("精霊の解放") + "：敵ごとに重なり、3回目で最大体力の{p_hp_pct}%＋" + setup.APi + "100ごと{p_hp_ap_pct}%の魔法ダメージ、" +
                  "精霊が" + t("{sp_t}秒") + "間毎秒{sp0}–{sp1}＋{sp_ap}%魔力" + hl("回復") + "。" + n("ベールを越えて") +
                  "：体力{w_low}%未満で詰められると後ろへ跳び" + t("{w_inv}秒") + "透明、移動速度+{w_ms}%（" + t("{w_cd}秒") + "ごと、キルかアシストで再使用）。",
        "skill": "【拡張】呪弾が敵を貫き" + mag("q_dmg", "q_ratio") + "の魔法ダメージと呪い、" + t("{q_hold}秒") + "後に引き戻し" +
                 mag("q2_dmg", "q2_ratio") + "の魔法ダメージ、失った体力に応じ最大+{q2_miss}%（ミニオン{q2_minion}%、モンスター{q2_monster}%）。",
        "ult": "【拡張】敵英雄の方へ短く跳び移動速度+{r_ms}%。前方の衝撃波で" + mag("r_dmg", "r_ratio") + "の魔法ダメージと{r_slow1}%" +
               cc("スロウ") + "、" + t("{r_grow}秒") + "後に領域（" + t("{r_t1}/{r_t2}/{r_t3}秒") + "）：境界に触れた敵は{r_edge}%" + cc("スロウ") +
               "、彼女は境界に触れると反対側へ渡る。中に敵がいなければ早く閉じる。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """Params::default() in src/lib.rs as {field: value}."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    return {k.strip(): int(v.strip().rstrip(",")) for k, v in re.findall(r"(\w+): (\d+),?", m.group(1))}


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_aurora differs from build_aurora.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_aurora.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":veil":
        sys.exit("the copy has no league_aurora:veil passive: update this script")
    if '"league_aurora_low"' not in json.dumps(champion):
        sys.exit("the copy's veil does not read league_aurora_low: update this script")
    if '"' + MOD_ID + ':rift"' not in json.dumps(champion["ult"]) or '"league_aurora_r_field"' in json.dumps(champion["ult"]):
        sys.exit("the copy's ult does not leave its rift to league_aurora:rift: update this script")
    for native in [f"{MOD_ID}:mark_{src}" for src in ("a", "q", "q2", "e", "r")] + [f"{MOD_ID}:hex_back"]:
        if '"' + native + '"' not in json.dumps(champion):
            sys.exit(f"the copy has no {native}: update this script")
    if '"league_aurora_s_1"' in json.dumps(champion):
        sys.exit("the copy still counts Spirit Abjuration on her (the add-on counts on each enemy): update this script")
    # 领域的光圈：rift.rs 放的开场和一圈要在副本的 views 里登记（play_view_effect 只认登记过的名字），表里要有这两个
    # 标签和 hd_ 版（tools/art/aurora_realm_tags.py）
    views = {v["name"]: v for v in champion["view_effects"]}
    rift_rs = open(lp(os.path.join(ADDON, "src", "rift.rs")), encoding="utf-8").read()
    with open(lp(os.path.join(ROOT, "league", "effects", "league_aurora_big#anim.fanim")), encoding="utf-8") as f:
        big = json.load(f)["anims"]
    for tag in ("r_zone_in", "r_zone_loop"):
        v = views.get(f"{HERO}_{tag}")
        if not v or v["tag"] != tag or not v["anim"].endswith("/league_aurora_big") or f'"{HERO}_{tag}"' not in rift_rs:
            sys.exit(f"the copy's view {HERO}_{tag} and src/rift.rs do not match: update this script")
        if tag not in big or "hd_" + tag not in big:
            sys.exit(f"league_aurora_big has no {tag} / hd_{tag}: python -I tools/art/aurora_realm_tags.py")
    for slot in ("attack", "skill", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
