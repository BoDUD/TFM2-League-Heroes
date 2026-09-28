"""Pull Ekko's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ekko.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Ekko.wad.client and Ekko.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Ekko's skin bin. Timewinder has a throw, a field that hums while it
lasts (its 4.8 s loop is cut to the field's second) and a return; Parallel Convergence has a cast,
the sphere forming where it lands and the stun-and-shield burst (EkkoWShield). Phase Dive's roll
and its blink strike are two sounds; Chronobreak's cast and its rewind (the buff ending) as well.
Z-Drive Resonance's third hit has a sound of its own. Every zh_CN voice line picked here differs
from en_US (none is a wordless shout); Q, W and R get one each, E none (skill2 casts every 7 s).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ekko/skins/base/ekko_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ekko/skins/base/ekko_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_ekko_sfx_attack_hit": ("Play_sfx_Ekko_EkkoBasicAttack_OnHit", 31053442, 0.8, -8),
    "league_ekko_sfx_z_proc": ("Play_sfx_Ekko_EkkoPassive_hit", 614206374, 1.0, -5),
    "league_ekko_sfx_q_cast": ("Play_sfx_Ekko_EkkoQ_OnCast", 142670307, 0.9, -5),
    "league_ekko_sfx_q_hit": ("Play_sfx_Ekko_EkkoQMis_hit", 143821687, 0.7, -7),
    "league_ekko_sfx_q_field": ("Play_sfx_Ekko_EkkoQMis_buffactivate", 642266259, 1.0, -8),
    "league_ekko_sfx_q_return": ("Play_sfx_Ekko_EkkoQReturn_OnMissileLaunch", 1070920809, 1.1, -6),
    "league_ekko_sfx_w_cast": ("Play_sfx_Ekko_EkkoW_OnCast", 668602696, 1.2, -6),
    "league_ekko_sfx_w_form": ("Play_sfx_Ekko_EkkoWMis_OnHitLocation", 536965158, 2.0, -7),
    "league_ekko_sfx_w_boom": ("Play_sfx_Ekko_EkkoWShield_OnBuffCast", 3275188, 1.6, -4),
    "league_ekko_sfx_e_cast": ("Play_sfx_Ekko_EkkoE_OnCast", 493849336, 0.8, -6),
    "league_ekko_sfx_e_hit": ("Play_sfx_Ekko_EkkoEAttack_OnHit", 804657956, 1.2, -5),
    "league_ekko_sfx_r_cast": ("Play_sfx_Ekko_EkkoR_OnCast", 499800238, 0.9, -5),
    "league_ekko_sfx_r_rewind": ("Play_sfx_Ekko_EkkoR_buffdeactivate", 799097783, 2.2, -3),
    "league_ekko_vo_q": ("Play_vo_Ekko_EkkoQ_cast3D", 1219931135, 1.5, -2),
    "league_ekko_vo_w": ("Play_vo_Ekko_EkkoW_cast3D", 850402348, 1.5, -2),
    "league_ekko_vo_r": ("Play_vo_Ekko_EkkoR_cast3D", 1566055489, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill2 is E with W folded in: E's icon)
    "league_ekko_skill": "ASSETS/Characters/Ekko/HUD/Icons2D/Ekko_Q.dds",
    "league_ekko_skill2": "ASSETS/Characters/Ekko/HUD/Icons2D/Ekko_E.dds",
    "league_ekko_ult": "ASSETS/Characters/Ekko/HUD/Icons2D/Ekko_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ekko.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ekko.{args.lang}.wad.client"))
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
