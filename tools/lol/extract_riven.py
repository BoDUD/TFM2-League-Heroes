"""Pull Riven's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_riven.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Riven.wad.client and Riven.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her spells in the base bins: RivenTriCleave = Broken Wings (hit_a the slash of the first two casts, hit_b the
third cast's leap, hit_ground_lrg its landing), RivenMartyr = Ki Burst (OnCast the burst, stun on each stunned
unit), RivenFeint = Valor (OnCast the dash, OnBuffActivate the shield), RivenFengShuiEngine = Blade of the
Exile, RivenIzunaBlade + RivenLightsaberMissile = Wind Slash (the swing, the wave leaving, the wave hitting).
The basic attack's swing is `league_riven_attack`, which the engine plays by itself at every attack
(text-audio.md). Voice lines on the third Broken Wings cast, Ki Burst, Blade of the Exile and Wind Slash only:
the first two Q casts come every few seconds and would drown the fight.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/riven/skins/base/riven_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/riven/skins/base/riven_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_riven_sfx_attack": ("Play_sfx_Riven_RivenBasicAttack_OnCast", 984997526, 0.6, -7),
    "league_riven_sfx_attack_hit": ("Play_sfx_Riven_RivenBasicAttack_OnHit", 61999722, 0.7, -7),
    "league_riven_sfx_rune_hit": ("Play_sfx_Riven_RivenBasicAttack_OnHit", 493964780, 0.9, -5),
    "league_riven_sfx_q1": ("Play_sfx_Riven_RivenTriCleave_hit_a", 974985210, 0.5, -5),
    "league_riven_sfx_q2": ("Play_sfx_Riven_RivenTriCleave_hit_a", 807992497, 0.5, -5),
    "league_riven_sfx_q3": ("Play_sfx_Riven_RivenTriCleave_hit_b", 168033260, 1.2, -5),
    "league_riven_sfx_q3_slam": ("Play_sfx_Riven_RivenTriCleave_hit_ground_lrg", 67969504, 1.3, -4),
    "league_riven_sfx_e": ("Play_sfx_Riven_RivenFeint_OnCast", 524108470, 0.9, -6),
    "league_riven_sfx_e_shield": ("Play_sfx_Riven_RivenFeint_OnBuffActivate", 213238539, 1.0, -7),
    "league_riven_sfx_w": ("Play_sfx_Riven_RivenMartyr_OnCast", 656120570, 1.4, -4),
    "league_riven_sfx_w_stun": ("Play_sfx_Riven_RivenMartyr_stun", 68295027, 0.7, -7),
    "league_riven_sfx_r_cast": ("Play_sfx_Riven_RivenFengShuiEngine_OnCast", 416317847, 1.8, -4),
    "league_riven_sfx_r_slash": ("Play_sfx_Riven_RivenIzunaBlade_OnCast", 877386398, 1.1, -4),
    "league_riven_sfx_r_wave": ("Play_sfx_Riven_RivenLightsaberMissile_missilelaunch", 999030544, 0.8, -6),
    "league_riven_sfx_r_hit": ("Play_sfx_Riven_RivenLightsaberMissile_hit_champ", 122512945, 1.0, -5),
    "league_riven_vo_q3": ("Play_vo_Riven_Spell3DQ3Cast", 2098126575, 0.8, -2),
    "league_riven_vo_w": ("Play_vo_Riven_RivenMartyr_cast3D", 2015564017, 1.0, -2),
    "league_riven_vo_r": ("Play_vo_Riven_RivenFengShuiEngine_cast3D", 526433837, 1.8, -2),
    "league_riven_vo_r_slash": ("Play_vo_Riven_RivenIzunaBlade_cast3D", 651493721, 1.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Ki Burst rides on Valor, Wind Slash on Blade of the Exile)
    "league_riven_skill": "ASSETS/Characters/Riven/HUD/Icons2D/RivenBrokenWings.dds",
    "league_riven_skill2": "ASSETS/Characters/Riven/HUD/Icons2D/RivenPathoftheExile.dds",
    "league_riven_ult": "ASSETS/Characters/Riven/HUD/Icons2D/RivenBladeoftheExile.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Riven.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Riven.{args.lang}.wad.client"))
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
