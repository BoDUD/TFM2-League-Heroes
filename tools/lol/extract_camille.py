"""Pull Camille's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_camille.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Camille.wad.client and Camille.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events in the base bank: CamilleBasicAttack_OnCast / _OnHit (the kick), CamilleQ_OnCast and CamilleQAttack_OnHit
(Precision Protocol), CamilleQAttackEmpowered_OnCast (the charged second kick), CamillePassiveShieldPhysical_buffcast
(Adaptive Defenses), CamilleWConeSlashCharge_OnBuffCast / CamilleWConeSlash_outer_hit (Tactical Sweep's wind-up and
slash), CamilleEDash1_CableLatch_buffcast / _OnBuffActivate (the hook latching, the pull), CamilleEDash2_OnBuffCast /
CamilleEKnockBack2_OnBuffCast (the dive, the landing), CamilleR_cast / CamilleRMoveAway_OnBuffActivate /
CamilleRTether_hit (the leap, the field's knock-away, an enemy hitting its wall); voice: Spell3DE1Cast (the hook) and
CamilleR_cast3D (the ult). The icons: Camille_W = Tactical Sweep, Camille_E = Hookshot, Camille_R = The Hextech
Ultimatum (Precision Protocol and Adaptive Defenses ride on the attack, which has no icon).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/camille/skins/base/camille_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/camille/skins/base/camille_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_camille_sfx_attack": ("Play_sfx_Camille_CamilleBasicAttack_OnCast", 174652782, 0.35, -10),
    "league_camille_sfx_attack_hit": ("Play_sfx_Camille_CamilleBasicAttack_OnHit", 46887588, 0.5, -9),
    "league_camille_sfx_q_cast": ("Play_sfx_Camille_CamilleQ_OnCast", 895982467, 0.8, -7),
    "league_camille_sfx_q_hit": ("Play_sfx_Camille_CamilleQAttack_OnHit", 31842945, 0.6, -7),
    "league_camille_sfx_q2_cast": ("Play_sfx_Camille_CamilleQAttackEmpowered_OnCast", 313527947, 0.8, -6),
    "league_camille_sfx_q2_hit": ("Play_sfx_Camille_CamilleQAttack_OnHit", 12215918, 0.7, -5),
    "league_camille_sfx_p_shield": ("Play_sfx_Camille_CamillePassiveShieldPhysical_buffcast", 580715846, 1.0, -7),
    "league_camille_sfx_w_cast": ("Play_sfx_Camille_CamilleWConeSlashCharge_OnBuffCast", 480503851, 0.9, -7),
    "league_camille_sfx_w_sweep": ("Play_sfx_Camille_CamilleWConeSlash_outer_hit", 755924213, 0.9, -6),
    "league_camille_sfx_e_cast": ("Play_sfx_Camille_CamilleEDash1_CableLatch_buffcast", 767971437, 0.6, -7),
    "league_camille_sfx_e_pull": ("Play_sfx_Camille_CamilleEDash1_OnBuffActivate", 1004113704, 0.8, -7),
    "league_camille_sfx_e_dash": ("Play_sfx_Camille_CamilleEDash2_OnBuffCast", 251410793, 0.6, -7),
    "league_camille_sfx_e_land": ("Play_sfx_Camille_CamilleEKnockBack2_OnBuffCast", 12215918, 0.8, -5),
    "league_camille_sfx_r_cast": ("Play_sfx_Camille_CamilleR_cast", 301155100, 1.5, -6),
    "league_camille_sfx_r_land": ("Play_sfx_Camille_CamilleRMoveAway_OnBuffActivate", 688195706, 1.2, -5),
    "league_camille_sfx_r_wall": ("Play_sfx_Camille_CamilleRTether_hit", 881661743, 0.6, -8),
    "league_camille_vo_e": ("Play_vo_Camille_Spell3DE1Cast", 1061321456, 2.0, -2),
    "league_camille_vo_r": ("Play_vo_Camille_CamilleR_cast3D", 178021743, 2.5, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_camille_skill": "ASSETS/Characters/Camille/HUD/Icons2D/Camille_W.dds",
    "league_camille_skill2": "ASSETS/Characters/Camille/HUD/Icons2D/Camille_E.dds",
    "league_camille_ult": "ASSETS/Characters/Camille/HUD/Icons2D/Camille_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Camille.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Camille.{args.lang}.wad.client"))
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
