"""Pull Teemo's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_teemo.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Teemo.wad.client and Teemo.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Teemo's champion bin. Toxic Shot is always on in this kit, so the basic
attack uses the E-empowered shot and hit (TeemoEAttack_*). W plays its own cast and the passive's
camouflage (TeemoPStealthBuff_cast); W has no voice line, so the camouflage line (Spell3DPCast) goes
with it. R: the throw, the mushroom arming (TeemoRTrap_OnBuffActivate) and its burst
(TeemoMushroom_TeemoRTrap_hitlocation). Voice variants were picked by length (1.1-1.6 s): the
zh_CN bank has its own media ids, so no line can be found wordless by comparing it with en_US.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/teemo/skins/base/teemo_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/teemo/skins/base/teemo_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_teemo_sfx_attack_shot": ("Play_sfx_Teemo_TeemoEAttack_OnMissileLaunch", 165806091, 0.6, -6),
    "league_teemo_sfx_attack_hit": ("Play_sfx_Teemo_TeemoEAttack_OnHit", 1037537174, 0.7, -6),
    "league_teemo_sfx_q_shot": ("Play_sfx_Teemo_TeemoQ_OnMissileLaunch", 1030668168, 0.7, -4),
    "league_teemo_sfx_q_hit": ("Play_sfx_Teemo_TeemoQ_OnHit", 63286599, 1.0, -4),
    "league_teemo_sfx_w_cast": ("Play_sfx_Teemo_TeemoW_OnCast", 432173883, 0.9, -5),
    "league_teemo_sfx_w_stealth": ("Play_sfx_Teemo_TeemoPStealthBuff_cast", 738087181, 1.3, -6),
    "league_teemo_sfx_r_cast": ("Play_sfx_Teemo_TeemoR_OnCast", 128789974, 0.5, -5),
    "league_teemo_sfx_r_throw": ("Play_sfx_Teemo_TeemoR_missilelaunch", 296262384, 0.7, -5),
    "league_teemo_sfx_r_arm": ("Play_sfx_Teemo_TeemoRTrap_OnBuffActivate", 826741817, 1.2, -6),
    "league_teemo_sfx_r_burst": ("Play_sfx_TeemoMushroom_TeemoRTrap_hitlocation", 624392861, 1.2, -3),
    "league_teemo_vo_q": ("Play_vo_Teemo_TeemoQ_cast3D", 1504042499, 1.1, -2),
    "league_teemo_vo_w": ("Play_vo_Teemo_Spell3DPCast", 450866780, 1.6, -2),
    "league_teemo_vo_r": ("Play_vo_Teemo_TeemoR_cast3D", 1473079911, 1.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Toxic Shot rides on the basic attack: no slot)
    "league_teemo_skill": "ASSETS/Characters/Teemo/HUD/Icons2D/TeemoQ.dds",
    "league_teemo_skill2": "ASSETS/Characters/Teemo/HUD/Icons2D/TeemoW.dds",
    "league_teemo_ult": "ASSETS/Characters/Teemo/HUD/Icons2D/TeemoR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Teemo.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Teemo.{args.lang}.wad.client"))
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
