"""Pull Blitzcrank's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_blitzcrank.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Blitzcrank.wad.client and Blitzcrank.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Blitzcrank's skin bins. The basic attack has its swing and its hit; Rocket Grab (Q) the cast,
the hand leaving and its hit; Overdrive (W) the cast; Power Fist (E) the wind-up and its hit; Static Field (R) the
discharge round him and the lightning hit (also the passive's bolt after an attack); Mana Barrier its shield. The base
skin has no ability voice lines (only move, attack, joke, taunt, laugh and death), so W and R take two of his
general lines (zh_CN): a short move line on Overdrive and an attack line on Static Field.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/blitzcrank/skins/base/blitzcrank_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/blitzcrank/skins/base/blitzcrank_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_blitzcrank_sfx_attack_swing": ("Play_sfx_Blitzcrank_BlitzcrankBasicAttack_OnCast", 638514227, 0.6, -8),
    "league_blitzcrank_sfx_attack_hit": ("Play_sfx_Blitzcrank_BlitzcrankBasicAttack_OnHit", 378438823, 0.6, -7),
    "league_blitzcrank_sfx_q_cast": ("Play_sfx_Blitzcrank_RocketGrab_OnCast", 399029776, 0.5, -6),
    "league_blitzcrank_sfx_q_launch": ("Play_sfx_Blitzcrank_RocketGrabMissile_OnMissileLaunch", 803376522, 1.0, -6),
    "league_blitzcrank_sfx_q_hit": ("Play_sfx_Blitzcrank_RocketGrabMissile_OnHit", 255492812, 0.7, -4),
    "league_blitzcrank_sfx_w_cast": ("Play_sfx_Blitzcrank_Overdrive_OnCast", 491938012, 1.6, -5),
    "league_blitzcrank_sfx_e_cast": ("Play_sfx_Blitzcrank_PowerFist_OnCast", 790371558, 1.0, -6),
    "league_blitzcrank_sfx_e_hit": ("Play_sfx_Blitzcrank_PowerFist_hit", 760940080, 1.3, -4),
    "league_blitzcrank_sfx_r_burst": ("Play_sfx_Blitzcrank_StaticField_OnCast", 699527213, 1.6, -4),
    "league_blitzcrank_sfx_bolt": ("Play_sfx_Blitzcrank_StaticField_hit", 1020508970, 0.7, -7),
    "league_blitzcrank_sfx_mb_on": ("Play_sfx_Blitzcrank_ManaBarrier_OnBuffActivate", 333084087, 1.9, -6),
    "league_blitzcrank_vo_w": ("Play_vo_Blitzcrank_Move2DStandard", 1705931446, 0.9, -3),
    "league_blitzcrank_vo_r": ("Play_vo_Blitzcrank_Attack2DGeneral", 364065329, 3.1, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_blitzcrank_skill": "ASSETS/Characters/Blitzcrank/HUD/Icons2D/BlitzcrankQ.dds",
    "league_blitzcrank_skill2": "ASSETS/Characters/Blitzcrank/HUD/Icons2D/BlitzcrankE.dds",
    "league_blitzcrank_ult": "ASSETS/Characters/Blitzcrank/HUD/Icons2D/BlitzcrankR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Blitzcrank.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Blitzcrank.{args.lang}.wad.client"))
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
