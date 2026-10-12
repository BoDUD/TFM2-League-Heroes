r"""Pull Corki's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_corki.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_gragas.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Corki.wad.client and Corki.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, picked by size among the variants): the shot CorkiBasicAttack_OnMissileLaunch / _OnHit;
Phosphorus Bomb's throw PhosphorusBomb_OnCast and its blast PhosphorusBomb_boom; Gatling Gun's spin-up
GGun_OnBuffActivate; Valkyrie's engine ValkyrieSound_OnBuffActivate and the fire Valkyrie_boom; the Package's launch
CarpetBombMega_OnCast and its blasts CarpetBombMega_hit; Missile Barrage's launch MissileBarrageMissile_OnMissileLaunch
and blast _boom, the Big One's MissileBarrageMissile2_OnMissileLaunch / _boom. Voice (he has no spell lines but these):
three of his attack lines for Q, E and R, the Package's cast line for W with the Package.
Icons: Corki_PhosphorusBomb = skill (Q), Corki_GatlingGun = skill2 (E, W folded), Corki_MissileBarrage = ult (R);
Corki_Valkyrie (W) and Corki_RapidReload (the passive) are written too.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/corki/skins/base/corki_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/corki/skins/base/corki_base_vo_"  # same in every language
P = "Play_sfx_Corki_"
V = "Play_vo_Corki_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_corki_sfx_a_fire": (P + "CorkiBasicAttack_OnMissileLaunch", 555908138, 0.5, -12),
    "league_corki_sfx_a_hit": (P + "CorkiBasicAttack_OnHit", 344379843, 0.5, -12),
    "league_corki_sfx_q": (P + "PhosphorusBomb_OnCast", 336888845, 0.6, -10),
    "league_corki_sfx_q_boom": (P + "PhosphorusBomb_boom", 158754893, 1.4, -9),
    "league_corki_sfx_e": (P + "GGun_OnBuffActivate", 149133673, 1.2, -11),
    "league_corki_sfx_w": (P + "ValkyrieSound_OnBuffActivate", 73259397, 1.0, -10),
    "league_corki_sfx_w_boom": (P + "Valkyrie_boom", 399068665, 1.2, -10),
    "league_corki_sfx_w_pkg": (P + "CarpetBombMega_OnCast", 729750138, 1.4, -9),
    "league_corki_sfx_w_pkg_hit": (P + "CarpetBombMega_hit", 378971083, 1.0, -9),
    "league_corki_sfx_r": (P + "MissileBarrageMissile_OnMissileLaunch", 314284036, 0.6, -10),
    "league_corki_sfx_r_boom": (P + "MissileBarrageMissile_boom", 426828175, 0.8, -10),
    "league_corki_sfx_r_big": (P + "MissileBarrageMissile2_OnMissileLaunch", 779157311, 0.8, -9),
    "league_corki_sfx_r_big_boom": (P + "MissileBarrageMissile2_boom", 880087752, 1.0, -8),
    "league_corki_sfx_vo_q": (V + "Attack2DGeneral", 1475074304, 1.6, -4),
    "league_corki_sfx_vo_e": (V + "Attack2DGeneral", 357937809, 1.6, -4),
    "league_corki_sfx_vo_r": (V + "Attack2DGeneral", 591533726, 1.6, -4),
    "league_corki_sfx_vo_w": (V + "CarpetBombMega_cast3D", 1499635118, 1.4, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_corki_skill": "ASSETS/Characters/Corki/HUD/Icons2D/Corki_PhosphorusBomb.dds",
    "league_corki_skill2": "ASSETS/Characters/Corki/HUD/Icons2D/Corki_GatlingGun.dds",
    "league_corki_ult": "ASSETS/Characters/Corki/HUD/Icons2D/Corki_MissileBarrage.dds",
    "league_corki_w": "ASSETS/Characters/Corki/HUD/Icons2D/Corki_Valkyrie.dds",
    "league_corki_passive": "ASSETS/Characters/Corki/HUD/Icons2D/Corki_RapidReload.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Corki.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Corki.{args.lang}.wad.client"))
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
