"""Pull Samira's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_samira.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Samira.wad.client and Samira.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

Her events (plain strings in the WAD's .bin files) are Play_sfx_Samira_Samira<spell>_<event>. The gun's report is
BasicAttack_missilecast (loudest in its first 10 ms; _OnMissileLaunch is the whoosh after), her bullets' hit
RMissile_OnHit (BasicAttack_OnHit1 has no media), the sword BasicAttackMelee_OnCast / _OnHit. Flair: QGun_OnCast (the
cock), QGun_OnMissileLaunch, QGun_OnHit, QSword_OnCast, QSword_OnHit. Wild Rush: E_cast, E_hit. Blade Whirl: W_OnCast,
W_hit. Inferno Trigger: R_OnCast, R_OnBuffActivate (the 2 s of fire), each shot RMissile_OnMissileCast and _OnHit.
Style: PassiveCombo_style_cast (a grade's sting), RReadyBuff_OnBuffActivate (S, the ult ready); the juggle's dash
PDash_cast. Voice: QGun_cast3D, QSword_cast3D, E_cast3D, R_cast3D.
Icons: SamiraQ = skill, SamiraE = skill2 (E leads the combo), SamiraR8 = ult (the S grade: R1-R7 are the rose and the grades E-A, unusable).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/samira/skins/base/samira_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/samira/skins/base/samira_base_vo_"  # same in every language
P = "Play_sfx_Samira_Samira"
V = "Play_vo_Samira_Samira"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_samira_sfx_shot": (P + "BasicAttack_missilecast", 218166557, 0.5, -10),
    "league_samira_sfx_hit": (P + "RMissile_OnHit", 164871394, 0.4, -14),
    "league_samira_sfx_swing": (P + "BasicAttackMelee_OnCast", 909407961, 0.5, -11),
    "league_samira_sfx_cut": (P + "BasicAttackMelee_OnHit", 252527482, 0.5, -11),
    "league_samira_sfx_q_cock": (P + "QGun_OnCast", 989068643, 0.6, -12),
    "league_samira_sfx_q_shot": (P + "QGun_OnMissileLaunch", 253583916, 0.9, -8),
    "league_samira_sfx_q_hit": (P + "QGun_OnHit", 848588543, 0.6, -11),
    "league_samira_sfx_q_swing": (P + "QSword_OnCast", 427924245, 0.8, -9),
    "league_samira_sfx_q_cut": (P + "QSword_OnHit", 390837308, 0.7, -10),
    "league_samira_sfx_e_cast": (P + "E_cast", 50287791, 0.8, -8),
    "league_samira_sfx_e_hit": (P + "E_hit", 1006569434, 0.6, -10),
    "league_samira_sfx_w_cast": (P + "W_OnCast", 312204363, 1.0, -8),
    "league_samira_sfx_w_hit": (P + "W_hit", 162944145, 0.5, -11),
    "league_samira_sfx_r_cast": (P + "R_OnCast", 465542607, 1.2, -8),
    "league_samira_sfx_r_loop": (P + "R_OnBuffActivate", 885394566, 2.2, -10),
    "league_samira_sfx_r_shot": (P + "RMissile_OnMissileCast", 988031923, 0.35, -14),
    "league_samira_sfx_style": (P + "PassiveCombo_style_cast", 627403248, 0.9, -12),
    "league_samira_sfx_s": (P + "RReadyBuff_OnBuffActivate", 412985637, 1.4, -9),
    "league_samira_sfx_dash": (P + "PDash_cast", 107071894, 0.6, -10),
    "league_samira_vo_q": (V + "QGun_cast3D", 1347959952, 1.1, -4),
    "league_samira_vo_q2": (V + "QSword_cast3D", 625574555, 1.2, -4),
    "league_samira_vo_e": (V + "E_cast3D", 616248774, 1.3, -4),
    "league_samira_vo_r": (V + "R_cast3D", 1006189096, 1.4, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_samira_skill": "ASSETS/Characters/Samira/HUD/Icons2D/SamiraQ.dds",
    "league_samira_skill2": "ASSETS/Characters/Samira/HUD/Icons2D/SamiraE.dds",
    "league_samira_ult": "ASSETS/Characters/Samira/HUD/Icons2D/SamiraR8.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Samira.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Samira.{args.lang}.wad.client"))
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
