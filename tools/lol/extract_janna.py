"""Pull Janna's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_janna.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Janna.wad.client and Janna.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Janna's skin bin. Howling Gale has a charge and a launch sound and no hit
sound of its own; the launch (the tornado on its way) plays with Q. Zephyr's launch and hit play with
skill2 (E with W folded in), next to Eye of the Storm's shield sound; Monsoon's buff sound covers the
whole 3 s channel. Janna has no spell voice lines, only general ones of four to six seconds; the
shortest move line (about 2.7 s) plays with R, during the channel.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/janna/skins/base/janna_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/janna/skins/base/janna_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_janna_sfx_attack_cast": ("Play_sfx_Janna_JannaBasicAttack_OnMissileLaunch", 154973761, 0.7, -8),
    "league_janna_sfx_attack_hit": ("Play_sfx_Janna_JannaBasicAttack_OnHit", 22729316, 0.6, -7),
    "league_janna_sfx_q_cast": ("Play_sfx_Janna_HowlingGale_launch", 570164569, 1.6, -4),
    "league_janna_sfx_w_cast": ("Play_sfx_Janna_SowTheWind_OnMissileLaunch", 446035385, 1.0, -6),
    "league_janna_sfx_w_hit": ("Play_sfx_Janna_SowTheWind_OnHit", 254358437, 0.9, -5),
    "league_janna_sfx_e_cast": ("Play_sfx_Janna_EyeOfTheStorm_OnBuffActivate", 457985427, 1.4, -5),
    "league_janna_sfx_r_cast": ("Play_sfx_Janna_ReapTheWhirlwind_OnBuffActivate", 753398077, 3.3, -4),
    "league_janna_vo_r": ("Play_vo_Janna_Move2DStandard", 417211718, 3.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill2 is E with W folded in: E's icon)
    "league_janna_skill": "ASSETS/Characters/Janna/HUD/Icons2D/JannaQ.dds",
    "league_janna_skill2": "ASSETS/Characters/Janna/HUD/Icons2D/JannaE.dds",
    "league_janna_ult": "ASSETS/Characters/Janna/HUD/Icons2D/JannaR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Janna.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Janna.{args.lang}.wad.client"))
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
            print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
