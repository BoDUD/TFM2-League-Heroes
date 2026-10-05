"""Pull Tryndamere's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_tryndamere.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Tryndamere.wad.client and Tryndamere.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank (the event names are plain strings in the WAD's .bin files): the swing is
TryndamereBasicAttack_OnCast and lands with _OnHit; Spinning Slash casts with TryndamereE_OnCast and hits with
TryndamereE_hit; Mocking Shout is TryndamereW_OnHit (a 2 s clip the bank loops); Undying Rage casts with
UndyingRage_OnCast and ends with UndyingRage_OnBuffDeactivate; Bloodlust is TryndamereQ_OnCast (the short variant).
His base voice bank has no spell lines (only the skins' banks do): Spell3DBasic (his attack shouts) for E, the taunt
for W and one Attack2DGeneral line for R.
Icons: Tryndamere_E = skill, Tryndamere_W = skill2, Tryndamere_R = ult (Q is folded into R, the passive into the attack).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/tryndamere/skins/base/tryndamere_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/tryndamere/skins/base/tryndamere_base_vo_"  # same in every language
P = "Play_sfx_Tryndamere_"
V = "Play_vo_Tryndamere_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_tryndamere_sfx_swing": (P + "TryndamereBasicAttack_OnCast", 471462952, 0.5, -9),
    "league_tryndamere_sfx_hit": (P + "TryndamereBasicAttack_OnHit", 966903000, 0.45, -12),
    "league_tryndamere_sfx_e": (P + "TryndamereE_OnCast", 228155261, 1.0, -8),
    "league_tryndamere_sfx_e_hit": (P + "TryndamereE_hit", 61397512, 0.6, -11),
    "league_tryndamere_sfx_w": (P + "TryndamereW_OnHit", 291210465, 1.2, -8),
    "league_tryndamere_sfx_r": (P + "UndyingRage_OnCast", 529922339, 1.5, -8),
    "league_tryndamere_sfx_r_end": (P + "UndyingRage_OnBuffDeactivate", 384020892, 1.0, -9),
    "league_tryndamere_sfx_q": (P + "TryndamereQ_OnCast", 576073200, 1.2, -8),
    "league_tryndamere_vo_e": (V + "Spell3DBasic", 1547723890, 1.0, -4),
    "league_tryndamere_vo_w": (V + "Taunt3DGeneral", 1483581180, 1.8, -4),
    "league_tryndamere_vo_r": (V + "Attack2DGeneral", 433182524, 1.7, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_tryndamere_skill": "ASSETS/Characters/Tryndamere/HUD/Icons2D/Tryndamere_E.dds",
    "league_tryndamere_skill2": "ASSETS/Characters/Tryndamere/HUD/Icons2D/Tryndamere_W.dds",
    "league_tryndamere_ult": "ASSETS/Characters/Tryndamere/HUD/Icons2D/Tryndamere_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Tryndamere.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Tryndamere.{args.lang}.wad.client"))
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
