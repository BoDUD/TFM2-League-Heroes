r"""Pull Syndra's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_syndra.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_viktor.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Syndra.wad.client and Syndra.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

Her events are Play_sfx_Syndra_Syndra<spell>_<event> (found by scanning her wad for Play_ strings; the other skins'
events resolve to no media in the base bank). The bolt SyndraBasicAttack_OnMissileLaunch (no base OnHit media: the
hit borrows SyndraQ_hit); Dark Sphere SyndraQSpell_buffactivate (the sphere forms), SyndraQ_explode (its blast);
Force of Will SyndraW_cast (the grab), SyndraWCast_missilelaunch (the
throw), SyndraWCast_land; Scatter the Weak SyndraE_OnCast, SyndraEMissile_missilelaunch (a sphere pushed),
SyndraEMissile_hit (the stun); Unleashed Power SyndraR_OnCast, SyndraRSpell_OnMissileLaunch, SyndraRSpell_OnHit;
Transcendent SyndraP_upgrade_buffactivate (a spell upgraded). Voice clips are league_syndra_sfx_vo_* (never the
sound's own name): Q, W and E share one cast pool in League (three of its lines), R has its own line.
Icons: Syndra_Q1 = skill (Q), Syndra_E1 = skill2 (W -> E; W is in its text), Syndra_R1 = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/syndra/skins/base/syndra_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/syndra/skins/base/syndra_base_vo_"  # same in every language
P = "Play_sfx_Syndra_Syndra"
V = "Play_vo_Syndra_Syndra"
POOL = V + "Q_cast3D"  # Q / W / E share these lines

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_syndra_sfx_shot": (P + "BasicAttack_OnMissileLaunch", 206796027, 0.6, -12),
    "league_syndra_sfx_hit": (P + "Q_hit", 65803573, 0.5, -13),
    "league_syndra_sfx_q_cast": (P + "QSpell_buffactivate", 376740915, 0.9, -10),
    "league_syndra_sfx_q_blast": (P + "Q_explode", 540145157, 1.0, -8),
    "league_syndra_sfx_w_grab": (P + "W_cast", 737625759, 0.9, -10),
    "league_syndra_sfx_w_throw": (P + "WCast_missilelaunch", 889972163, 0.8, -10),
    "league_syndra_sfx_w_land": (P + "WCast_land", 627239462, 1.0, -8),
    "league_syndra_sfx_e_cast": (P + "E_OnCast", 293515909, 1.0, -9),
    "league_syndra_sfx_e_push": (P + "EMissile_missilelaunch", 807799822, 0.8, -10),
    "league_syndra_sfx_e_stun": (P + "EMissile_hit", 775314805, 0.9, -9),
    "league_syndra_sfx_r_cast": (P + "R_OnCast", 468921591, 1.4, -9),
    "league_syndra_sfx_r_launch": (P + "RSpell_OnMissileLaunch", 753064571, 0.8, -11),
    "league_syndra_sfx_r_hit": (P + "RSpell_OnHit", 687020958, 0.9, -9),
    "league_syndra_sfx_evo": (P + "P_upgrade_buffactivate", 703233625, 1.4, -9),
    "league_syndra_sfx_vo_q": (POOL, 1635097978, 2.2, -4),
    "league_syndra_sfx_vo_w": (POOL, 480881063, 2.2, -4),
    "league_syndra_sfx_vo_e": (POOL, 1899396790, 2.2, -4),
    "league_syndra_sfx_vo_r": (V + "R_cast3D", 139999134, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_syndra_skill": "ASSETS/Characters/Syndra/HUD/Icons2D/Syndra_Q1.dds",
    "league_syndra_skill2": "ASSETS/Characters/Syndra/HUD/Icons2D/Syndra_E1.dds",
    "league_syndra_ult": "ASSETS/Characters/Syndra/HUD/Icons2D/Syndra_R1.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Syndra.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Syndra.{args.lang}.wad.client"))
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
