"""Pull Xin Zhao's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_xinzhao.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/XinZhao.wad.client and XinZhao.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default; every spell line below differs from the en_US bank's (a Chinese line).

His events in the base bank (plain strings in the WAD's .bin files): the swing is XinZhaoBasicAttack_OnCast and lands
with _OnHit; Determination's third hit is XinZhaoPassiveCritAttack_OnHit with XinZhaoPassive_heal_buffactivate;
Audacious Charge casts with XinZhaoEDash_cast and lands with XinZhaoEDash_hit; Three Talon Strike arms with
XinZhaoQ_OnCast, its thrusts hit with XinZhaoQThrust1/2_OnHit and the knock-up with XinZhaoQThrust3_OnHit (the 36 kB
variant: the slam); Wind Becomes Lightning casts with XinZhaoW_OnCast, the thrust leaves with XinZhaoW_missilelaunch
and hits with XinZhaoWMissile_OnHit; Crescent Guard sweeps with XinZhaoR_OnCast, knocks back with
XinZhaoR_hitlocation_knockback, marks the challenged one with _hitlocation_challenged and guards with
XinZhaoRRangedImmunity_OnBuffActivate / _OnBuffDeactivate. Voice: XinZhaoEDash_cast3D, Spell3DQKnockup (the Q3 shout),
XinZhaoW_cast3D, XinZhaoR_cast3D.
Icons: XinZhaoReworkE = skill (E with Q folded in), XinZhaoReworkW = skill2, XinZhaoReworkR = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/xinzhao/skins/base/xinzhao_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/xinzhao/skins/base/xinzhao_base_vo_"  # same in every language
P = "Play_sfx_XinZhao_XinZhao"
V = "Play_vo_XinZhao_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_xinzhao_sfx_swing": (P + "BasicAttack_OnCast", 906265197, 0.5, -10),
    "league_xinzhao_sfx_hit": (P + "BasicAttack_OnHit", 240807403, 0.5, -12),
    "league_xinzhao_sfx_p_hit": (P + "PassiveCritAttack_OnHit", 653179355, 0.7, -9),
    "league_xinzhao_sfx_p_heal": (P + "Passive_heal_buffactivate", 622087300, 0.8, -12),
    "league_xinzhao_sfx_e": (P + "EDash_cast", 207530361, 0.9, -8),
    "league_xinzhao_sfx_e_hit": (P + "EDash_hit", 850155836, 1.2, -7),
    "league_xinzhao_sfx_q": (P + "Q_OnCast", 1034827340, 1.0, -9),
    "league_xinzhao_sfx_q1": (P + "QThrust1_OnHit", 601454204, 0.7, -9),
    "league_xinzhao_sfx_q2": (P + "QThrust2_OnHit", 925593232, 0.7, -9),
    "league_xinzhao_sfx_q3": (P + "QThrust3_OnHit", 884078834, 1.5, -6),
    "league_xinzhao_sfx_w": (P + "W_OnCast", 374345902, 1.0, -8),
    "league_xinzhao_sfx_w_launch": (P + "W_missilelaunch", 866527190, 0.8, -8),
    "league_xinzhao_sfx_w_hit": (P + "WMissile_OnHit", 939377583, 0.8, -10),
    "league_xinzhao_sfx_r": (P + "R_OnCast", 51886756, 1.6, -6),
    "league_xinzhao_sfx_r_knock": (P + "R_hitlocation_knockback", 651931985, 1.5, -8),
    "league_xinzhao_sfx_r_chal": (P + "R_hitlocation_challenged", 393988992, 0.5, -10),
    "league_xinzhao_sfx_r_guard": (P + "RRangedImmunity_OnBuffActivate", 742855318, 2.0, -10),
    "league_xinzhao_sfx_r_end": (P + "RRangedImmunity_OnBuffDeactivate", 59884192, 1.0, -11),
    "league_xinzhao_vo_e": (V + "XinZhaoEDash_cast3D", 314355300, 1.2, -4),
    "league_xinzhao_vo_q3": (V + "Spell3DQKnockup", 231864153, 1.0, -4),
    "league_xinzhao_vo_w": (V + "XinZhaoW_cast3D", 336552855, 1.6, -4),
    "league_xinzhao_vo_r": (V + "XinZhaoR_cast3D", 375886638, 2.0, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_xinzhao_skill": "ASSETS/Characters/XinZhao/HUD/Icons2D/XinZhaoReworkE.dds",
    "league_xinzhao_skill2": "ASSETS/Characters/XinZhao/HUD/Icons2D/XinZhaoReworkW.dds",
    "league_xinzhao_ult": "ASSETS/Characters/XinZhao/HUD/Icons2D/XinZhaoReworkR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "XinZhao.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"XinZhao.{args.lang}.wad.client"))
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
