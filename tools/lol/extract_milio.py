r"""Pull Milio's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_milio.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_malzahar.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Milio.wad.client and Milio.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in skin0.bin, listed with %TEMP%/mi_work/sndprobe.py; one clear variant of each): the fireball
MilioBasicAttack_OnMissileLaunch / _OnHit; Ultra Mega Fire Kick's MilioQ_OnMissileLaunch (the kick), MilioQ1_hit_enemy
(the ball strikes and bounces up) and MilioQ2_hit (the fall); Warm Hugs' MilioE_buffactivate (the shield on the ally);
Cozy Campfire's MilioW_buffactivate (the fire lit on the ally) and MilioW_aoe_pulse_buffactivate (each heal pulse);
Breath of Life's MilioR_OnCast and MilioR_hit (on every ally it reaches); Fired Up!'s MilioP_hit (an ally enchanted).
Voice: MilioQ_cast3D, MilioE_cast3D, MilioW_cast3D, MilioR_cast3D. Clip names differ from the sound names
(league_milio_sfx_*, memory vo-clip-names).
Icons: Milio_Q = skill, Milio_E = skill2 (E + W), Milio_R = ult; W and the passive are written too (README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/milio/skins/base/milio_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/milio/skins/base/milio_base_vo_"  # same in every language
P = "Play_sfx_Milio_Milio"
V = "Play_vo_Milio_Milio"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_milio_sfx_a_cast": (P + "BasicAttack_OnMissileLaunch", 719361471, 0.6, -13),
    "league_milio_sfx_a_hit": (P + "BasicAttack_OnHit", 455474186, 0.5, -13),
    "league_milio_sfx_q_kick": (P + "Q_OnMissileLaunch", 768826923, 0.8, -10),
    "league_milio_sfx_q_hit": (P + "Q1_hit_enemy", 334145462, 0.8, -11),
    "league_milio_sfx_q_land": (P + "Q2_hit", 261848921, 1.2, -10),
    "league_milio_sfx_e_hug": (P + "E_buffactivate", 983184582, 1.2, -11),
    "league_milio_sfx_w_fire": (P + "W_buffactivate", 885831236, 1.3, -11),
    "league_milio_sfx_w_pulse": (P + "W_aoe_pulse_buffactivate", 737901549, 0.8, -15),
    "league_milio_sfx_r_cast": (P + "R_OnCast", 337987798, 1.6, -9),
    "league_milio_sfx_r_hit": (P + "R_hit", 825394502, 1.0, -14),
    "league_milio_sfx_p_fired": (P + "P_hit", 709572831, 0.7, -16),
    "league_milio_sfx_vo_q": (V + "Q_cast3D", 1342501141, 1.6, -6),
    "league_milio_sfx_vo_e": (V + "E_cast3D", 1161342453, 1.4, -6),
    "league_milio_sfx_vo_w": (V + "W_cast3D", 122933223, 1.6, -6),
    "league_milio_sfx_vo_r": (V + "R_cast3D", 333135970, 1.8, -6),
}
I = "ASSETS/Characters/Milio/HUD/Icons2D/Milio_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_milio_skill": I + "Q.dds",
    "league_milio_skill2": I + "E.dds",
    "league_milio_ult": I + "R.dds",
    "league_milio_w": I + "W.dds",
    "league_milio_passive": I + "P.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Milio.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Milio.{args.lang}.wad.client"))
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
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
