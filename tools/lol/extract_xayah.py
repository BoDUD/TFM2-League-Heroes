"""Pull Xayah's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_xayah.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Xayah.wad.client and Xayah.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events (the client's names, found in her bins by work/xy/snd_names.py and picked with work/xy/snd_probe_xy.py):
the attack is XayahBasicAttack_OnCast + _OnHit, an empowered one XayahPassiveAttack_OnCast; a feather landing is
XayahQMissile1_OnHitLocation's short variant; Double Daggers casts with XayahQ_OnCast; Deadly Plumage with XayahW_OnCast,
its second blade XayahWMissile_cast; Bladecaller with XayahE_cast, each returning feather XayahE_feather_hit's short
variant, the root XayahE_root_hit; Featherstorm with XayahR_OnCast + XayahRMissile_OnMissileLaunch. Voice: a Q, an E,
an R and a root line. Duo lines with Rakan (Receive3DShieldRakan ...) are added with the duo.
Icons: XayahQ = skill (Q -> E), XayahW = skill2, XayahR = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/xayah/skins/base/xayah_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/xayah/skins/base/xayah_base_vo_"  # same in every language
P = "Play_sfx_Xayah_Xayah"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_xayah_sfx_attack": (P + "BasicAttack_OnCast", 259875172, 0.45, -10),
    "league_xayah_sfx_attack_hit": (P + "BasicAttack_OnHit", 96252725, 0.4, -12),
    "league_xayah_sfx_attack_p": (P + "PassiveAttack_OnCast", 846198950, 0.6, -9),
    "league_xayah_sfx_feather": (P + "QMissile1_OnHitLocation", 34093138, 0.5, -13),
    "league_xayah_sfx_q": (P + "Q_OnCast", 947407279, 0.8, -8),
    "league_xayah_sfx_w": (P + "W_OnCast", 530879371, 0.9, -8),
    "league_xayah_sfx_w_blade": (P + "WMissile_cast", 508890712, 0.4, -13),
    "league_xayah_sfx_e": (P + "E_cast", 482031824, 0.6, -8),
    "league_xayah_sfx_e_hit": (P + "E_feather_hit", 24169822, 0.3, -12),
    "league_xayah_sfx_e_root": (P + "E_root_hit", 66955044, 1.0, -9),
    "league_xayah_sfx_r": (P + "R_OnCast", 979219185, 1.4, -8),
    "league_xayah_sfx_r_rain": (P + "RMissile_OnMissileLaunch", 798027026, 0.6, -9),
    "league_xayah_vo_q": ("Play_vo_Xayah_XayahQ_cast3D", 1861566411, 1.0, -4),
    "league_xayah_vo_e": ("Play_vo_Xayah_XayahE_cast3D", 894359086, 0.8, -4),
    "league_xayah_vo_r": ("Play_vo_Xayah_XayahR_cast3D", 1517303110, 1.8, -3),
    "league_xayah_vo_root": ("Play_vo_Xayah_Spell3DERoot", 935485957, 0.8, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_xayah_skill": "ASSETS/Characters/Xayah/HUD/Icons2D/XayahQ.dds",
    "league_xayah_skill2": "ASSETS/Characters/Xayah/HUD/Icons2D/XayahW.dds",
    "league_xayah_ult": "ASSETS/Characters/Xayah/HUD/Icons2D/XayahR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Xayah.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Xayah.{args.lang}.wad.client"))
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
