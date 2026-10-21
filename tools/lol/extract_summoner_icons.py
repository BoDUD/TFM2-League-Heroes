"""Pull the summoner spells' icons out of a local League of Legends install (for league_zoe's stolen spells).

    python tools/lol/extract_summoner_icons.py --lol "D:\\WeGameApps\\lol"

Reads (never writes) Game/DATA/FINAL/DATA.wad.client: data/spells/icons2d/<icon>.dds, 64 x 64, written as PNGs to
assets/source/zoe/summoner_icons/<spell>.png like the champions' ability icons (extract_aatrox.py's way, league/icons).
tools/art/draw_zoe_spells.py shrinks them into league_zoe_spell_icons (the user, 2026-10-22: 「直接拿英雄联盟客户端里面的
图标啊」). Ghost is summoner_haste, Cleanse summoner_boost.
"""
import argparse
import io
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from riot import Wad  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "zoe", "summoner_icons")
ICONS = {"flash": "summoner_flash", "ignite": "summonerignite", "exhaust": "summoner_exhaust", "heal": "summoner_heal",
         "barrier": "summonerbarrier", "ghost": "summoner_haste", "cleanse": "summoner_boost"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    a = ap.parse_args()
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "DATA.wad.client"))
    os.makedirs(OUT, exist_ok=True)
    for spell, name in ICONS.items():
        path = f"data/spells/icons2d/{name}.dds"
        img = Image.open(io.BytesIO(wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, spell + ".png"))
        print(f"{spell:8s} {img.size} <- {path}")


if __name__ == "__main__":
    main()
