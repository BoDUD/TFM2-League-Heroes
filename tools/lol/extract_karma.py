r"""Pull Karma's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_karma.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_kogmaw.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Karma.wad.client and Karma.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

Her events (found in her bins by work/kr/snd_names_kr.py, picked with work/kr/snd_probe_kr.py): the bolt
KarmaBasicAttack_OnMissileLaunch / _OnHit; Inner Flame KarmaQ_OnCast and KarmaQMissile_hit, Soulflare
KarmaQMissileMantra_hit (the burst) and its long variant (the field, its blast 1.5 s in: played when the field
appears, so the blast lands with the zone); Focused Resolve KarmaSpiritBind_OnCast and KarmaSpiritBindRoot_OnBuffActivate
(the snap); Inspire KarmaSolKimShield_OnCast, Defiance _buffactivatemantra; Mantra KarmaMantra_OnCast. Voice: Q, W,
E, R.
Icons: Karma_Q1 = skill (Q), Karma_W1 = skill2 (W), Karma_R = ult (Mantra).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/karma/skins/base/karma_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/karma/skins/base/karma_base_vo_"  # same in every language
P = "Play_sfx_Karma_Karma"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_karma_sfx_attack": (P + "BasicAttack_OnMissileLaunch", 435611240, 0.45, -11),
    "league_karma_sfx_attack_hit": (P + "BasicAttack_OnHit", 202554870, 0.45, -12),
    "league_karma_sfx_q": (P + "Q_OnCast", 104708941, 0.6, -10),
    "league_karma_sfx_q_hit": (P + "QMissile_hit", 107140710, 0.5, -9),
    "league_karma_sfx_rq_hit": (P + "QMissileMantra_hit", 578766782, 0.55, -8),
    "league_karma_sfx_rq_field": (P + "QMissileMantra_hit", 354744757, 2.1, -8),
    "league_karma_sfx_w": (P + "SpiritBind_OnCast", 338687296, 0.7, -10),
    "league_karma_sfx_w_root": (P + "SpiritBindRoot_OnBuffActivate", 113026965, 0.65, -9),
    "league_karma_sfx_e": (P + "SolKimShield_OnCast", 797404209, 1.1, -10),
    "league_karma_sfx_re": (P + "SolKimShield_buffactivatemantra", 987187396, 1.2, -9),
    "league_karma_sfx_r": (P + "Mantra_OnCast", 714769365, 0.5, -9),
    "league_karma_sfx_vo_q": ("Play_vo_Karma_KarmaQ_cast3D", 269970530, 0.4, -4),
    "league_karma_sfx_vo_w": ("Play_vo_Karma_KarmaSpiritBind_cast3D", 433711032, 0.8, -4),
    "league_karma_sfx_vo_e": ("Play_vo_Karma_KarmaSolKimShield_cast3D", 414173550, 0.95, -4),
    "league_karma_sfx_vo_r": ("Play_vo_Karma_KarmaMantra_cast3D", 951716649, 1.55, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_karma_skill": "ASSETS/Characters/Karma/HUD/Icons2D/Karma_Q1.dds",
    "league_karma_skill2": "ASSETS/Characters/Karma/HUD/Icons2D/Karma_W1.dds",
    "league_karma_ult": "ASSETS/Characters/Karma/HUD/Icons2D/Karma_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Karma.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Karma.{args.lang}.wad.client"))
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
