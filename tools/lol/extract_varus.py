"""Pull Varus's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_varus.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Varus.wad.client and Varus.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank (the client's own names, picked with work/vr/snd_probe_vr.py): the attack is
VarusBasicAttack_OnCast (the release, loud in its first 20 ms) layered with _OnMissileLaunch (the whoosh) and hits with
_OnHit; Blight bursting is VarusW_detonate (two variants: the stacks, and W's empowered pop); Piercing Arrow draws with
VarusQ_OnCast + VarusQ_OnBuffActivate (the charging hum), fires with VarusQMissile_OnMissileCast + _OnMissileLaunch
and hits with VarusQ_hit_champ; Hail of Arrows casts with VarusE_OnCast, lands with VarusEMissile_buffactivate (the
short variant) and hits with VarusEMissile_hit; Chain of Corruption casts with VarusR_OnCast + VarusRMissile_
OnMissileLaunch and hits with VarusRMissile_hit (another variant is the spread); Living Vengeance is
VarusPassiveBuffDisplay_OnBuffActivate. Voice: a Q line, an E line, an R line.
Icons: VarusQ = skill, VarusE = skill2, VarusR = ult (W is folded into the attack and Q).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/varus/skins/base/varus_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/varus/skins/base/varus_base_vo_"  # same in every language
P = "Play_sfx_Varus_Varus"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_varus_sfx_attack": (P + "BasicAttack_OnCast", 81048848, 0.5, -9),
    "league_varus_sfx_attack_fly": (P + "BasicAttack_OnMissileLaunch", 46286961, 0.45, -13),
    "league_varus_sfx_attack_hit": (P + "BasicAttack_OnHit", 72112728, 0.5, -12),
    "league_varus_sfx_blight": (P + "W_detonate", 515131643, 1.0, -9),
    "league_varus_sfx_w_pop": (P + "W_detonate", 165295408, 1.0, -7),
    "league_varus_sfx_q": (P + "Q_OnCast", 553592655, 0.6, -9),
    "league_varus_sfx_q_charge": (P + "Q_OnBuffActivate", 1022272436, 1.3, -11),
    "league_varus_sfx_q_fire": (P + "QMissile_OnMissileCast", 493184685, 0.5, -7),
    "league_varus_sfx_q_fly": (P + "QMissile_OnMissileLaunch", 328701184, 0.8, -11),
    "league_varus_sfx_q_hit": (P + "Q_hit_champ", 355790523, 0.6, -9),
    "league_varus_sfx_e": (P + "E_OnCast", 931080396, 1.0, -8),
    "league_varus_sfx_e_land": (P + "EMissile_buffactivate", 361380158, 0.8, -8),
    "league_varus_sfx_e_hit": (P + "EMissile_hit", 79664377, 0.5, -11),
    "league_varus_sfx_r": (P + "R_OnCast", 677320590, 0.9, -8),
    "league_varus_sfx_r_fly": (P + "RMissile_OnMissileLaunch", 872386892, 1.0, -10),
    "league_varus_sfx_r_hit": (P + "RMissile_hit", 192423992, 1.0, -7),
    "league_varus_sfx_r_spread": (P + "RMissile_hit", 951509779, 0.8, -9),
    "league_varus_sfx_rage": (P + "PassiveBuffDisplay_OnBuffActivate", 81197962, 1.0, -9),
    "league_varus_vo_q": ("Play_vo_Varus_Spell3DQCast", 11731689, 1.2, -4),
    "league_varus_vo_e": ("Play_vo_Varus_VarusE_cast3D", 96587500, 1.0, -4),
    "league_varus_vo_r": ("Play_vo_Varus_VarusR_cast3D", 548430249, 1.4, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_varus_skill": "ASSETS/Characters/Varus/HUD/Icons2D/VarusQ.dds",
    "league_varus_skill2": "ASSETS/Characters/Varus/HUD/Icons2D/VarusE.dds",
    "league_varus_ult": "ASSETS/Characters/Varus/HUD/Icons2D/VarusR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Varus.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Varus.{args.lang}.wad.client"))
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
