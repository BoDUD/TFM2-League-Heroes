"""Pull Vayne's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_vayne.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Vayne.wad.client and Vayne.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Vayne's skin bin. The basic attack has its shot and its hit, and the shot of her attacks
during Final Hour (VayneUltAttack); Tumble the roll, the bolt it empowers (TumbleAttack launch and hit), the
empowered bolt's ready shimmer (TumbleBonus) and the fade into invisibility under Final Hour (TumbleFade);
Silver Bolts the third ring's burst (SilveredBolts buff activation); Condemn the cast and two takes of the bolt's
impact, the shorter for the hit and the longer for the slam where the target lands; Final Hour the cast. Tumble
has no voice event; of Condemn's and Final Hour's zh_CN takes (each its own recording) the longest are used.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/vayne/skins/base/vayne_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/vayne/skins/base/vayne_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_vayne_sfx_attack_shot": ("Play_sfx_Vayne_VayneBasicAttack_OnMissileCast", 858317852, 0.45, -6),
    "league_vayne_sfx_attack_hit": ("Play_sfx_Vayne_VayneBasicAttack_OnHit", 186195165, 0.6, -8),
    "league_vayne_sfx_r_shot": ("Play_sfx_Vayne_VayneUltAttack_OnMissileCast", 50337729, 0.75, -6),
    "league_vayne_sfx_q_cast": ("Play_sfx_Vayne_VayneTumble_OnCast", 777142544, 0.7, -4),
    "league_vayne_sfx_q_ready": ("Play_sfx_Vayne_VayneTumbleBonus_OnBuffActivate", 301657218, 1.0, -8),
    "league_vayne_sfx_q_shot": ("Play_sfx_Vayne_VayneTumbleAttack_OnMissileLaunch", 655846613, 1.2, -4),
    "league_vayne_sfx_q_hit": ("Play_sfx_Vayne_VayneTumbleAttack_OnHit", 64817339, 0.45, -6),
    "league_vayne_sfx_q_stealth": ("Play_sfx_Vayne_VayneTumbleFade_cast", 17276274, 1.0, -4),
    "league_vayne_sfx_sb_proc": ("Play_sfx_Vayne_VayneSilveredBolts_OnBuffActivate", 710344357, 1.2, -4),
    "league_vayne_sfx_e_cast": ("Play_sfx_Vayne_VayneCondemn_OnCast", 800132908, 0.55, -4),
    "league_vayne_sfx_e_hit": ("Play_sfx_Vayne_VayneCondemnMissile_hit", 707378288, 1.0, -4),
    "league_vayne_sfx_e_slam": ("Play_sfx_Vayne_VayneCondemnMissile_hit", 397527245, 1.2, -3),
    "league_vayne_sfx_r_cast": ("Play_sfx_Vayne_VayneInquisition_OnCast", 158680766, 2.0, -3),
    "league_vayne_vo_e": ("Play_vo_Vayne_VayneCondemn_cast3D", 1614228695, 1.0, -2),
    "league_vayne_vo_r": ("Play_vo_Vayne_VayneInquisition_cast3D", 1247215384, 2.9, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_vayne_skill": "ASSETS/Characters/Vayne/HUD/Icons2D/Vayne_Q.dds",
    "league_vayne_skill2": "ASSETS/Characters/Vayne/HUD/Icons2D/Vayne_E.dds",
    "league_vayne_ult": "ASSETS/Characters/Vayne/HUD/Icons2D/Vayne_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Vayne.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Vayne.{args.lang}.wad.client"))
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
