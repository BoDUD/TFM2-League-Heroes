"""Pull Leona's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_leona.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Leona.wad.client and Leona.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in the base skin's bin (a few only with a length byte after them in the file:
ShieldOfDaybreakAttack_hit, ZenithBladeMissile_hitchampion, ZenithBladeDash_hit). Q's cast is the
shield lighting up (ShieldOfDaybreak_OnCast), its hit the bash; E is the throw, the blade's flight, the
champion hit and the landing of the dash; W the shield raised (SolarBarrier_OnCast) and its burst; R
the call and the flare's impact. The zh_CN voice bank shares Q's line with her basic-attack efforts
(four short shouts); E and R have their own lines; none is byte-equal to the en_US bank.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/leona/skins/base/leona_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/leona/skins/base/leona_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_leona_sfx_attack_hit": ("Play_sfx_Leona_LeonaBasicAttack_OnHit", 204822424, 0.6, -5),
    "league_leona_sfx_q_cast": ("Play_sfx_Leona_LeonaShieldOfDaybreak_OnCast", 457842275, 1.2, -6),
    "league_leona_sfx_q_hit": ("Play_sfx_Leona_LeonaShieldOfDaybreakAttack_hit", 149881516, 0.9, -3),
    "league_leona_sfx_e_cast": ("Play_sfx_Leona_LeonaZenithBlade_OnCast", 606727893, 0.7, -4),
    "league_leona_sfx_e_fly": ("Play_sfx_Leona_LeonaZenithBladeMissile_OnMissileLaunch", 348015755, 1.2, -5),
    "league_leona_sfx_e_hit": ("Play_sfx_Leona_LeonaZenithBladeMissile_hitchampion", 363819565, 0.6, -4),
    "league_leona_sfx_e_dash": ("Play_sfx_Leona_LeonaZenithBladeDash_hit", 387687679, 0.8, -4),
    "league_leona_sfx_w_cast": ("Play_sfx_Leona_LeonaSolarBarrier_OnCast", 148625443, 1.4, -6),
    "league_leona_sfx_w_burst": ("Play_sfx_Leona_LeonaSolarBarrier_hit", 424428543, 2.0, -3),
    "league_leona_sfx_r_cast": ("Play_sfx_Leona_LeonaSolarFlare_OnCast", 963566819, 1.1, -4),
    "league_leona_sfx_r_hit": ("Play_sfx_Leona_LeonaSolarFlare_hit", 88061807, 2.3, -2),
    "league_leona_vo_q": ("Play_vo_Leona_LeonaShieldOfDaybreakAttack_cast3D", 1223755917, 0.7, -2),
    "league_leona_vo_e": ("Play_vo_Leona_LeonaZenithBlade_cast3D", 1147964727, 0.8, -2),
    "league_leona_vo_r": ("Play_vo_Leona_LeonaSolarFlare_cast3D", 1299926458, 1.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (W rides on E, Sunlight is a passive: no slots)
    "league_leona_skill": "ASSETS/Characters/Leona/HUD/Icons2D/LeonaQ.dds",
    "league_leona_skill2": "ASSETS/Characters/Leona/HUD/Icons2D/LeonaE.dds",
    "league_leona_ult": "ASSETS/Characters/Leona/HUD/Icons2D/LeonaR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Leona.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Leona.{args.lang}.wad.client"))
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
            print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
