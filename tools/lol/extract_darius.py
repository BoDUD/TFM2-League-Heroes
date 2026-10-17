"""Pull Darius's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_darius.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Darius.wad.client and Darius.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

The champion bins name some events with a trailing character (DariusAxeGrabCone_OnHit2,
DariusHemoMax_OnBuffActivate5, DariusNoxianTacticsONH_cast3D2); the banks hold them without it.
Darius has no voice line for Apprehend, so skill2 (Apprehend + Crippling Strike) uses his
Crippling Strike cast line; Noxian Might uses his max-Hemorrhage line (Spell3DPMax).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/darius/skins/base/darius_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/darius/skins/base/darius_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_darius_sfx_attack_hit": ("Play_sfx_Darius_DariusBasicAttack_OnHit", 141715137, 0.8, -4),
    "league_darius_sfx_q_cast": ("Play_sfx_Darius_DariusCleave_OnCast", 997531811, 1.0, -4),
    "league_darius_sfx_q_spin": ("Play_sfx_Darius_DariusQCast_OnBuffDeactivate", 450092659, 1.0, -3),
    "league_darius_sfx_q_hit": ("Play_sfx_Darius_DariusCleave_hit_outter", 386105878, 1.0, -5),
    "league_darius_sfx_w_cast": ("Play_sfx_Darius_DariusNoxianTacticsONH_OnCast", 742668008, 0.9, -5),
    "league_darius_sfx_w_hit": ("Play_sfx_Darius_DariusNoxianTacticsONHAttack_OnHit", 30889466, 1.0, -3),
    "league_darius_sfx_e_cast": ("Play_sfx_Darius_DariusAxeGrabCone_OnCast", 998086056, 1.2, -3),
    "league_darius_sfx_e_hit": ("Play_sfx_Darius_DariusAxeGrabCone_OnHit", 545883039, 1.0, -6),
    "league_darius_sfx_r_cast": ("Play_sfx_Darius_DariusExecute_OnCast", 667872367, 1.0, -3),
    "league_darius_sfx_r_hit": ("Play_sfx_Darius_DariusExecute_OnHit", 464271686, 1.8, -2),
    "league_darius_sfx_might": ("Play_sfx_Darius_DariusHemoMax_OnBuffActivate", 182943585, 1.6, -4),
    "league_darius_vo_q": ("Play_vo_Darius_DariusCleave_cast3D", 541387022, 1.2, -2),
    "league_darius_vo_e": ("Play_vo_Darius_DariusNoxianTacticsONH_cast3D", 1157202123, 2.0, -2),
    "league_darius_vo_r": ("Play_vo_Darius_DariusExecute_cast3D", 1136790169, 2.0, -2),
    "league_darius_vo_might": ("Play_vo_Darius_Spell3DPMax", 128340887, 2.5, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Crippling Strike rides on Apprehend)
    "league_darius_skill": "ASSETS/Characters/Darius/HUD/Icons2D/Darius_Icon_Decimate.dds",
    "league_darius_skill2": "ASSETS/Characters/Darius/HUD/Icons2D/Darius_Icon_Axe_Grab.dds",
    "league_darius_ult": "ASSETS/Characters/Darius/HUD/Icons2D/Darius_Icon_Sudden_Death.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Darius.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Darius.{args.lang}.wad.client"))
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
