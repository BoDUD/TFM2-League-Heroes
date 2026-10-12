r"""Pull Kassadin's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kassadin.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_gragas.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Kassadin.wad.client and Kassadin.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in his bins, picked by size among the variants): the swipe KassadinBasicAttack_OnCast / _OnHit;
Null Sphere's NullLance_OnMissileLaunch and _OnHit; Nether Blade's NetherBlade_OnCast and _hit; Force Pulse's
ForcePulse_OnCast and _OnHit; Riftwalk's RiftWalk_OnCast and _buffactivate (the arrival). His spells have no voice
lines of their own: the four slots take four takes of his fighting lines (Attack2DGeneral).
Icons: Kassadin_Q = skill (Q), Kassadin_E = skill2 (E, W folded into the attack), Kassadin_R = ult (R); Kassadin_W and
Kassadin_Passive are written too (README / buff icons).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kassadin/skins/base/kassadin_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kassadin/skins/base/kassadin_base_vo_"  # same in every language
P = "Play_sfx_Kassadin_"
V = "Play_vo_Kassadin_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_kassadin_sfx_a_swing": (P + "KassadinBasicAttack_OnCast", 610637764, 0.45, -12),
    "league_kassadin_sfx_a_hit": (P + "KassadinBasicAttack_OnHit", 522616430, 0.6, -12),
    "league_kassadin_sfx_q": (P + "NullLance_OnMissileLaunch", 575535778, 0.9, -10),
    "league_kassadin_sfx_q_hit": (P + "NullLance_OnHit", 940682218, 1.0, -9),
    "league_kassadin_sfx_w": (P + "NetherBlade_OnCast", 287513080, 0.8, -10),
    "league_kassadin_sfx_w_hit": (P + "NetherBlade_hit", 895632474, 0.9, -9),
    "league_kassadin_sfx_e": (P + "ForcePulse_OnCast", 995813327, 0.9, -9),
    "league_kassadin_sfx_e_hit": (P + "ForcePulse_OnHit", 757210083, 0.8, -10),
    "league_kassadin_sfx_r": (P + "RiftWalk_OnCast", 1032762839, 1.0, -9),
    "league_kassadin_sfx_r_hit": (P + "RiftWalk_buffactivate", 891824491, 1.0, -9),
    "league_kassadin_sfx_vo_q": (V + "Attack2DGeneral", 1805154045, 2.2, -4),
    "league_kassadin_sfx_vo_w": (V + "Attack2DGeneral", 1402724244, 2.2, -4),
    "league_kassadin_sfx_vo_e": (V + "Attack2DGeneral", 1081734834, 2.2, -4),
    "league_kassadin_sfx_vo_r": (V + "Attack2DGeneral", 828075495, 2.2, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_kassadin_skill": "ASSETS/Characters/Kassadin/HUD/Icons2D/Kassadin_Q.dds",
    "league_kassadin_skill2": "ASSETS/Characters/Kassadin/HUD/Icons2D/Kassadin_E.dds",
    "league_kassadin_ult": "ASSETS/Characters/Kassadin/HUD/Icons2D/Kassadin_R.dds",
    "league_kassadin_w": "ASSETS/Characters/Kassadin/HUD/Icons2D/Kassadin_W.dds",
    "league_kassadin_passive": "ASSETS/Characters/Kassadin/HUD/Icons2D/Kassadin_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kassadin.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kassadin.{args.lang}.wad.client"))
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
