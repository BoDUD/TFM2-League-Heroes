#!/usr/bin/env python3
"""league_tristana R Buster Shot: the damage on the target alone, as League (2026-11-14).

    python tools/fix/parity_tristana.py [--check]

League (wiki, V26.21): "Tristana fires a massive cannonball at the target enemy that deals magic damage. They and
surrounding enemies are also knocked back and stunned" - "Applies spell damage to the primary target and deals 0 default
damage to secondary targets". Ours hit everyone within 20000 of the target for the full 200 + 120% AD (the user, on the
list of differences from League, 2026-11-14: 「全改吧」).

The blast is a hidden lob onto the champion the ball struck and, in its `end_effects`, the zone `r_zone` (radius 20000,
`EnemyWithoutTower`): Attack, Knockback, the stun, the bomb's stack. Now the Attack leaves `r_zone` and goes into a zone
of its own in front of it, `r_dmg` (radius 1000 on `EnemyChampion`, the same tick: the lob lands on the struck champion,
so only he - or a champion standing inside him - is in it); the push, the stun and the bomb's stack still reach
everyone within 20000, and the kill check (`r_zone_c`) still follows the damage. Both copies of the blast (her R picks a
champion in her face first) are changed. The damage stays physical with an AD ratio: `ApAttack` reads ability power
only, and she has none.

Texts: the ult's five languages in league/text/champion.i18n ("to it and the enemies around" -> the target alone).
Idempotent; --check reports whether the files are already done (exit 1 if not).
"""
import argparse
import io
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_tristana.data_champion")
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
ID = "league_tristana"
N = ID + "_"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
AD = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
O, R, A, E = "<#ff9028ff>", "<#ef5350ff>", "<#ffb900ff>", "<>"
ULT = {
    "zh-hans": "对敌方英雄发射巨型炮弹（优先贴身的），对目标造成" + O + "200" + E + " + " + AD + O + "120% 攻击力" + E + "的" + O +
               "物理伤害" + E + "，将他和周围敌人" + R + "击退" + E + "，落地后" + R + "眩晕" + E + A + "0.5秒" + E + "。",
    "zh-hant": "對敵方英雄發射巨型砲彈（優先貼身的），對目標造成" + O + "200" + E + " + " + AD + O + "120% 攻擊力" + E + "的" + O +
               "物理傷害" + E + "，將他和周圍敵人" + R + "擊退" + E + "，落地後" + R + "暈眩" + E + A + "0.5秒" + E + "。",
    "en": "Tristana fires a massive cannonball at an enemy champion (one close to her first), dealing " + O + "200" + E +
          " + " + AD + O + "120% AD" + E + " " + O + "physical damage" + E + " to it, " + R + "knocking it and the enemies "
          "around back" + E + " and " + R + "stunning" + E + " them for " + A + "0.5s" + E + " where they land.",
    "ko": "적 챔피언(가까운 적 우선)에게 거대한 포탄을 발사해 대상에게 " + O + "200" + E + " + " + AD + O + "공격력의 120%" + E +
          " " + O + "물리 피해" + E + "를 입히고, 대상과 주변 적을 " + R + "뒤로 밀어내며" + E + ", 떨어진 곳에서 " + A + "0.5초" + E +
          " 동안 " + R + "기절" + E + "시킵니다.",
    "ja": "敵チャンピオン（近くの敵を優先）に巨大な砲弾を撃ち、対象に" + O + "200" + E + " + " + AD + O + "攻撃力の120%" + E + "の" + O +
          "物理ダメージ" + E + "を与え、対象と周囲の敵を" + R + "ノックバック" + E + "し、着地後" + A + "0.5秒" + E + "間" + R + "スタン" +
          E + "させる。",
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    s = io.open(lp(path), encoding="utf-8", newline="").read()
    return json.loads(s, object_pairs_hook=OrderedDict), s


def dumps(data, like):
    nl = "\r\n" if "\r\n" in like else "\n"
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", nl) + like[len(like.rstrip("\r\n")):]


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def blasts(x, out):
    """Every effect list that holds the blast's zone `r_zone`."""
    if isinstance(x, dict):
        for v in x.values():
            blasts(v, out)
    elif isinstance(x, list):
        if any(isinstance(e, dict) and e.get("name") == N + "r_zone" for e in x):
            out.append(x)
        for v in x:
            blasts(v, out)
    return out


def fix_kit(kit):
    """Returns how many blasts were changed (0: done already)."""
    done = 0
    lists = blasts(kit["ult"], [])
    if len(lists) != 2:
        sys.exit(f"expected the blast twice in the ult, found {len(lists)}: update this script")
    for effects in lists:
        i = next(k for k, e in enumerate(effects) if isinstance(e, dict) and e.get("name") == N + "r_zone")
        zone = effects[i]
        hits = [a for a in zone["applied_effects"] if a["effect"].get("type") == "Attack"]
        has_own = any(isinstance(e, dict) and e.get("name") == N + "r_dmg" for e in effects)
        if not hits and has_own:
            continue
        if len(hits) != 1 or has_own:
            sys.exit("the blast is neither the old nor the new shape: update this script")
        zone["applied_effects"] = [a for a in zone["applied_effects"] if a is not hits[0]]
        own = OrderedDict([("type", "RangeProjectile"), ("name", N + "r_dmg"),
                           ("shape", OrderedDict([("Circle", OrderedDict([("radius", 1000)]))])),
                           ("delay", 1), ("apply", 1), ("applied_target", "EnemyChampion"),
                           ("applied_effects", [hits[0]])])
        effects.insert(i, own)
        done += 1
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    kit, kit_raw = load(KIT)
    changed = fix_kit(kit)
    text, text_raw = load(TEXT)
    long = {k: shown_length(v) for k, v in ULT.items() if shown_length(v) > TOOLTIP_MAX[k]}
    if long:
        sys.exit(f"tooltip too long: {long}")
    stale = [lang for lang in ULT if text[lang]["description"][ID]["ult"] != ULT[lang]]
    if a.check:
        print("kit:", "done" if not changed else f"{changed} blast(s) to change", "- texts:",
              "done" if not stale else f"{stale} to change")
        sys.exit(1 if changed or stale else 0)
    if changed:
        io.open(lp(KIT), "w", encoding="utf-8", newline="").write(dumps(kit, kit_raw))
    for lang in stale:
        text[lang]["description"][ID]["ult"] = ULT[lang]
    if stale:
        io.open(lp(TEXT), "w", encoding="utf-8", newline="").write(dumps(text, text_raw))
    print(f"kit: {changed} blast(s) changed; texts: {len(stale)} language(s) changed;",
          {k: f"{shown_length(v)}/{TOOLTIP_MAX[k]}" for k, v in ULT.items()})


if __name__ == "__main__":
    main()
