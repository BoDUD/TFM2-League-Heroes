"""Pull Brand's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_brand.py --lol D:/WeGameApps/lol --vgmstream path/to/vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Brand.wad.client and Brand.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events (plain strings in the WAD's .bin files) are Play_sfx_Brand_Brand<spell>_<event>. The attack: BasicAttack
OnMissileLaunch / OnHit. Sear: QMissile_OnMissileLaunch, QMissile_hit. Pillar of Flame: W_OnCast (the ground lights
up), W_hit (the pillar). Conflagration: E_OnCast, E_hit. Pyroclasm: R_OnCast, R_OnMissileLaunch (every bounce),
R_hit. Blaze: P_detonate1 (the third stack's blast). Voice: Q/W/E/R cast3D.
Icons: BrandW = skill (Pillar of Flame), BrandE = skill2 (E leads the E -> Q combo), BrandR = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/brand/skins/base/brand_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/brand/skins/base/brand_base_vo_"  # same in every language
P = "Play_sfx_Brand_Brand"
V = "Play_vo_Brand_Brand"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_brand_sfx_a_cast": (P + "BasicAttack_OnMissileLaunch", 407133761, 0.6, -12),
    "league_brand_sfx_a_hit": (P + "BasicAttack_OnHit", 809467561, 0.4, -13),
    "league_brand_sfx_q_cast": (P + "QMissile_OnMissileLaunch", 294565845, 0.8, -9),
    "league_brand_sfx_q_hit": (P + "QMissile_hit", 1060762819, 0.8, -9),
    "league_brand_sfx_w_cast": (P + "W_OnCast", 1022132913, 0.9, -10),
    "league_brand_sfx_w_blast": (P + "W_hit", 681263634, 1.2, -8),
    "league_brand_sfx_e_cast": (P + "E_OnCast", 481421054, 0.6, -10),
    "league_brand_sfx_e_hit": (P + "E_hit", 888741548, 1.4, -8),
    "league_brand_sfx_r_cast": (P + "R_OnCast", 941240548, 1.4, -8),
    "league_brand_sfx_r_bounce": (P + "R_OnMissileLaunch", 1036548260, 0.6, -10),
    "league_brand_sfx_r_hit": (P + "R_hit", 814047673, 0.6, -10),
    "league_brand_sfx_p_boom": ("Play_sfx_Brand_P_detonate1", 488590296, 1.4, -8),
    "league_brand_sfx_vo_q": (V + "Q_cast3D", 789762179, 1.4, -4),
    "league_brand_sfx_vo_w": (V + "W_cast3D", 1338850688, 1.8, -4),
    "league_brand_sfx_vo_e": (V + "E_cast3D", 86968150, 2.2, -4),
    "league_brand_sfx_vo_r": (V + "R_cast3D", 627385700, 2.0, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_brand_skill": "ASSETS/Characters/Brand/HUD/Icons2D/BrandW.dds",
    "league_brand_skill2": "ASSETS/Characters/Brand/HUD/Icons2D/BrandE.dds",
    "league_brand_ult": "ASSETS/Characters/Brand/HUD/Icons2D/BrandR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Brand.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Brand.{args.lang}.wad.client"))
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
