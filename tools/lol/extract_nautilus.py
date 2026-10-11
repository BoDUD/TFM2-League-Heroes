r"""Pull Nautilus's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_nautilus.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe
gmstream-cli.exe
gmstream-cli.exe

Same route as extract_viego.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Nautilus.wad.client and Nautilus.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, picked by decoding every variant): the anchor swing NautilusBasicAttack_OnCast / _OnHit;
Staggering Blow's root NautilusRavageStrikeAttack_OnHit; Dredge Line's throw NautilusAnchorDrag_OnCast and
NautilusAnchorDragMissile_OnMissileLaunch, the hook on a champion _hit_collision and on a wall _hit_terrain (the wall-hook
add-on); Titan's Wrath NautilusPiercingGaze_OnCast (the shield); Riptide NautilusSplashZone_OnCast (the slam); Depth
Charge NautilusGrandLine_OnCast, the shockwave on its way NautilusGrandLineTracker_hit and the knock-up
NautilusGrandLineTarget_OnBuffActivate. Voice: Q, E (the W+E cast) and R (his voice for W is a 12 s bed: none).
Icons: Nautilus_AnchorChain = skill (Q), Nautilus_Wrath = skill2 (W, Riptide folded in), Nautilus_GrandLine = ult (R).
"""
import argparse
import io
import os
import sys
import wave

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "league")
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/nautilus/skins/base/nautilus_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/nautilus/skins/base/nautilus_base_vo_"  # same in every language
P = "Play_sfx_Nautilus_Nautilus"
V = "Play_vo_Nautilus_Nautilus"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_nautilus_sfx_a_swing": (P + "BasicAttack_OnCast", 557550614, 0.45, -11),
    "league_nautilus_sfx_a_hit": (P + "BasicAttack_OnHit", 16639940, 0.6, -12),
    "league_nautilus_sfx_p": (P + "RavageStrikeAttack_OnHit", 587127548, 1.0, -10),
    "league_nautilus_sfx_q": (P + "AnchorDrag_OnCast", 40805579, 0.8, -10),
    "league_nautilus_sfx_q_fly": (P + "AnchorDragMissile_OnMissileLaunch", 392483178, 0.85, -11),
    "league_nautilus_sfx_q_hit": (P + "AnchorDragMissile_hit_collision", 19157459, 1.0, -9),
    "league_nautilus_sfx_q_wall": (P + "AnchorDragMissile_hit_terrain", 129934599, 0.9, -9),
    "league_nautilus_sfx_w": (P + "PiercingGaze_OnCast", 762087137, 1.4, -10),
    "league_nautilus_sfx_e": (P + "SplashZone_OnCast", 58959623, 1.6, -9),
    "league_nautilus_sfx_r": (P + "GrandLine_OnCast", 279664421, 0.65, -10),
    "league_nautilus_sfx_r_wave": (P + "GrandLineTracker_hit", 63064517, 1.5, -11),
    "league_nautilus_sfx_r_hit": (P + "GrandLineTarget_OnBuffActivate", 551322038, 1.6, -9),
    "league_nautilus_sfx_vo_q": (V + "AnchorDrag_cast3D", 1266469777, 1.6, -4),
    "league_nautilus_sfx_vo_e": (V + "SplashZone_cast3D", 404559524, 1.8, -4),
    "league_nautilus_sfx_vo_r": (V + "GrandLine_cast3D", 1215875013, 1.8, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_nautilus_skill": "ASSETS/Characters/Nautilus/HUD/Icons2D/Nautilus_AnchorChain.dds",
    "league_nautilus_skill2": "ASSETS/Characters/Nautilus/HUD/Icons2D/Nautilus_Wrath.dds",
    "league_nautilus_ult": "ASSETS/Characters/Nautilus/HUD/Icons2D/Nautilus_GrandLine.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Nautilus.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Nautilus.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if mid not in variants:
                sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
            sr, x = decode(media[mid], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:38s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:38s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
