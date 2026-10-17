"""Pull Sett's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_sett.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Sett.wad.client and Sett.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

His events in the base bank (the event names are plain strings in his .bin files): SettBasicAttack_OnHit / SettBasicAttack2_OnHit (the left and the right fist's impacts, sixteen each,
the swings layered in); SettQ_OnBuffActivate (Knuckle Down's 5.6 s buff loop: only its start is used) and
SettQAttack_OnHit (the empowered punches); SettE_cast (Facebreaker's grab) and SettE_hit_both / _hit_single (the
smash with two or more / one champion pulled - the kit stuns only with two, so _hit_both stands for the hit);
SettW_cast (Haymaker's wind-up), SettW_hit and SettW_hit_center_sweetener (the true-damage centre); SettR_cast,
SettRGrabbed_OnBuffActivate (the champion grabbed) and SettR_hit (the slam). Voice: the E / W / R cast3D lines; every variant was measured (length, peak, RMS) and none of the zh_CN lines repeats the
en_US bytes, so they are all spoken Chinese. The icons: Sett_E = E (Q rides on it), Sett_W = W, Sett_R = R.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/sett/skins/base/sett_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/sett/skins/base/sett_base_vo_"  # same path in every language

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_sett_sfx_attack_hit": ("Play_sfx_Sett_SettBasicAttack_OnHit", 964213463, 0.7, -9),
    "league_sett_sfx_attack2_hit": ("Play_sfx_Sett_SettBasicAttack2_OnHit", 18718757, 0.8, -9),
    "league_sett_sfx_q_buff": ("Play_sfx_Sett_SettQ_OnBuffActivate", 870946616, 1.0, -10),
    "league_sett_sfx_q_hit": ("Play_sfx_Sett_SettQAttack_OnHit", 750398786, 0.9, -7),
    "league_sett_sfx_e_cast": ("Play_sfx_Sett_SettE_cast", 113517863, 1.0, -8),
    "league_sett_sfx_e_hit": ("Play_sfx_Sett_SettE_hit_both", 493284039, 1.2, -6),
    "league_sett_sfx_w_cast": ("Play_sfx_Sett_SettW_cast", 296294238, 1.0, -8),
    "league_sett_sfx_w_hit": ("Play_sfx_Sett_SettW_hit", 587761099, 1.4, -6),
    "league_sett_sfx_w_center": ("Play_sfx_Sett_SettW_hit_center_sweetener", 357659307, 1.2, -9),
    "league_sett_sfx_r_cast": ("Play_sfx_Sett_SettR_cast", 18836543, 1.6, -7),
    "league_sett_sfx_r_grab": ("Play_sfx_Sett_SettRGrabbed_OnBuffActivate", 692733280, 1.2, -9),
    "league_sett_sfx_r_slam": ("Play_sfx_Sett_SettR_hit", 619210767, 2.0, -5),
    "league_sett_vo_w": ("Play_vo_Sett_SettW_cast3D", 1173767740, 1.8, -3),
    "league_sett_vo_e": ("Play_vo_Sett_SettE_cast3D", 317885812, 2.0, -3),
    "league_sett_vo_r": ("Play_vo_Sett_SettR_cast3D", 1169865610, 2.4, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_sett_skill": "ASSETS/Characters/Sett/HUD/Icons2D/Sett_E.dds",
    "league_sett_skill2": "ASSETS/Characters/Sett/HUD/Icons2D/Sett_W.dds",
    "league_sett_ult": "ASSETS/Characters/Sett/HUD/Icons2D/Sett_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Sett.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Sett.{args.lang}.wad.client"))
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
