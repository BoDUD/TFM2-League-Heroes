r"""Pull Tahm Kench's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_tahmkench.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_elise.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/TahmKench.wad.client and TahmKench.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

His events (named in skin0.bin): the tongue slap TahmKenchBasicAttack_OnCast / _OnHit; An Acquired Taste's stack
TahmKenchP_buffactivate; Tongue Lash TahmKenchQ_OnCast, TahmKenchQMissile_hit / _stun and TahmKenchQ_heal; Abyssal Dive
TahmKenchW_OnCast (the dive), _warning_enemy (the bubbles where he comes up) and TahmKenchWKnockup_OnBuffCast (the
landing); Thick Skin TahmKenchE_heal and TahmKenchEShield_buffdeactivate (the shield); Devour
TahmKenchRTargetEnemy_buffactivate (an enemy swallowed), TahmKenchR_buffactivate (an ally) and _buffdeactivate (the
spit). Voice: TahmKenchQ / W / E_cast3D, Attack2DGeneral for the devour, Spell3DREnd for the spit.
Icons: TahmKenchQ = skill, TahmKenchW = skill2, TahmKenchRWrapper = ult; E and the passive are written too
(league_tahmkench_e / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/tahmkench/skins/base/tahmkench_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/tahmkench/skins/base/tahmkench_base_vo_"  # same in every language

P = "Play_sfx_TahmKench_TahmKench"
V = "Play_vo_TahmKench_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_tahmkench_sfx_a_swing": (P + "BasicAttack_OnCast", 1059239467, 0.5, -13),
    "league_tahmkench_sfx_a_hit": (P + "BasicAttack_OnHit", 311086832, 0.6, -12),
    "league_tahmkench_sfx_p_stack": (P + "P_buffactivate", 452081676, 0.8, -13),
    "league_tahmkench_sfx_q": (P + "Q_OnCast", 496978628, 0.8, -12),
    "league_tahmkench_sfx_q_hit": (P + "QMissile_hit", 845802187, 0.8, -11),
    "league_tahmkench_sfx_q_stun": (P + "QMissile_stun", 110197506, 1.2, -11),
    "league_tahmkench_sfx_q_heal": (P + "Q_heal", 147185757, 1.0, -13),
    "league_tahmkench_sfx_w": (P + "W_OnCast", 733648669, 1.6, -11),
    "league_tahmkench_sfx_w_warn": (P + "W_warning_enemy", 33213547, 1.4, -12),
    "league_tahmkench_sfx_w_land": (P + "WKnockup_OnBuffCast", 986811136, 1.2, -10),
    "league_tahmkench_sfx_e_heal": (P + "E_heal", 386786145, 1.6, -13),
    "league_tahmkench_sfx_e_shield": (P + "EShield_buffdeactivate", 770914236, 1.0, -12),
    "league_tahmkench_sfx_r_enemy": (P + "RTargetEnemy_buffactivate", 569292774, 2.6, -10),
    "league_tahmkench_sfx_r_ally": (P + "R_buffactivate", 197067368, 1.6, -11),
    "league_tahmkench_sfx_r_spit": (P + "R_buffdeactivate", 954233518, 1.0, -11),
    "league_tahmkench_sfx_vo_q": (V + "TahmKenchQ_cast3D", 678765359, 1.6, -6),
    "league_tahmkench_sfx_vo_w": (V + "TahmKenchW_cast3D", 1603871270, 1.6, -6),
    "league_tahmkench_sfx_vo_e": (V + "TahmKenchE_cast3D", 1763100268, 2.4, -6),
    "league_tahmkench_sfx_vo_r": (V + "Attack2DGeneral", 464219399, 3.0, -6),
    "league_tahmkench_sfx_vo_r_end": (V + "Spell3DREnd", 502953741, 1.6, -6),
}
I = "ASSETS/Characters/TahmKench/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_tahmkench_skill": I + "TahmKenchQ.dds",
    "league_tahmkench_skill2": I + "TahmKenchW.dds",
    "league_tahmkench_ult": I + "TahmKenchRWrapper.dds",
    "league_tahmkench_e": I + "TahmKenchE.dds",
    "league_tahmkench_passive": I + "TahmKenchP.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "TahmKench.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"TahmKench.{args.lang}.wad.client"))
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
