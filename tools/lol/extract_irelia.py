r"""Pull Irelia's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_irelia.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_zeri.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Irelia.wad.client and Irelia.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

Her events are Play_sfx_Irelia_Irelia<spell>_<event> (found by scanning her wad for Play_ strings). Basic attack
IreliaBasicAttack_OnCast / _OnHit; Ionian Fervor full IreliaP_Max_OnBuffActivate; Bladesurge IreliaQ_OnCast, IreliaQ_hit
(the reset plays the same pool: another variant); Defiant Dance IreliaW_OnCast (the charge), IreliaWDefence_block_self,
IreliaW2_OnCast (the slash), IreliaW2_hit; Flawless Duet IreliaEMissile_OnMissileCast (a blade thrown),
IreliaE_missile_stop (it lands), IreliaESecondary_hit (the stun line); Vanguard's Edge IreliaR_OnCast,
IreliaR_onmissilelaunch, IreliaR_OnHit_champ (the burst), IreliaR2_hit (the wall cuts). Voice clips are
league_irelia_sfx_vo_* (never the sound's own name): Q, W, E and R.
Icons: Irelia_Q = skill (Q), Irelia_E = skill2 (E, W folded in), Irelia_R = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/irelia/skins/base/irelia_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/irelia/skins/base/irelia_base_vo_"  # same in every language
P = "Play_sfx_Irelia_Irelia"
V = "Play_vo_Irelia_Irelia"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_irelia_sfx_swing": (P + "BasicAttack_OnCast", 225765765, 0.4, -12),
    "league_irelia_sfx_hit": (P + "BasicAttack_OnHit", 71835836, 0.5, -12),
    "league_irelia_sfx_p_max": (P + "P_Max_OnBuffActivate", 203238813, 1.0, -11),
    "league_irelia_sfx_q_cast": (P + "Q_OnCast", 762458575, 0.7, -10),
    "league_irelia_sfx_q_hit": (P + "Q_hit", 481404348, 0.6, -10),
    "league_irelia_sfx_q_reset": (P + "Q_Hit_reset", 919110971, 0.6, -9),
    "league_irelia_sfx_w_cast": (P + "W_OnCast", 228710834, 1.6, -11),
    "league_irelia_sfx_w_block": (P + "WDefence_block_self", 738454969, 0.7, -12),
    "league_irelia_sfx_w_slash": (P + "W2_OnCast", 311921195, 0.9, -9),
    "league_irelia_sfx_w_hit": (P + "W2_hit", 1014456617, 0.8, -10),
    "league_irelia_sfx_e_cast": (P + "EMissile_OnMissileCast", 890463546, 0.7, -10),
    "league_irelia_sfx_e_stop": (P + "E_missile_stop", 121364514, 0.8, -10),
    "league_irelia_sfx_e_hit": (P + "ESecondary_hit", 429895068, 1.0, -9),
    "league_irelia_sfx_r_cast": (P + "R_OnCast", 159724666, 0.5, -10),
    "league_irelia_sfx_r_launch": (P + "R_onmissilelaunch", 719807401, 0.9, -9),
    "league_irelia_sfx_r_hit": (P + "R_OnHit_champ", 836368324, 2.2, -8),
    "league_irelia_sfx_r_wall": (P + "R2_hit", 837463383, 0.6, -11),
    "league_irelia_sfx_vo_q": (V + "Q_cast3D", 1455465911, 1.5, -4),
    "league_irelia_sfx_vo_w": (V + "W_cast3D", 1004312394, 2.0, -4),
    "league_irelia_sfx_vo_e": (V + "E_cast3D", 1441215317, 1.5, -4),
    "league_irelia_sfx_vo_r": (V + "R_cast3D", 60633847, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_irelia_skill": "ASSETS/Characters/Irelia/HUD/Icons2D/Irelia_Q.dds",
    "league_irelia_skill2": "ASSETS/Characters/Irelia/HUD/Icons2D/Irelia_E.dds",
    "league_irelia_ult": "ASSETS/Characters/Irelia/HUD/Icons2D/Irelia_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Irelia.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Irelia.{args.lang}.wad.client"))
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
