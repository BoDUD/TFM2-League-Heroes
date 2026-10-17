"""Pull Kai'Sa's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kaisa.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Kaisa.wad.client and Kaisa.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events in the base bank: KaisaBasicAttack_OnMissileLaunch (the plasma bolt) / _OnHit, KaisaPassiveAttack_hit's
two long variants (the rupture; the four short ones are the plain hit's), KaisaE_OnCast (Supercharge), KaisaEvolve
Self_cast, KaisaQ_OnCast (the pods opening) and KaisaQLeftMissile1_OnHit (one missile; up to twelve land, so it is
short and quiet), KaisaW_OnCast (the charge), KaisaW_OnHit's first four variants (the long shot - the same media as
KaisaW_OnMissileCast) and last four (the hit), KaisaR_OnCast, KaisaRDashCas_cast (the dash), KaisaRShield_OnBuff
Activate (the shield on landing). Voice: Q, W and R casts (E's lines run 4 s: left out).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kaisa/skins/base/kaisa_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kaisa/skins/base/kaisa_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_kaisa_sfx_attack_shot": ("Play_sfx_Kaisa_KaisaBasicAttack_OnMissileLaunch", 987882739, 0.5, -9),
    "league_kaisa_sfx_attack_hit": ("Play_sfx_Kaisa_KaisaBasicAttack_OnHit", 655294233, 0.45, -12),
    "league_kaisa_sfx_p_burst": ("Play_sfx_Kaisa_KaisaPassiveAttack_hit", 335518900, 1.2, -5),
    "league_kaisa_sfx_e_cast": ("Play_sfx_Kaisa_KaisaE_OnCast", 115561481, 1.6, -7),
    "league_kaisa_sfx_evolve": ("Play_sfx_Kaisa_KaisaEvolveSelf_cast", 473707729, 1.6, -5),
    "league_kaisa_sfx_q_cast": ("Play_sfx_Kaisa_KaisaQ_OnCast", 858046194, 1.4, -6),
    "league_kaisa_sfx_q_hit": ("Play_sfx_Kaisa_KaisaQLeftMissile1_OnHit", 638023863, 0.7, -13),
    "league_kaisa_sfx_w_cast": ("Play_sfx_Kaisa_KaisaW_OnCast", 886967540, 1.1, -8),
    "league_kaisa_sfx_w_fire": ("Play_sfx_Kaisa_KaisaW_OnHit", 612184376, 1.5, -5),
    "league_kaisa_sfx_w_hit": ("Play_sfx_Kaisa_KaisaW_OnHit", 432165955, 1.2, -6),
    "league_kaisa_sfx_r_cast": ("Play_sfx_Kaisa_KaisaR_OnCast", 909982851, 1.3, -6),
    "league_kaisa_sfx_r_dash": ("Play_sfx_Kaisa_KaisaRDashCas_cast", 339719110, 0.9, -6),
    "league_kaisa_sfx_r_land": ("Play_sfx_Kaisa_KaisaRShield_OnBuffActivate", 275292210, 1.5, -6),
    "league_kaisa_vo_q": ("Play_vo_Kaisa_KaisaQ_cast3D", 609832642, 1.0, -2),
    "league_kaisa_vo_w": ("Play_vo_Kaisa_KaisaW_cast3D", 1957921471, 1.1, -2),
    "league_kaisa_vo_r": ("Play_vo_Kaisa_KaisaR_cast3D", 1834298492, 0.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Supercharge and the passive ride on the attack)
    "league_kaisa_skill": "ASSETS/Characters/Kaisa/HUD/Icons2D/Kaisa_Q.dds",
    "league_kaisa_skill2": "ASSETS/Characters/Kaisa/HUD/Icons2D/Kaisa_W.dds",
    "league_kaisa_ult": "ASSETS/Characters/Kaisa/HUD/Icons2D/Kaisa_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kaisa.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kaisa.{args.lang}.wad.client"))
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
