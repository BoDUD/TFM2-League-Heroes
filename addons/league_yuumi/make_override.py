"""Build the add-on's copy of Yuumi from the main pack (a ride with no end, casting from the ally's head).

    python addons/league_yuumi/make_override.py

Rebuilds Yuumi with tools/kit/build_yuumi.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_yuumi.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_yuumi/override/league_yuumi.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the bolt, Prowling Projectile, the jump onto an ally with Zoomies, Final Chapter);
  * passive = the add-on's league_yuumi:bond with the numbers of P it uses (passive.params);
  * the jump marks the ally (league_yuumi_w_host) instead of the data's timed banish and following casts: the add-on
    keeps her on him; riding (league_yuumi_w_on), skill2 gives him Zoomies again;
  * a champion-only twin of Prowling Projectile carries Feline Friendship;
  * the attack and skill2 tooltips point to description.league_yuumi.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Yuumi changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yuumi")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_yuumi as kit  # noqa: E402
import setup_yuumi as setup  # noqa: E402

MOD_ID = "league_yuumi"
HERO = "league_yuumi"
SLOTS = ("attack", "skill2")
O, A, G, M, E = setup.O, setup.A, setup.G, setup.M, setup.E
mag, grn = setup.mag, setup.grn

TEXT = {
    "zh-hans": {
        "attack": "【扩展包】射出书页光弹。" + O + "猫的博爱" + E + "：每" + A + "{p_cd}秒" + E + "普攻或摸鱼飞弹命中英雄时多造成" +
                  mag("p_dmg", "p_ap") + "魔法伤害，回复自己" + grn("p_heal", "p_hap") + "生命，下次附身时队友也回复同样多。",
        "skill2": "【扩展包】" + O + "悠米出动！" + E + "：附身在交战中的队友身上，" + A + "不限时" + E + "（谁都选不中，出招时才现身），他每秒回复" +
                  grn("w_heal", "w_hap") + "生命，他死了才跳下来。" + O + "旺盛精力" + E + "：给他" + grn("e_sh", "e_ap") +
                  "护盾，攻速+{e_as}%、移速+{e_ms}%；附身时再放只给他旺盛精力。",
    },
    "zh-hant": {
        "attack": "【擴充包】射出書頁光彈。" + O + "貓貓摯友" + E + "：每" + A + "{p_cd}秒" + E + "普攻或奇幻圖騰命中英雄時多造成" +
                  mag("p_dmg", "p_ap") + "魔法傷害，回復自己" + grn("p_heal", "p_hap") + "生命，下次附身時隊友也回復同樣多。",
        "skill2": "【擴充包】" + O + "飛撲抱抱！" + E + "：附身在交戰中的隊友身上，" + A + "不限時" + E + "（誰都選不中，出招時才現身），他每秒回復" +
                  grn("w_heal", "w_hap") + "生命，他死了才跳下來。" + O + "蹦蹦衝刺" + E + "：給他" + grn("e_sh", "e_ap") +
                  "護盾，攻速+{e_as}%、移速+{e_ms}%；附身時再放只給他蹦蹦衝刺。",
    },
    "en": {
        "attack": "[Add-on] Fires a page bolt. " + O + "Feline Friendship" + E + ": every " + A + "{p_cd}s" + E + " an attack or a "
                  "Prowling Projectile on a champion deals " + mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + " more and "
                  "heals her " + grn("p_heal", "p_hap") + "; the ally she attaches to next is healed as much.",
        "skill2": "[Add-on] " + O + "You and Me!" + E + ": attaches to an ally in the fight with " + A + "no time limit" + E +
                  " (untargetable, showing only to cast); he heals " + grn("w_heal", "w_hap") + " a second; she jumps off when "
                  "he dies. " + O + "Zoomies" + E + ": he gets a " + grn("e_sh", "e_ap") + " shield, +{e_as}% attack speed and "
                  "+{e_ms}% move speed; recast while attached for Zoomies alone.",
    },
    "ko": {
        "attack": "[확장] 책장 탄을 쏜다. " + O + "야옹이 친구" + E + ": " + A + "{p_cd}초" + E + "마다 기본 공격이나 사르르탄이 챔피언에게 맞으면 " +
                  mag("p_dmg", "p_ap") + " 마법 피해 추가, 자신 " + grn("p_heal", "p_hap") + " 회복, 다음에 붙는 아군도 같은 만큼 회복.",
        "skill2": "[확장] " + O + "너랑 유미랑!" + E + ": 싸우는 아군에게 " + A + "시간 제한 없이" + E + " 붙는다(대상 지정 불가, 스킬을 쓸 때만 "
                  "보임). 아군은 초당 " + grn("w_heal", "w_hap") + " 회복, 아군이 죽으면 내려온다. " + O + "슈우우웅" + E + ": 보호막 " +
                  grn("e_sh", "e_ap") + ", 공격 속도 +{e_as}%, 이동 속도 +{e_ms}%. 붙은 채로 다시 쓰면 슈우우웅만.",
    },
    "ja": {
        "attack": "【拡張】ページ弾を撃つ。" + O + "ネコはトモダチ" + E + "：" + A + "{p_cd}秒" + E + "ごとに通常攻撃かきまぐれミサイルが"
                  "チャンピオンに当たると" + mag("p_dmg", "p_ap") + "の魔法ダメージ追加、自身を" + grn("p_heal", "p_hap") +
                  "回復、次にくっつく味方も同じだけ回復。",
        "skill2": "【拡張】" + O + "ユー＆ミー！" + E + "：戦闘中の味方に" + A + "時間制限なし" + E + "でくっつく（対象指定不可、スキルを使う時だけ"
                  "姿を見せる）。味方は毎秒" + grn("w_heal", "w_hap") + "回復、味方が倒れたら降りる。" + O + "バビューン！" + E +
                  "：シールド" + grn("e_sh", "e_ap") + "、攻撃速度+{e_as}%、移動速度+{e_ms}%。くっついたまま使うとバビューン！だけ。",
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
        sys.exit("the main pack's league_yuumi differs from build_yuumi.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":bond":
        sys.exit("the copy has no league_yuumi:bond passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
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
