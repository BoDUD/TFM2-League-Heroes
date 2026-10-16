r"""Pull Orianna's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_orianna.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_pantheon.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Orianna.wad.client and Orianna.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in skin0.bin): the bolt OriannaBasicAttack_OnMissileLaunch (the hit has no sound of its own: a quiet
copy of the Ball's hit); the Ball's flash OriannaBallFlash_buffactivate (it leaves her for Q, reaches an ally for E);
Command: Attack's landing OriannaIzuna_buffdeactivate and hit OriannaIzuna_hit; Dissonance
OriannaDissonanceCommand_buffactivate; Shockwave OriannaDetonateCommand_buffactivate, its hit a loud
OriannaDissonanceCommand_hit. Voice: OrianaIzunaCommand_cast3D, OrianaDissonanceCommand_cast3D,
OrianaRedactCommand_cast3D, OrianaDetonateCommand_cast3D.
Icons: OriannaQ (Command: Attack) = skill, OriannaE (Command: Protect) = skill2, OriannaR = ult; W (Dissonance, told in
skill's text) and the passive are written too (league_orianna_w / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/orianna/skins/base/orianna_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/orianna/skins/base/orianna_base_vo_"  # same in every language
P = "Play_sfx_Orianna_Orianna"
V = "Play_vo_Orianna_Oriana"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_orianna_sfx_a_shot": (P + "BasicAttack_OnMissileLaunch", 177148774, 0.6, -15),
    "league_orianna_sfx_a_hit": (P + "Izuna_hit", 450485132, 0.5, -18),
    "league_orianna_sfx_q": (P + "BallFlash_buffactivate", 495431216, 0.6, -13),
    "league_orianna_sfx_q_land": (P + "Izuna_buffdeactivate", 324184509, 0.8, -12),
    "league_orianna_sfx_q_hit": (P + "Izuna_hit", 580182307, 0.6, -12),
    "league_orianna_sfx_w": (P + "DissonanceCommand_buffactivate", 206112779, 1.6, -10),
    "league_orianna_sfx_e": (P + "BallFlash_buffactivate", 638901323, 0.6, -12),
    "league_orianna_sfx_e_shield": (P + "BallFlash_buffactivate", 369648006, 0.6, -14),
    "league_orianna_sfx_r": (P + "DetonateCommand_buffactivate", 1036935980, 1.6, -9),
    "league_orianna_sfx_r_hit": (P + "DissonanceCommand_hit", 969388321, 0.8, -11),
    "league_orianna_sfx_vo_q": (V + "IzunaCommand_cast3D", 3424654660, 1.6, -6),
    "league_orianna_sfx_vo_w": (V + "DissonanceCommand_cast3D", 992317345, 1.6, -6),
    "league_orianna_sfx_vo_e": (V + "RedactCommand_cast3D", 119979127, 1.6, -6),
    "league_orianna_sfx_vo_r": (V + "DetonateCommand_cast3D", 2084648638, 1.6, -6),
}
I = "ASSETS/Characters/Orianna/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_orianna_skill": I + "OriannaQ.dds",
    "league_orianna_skill2": I + "OriannaE.dds",
    "league_orianna_ult": I + "OriannaR.dds",
    "league_orianna_w": I + "OriannaW.dds",
    "league_orianna_passive": I + "OriannaPassive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Orianna.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Orianna.{args.lang}.wad.client"))
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
