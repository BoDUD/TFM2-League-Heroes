r"""Pull Twitch's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_twitch.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Twitch.wad.client and Twitch.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events (plain strings in the WAD's .bin files) are Play_sfx_Twitch_Twitch<spell>_<event>; the voice events
Play_vo_Twitch_Spell3D<key>Cast. The crossbow BasicAttack_OnMissileLaunch / _OnHit; Ambush HideInShadows_OnCast (the
fade), _OnBuffDeactivate (out of hiding) and _OnBuffActivate (the shimmer: Q's reset); Venom Cask VenomCask_OnCast,
VenomCaskMissile_OnMissileLaunch and _OnHitLocation; Contaminate Expunge_OnCast and Expunge_missilelaunch (the burst
on every poisoned unit); Spray and Pray FullAutomatic_OnCast, SprayAndPrayAttack_OnMissileLaunch and _OnHit.
Icons: Twitch_Q = skill, Twitch_W = skill2 (the cask; E is in its text), Twitch_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/twitch/skins/base/twitch_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/twitch/skins/base/twitch_base_vo_"  # same in every language
P = "Play_sfx_Twitch_Twitch"
V = "Play_vo_Twitch_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_twitch_sfx_shot": (P + "BasicAttack_OnMissileLaunch", 259262300, 0.6, -12),
    "league_twitch_sfx_hit": (P + "BasicAttack_OnHit", 94273227, 0.5, -12),
    "league_twitch_sfx_q_cast": (P + "HideInShadows_OnCast", 371138114, 1.4, -9),
    "league_twitch_sfx_q_out": (P + "HideInShadows_OnBuffDeactivate", 876396485, 0.9, -9),
    "league_twitch_sfx_q_reset": (P + "HideInShadows_OnBuffActivate", 696231807, 1.2, -10),
    "league_twitch_sfx_w_cast": (P + "VenomCask_OnCast", 463057964, 0.7, -10),
    "league_twitch_sfx_w_throw": (P + "VenomCaskMissile_OnMissileLaunch", 36741813, 0.8, -10),
    "league_twitch_sfx_w_land": (P + "VenomCaskMissile_OnHitLocation", 588053563, 1.4, -8),
    "league_twitch_sfx_e_cast": (P + "Expunge_OnCast", 586526595, 0.9, -9),
    "league_twitch_sfx_e_pop": (P + "Expunge_missilelaunch", 1053087744, 0.7, -9),
    "league_twitch_sfx_r_cast": (P + "FullAutomatic_OnCast", 880541898, 1.6, -8),
    "league_twitch_sfx_r_shot": (P + "SprayAndPrayAttack_OnMissileLaunch", 802388961, 0.8, -11),
    "league_twitch_sfx_r_hit": (P + "SprayAndPrayAttack_OnHit", 893827816, 0.6, -12),
    "league_twitch_sfx_vo_q": (V + "Spell3DQCast", 668859486, 2.4, -4),
    "league_twitch_sfx_vo_w": (V + "Spell3DWCast", 1959965583, 2.0, -4),
    "league_twitch_sfx_vo_e": (V + "Spell3DECast", 2068493795, 2.0, -4),
    "league_twitch_sfx_vo_r": (V + "Spell3DRCast", 1462055750, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_twitch_skill": "ASSETS/Characters/Twitch/HUD/Icons2D/Twitch_Q.dds",
    "league_twitch_skill2": "ASSETS/Characters/Twitch/HUD/Icons2D/Twitch_W.dds",
    "league_twitch_ult": "ASSETS/Characters/Twitch/HUD/Icons2D/Twitch_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Twitch.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Twitch.{args.lang}.wad.client"))
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
