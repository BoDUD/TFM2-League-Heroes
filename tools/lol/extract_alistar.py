"""Pull Alistar's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_alistar.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Alistar.wad.client and Alistar.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank (the client's own names): the punch AlistarBasicAttack_OnHit (its _OnCast clips are 12 s
of near silence); Pulverize casts with Pulverize_OnCast and slams with Pulverize_hitlocation; Headbutt_OnCast (the
charge) and Headbutt_hit; Trample AlistarE_hitlocation (a stomp), AlistarE_stack_final (the fifth stomp: the stun is
ready) and AlistarE_stun_buffactivate (the stun); Triumphant Roar AlistarP_cast; Unbreakable Will FerociousHowl_OnCast
(the roar). Voice: the Pulverize and Headbutt lines (the bank has no R line).
Icons: Alistar_Q = skill (E -> Q), Alistar_W = skill2 (W -> Q), Alistar_R = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/alistar/skins/base/alistar_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/alistar/skins/base/alistar_base_vo_"  # same in every language
P = "Play_sfx_Alistar_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_alistar_sfx_hit": (P + "AlistarBasicAttack_OnHit", 39949762, 0.5, -10),
    "league_alistar_sfx_q": (P + "Pulverize_OnCast", 782960778, 0.45, -9),
    "league_alistar_sfx_q_hit": (P + "Pulverize_hitlocation", 631107946, 0.9, -6),
    "league_alistar_sfx_w": (P + "Headbutt_OnCast", 1027165527, 0.8, -8),
    "league_alistar_sfx_w_hit": (P + "Headbutt_hit", 305751988, 0.6, -7),
    "league_alistar_sfx_e": (P + "AlistarE_hitlocation", 892248280, 0.6, -10),
    "league_alistar_sfx_e_ready": (P + "AlistarE_stack_final", 398621294, 0.6, -8),
    "league_alistar_sfx_e_stun": (P + "AlistarE_stun_buffactivate", 358684648, 0.8, -8),
    "league_alistar_sfx_p": (P + "AlistarP_cast", 699599675, 1.4, -7),
    "league_alistar_sfx_r": (P + "FerociousHowl_OnCast", 837801669, 1.8, -6),
    "league_alistar_vo_q": ("Play_vo_Alistar_Pulverize_cast3D", 2087350870, 0.9, -4),
    "league_alistar_vo_w": ("Play_vo_Alistar_Headbutt_cast3D", 704390147, 1.0, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_alistar_skill": "ASSETS/Characters/Alistar/HUD/Icons2D/Alistar_Q.dds",
    "league_alistar_skill2": "ASSETS/Characters/Alistar/HUD/Icons2D/Alistar_W.dds",
    "league_alistar_ult": "ASSETS/Characters/Alistar/HUD/Icons2D/Alistar_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Alistar.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Alistar.{args.lang}.wad.client"))
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
