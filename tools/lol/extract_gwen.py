"""Pull Gwen's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_gwen.py --lol D:/WeGameApps/lol --vgmstream path/to/vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Gwen.wad.client and Gwen.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events (plain strings in the WAD's .bin files) are Play_sfx_Gwen_Gwen<spell>_<event>. The attack's snip is
BasicAttack_Swipe_cast / _hit. Snip Snip!: Q_OnCast (the scissors open), QFirst_cast (one small snip, 0.23 s: every
mini cut), QLast_cast (the big one), QFirst_hit, QLast_hit_center (the true-damage centre). Skip 'n Slash: E_OnCast.
Hallowed Mist: W_buffactivate (the mist settling). Needlework: R_OnCast, R_missile (each volley), RMis_OnHitLocation.
Voice: QFirst/W/E/R cast3D.
Icons: Gwen_Q = skill, Gwen_E = skill2 (E leads the combo), Gwen_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/gwen/skins/base/gwen_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/gwen/skins/base/gwen_base_vo_"  # same in every language
P = "Play_sfx_Gwen_Gwen"
V = "Play_vo_Gwen_Gwen"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_gwen_sfx_a_swing": (P + "BasicAttack_Swipe_cast", 869530993, 0.5, -11),
    "league_gwen_sfx_a_hit": (P + "BasicAttack_Swipe_hit", 843161985, 0.4, -12),
    "league_gwen_sfx_q_open": (P + "Q_OnCast", 475827131, 0.8, -10),
    "league_gwen_sfx_q_snip": (P + "QFirst_cast", 719286715, 0.23, -12),
    "league_gwen_sfx_q_final": (P + "QLast_cast", 820524486, 0.7, -8),
    "league_gwen_sfx_q_hit": (P + "QFirst_hit", 115397365, 0.4, -13),
    "league_gwen_sfx_q_true": (P + "QLast_hit_center", 396871256, 0.5, -10),
    "league_gwen_sfx_e_cast": (P + "E_OnCast", 804849398, 0.6, -9),
    "league_gwen_sfx_w_cast": (P + "W_buffactivate", 574607003, 1.4, -9),
    "league_gwen_sfx_r_cast": (P + "R_OnCast", 675991025, 0.6, -9),
    "league_gwen_sfx_r_throw": (P + "R_missile", 380331369, 0.8, -9),
    "league_gwen_sfx_r_hit": (P + "RMis_OnHitLocation", 209986543, 0.3, -12),
    "league_gwen_vo_q": (V + "Q_cast3D", 448126549, 1.4, -4),
    "league_gwen_vo_w": (V + "W_cast3D", 476878312, 1.2, -4),
    "league_gwen_vo_e": (V + "E_cast3D", 1432988918, 0.8, -4),
    "league_gwen_vo_r": (V + "R_cast3D", 380381241, 1.2, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_gwen_skill": "ASSETS/Characters/Gwen/HUD/Icons2D/Gwen_Q.dds",
    "league_gwen_skill2": "ASSETS/Characters/Gwen/HUD/Icons2D/Gwen_E.dds",
    "league_gwen_ult": "ASSETS/Characters/Gwen/HUD/Icons2D/Gwen_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Gwen.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Gwen.{args.lang}.wad.client"))
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
