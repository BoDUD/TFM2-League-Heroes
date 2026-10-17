"""Pull Tristana's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_tristana.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Tristana.wad.client and Tristana.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her events in the base bank: TristanaBasicAttack_OnCast (the cannon's shot) / _OnHit (20 impacts),
TristanaQ_OnCast (Rapid Fire's reload), TristanaE_OnCast (the throw), TristanaE_OnHit (the charge sticking),
TristanaE_stack (a stack added), TristanaEChargeSound_buffdeactivate (the charge exploding; the base bins only
name its empty variants, the WAD's other bins name this one), TristanaW_OnCast (the launch), TristanaWSlow_hit
(the landing), TristanaR_OnCast / _OnMissileLaunch / _OnHit (Buster Shot). The kill explosion (Explosive Charge's
passive) has no event of its own: a quieter take of the charge's explosion.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/tristana/skins/base/tristana_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/tristana/skins/base/tristana_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_tristana_sfx_attack_shot": ("Play_sfx_Tristana_TristanaBasicAttack_OnCast", 809448885, 0.6, -8),
    "league_tristana_sfx_attack_hit": ("Play_sfx_Tristana_TristanaBasicAttack_OnHit", 356227766, 0.45, -9),
    "league_tristana_sfx_q_cast": ("Play_sfx_Tristana_TristanaQ_OnCast", 487512625, 1.2, -7),
    "league_tristana_sfx_e_cast": ("Play_sfx_Tristana_TristanaE_OnCast", 533978940, 0.6, -7),
    "league_tristana_sfx_e_plant": ("Play_sfx_Tristana_TristanaE_OnHit", 1029420245, 0.7, -7),
    "league_tristana_sfx_e_stack": ("Play_sfx_Tristana_TristanaE_stack", 907859369, 0.45, -9),
    "league_tristana_sfx_e_boom": ("Play_sfx_Tristana_TristanaEChargeSound_buffdeactivate", 526656350, 1.4, -4),
    "league_tristana_sfx_p_boom": ("Play_sfx_Tristana_TristanaEChargeSound_buffdeactivate", 993109953, 0.9, -10),
    "league_tristana_sfx_w_cast": ("Play_sfx_Tristana_TristanaW_OnCast", 101255389, 0.8, -6),
    "league_tristana_sfx_w_land": ("Play_sfx_Tristana_TristanaWSlow_hit", 828998145, 1.2, -5),
    "league_tristana_sfx_r_cast": ("Play_sfx_Tristana_TristanaR_OnCast", 757141173, 1.2, -5),
    "league_tristana_sfx_r_launch": ("Play_sfx_Tristana_TristanaR_OnMissileLaunch", 657676408, 0.8, -6),
    "league_tristana_sfx_r_hit": ("Play_sfx_Tristana_TristanaR_OnHit", 560806986, 1.3, -4),
    "league_tristana_vo_q": ("Play_vo_Tristana_TristanaQ_cast3D", 1994069507, 1.2, -2),
    "league_tristana_vo_e": ("Play_vo_Tristana_TristanaE_cast3D", 1822618912, 0.9, -2),
    "league_tristana_vo_w": ("Play_vo_Tristana_TristanaW_cast3D", 371267577, 0.7, -2),
    "league_tristana_vo_r": ("Play_vo_Tristana_TristanaR_hit3D", 638760856, 1.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Rapid Fire rides on Explosive Charge, Draw a Bead on the attack)
    "league_tristana_skill": "ASSETS/Characters/Tristana/HUD/Icons2D/Tristana_E.dds",
    "league_tristana_skill2": "ASSETS/Characters/Tristana/HUD/Icons2D/Tristana_W.dds",
    "league_tristana_ult": "ASSETS/Characters/Tristana/HUD/Icons2D/Tristana_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Tristana.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Tristana.{args.lang}.wad.client"))
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
