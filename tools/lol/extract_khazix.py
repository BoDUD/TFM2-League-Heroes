r"""Pull Kha'Zix's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_khazix.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Khazix.wad.client and Khazix.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events (plain strings in the WAD's .bin files) are Play_sfx_Khazix_Khazix<spell>_<event>; the voice events
Play_vo_Khazix_<...>. The claw swing BasicAttack_OnCast / _OnHit; Unseen Threat PDamage_hit (the proc) and
PDamage_OnBuffActivate (ready); Taste Their Fear Q_OnCast, Q_hit2 (plain) and Q_hit3 (isolated, the heavier one); Leap
E_OnCast (the jump) and E_hit (the landing); Void Spike WMissile_OnMissileCast and WMissile_hit; Void Assault R_OnCast;
the evolution QEvo_OnCast; the takedown reset HuntEnemy_OnBuffActivate. Voice: Q_cast3D, E_cast3D, an
Attack2DGeneral line on R (whole) (no R cast line in the bank), and three of the shared evolution lines (*Evo_cast3D, the
short variants, whole) for the three evolutions.
Icons: Khazix_Q = skill, Khazix_E = skill2 (the combo's leap; W is in its text), Khazix_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/khazix/skins/base/khazix_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/khazix/skins/base/khazix_base_vo_"  # same in every language
P = "Play_sfx_Khazix_Khazix"
V = "Play_vo_Khazix_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_khazix_sfx_swing": (P + "BasicAttack_OnCast", 470214744, 0.5, -11),
    "league_khazix_sfx_hit": (P + "BasicAttack_OnHit", 593622341, 0.5, -11),
    "league_khazix_sfx_p_hit": (P + "PDamage_hit", 294939257, 0.8, -9),
    "league_khazix_sfx_p_ready": (P + "PDamage_OnBuffActivate", 187515165, 0.8, -12),
    "league_khazix_sfx_q_swing": (P + "Q_OnCast", 38855563, 0.6, -10),
    "league_khazix_sfx_q_hit": (P + "Q_hit2", 74110991, 0.6, -10),
    "league_khazix_sfx_q_iso_hit": (P + "Q_hit3", 177330944, 0.9, -8),
    "league_khazix_sfx_e_jump": (P + "E_OnCast", 19389465, 0.8, -9),
    "league_khazix_sfx_e_land": (P + "E_hit", 976503217, 1.0, -8),
    "league_khazix_sfx_e_reset": (P + "HuntEnemy_OnBuffActivate", 22670336, 1.0, -9),
    "league_khazix_sfx_w_throw": (P + "WMissile_OnMissileCast", 936043682, 0.8, -9),
    "league_khazix_sfx_w_hit": (P + "WMissile_hit", 364395639, 1.0, -9),
    "league_khazix_sfx_r_cast": (P + "R_OnCast", 375610459, 1.2, -9),
    "league_khazix_sfx_evo": (P + "QEvo_OnCast", 256071492, 1.2, -9),
    "league_khazix_sfx_vo_q": (V + "KhazixQ_cast3D", 693285072, 1.8, -4),
    "league_khazix_sfx_vo_e": (V + "KhazixE_cast3D", 34229015, 2.2, -4),
    "league_khazix_sfx_vo_r": (V + "Attack2DGeneral", 573309130, 4.2, -4),
    "league_khazix_sfx_vo_evo_q": (V + "KhazixQEvo_cast3D", 1201279788, 2.5, -3),
    "league_khazix_sfx_vo_evo_e": (V + "KhazixEEvo_cast3D", 652586847, 2.7, -3),
    "league_khazix_sfx_vo_evo_r": (V + "KhazixREvo_cast3D", 2049473451, 3.2, -3),
    # the Rengar easter egg: another evolution line (the W evolution's, unused by the three) for the extra evolution,
    # a laugh when he first meets Rengar
    "league_khazix_sfx_vo_evo_x": (V + "KhazixWEvo_cast3D", 1030460470, 3.5, -3),
    "league_khazix_sfx_vo_rengar": (V + "Laugh3DGeneral", 1744272967, 2.6, -4),
}
ICONS = {  # TFM2 slot -> Riot icon (the _red ones are the evolved icons)
    "league_khazix_skill": "ASSETS/Characters/KhaZix/HUD/Icons2D/Khazix_Q.dds",
    "league_khazix_skill2": "ASSETS/Characters/KhaZix/HUD/Icons2D/Khazix_E.dds",
    "league_khazix_ult": "ASSETS/Characters/KhaZix/HUD/Icons2D/Khazix_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Khazix.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Khazix.{args.lang}.wad.client"))
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
