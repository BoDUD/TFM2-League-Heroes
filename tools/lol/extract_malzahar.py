r"""Pull Malzahar's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_malzahar.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_bard.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Malzahar.wad.client and Malzahar.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.

His events (named in skin0.bin, listed with %TEMP%/mz_work/sndprobe.py; the clearest variant of each): the attack
MalZaharBasicAttack_OnMissileLaunch / _OnHit; Void Shift's MalzaharPassiveShield_OnBuffActivate; Malefic Visions'
MalzaharE_OnCast and _OnBuffActivate (the burn landing, another variant for the jump); the voidlings'
MalzaharVoidling_buffactivate (spawn) and MalzaharVoidlingBasicAttack_OnHit (bite); Call of the Void's MalzaharQ_OnCast,
_missilelaunch (the rifts closing) and _buffactivate (the silence); Nether Grasp's MalzaharR_OnBuffActivate (the grasp,
a short one for every wave) and MalzaharRZone_buffactivate (the null zone). Voice: MalzaharQ_cast3D / MalzaharE_cast3D
(one pool, two different lines) and MalzaharR_hit3D. Clip names differ from the sound names (league_malzahar_sfx_vo_*,
memory vo-clip-names).
Icons: Malzahar_E = skill (E + W), Malzahar_Q = skill2, Malzahar_R = ult; W and the passive are written too (README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/malzahar/skins/base/malzahar_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/malzahar/skins/base/malzahar_base_vo_"  # same in every language
P = "Play_sfx_Malzahar_"
PV = "Play_sfx_MalzaharVoidling_"
V = "Play_vo_Malzahar_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_malzahar_sfx_a_cast": (P + "MalZaharBasicAttack_OnMissileLaunch", 507102217, 0.6, -13),
    "league_malzahar_sfx_a_hit": (P + "MalZaharBasicAttack_OnHit", 425603493, 0.5, -13),
    "league_malzahar_sfx_p_shift": (P + "MalzaharPassiveShield_OnBuffActivate", 272217207, 0.8, -12),
    "league_malzahar_sfx_e_cast": (P + "MalzaharE_OnCast", 701391027, 0.6, -11),
    "league_malzahar_sfx_e_hit": (P + "MalzaharE_OnBuffActivate", 295049387, 1.0, -11),
    "league_malzahar_sfx_e_jump": (P + "MalzaharE_OnBuffActivate", 1030778148, 1.0, -11),
    "league_malzahar_sfx_w_spawn": (P + "MalzaharVoidling_buffactivate", 584044127, 0.8, -12),
    "league_malzahar_sfx_w_bite": (PV + "MalzaharVoidlingBasicAttack_OnHit", 672191120, 0.4, -15),
    "league_malzahar_sfx_q_cast": (P + "MalzaharQ_OnCast", 31904061, 0.8, -10),
    "league_malzahar_sfx_q_close": (P + "MalzaharQ_missilelaunch", 819621174, 0.8, -10),
    "league_malzahar_sfx_q_hit": (P + "MalzaharQ_buffactivate", 252660833, 0.9, -11),
    "league_malzahar_sfx_r_cast": (P + "MalzaharR_OnBuffActivate", 266716837, 1.4, -8),
    "league_malzahar_sfx_r_tick": (P + "MalzaharR_OnBuffActivate", 508933268, 0.3, -14),
    "league_malzahar_sfx_r_pool": (P + "MalzaharRZone_buffactivate", 995461833, 1.4, -10),
    "league_malzahar_sfx_vo_q": (V + "MalzaharQ_cast3D", 1556452098, 1.6, -6),
    "league_malzahar_sfx_vo_e": (V + "MalzaharE_cast3D", 951437620, 1.6, -6),
    "league_malzahar_sfx_vo_r": (V + "MalzaharR_hit3D", 1650059502, 2.0, -6),
}
I = "ASSETS/Characters/Malzahar/HUD/Icons2D/Malzahar_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_malzahar_skill": I + "E.dds",
    "league_malzahar_skill2": I + "Q.dds",
    "league_malzahar_ult": I + "R.dds",
    "league_malzahar_w": I + "W.dds",
    "league_malzahar_passive": I + "Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Malzahar.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Malzahar.{args.lang}.wad.client"))
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
