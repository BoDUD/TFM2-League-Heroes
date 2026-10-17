r"""Pull Yunara's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_yunara.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe [--list]

Same route as extract_aphelios.py: reads (never writes) Game/DATA/FINAL/Champions/Yunara.wad.client and
Yunara.<lang>.wad.client, resolves the base-skin Wwise events below to their media, decodes them with vgmstream and
writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to
league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN. --list prints every event's variants.

Her events (named in skin0.bin): the bead attacks YunaraBasicAttack(2) / CritAttack _OnCast + _OnHit, Q's empowered
attacks YunaraQAttack _OnCast / _OnHit and the spread YunaraQBounceMissile_OnHit, Q's activation YunaraQ_buffactivate,
W's bead YunaraW_OnCast / _OnMissileLaunch / _OnHit, R's laser YunaraW2_OnCast / _missilelaunch / _hit, E YunaraE_cast,
R's dash YunaraE2_dash_cast, R YunaraR_buffactivate, death Death3D_cast. Voice: the casts' cast3D lines.
Icons: Yunara_W = skill, Yunara_E = skill2, Yunara_R = ult; Q (folded into the attack), the passive, R's W and E are
written too (league_yunara_q / _passive / _rw / _re, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/yunara/skins/base/yunara_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/yunara/skins/base/yunara_base_vo_"  # same in every language

P = "Play_sfx_Yunara_"
V = "Play_vo_Yunara_"
C = "league_yunara_sfx_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    C + "a": (P + "YunaraBasicAttack_OnCast", None, 0.7, -14),
    C + "a2": (P + "YunaraBasicAttack2_OnCast", None, 0.7, -14),
    C + "a_hit": (P + "YunaraBasicAttack_OnHit", None, 0.6, -14),
    C + "a_crit": (P + "YunaraCritAttack_OnCast", None, 0.8, -13),
    C + "a_crit_hit": (P + "YunaraCritAttack_OnHit", None, 0.7, -13),
    C + "q_on": (P + "YunaraQ_buffactivate", None, 1.4, -11),
    C + "q_a": (P + "YunaraQAttack_OnCast", None, 0.7, -13),
    C + "q_hit": (P + "YunaraQAttack_OnHit", None, 0.7, -13),
    C + "q_bounce": (P + "YunaraQBounceMissile_OnHit", None, 0.6, -15),
    C + "w": (P + "YunaraW_OnCast", None, 1.0, -11),
    C + "w_fly": (P + "YunaraW_OnMissileLaunch", None, 1.4, -12),
    C + "w_hit": (P + "YunaraW_OnHit", None, 0.9, -11),
    C + "rw": (P + "YunaraW2_OnCast", None, 1.2, -11),
    C + "rw_beam": (P + "YunaraW2_missilelaunch", 256113000, 1.4, -10),
    C + "rw_hit": (P + "YunaraW2_hit", None, 1.0, -11),
    C + "e": (P + "YunaraE_cast", None, 1.2, -12),
    C + "re": (P + "YunaraE2_dash_cast", None, 1.0, -11),
    C + "r": (P + "YunaraR_buffactivate", None, 2.4, -10),
    C + "death": (P + "Death3D_cast", None, 1.6, -12),
    C + "vo_q": (V + "MaxResource3DQ", None, 2.4, -6),
    C + "vo_w": (V + "YunaraW_cast3DK", None, 2.4, -6),
    C + "vo_rw": (V + "YunaraW2_cast3D", None, 2.4, -6),
    C + "vo_e": (V + "YunaraE_cast3D", None, 2.4, -6),
    C + "vo_r": (V + "YunaraR_cast3D", None, 3.0, -6),
    C + "vo_kill": (V + "Kill3DGeneral", None, 3.0, -6),
    C + "vo_death": (V + "Death3D", None, 2.4, -6),
}
I = "ASSETS/Characters/Yunara/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_yunara_skill": I + "Yunara_W.dds",
    "league_yunara_skill2": I + "Yunara_E.dds",
    "league_yunara_ult": I + "Yunara_R.dds",
    "league_yunara_q": I + "Yunara_Q2.dds",
    "league_yunara_passive": I + "Yunara_Passive.dds",
    "league_yunara_rw": I + "Yunara_RW.dds",
    "league_yunara_re": I + "Yunara_RE.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--list", action="store_true", help="print every event's media variants and their lengths")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Yunara.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Yunara.{args.lang}.wad.client"))
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
