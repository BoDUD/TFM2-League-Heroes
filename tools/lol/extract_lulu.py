"""Pull Lulu's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_lulu.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Lulu.wad.client and Lulu.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events in the base bank (the client's own names, read from her skin and spell bins): the bolt
LuluBasicAttack_OnCast / _OnHit; Pix's bolts LuluPassiveMissileController_OnMissileCast; Glitterlance LuluQ_OnCast and
LuluQ_hit; Whimsy on an enemy LuluWTwo_OnCast / _OnHit; Help, Pix! Pix's hop LuluFaerieOverride_blink and the shield
LuluFaerieShield_OnBuffActivate; Wild Growth LuluR_OnCast and the growth LuluRBoom_OnBuffActivate. Voice: the Whimsy
(enemy) and Wild Growth lines.
Icons: Lulu_Glitterbolt = skill (Q), Lulu_Whimsy = skill2 (W + E), Lulu_GiantGrowth = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/lulu/skins/base/lulu_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/lulu/skins/base/lulu_base_vo_"  # same in every language
P = "Play_sfx_Lulu_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_lulu_sfx_a": (P + "LuluBasicAttack_OnCast", 94604333, 0.5, -10),
    "league_lulu_sfx_hit": (P + "LuluBasicAttack_OnHit", 2590342, 0.5, -10),
    "league_lulu_sfx_p": (P + "LuluPassiveMissileController_OnMissileCast", 83153764, 0.4, -13),
    "league_lulu_sfx_q": (P + "LuluQ_OnCast", 998039884, 0.8, -8),
    "league_lulu_sfx_q_hit": (P + "LuluQ_hit", 1011703382, 0.5, -9),
    "league_lulu_sfx_w": (P + "LuluWTwo_OnCast", 69425920, 0.5, -8),
    "league_lulu_sfx_w_hit": (P + "LuluWTwo_OnHit", 768435917, 1.0, -7),
    "league_lulu_sfx_e": (P + "LuluFaerieOverride_blink", 280134572, 0.45, -9),
    "league_lulu_sfx_e_shield": (P + "LuluFaerieShield_OnBuffActivate", 1018041099, 1.2, -8),
    "league_lulu_sfx_r": (P + "LuluR_OnCast", 191953457, 0.7, -7),
    "league_lulu_sfx_r_grow": (P + "LuluRBoom_OnBuffActivate", 412872382, 1.8, -6),
    "league_lulu_vo_w": ("Play_vo_Lulu_LuluW_cast3DEnemy", 2141393217, 1.1, -4),
    "league_lulu_vo_r": ("Play_vo_Lulu_LuluR_cast3D", 1114018794, 1.6, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_lulu_skill": "ASSETS/Characters/Lulu/HUD/Icons2D/Lulu_Glitterbolt.dds",
    "league_lulu_skill2": "ASSETS/Characters/Lulu/HUD/Icons2D/Lulu_Whimsy.dds",
    "league_lulu_ult": "ASSETS/Characters/Lulu/HUD/Icons2D/Lulu_GiantGrowth.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Lulu.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Lulu.{args.lang}.wad.client"))
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
