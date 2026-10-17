"""Pull Akali's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_akali.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Akali.wad.client and Akali.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her spells in the base bins: AkaliQ = Five Point Strike (AkaliQ_OnCast, AkaliQ_hit / _hitchamp), AkaliW =
Twilight Shroud (AkaliW_OnCastSelf), AkaliE = Shuriken Flip (AkaliE_OnCast the flip, AkaliEmis the shuriken,
AkaliEb_leap / AkaliEbattack_hit the recast dash), AkaliR = Perfect Execution (AkaliR_Cast + AkaliR1_hit, AkaliRb
the second dash), the passive's empowered attack (AkaliBasicAttackPassive). Twilight Shroud has no voice line of
its own (its vo events only filter her voice), so W plays none; every spell line differs between the zh_CN and
en_US banks (translated) and a short one of each is taken.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/akali/skins/base/akali_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/akali/skins/base/akali_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_akali_sfx_attack_hit": ("Play_sfx_Akali_AkaliBasicAttack_OnHit", 918119877, 0.5, -7),
    "league_akali_sfx_p_cast": ("Play_sfx_Akali_AkaliBasicAttackPassive_OnCast", 645964678, 0.4, -7),
    "league_akali_sfx_p_hit": ("Play_sfx_Akali_AkaliBasicAttackPassive_OnHit", 159779918, 0.8, -5),
    "league_akali_sfx_q_cast": ("Play_sfx_Akali_AkaliQ_OnCast", 195345266, 0.6, -5),
    "league_akali_sfx_q_hit": ("Play_sfx_Akali_AkaliQ_hitchamp", 232190810, 0.5, -8),
    "league_akali_sfx_w_cast": ("Play_sfx_Akali_AkaliW_OnCastSelf", 258351474, 1.5, -5),
    "league_akali_sfx_e_cast": ("Play_sfx_Akali_AkaliE_OnCast", 82240103, 0.7, -5),
    "league_akali_sfx_e_throw": ("Play_sfx_Akali_AkaliEmis_OnMissileLaunch", 531094658, 0.9, -8),
    "league_akali_sfx_e_hit": ("Play_sfx_Akali_AkaliEmis_Hit", 14071628, 0.65, -6),
    "league_akali_sfx_e2_cast": ("Play_sfx_Akali_AkaliEb_leap", 824285208, 0.4, -5),
    "league_akali_sfx_e2_hit": ("Play_sfx_Akali_AkaliEbattack_hit", 943091896, 0.65, -5),
    "league_akali_sfx_r1_cast": ("Play_sfx_Akali_AkaliR_Cast", 628296178, 0.95, -4),
    "league_akali_sfx_r1_hit": ("Play_sfx_Akali_AkaliR1_hit", 675334627, 0.75, -6),
    "league_akali_sfx_r2_cast": ("Play_sfx_Akali_AkaliRb_OnCast", 527355819, 0.95, -4),
    "league_akali_sfx_r2_hit": ("Play_sfx_Akali_AkaliRb_hit", 895445165, 1.2, -5),
    "league_akali_vo_q": ("Play_vo_Akali_AkaliQ_cast3D", 1476047792, 0.6, -2),
    "league_akali_vo_e": ("Play_vo_Akali_AkaliE_cast3D", 1230189283, 0.8, -2),
    "league_akali_vo_r": ("Play_vo_Akali_AkaliR_cast3D", 1085450652, 0.7, -2),
    "league_akali_vo_r2": ("Play_vo_Akali_AkaliRb_cast3D", 311353754, 1.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Twilight Shroud rides on Shuriken Flip, Assassin's Mark on the attack)
    "league_akali_skill": "ASSETS/Characters/Akali/HUD/Icons2D/Akali_Q.dds",
    "league_akali_skill2": "ASSETS/Characters/Akali/HUD/Icons2D/Akali_E.dds",
    "league_akali_ult": "ASSETS/Characters/Akali/HUD/Icons2D/Akali_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Akali.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Akali.{args.lang}.wad.client"))
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
