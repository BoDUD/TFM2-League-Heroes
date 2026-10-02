"""Pull LeBlanc's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_leblanc.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Leblanc.wad.client and Leblanc.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

Her events in the base bank: LeblancBasicAttack_OnMissileLaunch (the orb), LeblancQ_OnCast / _OnHit and
LeblancQDetonate_buffactivate (Q: the sigil and its burst), LeblancW_missilelaunch / _hitlocation and
LeblancWReturn_cast (W: the dash, the blast, the return), LeblancEMissile_missilelaunch, LeblancE_OnBuffActivate and
LeblancERoot_buffactivate_target (E: the chain, the tether, the root), LeblancP_buffactivate_self (the passive's
vanishing), and the mimicked spells' extra layer in LeblancRQ_OnCast (its R variants 188154843 / 549360314 /
543785790); her basic attacks' OnHit events have no media, so the hit borrows a soft variant of Q's. Voice:
LeBlancQ / W / E / P / RQ / RW / RE _cast3D. The icons: LeblancQ = Q, LeblancW = W, LeblancR = R (E rides on the attack
and the passive on the attack and Q, which have no icon of their own).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/leblanc/skins/base/leblanc_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/leblanc/skins/base/leblanc_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_leblanc_sfx_attack": ("Play_sfx_Leblanc_LeblancBasicAttack_OnMissileLaunch", 699496021, 0.6, -10),
    "league_leblanc_sfx_attack_hit": ("Play_sfx_Leblanc_LeblancQ_OnHit", 160525364, 0.5, -14),
    "league_leblanc_sfx_q_cast": ("Play_sfx_Leblanc_LeblancQ_OnCast", 28542573, 0.8, -7),
    "league_leblanc_sfx_q_hit": ("Play_sfx_Leblanc_LeblancQ_OnHit", 954172860, 0.8, -8),
    "league_leblanc_sfx_q_pop": ("Play_sfx_Leblanc_LeblancQDetonate_buffactivate", 1009323411, 1.2, -6),
    "league_leblanc_sfx_w_cast": ("Play_sfx_Leblanc_LeblancW_missilelaunch", 436058226, 0.9, -7),
    "league_leblanc_sfx_w_hit": ("Play_sfx_Leblanc_LeblancW_hitlocation", 7178671, 1.2, -6),
    "league_leblanc_sfx_w_back": ("Play_sfx_Leblanc_LeblancWReturn_cast", 196128323, 1.2, -7),
    "league_leblanc_sfx_e_cast": ("Play_sfx_Leblanc_LeblancEMissile_missilelaunch", 35208391, 1.0, -7),
    "league_leblanc_sfx_e_hit": ("Play_sfx_Leblanc_LeblancE_OnBuffActivate", 494097158, 1.2, -8),
    "league_leblanc_sfx_e_root": ("Play_sfx_Leblanc_LeblancERoot_buffactivate_target", 88338608, 1.6, -6),
    "league_leblanc_sfx_p_cast": ("Play_sfx_Leblanc_LeblancP_buffactivate_self", 799628405, 1.8, -6),
    "league_leblanc_sfx_r_cast": ("Play_sfx_Leblanc_LeblancRQ_OnCast", 188154843, 1.2, -6),
    "league_leblanc_vo_q": ("Play_vo_Leblanc_LeBlancQ_cast3D", 507493015, 1.6, -2),
    "league_leblanc_vo_w": ("Play_vo_Leblanc_LeBlancW_cast3D", 351696877, 1.4, -2),
    "league_leblanc_vo_e": ("Play_vo_Leblanc_LeBlancE_cast3D", 411760926, 1.8, -2),
    "league_leblanc_vo_p": ("Play_vo_Leblanc_LeBlancP_cast3D", 655657990, 3.2, -2),
    "league_leblanc_vo_rq": ("Play_vo_Leblanc_LeBlancRQ_cast3D", 243845907, 2.6, -2),
    "league_leblanc_vo_rw": ("Play_vo_Leblanc_LeBlancRW_cast3D", 1279878036, 2.6, -2),
    "league_leblanc_vo_re": ("Play_vo_Leblanc_LeBlancRE_cast3D", 779757931, 2.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_leblanc_skill": "ASSETS/Characters/Leblanc/HUD/Icons2D/LeblancQ.dds",
    "league_leblanc_skill2": "ASSETS/Characters/Leblanc/HUD/Icons2D/LeblancW.dds",
    "league_leblanc_ult": "ASSETS/Characters/Leblanc/HUD/Icons2D/LeblancR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Leblanc.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Leblanc.{args.lang}.wad.client"))
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
            print(f"{name:34s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:34s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
