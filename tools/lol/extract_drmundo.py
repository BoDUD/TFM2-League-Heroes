r"""Pull Dr. Mundo's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_drmundo.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe [--list]

Same route as extract_tahmkench.py: reads (never writes) Game/DATA/FINAL/Champions/DrMundo.wad.client and
DrMundo.<lang>.wad.client, resolves the base-skin Wwise events below to their media, decodes them with vgmstream and
writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to
league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN. --list prints every event's variants.

His events (named in skin0.bin): the cleaver DrMundoBasicAttack_OnCast / _OnHit; Blunt Force Trauma DrMundoEAttack_cast
/ _OnHit and the flung corpse DrMundoEMissile_hit (_missilelaunch0 has no media); Infected Bonesaw DrMundoQ_OnCast / _OnHit; Heart
Zapper DrMundoW_OnCast (on), _hit (the zaps), _buffdeactivate (the end) and _heal_buffactivate (the grey health back);
Maximum Dosage DrMundoR_OnCast; Goes Where He Pleases DrMundoPObject_missilelaunch (the control shaken off, the
tank thrown; DrMundoPImmunity_OnBuffActivate2 has no media), DrMundoPObject_land / _pickup / _break (the chem-tank). Voice: DrMundoQ / W / E / R_cast3D, Laugh3DGeneral for the
passive.
Icons: DrMundo_Q = skill, DrMundo_W = skill2, DrMundo_R = ult; E and the passive are written too (league_drmundo_e /
_passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/drmundo/skins/base/drmundo_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/drmundo/skins/base/drmundo_base_vo_"  # same in every language

P = "Play_sfx_DrMundo_DrMundo"
V = "Play_vo_DrMundo_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_drmundo_sfx_a_swing": (P + "BasicAttack_OnCast", None, 0.6, -13),
    "league_drmundo_sfx_a_hit": (P + "BasicAttack_OnHit", None, 0.6, -12),
    "league_drmundo_sfx_e": (P + "EAttack_cast", None, 0.8, -12),
    "league_drmundo_sfx_e_hit": (P + "EAttack_OnHit", None, 0.9, -11),
    "league_drmundo_sfx_e_fling_hit": (P + "EMissile_hit", None, 0.8, -12),
    "league_drmundo_sfx_q": (P + "Q_OnCast", None, 0.9, -12),
    "league_drmundo_sfx_q_hit": (P + "Q_OnHit", None, 0.9, -11),
    "league_drmundo_sfx_q_heal": (P + "W_heal_buffactivate", None, 1.0, -14),
    "league_drmundo_sfx_w": (P + "W_OnCast", None, 1.4, -12),
    "league_drmundo_sfx_w_end": (P + "W_buffdeactivate", None, 1.4, -11),
    "league_drmundo_sfx_r": (P + "R_OnCast", None, 2.0, -11),
    "league_drmundo_sfx_p_shake": (P + "PObject_missilelaunch", None, 1.2, -11),
    "league_drmundo_sfx_p_land": (P + "PObject_land", None, 0.8, -13),
    "league_drmundo_sfx_p_pick": (P + "PObject_pickup", None, 1.0, -12),
    "league_drmundo_sfx_p_break": (P + "PObject_break", None, 1.0, -12),
    "league_drmundo_sfx_vo_q": (V + "DrMundoQ_cast3D", None, 2.0, -6),
    "league_drmundo_sfx_vo_w": (V + "DrMundoW_cast3D", None, 2.0, -6),
    "league_drmundo_sfx_vo_e": (V + "DrMundoE_cast3D", None, 2.0, -6),
    "league_drmundo_sfx_vo_r": (V + "DrMundoR_cast3D", None, 3.0, -6),
    "league_drmundo_sfx_vo_p": (V + "Laugh3DGeneral", None, 3.0, -6),
}
I = "ASSETS/Characters/DrMundo/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_drmundo_skill": I + "DrMundo_Q.dds",
    "league_drmundo_skill2": I + "DrMundo_W.dds",
    "league_drmundo_ult": I + "DrMundo_R.dds",
    "league_drmundo_e": I + "DrMundo_E.dds",
    "league_drmundo_passive": I + "DrMundo_P.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--list", action="store_true", help="print every event's media variants and their lengths")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "DrMundo.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"DrMundo.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if args.list:
                lens = []
                for v in variants:
                    try:
                        r, xx = decode(media[v], args.vgmstream)
                        lens.append(f"{v}:{len(xx) / r:.2f}s")
                    except Exception as ex:  # noqa: BLE001 - a listing, keep going
                        lens.append(f"{v}:?{ex}")
                print(f"{name:36s} {event}: {' '.join(lens)}")
                continue
            if mid is None:
                mid = variants[0]
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
