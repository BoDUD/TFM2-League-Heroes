"""Pull Caitlyn's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_caitlyn.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Caitlyn.wad.client and Caitlyn.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her events in the base bank: CaitlynBasicAttack_OnMissileLaunch (the rifle shot; its OnHit events have no media, so
the hit is the lighter impact of Piltover Peacemaker's later targets, CaitlynQ2_OnHit), CaitlynPassiveMissile_
OnMissileLaunch (the Headshot), CaitlynQ_OnCast / _OnMissileLaunch / _OnHit, CaitlynW_OnCast (the throw),
CaitlynW_buffactivate (the trap set down), CaitlynWSnare_OnBuffActivate (the snap), CaitlynEMissile_decal_
buffactivate (the net spreading; the net's own launch events are empty) / CaitlynEMissile_hit, CaitlynR_OnCast (the
aim), CaitlynRMissile_OnMissileLaunch / _hit. Voice: Q, W, E and R casts, the snap and R's hit. Headshots have a
voice line too, left out: every sixth shot would talk.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/caitlyn/skins/base/caitlyn_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/caitlyn/skins/base/caitlyn_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_caitlyn_sfx_attack_shot": ("Play_sfx_Caitlyn_CaitlynBasicAttack_OnMissileLaunch", 123669469, 0.4, -8),
    "league_caitlyn_sfx_attack_hit": ("Play_sfx_Caitlyn_CaitlynQ2_OnHit", 279515651, 0.35, -11),
    "league_caitlyn_sfx_hs_shot": ("Play_sfx_Caitlyn_CaitlynPassiveMissile_OnMissileLaunch", 887934776, 0.6, -5),
    "league_caitlyn_sfx_hs_hit": ("Play_sfx_Caitlyn_CaitlynQ_OnHit", 341738509, 0.6, -7),
    "league_caitlyn_sfx_q_cast": ("Play_sfx_Caitlyn_CaitlynQ_OnCast", 482037386, 0.6, -7),
    "league_caitlyn_sfx_q_fire": ("Play_sfx_Caitlyn_CaitlynQ_OnMissileLaunch", 749951350, 0.7, -5),
    "league_caitlyn_sfx_q_hit": ("Play_sfx_Caitlyn_CaitlynQ_OnHit", 547173913, 0.8, -6),
    "league_caitlyn_sfx_w_cast": ("Play_sfx_Caitlyn_CaitlynW_OnCast", 177088163, 0.4, -7),
    "league_caitlyn_sfx_w_land": ("Play_sfx_Caitlyn_CaitlynW_buffactivate", 507194553, 1.2, -9),
    "league_caitlyn_sfx_w_snap": ("Play_sfx_Caitlyn_CaitlynWSnare_OnBuffActivate", 520199680, 1.2, -4),
    "league_caitlyn_sfx_e_cast": ("Play_sfx_Caitlyn_CaitlynEMissile_decal_buffactivate", 56624172, 0.9, -6),
    "league_caitlyn_sfx_e_hit": ("Play_sfx_Caitlyn_CaitlynEMissile_hit", 408477749, 1.0, -5),
    "league_caitlyn_sfx_r_cast": ("Play_sfx_Caitlyn_CaitlynR_OnCast", 609887489, 1.3, -6),
    "league_caitlyn_sfx_r_fire": ("Play_sfx_Caitlyn_CaitlynRMissile_OnMissileLaunch", 918606956, 1.1, -4),
    "league_caitlyn_sfx_r_hit": ("Play_sfx_Caitlyn_CaitlynRMissile_hit", 546167979, 1.2, -3),
    "league_caitlyn_vo_q": ("Play_vo_Caitlyn_CaitlynQ_cast3D", 932136392, 1.3, -2),
    "league_caitlyn_vo_w": ("Play_vo_Caitlyn_CaitlynW_cast3D", 476008388, 0.6, -2),
    "league_caitlyn_vo_snap": ("Play_vo_Caitlyn_CaitlynWSnare_hit3D", 548281555, 0.9, -2),
    "league_caitlyn_vo_e": ("Play_vo_Caitlyn_CaitlynE_cast3D", 986500927, 0.9, -2),
    "league_caitlyn_vo_r": ("Play_vo_Caitlyn_CaitlynR_cast3D", 1971660598, 1.3, -2),
    "league_caitlyn_vo_r_hit": ("Play_vo_Caitlyn_CaitlynRMissile_hit3D", 1244615267, 1.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Headshot and the net ride on the attack)
    "league_caitlyn_skill": "ASSETS/Characters/Caitlyn/HUD/Icons2D/CaitlynQ.dds",
    "league_caitlyn_skill2": "ASSETS/Characters/Caitlyn/HUD/Icons2D/CaitlynW.dds",
    "league_caitlyn_ult": "ASSETS/Characters/Caitlyn/HUD/Icons2D/CaitlynR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Caitlyn.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Caitlyn.{args.lang}.wad.client"))
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
            print(f"{name:34s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:34s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
