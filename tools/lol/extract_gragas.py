r"""Pull Gragas's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_gragas.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe
gmstream-cli.exe
gmstream-cli.exe

Same route as extract_viego.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Gragas.wad.client and Gragas.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, picked by size among the variants): the punch GragasBasicAttack_OnCast / _OnHit;
Barrel Roll's throw GragasQ_OnCast and its blast GragasQMissile_boom; Drunken Rage's gulp GragasW_OnCast, the
empowered attack's hit GragasW_hit; Body Slam's charge GragasE_OnCast and the slam GragasE_hit; Explosive Cask's throw
GragasR_OnCast and its blast GragasR_boom; Happy Hour's drink GragasWSelf_OnBuffActivate. Voice: his grunts for Q, E
and R (the bigger takes of the shared cast set) and the W drink line.
Icons: GragasBarrelRoll = skill (Q), GragasBodySlam = skill2 (E, W folded), GragasExplosiveCask = ult (R); GragasDrunkenRage is written too (the empowered
attack's buff icon).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/gragas/skins/base/gragas_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/gragas/skins/base/gragas_base_vo_"  # same in every language
P = "Play_sfx_Gragas_Gragas"
V = "Play_vo_Gragas_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_gragas_sfx_a_swing": (P + "BasicAttack_OnCast", 353671218, 0.45, -11),
    "league_gragas_sfx_a_hit": (P + "BasicAttack_OnHit", 195395622, 0.6, -12),
    "league_gragas_sfx_p": (P + "WSelf_OnBuffActivate", 257853551, 1.2, -12),
    "league_gragas_sfx_q": (P + "Q_OnCast", 843673933, 0.9, -10),
    "league_gragas_sfx_q_boom": (P + "QMissile_boom", 99092660, 1.3, -9),
    "league_gragas_sfx_w": (P + "W_OnCast", 752756167, 0.6, -10),
    "league_gragas_sfx_w_hit": (P + "W_hit", 480417440, 1.0, -9),
    "league_gragas_sfx_e": (P + "E_OnCast", 137416781, 0.6, -10),
    "league_gragas_sfx_e_hit": (P + "E_hit", 215166354, 0.9, -9),
    "league_gragas_sfx_r": (P + "R_OnCast", 421591823, 0.8, -10),
    "league_gragas_sfx_r_boom": (P + "R_boom", 595477819, 1.8, -8),
    "league_gragas_sfx_vo_q": (V + "GragasQ_cast3D", 153944089, 1.0, -4),
    "league_gragas_sfx_vo_w": (V + "GragasW_OnCast", 205528052, 2.0, -4),
    "league_gragas_sfx_vo_e": (V + "GragasE_cast3D", 1168020846, 1.0, -4),
    "league_gragas_sfx_vo_r": (V + "GragasR_cast3D", 783153009, 1.0, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_gragas_skill": "ASSETS/Characters/Gragas/HUD/Icons2D/GragasBarrelRoll.dds",
    "league_gragas_skill2": "ASSETS/Characters/Gragas/HUD/Icons2D/GragasBodySlam.dds",
    "league_gragas_ult": "ASSETS/Characters/Gragas/HUD/Icons2D/GragasExplosiveCask.dds",
    "league_gragas_w": "ASSETS/Characters/Gragas/HUD/Icons2D/GragasDrunkenRage.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Gragas.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Gragas.{args.lang}.wad.client"))
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
