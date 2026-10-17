"""Build the add-on's copy of Nocturne from the main pack (Paranoia darkness v3).

    python addons/league_nocturne_dark/make_override.py

Reads league/champion/league_nocturne.data_champion and league/text/champion.i18n and writes
addons/league_nocturne_dark/override/league_nocturne.data_champion, .../text/champion.i18n and
.../effects/league_nocturne_dark#sheet.png + #anim.fanim: the same kit with three changes -
  * R's "every allied champion Invisible" at the cast (until the landing, at most 32 ticks) and at the
    landing (20 ticks, the burst) are dropped and R calls the add-on's native effects
    league_nocturne_dark:start / :land instead, which for as long hide each allied champion that has no
    enemy champion within 40000 (re-applied every tick) and play the map veil below (v4: only while
    the ult plays - 180 ticks outlasted it: 「魔腾不放大的时候也全队隐身」); the veil pictures, the mist on
    enemies, the flight and the hit stay as they are;
  * a view effect league_nocturne_dark_veil: one 1280 x 1280 frame of translucent night blue
    (the whole map picture, 128 px border included) shown for 0.75 s under the units (z -1); the
    native code plays it three times at the map centre, a few ticks apart, so the map darkens in
    steps and lightens the same way. It is an ordinary effect event, so it plays in step with the
    match picture (v1 darkened the screen from the client and drifted, see the README);
  * R's tooltip points to description.league_nocturne_dark.ult (the darkness text with a
    "darkness test build" lead, so the tooltip in game shows whether the override took).
Run it again whenever the main pack's Nocturne changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_nocturne_dark")
MOD_ID = "league_nocturne_dark"
TEXT_KEY = "description.league_nocturne_dark.ult"
AD = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TEXT = {
    "zh-hans": "【黑暗测试版】黑暗降临：<#ffb900ff>魔腾飞扑和落地期间<>全地图变暗，敌人只看得见、只打得到身边的我方单位；"
               f"魔腾飞扑一名敌方英雄，落地造成<#ff9028ff>120<> + {AD}<#ff9028ff>120% 攻击力<>的<#ff9028ff>物理伤害<>，"
               "飞行中免疫控制。",
    "zh-hant": "【黑暗測試版】黑暗降臨：<#ffb900ff>夜曲飛撲和落地期間<>全地圖變暗，敵人只看得見、只打得到身邊的我方單位；"
               f"夜曲飛撲一名敵方英雄，落地造成<#ff9028ff>120<> + {AD}<#ff9028ff>120% 攻擊力<>的<#ff9028ff>物理傷害<>，"
               "飛行中免疫控制。",
    "en": "[Darkness test build] Darkness falls: <#ffb900ff>while Nocturne flies and lands<> the map goes dark and enemies see and hit "
          "only the allied units right next to them; Nocturne flies at an enemy champion, dealing "
          f"<#ff9028ff>120<> + {AD}<#ff9028ff>120% AD<> <#ff9028ff>physical damage<> on landing. He is immune to "
          "crowd control in flight.",
    "ko": "[어둠 테스트판] 어둠이 내려 <#ffb900ff>녹턴이 날아가 착지하는 동안<> 지도가 어두워지고, 적은 바로 옆의 아군 유닛만 "
          f"보고 공격할 수 있습니다. 녹턴이 적 챔피언에게 날아가 착지 시 <#ff9028ff>120<> + {AD}<#ff9028ff>공격력의 120%<> "
          "<#ff9028ff>물리 피해<>를 입힙니다. 비행 중 군중 제어에 면역입니다.",
    "ja": "【闇の試験版】闇が訪れ<#ffb900ff>飛びかかって着地するまで<>マップが暗くなり、敵はすぐ近くの味方ユニットしか見えず攻撃できない。"
          f"敵チャンピオンへ飛びかかり、着地で<#ff9028ff>120<> + {AD}<#ff9028ff>攻撃力の120%<>の<#ff9028ff>物理ダメージ<>。"
          "飛行中は行動妨害無効。",
}


VEIL = "league_nocturne_dark_veil"
VEIL_ANIM = "effects/league_nocturne_dark"
VEIL_TAG = "dark"
VEIL_SIZE = 1280
# night blue, alpha per layer: three layers = 1 - (1 - 60/255)^3, about 55 % dark
VEIL_RGBA = (5, 8, 26, 60)
VEIL_SECONDS = 0.75             # the three layers end ~53 ticks after the cast: the ult's flight and landing


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def png_rgba(width, height, rgba):
    """One-colour RGBA PNG without third-party modules."""
    import struct
    import zlib

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    row = b"\x00" + bytes(rgba) * width
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * height, 9)) + chunk(b"IEND", b""))


def write_veil():
    base = os.path.join(ADDON, *VEIL_ANIM.split("/"))
    os.makedirs(lp(os.path.dirname(base)), exist_ok=True)
    with open(lp(base + "#sheet.png"), "wb") as f:
        f.write(png_rgba(VEIL_SIZE, VEIL_SIZE, VEIL_RGBA))
    anim = {"anims": {VEIL_TAG: {"frames": [
        {"duration": VEIL_SECONDS, "data": {"x": 0, "y": 0, "w": VEIL_SIZE, "h": VEIL_SIZE}}]}}}
    with open(lp(base + "#anim.fanim"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(anim) + "\n")
    return base


def main():
    src = os.path.join(ROOT, "league", "champion", "league_nocturne.data_champion")
    with open(lp(src), encoding="utf-8") as f:
        champion = json.load(f)
    ult = champion["ult"]
    ult["description"] = "#asset/base/text/champion?" + TEXT_KEY
    top = ult["effect"]
    if top.get("type") != "Combine":
        sys.exit("R's effect is no longer a Combine: update this script")
    veils = [e for e in top["effects"] if e.get("type") == "RangeEffect" and e.get("target") == "AllyChampion"]
    if len(veils) != 1:
        sys.exit("expected one RangeEffect on AllyChampion in R, found %d: update this script" % len(veils))
    before = len(veils[0]["effects"])
    veils[0]["effects"] = [e for e in veils[0]["effects"] if e.get("type") != "Invisible"]
    if len(veils[0]["effects"]) != before - 1:
        sys.exit("R's allies no longer get one Invisible: update this script")
    burst = next((i for i, e in enumerate(top["effects"]) if e.get("name") == "league_nocturne_r_burst"), None)
    if burst is None:
        sys.exit("R's r_burst picture is gone: update this script")
    top["effects"].insert(burst + 1, {"type": "Native", "effect_ref": MOD_ID + ":start"})
    dives = [e for e in top["effects"] if e.get("type") == "MoveToTarget"]
    if len(dives) != 1:
        sys.exit("R no longer has one MoveToTarget: update this script")
    ends = dives[0]["end_effects"]
    lands = [i for i, e in enumerate(ends) if e.get("type") == "RangeEffect" and e.get("target") == "AllyChampion"
             and [x.get("type") for x in e.get("effects", [])] == ["Invisible"]]
    if len(lands) != 1:
        sys.exit("R's landing no longer hides the allies once: update this script")
    ends[lands[0]] = {"type": "Native", "effect_ref": MOD_ID + ":land"}
    views = champion.setdefault("view_effects", [])
    if any(v.get("name") == VEIL for v in views):
        sys.exit("the main pack already has a %s view effect" % VEIL)
    views.append({"type": "Animation", "name": VEIL, "anim": "asset/%s/%s" % (MOD_ID, VEIL_ANIM),
                  "tag": VEIL_TAG, "z": -1, "is_follow": False})
    veil = write_veil()

    out = os.path.join(ADDON, "override", "league_nocturne.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(TEXT)
    if missing:
        sys.exit("no darkness text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"ult": TEXT[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), os.path.relpath(out_text, ROOT), "and", os.path.relpath(veil, ROOT) + "#*")


if __name__ == "__main__":
    main()
