r"""Pull Lillia's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_lillia.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Lillia.wad.client and Lillia.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events are Play_sfx_Lillia_Lillia<spell>_<event> (the passive's is spelled Play_sfx_Lilla_LilliaP_*, unused: silent);
the voice events Play_vo_Lillia_Lillia<key>_cast3D. The branch swing BasicAttack1_OnCast / _OnHit; Blooming Blows
Q_OnCast, Q_Inner_hit and Q_Outer_hit (the true-damage edge); Watch Out! Eep! W_OnCast, W_Inner_hit (the sweet spot) and
W_Outer_hit; Swirlseed E_OnCast and ERollingMissile_hit (its launch event is a 20 s rolling loop: not used); Lilting
Lullaby R_OnCast, R_Drowsey_buffactivate, RSleep_OnBuffActivate and RSleep_OnBuffDeactivate (the wake).
Voice clips are league_lillia_sfx_vo_* (never the sound's own name).
Icons: Lillia_Icon_Q = skill, Lillia_Icon_E = skill2 (E->W; W is in its text), Lillia_Icon_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/lillia/skins/base/lillia_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/lillia/skins/base/lillia_base_vo_"  # same in every language
P = "Play_sfx_Lillia_Lillia"
V = "Play_vo_Lillia_Lillia"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_lillia_sfx_swing": (P + "BasicAttack1_OnCast", 713028939, 0.5, -12),
    "league_lillia_sfx_hit": (P + "BasicAttack1_OnHit", 75595394, 0.5, -12),
    "league_lillia_sfx_q_cast": (P + "Q_OnCast", 535728457, 1.0, -10),
    "league_lillia_sfx_q_hit": (P + "Q_Inner_hit", 332032202, 0.8, -12),
    "league_lillia_sfx_q_edge": (P + "Q_Outer_hit", 787272199, 0.9, -10),
    "league_lillia_sfx_w_cast": (P + "W_OnCast", 1047728350, 0.9, -10),
    "league_lillia_sfx_w_sweet": (P + "W_Inner_hit", 156575393, 1.1, -8),
    "league_lillia_sfx_w_hit": (P + "W_Outer_hit", 940878488, 0.7, -10),
    "league_lillia_sfx_e_cast": (P + "E_OnCast", 161088696, 0.6, -10),
    "league_lillia_sfx_e_hit": (P + "ERollingMissile_hit", 178111461, 0.7, -10),
    "league_lillia_sfx_r_cast": (P + "R_OnCast", 408991955, 1.3, -8),
    "league_lillia_sfx_drowsy": (P + "R_Drowsey_buffactivate", 100278932, 1.4, -11),
    "league_lillia_sfx_sleep": (P + "RSleep_OnBuffActivate", 641247992, 1.0, -11),
    "league_lillia_sfx_wake": (P + "RSleep_OnBuffDeactivate", 428463978, 0.5, -10),
    "league_lillia_sfx_vo_q": (V + "Q_cast3D", 753980793, 2.0, -4),
    "league_lillia_sfx_vo_w": (V + "W_cast3D", 1054100831, 2.0, -4),
    "league_lillia_sfx_vo_e": (V + "E_cast3D", 829217580, 2.0, -4),
    "league_lillia_sfx_vo_r": (V + "R_cast3D", 967564636, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_lillia_skill": "ASSETS/Characters/Lillia/HUD/Icons2D/Lillia_Icon_Q.dds",
    "league_lillia_skill2": "ASSETS/Characters/Lillia/HUD/Icons2D/Lillia_Icon_E.dds",
    "league_lillia_ult": "ASSETS/Characters/Lillia/HUD/Icons2D/Lillia_Icon_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Lillia.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Lillia.{args.lang}.wad.client"))
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
