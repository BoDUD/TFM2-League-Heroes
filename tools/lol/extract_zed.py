r"""Pull Zed's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zed.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_rengar.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Zed.wad.client and Zed.<lang>.wad.client, resolves the base-skin Wwise events below to their
media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games)
plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/zd/snd_names_zd.py, picked with work/zd/snd_probe_zd.py): the swing
ZedBasicAttack_OnCast / _OnHit, the passive's hit ZedCritAttack_OnHit; Razor Shuriken ZedQ_OnCast,
ZedQMissile_OnMissileLaunch and ZedShurikenMisOne_hit; Living Shadow ZedShadowDashMissile_OnMissileLaunch (the shadow
flies), ZedWShadowBuff_OnBuffActivate (it stands), ZedW2_OnCast (the swap); Shadow Slash ZedPBAOE_buffactivate and
ZedPBAOE_hit; Death Mark ZedR_OnCast, ZedR_OnHit (the strike), ZedUlt_hit (the mark), ZedUltExecute_buffdeactivate (the
burst). Voice: Q, W (W2's lines: the base W has none), E, R.
Icons: ZedW = skill (Living Shadow), ZedQ = skill2 (Razor Shuriken), ZedR = ult (Shadow Slash is automatic).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zed/skins/base/zed_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zed/skins/base/zed_base_vo_"  # same in every language
P = "Play_sfx_Zed_Zed"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_zed_sfx_attack": (P + "BasicAttack_OnCast", 1073708781, 0.4, -11),
    "league_zed_sfx_attack_hit": (P + "BasicAttack_OnHit", 48781906, 0.4, -11),
    "league_zed_sfx_cw_hit": (P + "CritAttack_OnHit", 237088468, 0.6, -9),
    "league_zed_sfx_q": (P + "Q_OnCast", 51708590, 0.6, -9),
    "league_zed_sfx_q_fly": (P + "QMissile_OnMissileLaunch", 714470164, 0.5, -10),
    "league_zed_sfx_q_hit": (P + "ShurikenMisOne_hit", 521579405, 0.55, -10),
    "league_zed_sfx_w": (P + "ShadowDashMissile_OnMissileLaunch", 736651813, 0.7, -9),
    "league_zed_sfx_w_land": (P + "WShadowBuff_OnBuffActivate", 100306220, 0.6, -9),
    "league_zed_sfx_w2": (P + "W2_OnCast", 60553523, 0.6, -8),
    "league_zed_sfx_e": (P + "PBAOE_buffactivate", 618192499, 0.6, -9),
    "league_zed_sfx_e_hit": (P + "PBAOE_hit", 482127819, 0.4, -11),
    "league_zed_sfx_r": (P + "R_OnCast", 44997049, 0.7, -8),
    "league_zed_sfx_r_hit": (P + "R_OnHit", 68218858, 0.8, -8),
    "league_zed_sfx_r_mark": (P + "Ult_hit", 954204873, 0.7, -9),
    "league_zed_sfx_r_pop": (P + "UltExecute_buffdeactivate", 218261741, 0.6, -7),
    "league_zed_sfx_vo_q": ("Play_vo_Zed_ZedQ_cast3D", 1133248817, 0.7, -4),
    "league_zed_sfx_vo_w": ("Play_vo_Zed_ZedW2_cast3D", 724566853, 1.2, -4),
    "league_zed_sfx_vo_e": ("Play_vo_Zed_ZedE_cast3D", 1122545617, 0.8, -4),
    "league_zed_sfx_vo_r": ("Play_vo_Zed_ZedR_cast3D", 1502749877, 1.3, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_zed_skill": "ASSETS/Characters/Zed/HUD/Icons2D/ZedW.dds",
    "league_zed_skill2": "ASSETS/Characters/Zed/HUD/Icons2D/ZedQ.dds",
    "league_zed_ult": "ASSETS/Characters/Zed/HUD/Icons2D/ZedR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zed.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zed.{args.lang}.wad.client"))
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
