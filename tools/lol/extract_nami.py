"""Pull Nami's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_nami.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Nami.wad.client and Nami.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her spells in the base bins: NamiQ = Aqua Prison (NamiQMissile_OnMissileCast the bubble thrown, NamiQ_hit
its landing, NamiQDebuff_OnBuffActivate the prison closing round a champion), NamiW = Ebb and Flow (W_OnCast,
NamiW_hit on an enemy, NamiWMissileAlly_hit on an ally healed), NamiE = Tidecaller's Blessing
(NamiE_OnBuffActivate on the blessed ally), NamiR = Tidal Wave (R_OnCast, R_missilelaunch the wave rolling,
NamiRMissile_hit a unit it knocks up). The basic attack's cast sound is `league_nami_attack`, which the
engine plays by itself at every attack (text-audio.md). Only Q and R have spell voice lines in the zh_CN
bank (W and E have none).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/nami/skins/base/nami_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/nami/skins/base/nami_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_nami_sfx_attack": ("Play_sfx_Nami_NamiBasicAttack_OnCast", 141374775, 0.7, -7),
    "league_nami_sfx_attack_hit": ("Play_sfx_Nami_NamiBasicAttack_OnHit", 96778279, 0.9, -7),
    "league_nami_sfx_w_cast": ("Play_sfx_Nami_NamiW_OnCast", 886479237, 1.3, -5),
    "league_nami_sfx_w_hit": ("Play_sfx_Nami_NamiW_hit", 985653567, 1.2, -5),
    "league_nami_sfx_w_heal": ("Play_sfx_Nami_NamiWMissileAlly_hit", 360119738, 1.4, -5),
    "league_nami_sfx_e_bless": ("Play_sfx_Nami_NamiE_OnBuffActivate", 120872265, 1.2, -8),
    "league_nami_sfx_q_cast": ("Play_sfx_Nami_NamiQMissile_OnMissileCast", 288797303, 1.0, -5),
    "league_nami_sfx_q_hit": ("Play_sfx_Nami_NamiQ_hit", 281172758, 0.9, -5),
    "league_nami_sfx_q_trap": ("Play_sfx_Nami_NamiQDebuff_OnBuffActivate", 1509815, 1.3, -5),
    "league_nami_sfx_r_cast": ("Play_sfx_Nami_NamiR_OnCast", 86594569, 2.0, -4),
    "league_nami_sfx_r_wave": ("Play_sfx_Nami_NamiR_missilelaunch", 105304883, 2.2, -6),
    "league_nami_sfx_r_hit": ("Play_sfx_Nami_NamiRMissile_hit", 163591658, 1.5, -5),
    "league_nami_vo_q": ("Play_vo_Nami_NamiQ_cast3D", 544366090, 0.6, -2),
    "league_nami_vo_r": ("Play_vo_Nami_NamiR_cast3D", 1409133544, 1.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Tidecaller's Blessing rides on Ebb and Flow, Surging Tides on every spell)
    "league_nami_skill": "ASSETS/Characters/Nami/HUD/Icons2D/NamiW.dds",
    "league_nami_skill2": "ASSETS/Characters/Nami/HUD/Icons2D/NamiQ.dds",
    "league_nami_ult": "ASSETS/Characters/Nami/HUD/Icons2D/NamiR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Nami.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Nami.{args.lang}.wad.client"))
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
