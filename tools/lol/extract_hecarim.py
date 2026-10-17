r"""Pull Hecarim's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_hecarim.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_karma.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Hecarim.wad.client and Hecarim.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/hc/snd_names_hc.py, picked with work/hc/snd_probe_hc.py): the glaive
HecarimBasicAttack_OnCast / _OnHit; Rampage HecarimRapidSlash_OnCast / _hit; Spirit of Dread HecarimW_OnCast;
Devastating Charge HecarimRamp_OnCast (the gallop) and HecarimRampAttack_OnHit (the knockback blow); Onslaught of
Shadows HecarimUltMissile_OnMissileLaunch (the riders' thunder), HecarimUltCharge_hit (the landing) and a short glaive
hit for each rider pass. Voice: Q, W, R (League gives his E no line).
Icons: Hecarim_Rampage = skill (Q), Hecarim_DevastingCharge = skill2 (E), Hecarim_OnslaughtofShadows = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/hecarim/skins/base/hecarim_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/hecarim/skins/base/hecarim_base_vo_"  # same in every language
P = "Play_sfx_Hecarim_Hecarim"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_hecarim_sfx_a_swing": (P + "BasicAttack_OnCast", 179811759, 0.45, -11),
    "league_hecarim_sfx_a_hit": (P + "BasicAttack_OnHit", 634223747, 0.4, -12),
    "league_hecarim_sfx_q": (P + "RapidSlash_OnCast", 545141109, 0.75, -10),
    "league_hecarim_sfx_q_hit": (P + "RapidSlash_hit", 470549977, 0.4, -12),
    "league_hecarim_sfx_w": (P + "W_OnCast", 370682124, 1.6, -10),
    "league_hecarim_sfx_e": (P + "Ramp_OnCast", 863465441, 1.3, -10),
    "league_hecarim_sfx_e_hit": (P + "RampAttack_OnHit", 649514276, 0.7, -8),
    "league_hecarim_sfx_r": (P + "UltMissile_OnMissileLaunch", 350076233, 1.9, -8),
    "league_hecarim_sfx_r_hit": (P + "UltCharge_hit", 588978893, 0.9, -8),
    "league_hecarim_sfx_r_pass": (P + "BasicAttack_OnHit", 284511018, 0.3, -14),
    "league_hecarim_sfx_vo_q": ("Play_vo_Hecarim_HecarimRapidSlash_cast3D", 814416636, 0.8, -4),
    "league_hecarim_sfx_vo_w": ("Play_vo_Hecarim_HecarimW_cast3D", 152000445, 0.8, -4),
    "league_hecarim_sfx_vo_r": ("Play_vo_Hecarim_HecarimUlt_cast3D", 1671840385, 1.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_hecarim_skill": "ASSETS/Characters/Hecarim/HUD/Icons2D/Hecarim_Rampage.dds",
    "league_hecarim_skill2": "ASSETS/Characters/Hecarim/HUD/Icons2D/Hecarim_DevastingCharge.dds",
    "league_hecarim_ult": "ASSETS/Characters/Hecarim/HUD/Icons2D/Hecarim_OnslaughtofShadows.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Hecarim.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Hecarim.{args.lang}.wad.client"))
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
