"""Pull Pyke's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_pyke.py --lol "D:\\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Pyke.wad.client and Pyke.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events (plain strings in the WAD's .bin files) are Play_sfx_Pyke_Pyke<spell>_<event>; the voice events
(Play_vo_Pyke_...) are named only in the skin .bin files. The harpoon swing BasicAttack_OnCast / _OnHit; Bone
Skewer's stab QMelee_OnCast / _hit, the charge Q_OnCast (a long rising loop, cut), the throw QRange_OnCast, the hook's
hit QRange_hit_champion; Ghostwater Dive W_buffactivate; Phantom Undertow E_OnCast (the dash), EMissile_return (the
phantom coming back), EMissile_hit (its stun); Death from Below R_cast, R_hitlocation_enemy (the X striking),
R_kill_reset_selfonly (the reset); the grey health Passive_heal_start. Voice: QRange_cast3D, QMelee_cast3D,
E_stealthExit3D, W_cast2D, RExecuteEnemy2D (the zh_CN bank has no R_cast3D media).
Icons: PykeQ = skill, PykeE = skill2 (the combo's dash and stun), PykeR = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/pyke/skins/base/pyke_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/pyke/skins/base/pyke_base_vo_"  # same in every language
P = "Play_sfx_Pyke_Pyke"
V = "Play_vo_Pyke_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_pyke_sfx_swing": (P + "BasicAttack_OnCast", 567219283, 0.5, -11),
    "league_pyke_sfx_hit": (P + "BasicAttack_OnHit", 931656764, 0.5, -11),
    "league_pyke_sfx_q_stab": (P + "QMelee_OnCast", 699085510, 0.7, -9),
    "league_pyke_sfx_q_stab_hit": (P + "QMelee_hit", 199979917, 0.6, -10),
    "league_pyke_sfx_q_charge": (P + "Q_OnCast", 113913074, 0.9, -12),
    "league_pyke_sfx_q_throw": (P + "QRange_OnCast", 409506034, 0.7, -9),
    "league_pyke_sfx_q_hit": (P + "QRange_hit_champion", 995904696, 0.9, -9),
    "league_pyke_sfx_w_cast": (P + "W_buffactivate", 450168093, 1.4, -9),
    "league_pyke_sfx_e_dash": (P + "E_OnCast", 893859128, 0.9, -9),
    "league_pyke_sfx_e_return": (P + "EMissile_return", 574464180, 0.9, -10),
    "league_pyke_sfx_e_hit": (P + "EMissile_hit", 782224351, 1.0, -9),
    "league_pyke_sfx_r_cast": (P + "R_cast", 554757553, 1.0, -9),
    "league_pyke_sfx_r_strike": (P + "R_hitlocation_enemy", 887819556, 1.2, -8),
    "league_pyke_sfx_r_reset": (P + "R_kill_reset_selfonly", 175121820, 1.4, -9),
    "league_pyke_sfx_p_heal": (P + "Passive_heal_start", 285925337, 1.2, -12),
    "league_pyke_vo_q": (V + "PykeQRange_cast3D", 1546633707, 1.3, -4),
    "league_pyke_vo_q2": (V + "PykeQMelee_cast3D", 507620540, 1.0, -4),
    "league_pyke_vo_w": (V + "PykeW_cast2D", 1418121795, 2.3, -4),
    "league_pyke_vo_e": (V + "PykeE_stealthExit3D", 1240967689, 1.5, -4),
    "league_pyke_vo_r": (V + "RExecuteEnemy2D", 879376418, 2.3, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_pyke_skill": "ASSETS/Characters/Pyke/HUD/Icons2D/PykeQ.dds",
    "league_pyke_skill2": "ASSETS/Characters/Pyke/HUD/Icons2D/PykeE.dds",
    "league_pyke_ult": "ASSETS/Characters/Pyke/HUD/Icons2D/PykeR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Pyke.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Pyke.{args.lang}.wad.client"))
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
