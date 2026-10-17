r"""Pull Viego's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_viego.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_shen.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Viego.wad.client and Viego.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (named in his bins, picked by decoding every variant): the swing ViegoBasicAttack_OnCast / _OnHit; the
marked double strike ViegoQDoubleAttack_OnHit; Blade of the Ruined King ViegoQ_OnCast / ViegoQ_hit; Spectral Maw's charge
ViegoW_buffactivate (cut), the launch ViegoW_missilelaunch, the stun ViegoWMis_OnHit; Harrowed Path ViegoE_OnCast and the
mist taken ViegoE_buffactivate; Sovereign's Domination ViegoP_cast (the soul taken), ViegoP_hit (the possession) and
ViegoPassiveTransform_OnBuffDeactivate (back to himself); Heartbreaker ViegoR_cast, ViegoR_hitlocation (the landing) and
ViegoR_Execution_hit (the champion struck). Voice: Q, W (Spell3DW2Cast), E, R and a takedown line for the possession.
Icons: Viego_Q = skill (Q), Viego_W = skill2 (W, the mist of E folded in), Viego_R = ult (R).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/viego/skins/base/viego_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/viego/skins/base/viego_base_vo_"  # same in every language
P = "Play_sfx_Viego_Viego"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_viego_sfx_a_swing": (P + "BasicAttack_OnCast", 757639912, 0.5, -11),
    "league_viego_sfx_a_hit": (P + "BasicAttack_OnHit", 87159301, 0.35, -12),
    "league_viego_sfx_a_double": (P + "QDoubleAttack_OnHit", 412731487, 0.5, -10),
    "league_viego_sfx_q": (P + "Q_OnCast", 137852511, 0.9, -10),
    "league_viego_sfx_q_hit": (P + "Q_hit", 893799730, 0.8, -11),
    "league_viego_sfx_w_charge": (P + "W_buffactivate", 518642850, 0.9, -12),
    "league_viego_sfx_w": (P + "W_missilelaunch", 988116032, 1.0, -9),
    "league_viego_sfx_w_hit": (P + "WMis_OnHit", 853567206, 0.9, -9),
    "league_viego_sfx_e": (P + "E_OnCast", 327747289, 1.0, -10),
    "league_viego_sfx_e_mist": (P + "E_buffactivate", 102140343, 0.7, -12),
    "league_viego_sfx_p": (P + "P_cast", 1066142186, 1.7, -9),
    "league_viego_sfx_p_hit": (P + "P_hit", 981558616, 1.3, -9),
    "league_viego_sfx_p_end": (P + "PassiveTransform_OnBuffDeactivate", 648939083, 0.65, -11),
    "league_viego_sfx_r": (P + "R_cast", 961211742, 0.6, -9),
    "league_viego_sfx_r_land": (P + "R_hitlocation", 409667577, 0.7, -9),
    "league_viego_sfx_r_hit": (P + "R_Execution_hit", 1003281412, 1.4, -9),
    "league_viego_sfx_vo_q": ("Play_vo_Viego_ViegoQ_cast3D", 1445420034, 0.5, -4),
    "league_viego_sfx_vo_w": ("Play_vo_Viego_Spell3DW2Cast", 2124795575, 0.85, -4),
    "league_viego_sfx_vo_e": ("Play_vo_Viego_ViegoE_cast3D", 480177394, 1.8, -4),
    "league_viego_sfx_vo_r": ("Play_vo_Viego_ViegoR_cast3D", 1946177867, 1.35, -4),
    "league_viego_sfx_vo_p": ("Play_vo_Viego_Kill3DGeneral", 225021047, 1.9, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_viego_skill": "ASSETS/Characters/Viego/HUD/Icons2D/Viego_Q.dds",
    "league_viego_skill2": "ASSETS/Characters/Viego/HUD/Icons2D/Viego_W.dds",
    "league_viego_ult": "ASSETS/Characters/Viego/HUD/Icons2D/Viego_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Viego.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Viego.{args.lang}.wad.client"))
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
