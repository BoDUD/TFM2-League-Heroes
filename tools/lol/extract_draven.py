r"""Pull Draven's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_draven.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_draven.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Draven.wad.client and Draven.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/dv/snd_names_dv.py, picked with work/dv/snd_probe_dv.py): the axe throw
DravenAttackP_R_OnMissileCast / _OnHit; the spinning axe DravenAttackP_RQ_OnMissileCast / _OnHit, DravenSpinning_OnCast
(Q), DravenSpinningReturn_catch (a catch), DravenSpinning_buffdeactivate (a dropped axe); Blood Rush DravenFury_OnCast;
Stand Aside DravenDoubleShot_OnCast, DravenDoubleShotMissile_OnMissileLaunch / _OnHit; Whirling Death DravenRCast_OnCast,
DravenR_buffactivate (the blades leave), DravenR_hit, DravenR_buffdeactivate (they turn); League of Draven
DravenNewPassive_buffactivate (the cash-in). Voice: Q, the spinning attack (W), E and R.
Icons: Draven_SpinningAxe = skill (Q), Draven_TwinAxe = skill2 (E), Draven_WhirlingDeath = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/draven/skins/base/draven_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/draven/skins/base/draven_base_vo_"  # same in every language
P = "Play_sfx_Draven_Draven"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_draven_sfx_a_throw": (P + "AttackP_R_OnMissileCast", 488366016, 0.35, -11),
    "league_draven_sfx_a_hit": (P + "AttackP_R_OnHit", 335926001, 0.35, -12),
    "league_draven_sfx_q": (P + "Spinning_OnCast", 925187250, 0.4, -10),
    "league_draven_sfx_q_throw": (P + "AttackP_RQ_OnMissileCast", 35826919, 0.4, -10),
    "league_draven_sfx_q_hit": (P + "AttackP_RQ_OnHit", 803308726, 0.4, -10),
    "league_draven_sfx_q_catch": (P + "SpinningReturn_catch", 520268478, 0.45, -9),
    "league_draven_sfx_q_lost": (P + "Spinning_buffdeactivate", 138096074, 0.3, -12),
    "league_draven_sfx_w": (P + "Fury_OnCast", 406651520, 0.7, -10),
    "league_draven_sfx_e": (P + "DoubleShot_OnCast", 285310839, 0.6, -10),
    "league_draven_sfx_e_throw": (P + "DoubleShotMissile_OnMissileLaunch", 403843587, 0.6, -9),
    "league_draven_sfx_e_hit": (P + "DoubleShotMissile_OnHit", 481603445, 0.4, -10),
    "league_draven_sfx_r": (P + "RCast_OnCast", 481259678, 1.0, -9),
    "league_draven_sfx_r_throw": (P + "R_buffactivate", 828486608, 0.7, -9),
    "league_draven_sfx_r_hit": (P + "R_hit", 44409577, 0.5, -9),
    "league_draven_sfx_r_turn": (P + "R_buffdeactivate", 1038807243, 0.4, -10),
    "league_draven_sfx_p_cash": (P + "NewPassive_buffactivate", 432739513, 1.7, -9),
    "league_draven_sfx_vo_q": ("Play_vo_Draven_Spell3DQPCast", 596733307, 0.75, -4),
    "league_draven_sfx_vo_w": ("Play_vo_Draven_DravenSpinningAttack_cast3D", 265840386, 0.7, -4),
    "league_draven_sfx_vo_e": ("Play_vo_Draven_DravenDoubleShot_cast3D", 569478755, 0.7, -4),
    "league_draven_sfx_vo_r": ("Play_vo_Draven_DravenRCast_cast3D", 1871464748, 0.8, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_draven_skill": "ASSETS/Characters/Draven/HUD/Icons2D/Draven_SpinningAxe.dds",
    "league_draven_skill2": "ASSETS/Characters/Draven/HUD/Icons2D/Draven_TwinAxe.dds",
    "league_draven_ult": "ASSETS/Characters/Draven/HUD/Icons2D/Draven_WhirlingDeath.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Draven.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Draven.{args.lang}.wad.client"))
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
