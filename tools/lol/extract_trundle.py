r"""Pull Trundle's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_trundle.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

The Zac route (extract_yorick.py's): reads (never writes) Game/DATA/FINAL/Champions/Trundle.wad.client and
Trundle.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice:
zh_CN. Events (prefix Play_sfx_Trundle_Trundle, the names his bins carry): the club's swing and hit; Chomp's cast and
bite; Frozen Domain's cast; Pillar of Ice's cast and the pillar rising (its buff, two variants: the rise and a unit at
it); Subjugate's cast and the drain on the champion; King's Tribute's heal (Subjugate's heal missile). Voice
(Play_vo_Trundle_Trundle): Chomp's, the Domain's, the Pillar's and Subjugate's casts.
Icons (the champion bin's hud/icons2d): trundle_q = skill, trundle_e = skill2, trundle_r = ult, trundle_passive = King's
Tribute (league_trundle_passive), trundle_w = Frozen Domain (league_trundle_w).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/trundle/skins/base/trundle_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/trundle/skins/base/trundle_base_vo_"  # same in every language
P = "Play_sfx_Trundle_Trundle"
V = "Play_vo_Trundle_Trundle"
C = "league_trundle_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -8),
    C + "q": ([P + "TrollSmash_OnCast", P + "Q_OnCast"], None, 1.0, -7),
    C + "q_hit": ([P + "Q_OnHit", P + "Q_OnHit1"], None, 1.0, -6),
    C + "w": ([P + "Desecrate_OnCast"], None, 1.8, -6),
    C + "e": ([P + "Circle_OnCast"], None, 1.0, -7),
    C + "e_rise": ([P + "Circle_buffactivate"], None, 1.8, -5),
    C + "e_hit": ([P + "Circle_buffactivate"], 1, 1.0, -8),
    C + "r": ([P + "Pain_OnCast"], None, 1.5, -6),
    C + "r_hit": ([P + "Pain_OnBuffActivate", P + "PainBuff_OnBuffActivate0"], None, 1.8, -6),
    C + "p_heal": ([P + "PainHeal_OnMissileLaunch"], None, 1.0, -9),
    C + "vo_q": ([V + "Q_cast3DK", V + "Q_cast3D"], None, 2.5, -6),
    C + "vo_w": ([V + "Desecrate_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "Circle_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "Pain_hit3D"], None, 3.0, -6),
}
I = "assets/characters/trundle/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_trundle_skill": "trundle_q",
    "league_trundle_skill2": "trundle_e",
    "league_trundle_ult": "trundle_r",
    "league_trundle_w": "trundle_w",
    "league_trundle_passive": "trundle_passive",
}


def icon_path(wad, stem):
    """The WAD path of an icon: hud/icons2d/<stem>.dds or .tex (None when neither is there)."""
    for ext in (".dds", ".tex", ".png"):
        p = I + stem + ext
        try:
            wad.read_path(p)
            return p
        except Exception:
            pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--icon", nargs="*", default=[], help="slot=wad/path overrides")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Trundle.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Trundle.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            for ev in events:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else variants[min(mid, len(variants) - 1)]
            sr, x = decode(media[m], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event} ({len(variants)} variants)")

    over = dict(kv.split("=", 1) for kv in args.icon)
    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, stem in ICONS.items():
        path = over.get(name) or icon_path(main_wad, stem)
        if path is None:
            sys.exit(f"{name}: no {I}{stem}.dds - pass --icon {name}=<wad path> (see the WAD's hud/icons2d entries)")
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
