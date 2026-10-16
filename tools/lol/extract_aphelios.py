r"""Pull Aphelios's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_aphelios.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe [--list]

Same route as extract_drmundo.py: reads (never writes) Game/DATA/FINAL/Champions/Aphelios.wad.client and
Aphelios.<lang>.wad.client, resolves the base-skin Wwise events below to their media, decodes them with vgmstream and
writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to
league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN (Alune speaks; he is mute). --list prints
every event's variants.

His events (named in skin0.bin; the bin's strings run into the next byte, so a name is tried with and without its last
character): each weapon's shot Apheliosxxx Attack_OnCast and its hit (Calibrum / Severum / Gravitum / Infernum _hit,
Crescendum AttackMisOut_OnHit); the Qs CalibrumQ_cast (+ _OnHit, the mark's QMarkRed_hit), SeverumQ_OnCast,
GravitumQ_cast (+ the root GravitumRoot_buffactivate), InfernumQ_OnCast, CrescendumQ_OnCast (+ _OnHitLocation, the
sentry landing); the weapon swap W<weapon>_swap; R_OnCast, RMis_OnMissileLaunch, RMis_OnHit. Voice: the Qs'
<weapon>Q_cast3D, W_cast3D, R_cast3D.
Icons: ApheliosQ = skill, ApheliosW = skill2, ApheliosR = ult; the five weapons' Qs and the passive are written too
(league_aphelios_q_<weapon> / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/aphelios/skins/base/aphelios_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/aphelios/skins/base/aphelios_base_vo_"  # same in every language

P = "Play_sfx_Aphelios_Aphelios"
V = "Play_vo_Aphelios_Aphelios"
C = "league_aphelios_sfx_"
W = {"cal": "Calibrum", "sev": "Severum", "grav": "Gravitum", "inf": "Infernum", "cre": "Crescendum"}

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {}
for w, name in W.items():
    CLIPS[C + f"a_{w}"] = (P + name + "Attack_OnCast", None, 0.7, -14)
    CLIPS[C + f"a_{w}_hit"] = (P + name + ("AttackMisOut_OnHit" if w == "cre" else "Attack_hit"), None, 0.6, -14)
    CLIPS[C + f"swap_{w}"] = (P + f"W{name}_swap", None, 0.9, -13)
    CLIPS[C + f"vo_q_{w}"] = (V + name + "Q_cast3D", None, 2.4, -6)
CLIPS.update({
    C + "q_cal": (P + "CalibrumQ_cast", None, 1.0, -11),
    C + "q_c_hit": (P + "CalibrumQ_OnHit", None, 0.9, -11),
    C + "q_c_pop": (P + "CalibrumQMarkRed_hit", None, 0.9, -11),
    C + "q_sev": (P + "SeverumQ_OnCast", None, 1.8, -11),
    C + "q_grav": (P + "GravitumQ_cast", None, 1.0, -11),
    C + "q_g_hit": (P + "GravitumRoot_buffactivate", None, 1.0, -11),
    C + "q_inf": (P + "InfernumQ_OnCast", None, 1.2, -11),
    C + "q_cre": (P + "CrescendumQ_OnCast", None, 1.0, -11),
    C + "q_r_land": (P + "CrescendumQ_OnHitLocation", None, 1.0, -12),
    C + "r": (P + "R_OnCast", None, 1.6, -11),
    C + "r_shot": (P + "RMis_OnMissileLaunch", None, 1.4, -10),
    C + "r_boom": (P + "RMis_OnHit", None, 1.6, -9),
    C + "vo_w": (V + "W_cast3D", None, 2.4, -6),
    C + "vo_r": (V + "R_cast3D", None, 3.0, -6),
})
I = "ASSETS/Characters/Aphelios/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_aphelios_skill": I + "ApheliosQ.dds",
    "league_aphelios_skill2": I + "ApheliosW.dds",
    "league_aphelios_ult": I + "ApheliosR.dds",
    "league_aphelios_passive": I + "ApheliosP.dds",
}
ICONS.update({f"league_aphelios_q_{w}": I + f"Q_{name}.dds" for w, name in W.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--list", action="store_true", help="print every event's media variants and their lengths")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Aphelios.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Aphelios.{args.lang}.wad.client"))
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
