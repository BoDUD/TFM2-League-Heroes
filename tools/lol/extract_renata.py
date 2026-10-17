r"""Pull Renata Glasc's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_renata.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe [--list]

Same route as extract_yunara.py: reads (never writes) Game/DATA/FINAL/Champions/Renata.wad.client and
Renata.<lang>.wad.client, resolves the base-skin Wwise events below to their media, decodes them with vgmstream and
writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to
league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN. --list prints every event's variants.

Her events (named in skin0.bin): the pistol RenataBasicAttack _OnCast / _OnMissileCast / _OnHit, Leverage's
RenataPassive_hit / _detonate, Q's hand RenataQ_OnCast / _OnMissileLaunch / _OnHit, the throw RenataQRecast_OnCast and
the landing RenataQ_stun, W RenataW_OnCast / _buffcast_others / _revive_buffactivate, E RenataE_OnCast /
_OnMissileLaunch / _hit / RenataE_OnBuffActivate (the shield), R RenataR_OnCast / RenataRMissile_OnMissileLaunch /
_hit, death Death3D_cast. Voice: the casts' cast3D lines.
Icons: Renata_E = skill, Renata_Q = skill2, Renata_R = ult; W (fired by the passive controller), the passive and Q's
recast are written too (league_renata_w / _passive / _q2, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/renata/skins/base/renata_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/renata/skins/base/renata_base_vo_"  # same in every language

P = "Play_sfx_Renata_"
V = "Play_vo_Renata_"
C = "league_renata_sfx_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    C + "a": (P + "RenataBasicAttack_OnCast", None, 0.7, -14),
    C + "a_fly": (P + "RenataBasicAttack_OnMissileCast", None, 0.6, -15),
    C + "a_hit": (P + "RenataBasicAttack_OnHit", None, 0.6, -14),
    C + "p_hit": (P + "RenataPassive_hit", None, 0.7, -14),
    C + "p_pop": (P + "RenataPassive_detonate", None, 0.9, -12),
    C + "q": (P + "RenataQ_OnCast", None, 1.0, -12),
    C + "q_fly": (P + "RenataQ_OnMissileLaunch", None, 1.2, -12),
    C + "q_hit": (P + "RenataQ_OnHit", None, 0.9, -11),
    C + "q_fling": (P + "RenataQRecast_OnCast", None, 1.0, -11),
    C + "q_crash": (P + "RenataQ_stun", None, 0.9, -11),
    C + "w": (P + "RenataW_OnCast", None, 1.0, -12),
    C + "w_buff": (P + "RenataW_buffcast_others", None, 1.2, -12),
    C + "w_save": (P + "RenataW_revive_buffactivate", None, 1.6, -11),
    C + "e": (P + "RenataE_OnCast", None, 0.9, -12),
    C + "e_fly": (P + "RenataE_OnMissileLaunch", None, 1.2, -12),
    C + "e_hit": (P + "RenataE_hit", None, 0.8, -12),
    C + "e_boom": (P + "RenataE_hitlocation", None, 0.9, -12),
    C + "e_shield": (P + "RenataE_OnBuffActivate", None, 0.9, -13),
    C + "r": (P + "RenataR_OnCast", None, 1.4, -10),
    C + "r_wave": (P + "RenataRMissile_OnMissileLaunch", None, 2.0, -10),
    C + "r_hit": (P + "RenataRMissile_hit", None, 1.2, -11),
    C + "death": (P + "Death3D_cast", None, 1.6, -12),
    C + "vo_q": (V + "RenataQ_cast3D", None, 2.4, -6),
    C + "vo_w": (V + "RenataW_cast3D", None, 2.4, -6),
    C + "vo_e": (V + "RenataE_cast3D", None, 2.4, -6),
    C + "vo_r": (V + "RenataR_cast3D", None, 3.0, -6),
    C + "vo_kill": (V + "Kill3DGeneral", None, 3.0, -6),
    C + "vo_death": (V + "Death3D", None, 2.4, -6),
}
I = "ASSETS/Characters/Renata/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_renata_skill": I + "Renata_E.dds",
    "league_renata_skill2": I + "Renata_Q.dds",
    "league_renata_ult": I + "Renata_R.dds",
    "league_renata_w": I + "Renata_W.dds",
    "league_renata_passive": I + "Renata_P.dds",
    "league_renata_q2": I + "Renata_Q2.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--list", action="store_true", help="print every event's media variants and their lengths")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Renata.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Renata.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event) or banks.event_media(event[:-1])
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
