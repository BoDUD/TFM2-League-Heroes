r"""Pull Senna's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_senna.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_draven.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Senna.wad.client and Senna.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

Her events (found in her bins by work/se/snd_names_se.py, picked with work/se/snd_probe_se.py): the relic cannon
SennaBasicAttack_missilecast (the shot: league_senna_attack, which the engine plays on every attack) /
SennaBasicAttack2_OnHit; Absolution SennaPassiveStacks_OnHitLocation (Mist taken from a
champion), SennaSoul_buffactivate (a Mist gathered); Piercing Darkness SennaQ_OnCast / _enemy_hit / _ally_hit; Last
Embrace SennaW_OnMissileLaunch / _OnHit, SennaWRoot_ground_hit (the spread); Curse of the Black Mist SennaE_OnCast;
Dawning Shadow SennaR_OnCast (the charge, from the ult's first tick) / _OnMissileLaunch / _OnHit,
SennaRAlly_OnHit (the shield). Voice: Q, W, E and R.
Icons: Senna_Q = skill (Q), Senna_W = skill2 (W), Senna_R = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/senna/skins/base/senna_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/senna/skins/base/senna_base_vo_"  # same in every language
P = "Play_sfx_Senna_Senna"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_senna_sfx_attack": (P + "BasicAttack_missilecast", 849292322, 0.45, -10),
    "league_senna_sfx_a_hit": (P + "BasicAttack2_OnHit", 175133967, 0.4, -12),
    "league_senna_sfx_p_take": (P + "PassiveStacks_OnHitLocation", 870180486, 0.5, -10),
    "league_senna_sfx_p_gain": (P + "Soul_buffactivate", 1067676518, 0.5, -12),
    "league_senna_sfx_q": (P + "Q_OnCast", 960490241, 0.5, -9),
    "league_senna_sfx_q_hit": (P + "Q_enemy_hit", 618442981, 0.5, -11),
    "league_senna_sfx_q_heal": (P + "Q_ally_hit", 399000466, 0.7, -11),
    "league_senna_sfx_w": (P + "W_OnMissileLaunch", 254998721, 0.7, -10),
    "league_senna_sfx_w_hit": (P + "W_OnHit", 131314647, 0.6, -10),
    "league_senna_sfx_w_root": (P + "WRoot_ground_hit", 329446178, 0.8, -9),
    "league_senna_sfx_e": (P + "E_OnCast", 905936624, 1.1, -10),
    "league_senna_sfx_r_cast": (P + "R_OnCast", 186906369, 1.1, -9),
    "league_senna_sfx_r_fire": (P + "R_OnMissileLaunch", 703264946, 1.0, -8),
    "league_senna_sfx_r_hit": (P + "R_OnHit", 458512916, 0.6, -9),
    "league_senna_sfx_r_sh": (P + "RAlly_OnHit", 541991647, 0.7, -11),
    "league_senna_sfx_vo_q": ("Play_vo_Senna_SennaQ_cast3D", 1422614143, 1.0, -4),
    "league_senna_sfx_vo_w": ("Play_vo_Senna_SennaW_cast3D", 435224340, 1.0, -4),
    "league_senna_sfx_vo_e": ("Play_vo_Senna_SennaE_cast3D", 1547143787, 1.6, -4),
    "league_senna_sfx_vo_r": ("Play_vo_Senna_SennaR_cast3D", 44679563, 1.6, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_senna_skill": "ASSETS/Characters/Senna/HUD/Icons2D/Senna_Q.dds",
    "league_senna_skill2": "ASSETS/Characters/Senna/HUD/Icons2D/Senna_W.dds",
    "league_senna_ult": "ASSETS/Characters/Senna/HUD/Icons2D/Senna_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Senna.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Senna.{args.lang}.wad.client"))
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
