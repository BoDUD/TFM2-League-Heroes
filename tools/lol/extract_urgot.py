r"""Pull Urgot's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_urgot.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_pantheon.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Urgot.wad.client and Urgot.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in skin0.bin): the shot UrgotBasicAttack_OnMissileLaunch / _OnHit; Echoing Flames' leg UrgotP_cast;
Purge's start UrgotW_OnCast and each gun shot UrgotWMissileExtra_OnMissileLaunch; Corrosive Charge's throw UrgotQ_OnCast
and blast UrgotQ_hit; Disdain's charge UrgotE_OnCast and the toss UrgotEToss_OnBuffCast; Fear Beyond Death's cast
UrgotR_OnCast, the drill UrgotR_OnMissileLaunch and its hit UrgotR_OnHit, the execution's grinders UrgotRGrind_cast and
the fear UrgotRGrind_fear_hit. Voice: UrgotQ_cast3D, Spell3DEHit, UrgotR_cast3D, UrgotRRecastMissile_cast3D (the
execution).
Icons: Urgot_Q (Corrosive Charge) = skill, Urgot_E (Disdain) = skill2, Urgot_R (Fear Beyond Death) = ult; W (Purge,
told in Q's and E's texts) and the passive are written too (league_urgot_w / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/urgot/skins/base/urgot_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/urgot/skins/base/urgot_base_vo_"  # same in every language
P = "Play_sfx_Urgot_Urgot"
V = "Play_vo_Urgot_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_urgot_sfx_a_shot": (P + "BasicAttack_OnMissileLaunch", 295133134, 0.8, -13),
    "league_urgot_sfx_a_hit": (P + "BasicAttack_OnHit", 77645252, 0.6, -14),
    "league_urgot_sfx_p_leg": (P + "P_cast", 19085774, 1.0, -12),
    "league_urgot_sfx_w_on": (P + "W_OnCast", 264170470, 1.2, -12),
    "league_urgot_sfx_w_shot": (P + "WMissileExtra_OnMissileLaunch", 1023839766, 0.4, -16),
    "league_urgot_sfx_q": (P + "Q_OnCast", 965654765, 0.8, -12),
    "league_urgot_sfx_q_land": (P + "Q_hit", 441733458, 1.2, -10),
    "league_urgot_sfx_e": (P + "E_OnCast", 583277064, 1.2, -11),
    "league_urgot_sfx_e_hit": (P + "EToss_OnBuffCast", 247818755, 1.2, -11),
    "league_urgot_sfx_r": (P + "R_OnCast", 924147906, 1.4, -11),
    "league_urgot_sfx_r_fire": (P + "R_OnMissileLaunch", 58479280, 1.2, -10),
    "league_urgot_sfx_r_hit": (P + "R_OnHit", 365431487, 1.2, -10),
    "league_urgot_sfx_r_ex": (P + "RGrind_cast", 837423464, 1.6, -10),
    "league_urgot_sfx_r_fear": (P + "RGrind_fear_hit", 1004693697, 1.2, -10),
    "league_urgot_sfx_vo_q": (V + "UrgotQ_cast3D", 1268956908, 2.0, -6),
    "league_urgot_sfx_vo_e": (V + "Spell3DEHit", 1442286312, 2.0, -6),
    "league_urgot_sfx_vo_r": (V + "UrgotR_cast3D", 1377706129, 2.6, -6),
    "league_urgot_sfx_vo_r_kill": (V + "UrgotRRecastMissile_cast3D", 527175340, 2.6, -6),
}
I = "ASSETS/Characters/Urgot/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_urgot_skill": I + "Urgot_Q.dds",
    "league_urgot_skill2": I + "Urgot_E.dds",
    "league_urgot_ult": I + "Urgot_R.dds",
    "league_urgot_w": I + "Urgot_W.dds",
    "league_urgot_passive": I + "Urgot_Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Urgot.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Urgot.{args.lang}.wad.client"))
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
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
