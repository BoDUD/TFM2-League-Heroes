r"""Pull Renekton's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_renekton.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Renekton.wad.client and Renekton.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events (plain strings in the WAD's .bin files) are Play_sfx_Renekton_Renekton<spell>_<event>; the voice events
Play_vo_Renekton_Renekton<spell>_cast3D. The blade RenektonBasicAttack_OnCast / _OnHit; Cull the Meek RenektonCleave_
OnCast / _OnHit; Ruthless Predator RenektonExecute_OnCast (the double strike), RenektonSuperExecute_OnCast / _OnHit (the
empowered triple strike and its stun); Slice and Dice RenektonDice_OnCast (the dash: Slice has no cast event of its own)
and RenektonSliceAndDice_hit; Dominus RenektonReignOfTheTyrant_OnCast and _OnBuffActivate (the transformation's roar).
Icons: Renekton_Q = skill, Renekton_E = skill2 (the dash leads the E -> W combo; W is in its text), Renekton_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/renekton/skins/base/renekton_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/renekton/skins/base/renekton_base_vo_"  # same in every language
P = "Play_sfx_Renekton_Renekton"
V = "Play_vo_Renekton_Renekton"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_renekton_sfx_swing": (P + "BasicAttack_OnCast", 923626494, 0.5, -12),
    "league_renekton_sfx_hit": (P + "BasicAttack_OnHit", 1055400816, 0.5, -12),
    "league_renekton_sfx_q_cast": (P + "Cleave_OnCast", 825888534, 1.0, -9),
    "league_renekton_sfx_q_hit": (P + "Cleave_OnHit", 288916571, 0.5, -11),
    "league_renekton_sfx_w_cast": (P + "Execute_OnCast", 389450241, 1.0, -10),
    "league_renekton_sfx_w_super": (P + "SuperExecute_OnCast", 58855230, 1.2, -9),
    "league_renekton_sfx_w_hit": (P + "SuperExecute_OnHit", 864443351, 0.6, -10),
    "league_renekton_sfx_e_dash": (P + "Dice_OnCast", 692791419, 0.8, -10),
    "league_renekton_sfx_e_hit": (P + "SliceAndDice_hit", 67288056, 0.8, -10),
    "league_renekton_sfx_r_cast": (P + "ReignOfTheTyrant_OnCast", 382611479, 1.5, -8),
    "league_renekton_sfx_r_roar": (P + "ReignOfTheTyrant_OnBuffActivate", 518252082, 2.5, -8),
    "league_renekton_sfx_vo_q": (V + "Cleave_cast3D", 1871613460, 2.0, -4),
    "league_renekton_sfx_vo_w": (V + "SuperExecute_cast3D", 215581971, 2.0, -4),
    "league_renekton_sfx_vo_e": (V + "SliceAndDice_cast3D", 1358477758, 2.0, -4),
    "league_renekton_sfx_vo_r": (V + "ReignOfTheTyrant_cast3D", 1229598838, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_renekton_skill": "ASSETS/Characters/Renekton/HUD/Icons2D/Renekton_Q.dds",
    "league_renekton_skill2": "ASSETS/Characters/Renekton/HUD/Icons2D/Renekton_E.dds",
    "league_renekton_ult": "ASSETS/Characters/Renekton/HUD/Icons2D/Renekton_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Renekton.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Renekton.{args.lang}.wad.client"))
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
