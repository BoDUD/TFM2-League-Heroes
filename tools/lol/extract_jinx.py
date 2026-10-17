"""Pull Jinx's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_jinx.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Jinx.wad.client and Jinx.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in the base skin's bin. Pow-Pow and Fishbones each have OnCast, OnMissileCast,
OnMissileLaunch and OnHit events; the shot is OnMissileCast (Pow-Pow's opens with four gunshots), the
rocket's launch is Fishbones' OnCast. Chompers: E_OnCast is the throw, EMine_OnBuffActivate (short
variants) the landing, EMineSnare the bite. The zh_CN bank has one W line, four short E shouts and six
R lines (none shared with en_US); Get Excited! has no line of its own, so it plays her laugh.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/jinx/skins/base/jinx_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/jinx/skins/base/jinx_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_jinx_sfx_minigun": ("Play_sfx_Jinx_JinxBasicAttack_OnMissileCast", 850350830, 0.8, -5),
    "league_jinx_sfx_minigun_hit": ("Play_sfx_Jinx_JinxBasicAttack_OnHit", 596411761, 0.6, -6),
    "league_jinx_sfx_rocket": ("Play_sfx_Jinx_JinxQAttack_OnCast", 655843727, 0.9, -4),
    "league_jinx_sfx_rocket_hit": ("Play_sfx_Jinx_JinxQAttack_hit", 1030342883, 1.2, -4),
    "league_jinx_sfx_swap": ("Play_sfx_Jinx_JinxQ_OnBuffActivate", 630900835, 1.2, -5),
    "league_jinx_sfx_w_cast": ("Play_sfx_Jinx_JinxW_OnCast", 447468533, 0.9, -5),
    "league_jinx_sfx_w_fire": ("Play_sfx_Jinx_JinxWMissile_OnMissileCast", 34776271, 1.0, -4),
    "league_jinx_sfx_w_hit": ("Play_sfx_Jinx_JinxWMissile_hit", 75287510, 1.0, -4),
    "league_jinx_sfx_e_cast": ("Play_sfx_Jinx_JinxE_OnCast", 771564994, 0.8, -4),
    "league_jinx_sfx_e_arm": ("Play_sfx_Jinx_JinxEMine_OnBuffActivate", 119438045, 0.8, -6),
    "league_jinx_sfx_e_snap": ("Play_sfx_Jinx_JinxEMineSnare_OnBuffActivate", 281450065, 1.2, -3),
    "league_jinx_sfx_r_cast": ("Play_sfx_Jinx_JinxR_OnCast", 81860824, 0.6, -4),
    "league_jinx_sfx_r_fire": ("Play_sfx_Jinx_JinxR_OnMissileCast", 932608779, 1.6, -3),
    "league_jinx_sfx_r_hit": ("Play_sfx_Jinx_JinxR_hit", 631062962, 2.0, -3),
    "league_jinx_sfx_excited": ("Play_sfx_Jinx_JinxPassiveKill_OnBuffActivate", 233505554, 1.4, -5),
    "league_jinx_vo_w": ("Play_vo_Jinx_JinxW_cast3D", 709405216, 1.0, -2),
    "league_jinx_vo_e": ("Play_vo_Jinx_JinxE_cast3D", 532130055, 0.8, -2),
    "league_jinx_vo_r": ("Play_vo_Jinx_JinxR_cast3D", 663930704, 1.0, -2),
    "league_jinx_vo_laugh": ("Play_vo_Jinx_laugh3D_in", 646090362, 1.7, -3),
}
ICONS = {  # TFM2 slot -> Riot icon (Switcheroo! rides on the basic attack, Get Excited! is a passive: no slots)
    "league_jinx_skill": "ASSETS/Characters/Jinx/HUD/Icons2D/Jinx_W.dds",
    "league_jinx_skill2": "ASSETS/Characters/Jinx/HUD/Icons2D/Jinx_E.dds",
    "league_jinx_ult": "ASSETS/Characters/Jinx/HUD/Icons2D/Jinx_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Jinx.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Jinx.{args.lang}.wad.client"))
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
