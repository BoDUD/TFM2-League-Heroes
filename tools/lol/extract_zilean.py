"""Pull Zilean's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zilean.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Zilean.wad.client and Zilean.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

His events in the base bank (the client's own names): ZileanBasicAttack_OnMissileLaunch (the orb), ZileanQ_OnCast
(the throw), ZileanQAttachAudio_OnHit (the bomb sticks), ZileanQGround_buffactivate (3 s of ticking: the fuse),
ZileanQDetonateAudio_buffcast (the blast), ZileanQEnemyHitAudio_OnBuffCast (a unit hit), Rewind_OnCast (W),
TimeWarpSlow_OnCast / _OnBuffActivate and TimeWarp_OnCast / _OnBuffActivate (E on an enemy / an ally),
ChronoShift_OnCast / _OnBuffActivate (R: the rune), ChronoRevive_buffactivate (the rewind), ZileanP_recourse_buffactivate
(the passive's bottle). Several decode as loops (the rune, the rewind, W): only the first cycle is kept. The basic
attack's and the stun's hit events have no media; the attack's hit borrows the bomb's quiet enemy-hit tick. His spells
have no voice of their own; R borrows a line of his attack voice set (Attack2DGeneral). The icons: Zilean_Q = Q (W
rides on it), Zilean_E = E, Zilean_R = R (the passive has no slot).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zilean/skins/base/zilean_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zilean/skins/base/zilean_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_zilean_sfx_attack": ("Play_sfx_Zilean_ZileanBasicAttack_OnMissileLaunch", 522492695, 0.7, -10),
    "league_zilean_sfx_attack_hit": ("Play_sfx_Zilean_ZileanQEnemyHitAudio_OnBuffCast", 670442260, 0.4, -16),
    "league_zilean_sfx_q_cast": ("Play_sfx_Zilean_ZileanQ_OnCast", 192985377, 0.9, -7),
    "league_zilean_sfx_q_stick": ("Play_sfx_Zilean_ZileanQAttachAudio_OnHit", 1014070384, 0.7, -8),
    "league_zilean_sfx_q_tick": ("Play_sfx_Zilean_ZileanQGround_buffactivate", 614681471, 0.5, -12),
    "league_zilean_sfx_q_ground": ("Play_sfx_Zilean_ZileanQGround_buffactivate", 645192796, 3.0, -12),
    "league_zilean_sfx_q_boom": ("Play_sfx_Zilean_ZileanQDetonateAudio_buffcast", 319835156, 2.0, -6),
    "league_zilean_sfx_q_boom2": ("Play_sfx_Zilean_ZileanQDetonateAudio_buffcast", 403594497, 2.2, -4),
    "league_zilean_sfx_w_cast": ("Play_sfx_Zilean_Rewind_OnCast", 457800218, 1.3, -6),
    "league_zilean_sfx_e_cast": ("Play_sfx_Zilean_TimeWarpSlow_OnCast", 379862051, 0.9, -7),
    "league_zilean_sfx_e_slow": ("Play_sfx_Zilean_TimeWarpSlow_OnBuffActivate", 807439433, 1.5, -9),
    "league_zilean_sfx_e_haste": ("Play_sfx_Zilean_TimeWarp_OnBuffActivate", 998664628, 1.5, -9),
    "league_zilean_sfx_bottle": ("Play_sfx_Zilean_ZileanP_recourse_buffactivate", 332260138, 1.6, -8),
    "league_zilean_sfx_r_cast": ("Play_sfx_Zilean_ChronoShift_OnCast", 1051645811, 1.6, -6),
    "league_zilean_sfx_r_rune": ("Play_sfx_Zilean_ChronoShift_OnBuffActivate", 478010557, 2.5, -8),
    "league_zilean_sfx_r_rewind": ("Play_sfx_Zilean_ChronoRevive_buffactivate", 193123188, 2.2, -5),
    "league_zilean_vo_r": ("Play_vo_Zilean_Attack2DGeneral", 1868314186, 1.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_zilean_skill": "ASSETS/Characters/Zilean/HUD/Icons2D/Zilean_Q.dds",
    "league_zilean_skill2": "ASSETS/Characters/Zilean/HUD/Icons2D/Zilean_E.dds",
    "league_zilean_ult": "ASSETS/Characters/Zilean/HUD/Icons2D/Zilean_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zilean.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zilean.{args.lang}.wad.client"))
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
