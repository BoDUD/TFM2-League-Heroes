"""Pull Amumu's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_amumu.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Amumu.wad.client and Amumu.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

The champion bins name every event used here except Play_sfx_Amumu_Tantrum_hit and
Play_sfx_Amumu_CurseoftheSadMummy_hit (found by hashing candidate names against the event ids of
the sfx bank). Amumu speaks only a few lines: Bandage Toss has its own cast line, the other
abilities have none, so the ult borrows one of his general attack lines (Attack2DGeneral).
Despair's crying comes from its buff-activate event (the 5 s variant; the 17 s one is the loop bed).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/amumu/skins/base/amumu_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/amumu/skins/base/amumu_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_amumu_sfx_attack_hit": ("Play_sfx_Amumu_AmumuBasicAttack_OnHit", 96030891, 0.6, -4),
    "league_amumu_sfx_q_cast": ("Play_sfx_Amumu_BandageToss_OnCast", 762508972, 0.7, -4),
    "league_amumu_sfx_q_throw": ("Play_sfx_Amumu_BandageToss_missilelaunch", 169957955, 0.9, -5),
    "league_amumu_sfx_q_hit": ("Play_sfx_Amumu_BandageToss_hit", 760786146, 1.2, -3),
    "league_amumu_sfx_w": ("Play_sfx_Amumu_AuraofDespair_OnBuffActivate", 374969195, 2.5, -6),
    "league_amumu_sfx_e": ("Play_sfx_Amumu_Tantrum_OnCast", 1005599266, 1.6, -3),
    "league_amumu_sfx_e_hit": ("Play_sfx_Amumu_Tantrum_hit", 1020662474, 0.8, -6),
    "league_amumu_sfx_r_cast": ("Play_sfx_Amumu_CurseoftheSadMummy_OnCast", 137511031, 0.6, -3),
    "league_amumu_sfx_r_hit": ("Play_sfx_Amumu_CurseoftheSadMummy_hit", 956399926, 1.6, -3),
    "league_amumu_vo_q": ("Play_vo_Amumu_BandageToss_cast3D", 1994428286, 0.6, -2),
    "league_amumu_vo_r": ("Play_vo_Amumu_Attack2DGeneral", 1997515801, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Cursed Touch and Despair ride on the basic attack, so they have no slot)
    "league_amumu_skill": "ASSETS/Characters/Amumu/HUD/Icons2D/Amumu_Q.dds",
    "league_amumu_skill2": "ASSETS/Characters/Amumu/HUD/Icons2D/Amumu_E.dds",
    "league_amumu_ult": "ASSETS/Characters/Amumu/HUD/Icons2D/Amumu_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Amumu.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Amumu.{args.lang}.wad.client"))
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
