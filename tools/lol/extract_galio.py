r"""Pull Galio's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_galio.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_braum.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Galio.wad.client and Galio.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, picked by size among the variants): the punch GalioBasicAttack_OnCast / _OnHit; the
passive's charge GalioPassiveBuff_OnBuffActivate and its smash GalioPassiveAttack_OnHit; Winds of War's GalioQ_OnCast
and the tornado's GalioQMissile_buffactivate; Justice Punch's GalioE_OnCast and GalioE_hit; Shield of Durand's
GalioW_OnCast and GalioW_hit; Hero's Entrance's GalioR_OnCast, the ally's shield GalioRShield_OnBuffCast and the landing
GalioR_aoe. Voice: the longest take of each spell's own line (GalioQ_cast3D, GalioW_cast3D, GalioE_cast3D,
GalioR_cast3D).
Icons: Galio_Q = skill (Q), Galio_E = skill2 (E, W folded in), Galio_R = ult (R); Galio_W and Galio_Passive are
written too (README / buff icons).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/galio/skins/base/galio_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/galio/skins/base/galio_base_vo_"  # same in every language
P = "Play_sfx_Galio_"
V = "Play_vo_Galio_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_galio_sfx_a_swing": (P + "GalioBasicAttack_OnCast", 219247345, 0.45, -12),
    "league_galio_sfx_a_hit": (P + "GalioBasicAttack_OnHit", 163671250, 0.6, -12),
    "league_galio_sfx_p": (P + "GalioPassiveBuff_OnBuffActivate", 240475849, 0.8, -11),
    "league_galio_sfx_p_hit": (P + "GalioPassiveAttack_OnHit", 557393355, 1.0, -9),
    "league_galio_sfx_q": (P + "GalioQ_OnCast", 160350103, 1.0, -10),
    "league_galio_sfx_q_hit": (P + "GalioQMissile_buffactivate", 521565133, 1.6, -10),
    "league_galio_sfx_e": (P + "GalioE_OnCast", 990216523, 0.8, -10),
    "league_galio_sfx_e_hit": (P + "GalioE_hit", 182078502, 0.9, -9),
    "league_galio_sfx_w": (P + "GalioW_OnCast", 224739640, 1.2, -10),
    "league_galio_sfx_w_hit": (P + "GalioW_hit", 183711108, 1.2, -9),
    "league_galio_sfx_r": (P + "GalioR_OnCast", 632778186, 1.8, -9),
    "league_galio_sfx_r_ally": (P + "GalioRShield_OnBuffCast", 1005869342, 1.6, -11),
    "league_galio_sfx_r_land": (P + "GalioR_aoe", 668962657, 1.6, -8),
    "league_galio_sfx_vo_q": (V + "GalioQ_cast3D", 1187959896, 2.2, -4),
    "league_galio_sfx_vo_w": (V + "GalioW_cast3D", 1217893604, 2.2, -4),
    "league_galio_sfx_vo_e": (V + "GalioE_cast3D", 1970383794, 2.2, -4),
    "league_galio_sfx_vo_r": (V + "GalioR_cast3D", 1069087867, 2.4, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_galio_skill": "ASSETS/Characters/Galio/HUD/Icons2D/Galio_Q.dds",
    "league_galio_skill2": "ASSETS/Characters/Galio/HUD/Icons2D/Galio_E.dds",
    "league_galio_ult": "ASSETS/Characters/Galio/HUD/Icons2D/Galio_R.dds",
    "league_galio_w": "ASSETS/Characters/Galio/HUD/Icons2D/Galio_W.dds",
    "league_galio_passive": "ASSETS/Characters/Galio/HUD/Icons2D/Galio_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Galio.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Galio.{args.lang}.wad.client"))
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
