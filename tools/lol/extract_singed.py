r"""Pull Singed's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_singed.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Zac route (extract_zac.py): reads (never writes) Game/DATA/FINAL/Champions/Singed.wad.client and
Singed.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Singed_, the event names his skin bins name): his plate's blow and its hit; Fling's
cast, its grab (Fling_OnHit) and the landing in the glue (Fling_landg); Mega Adhesive's throw and the glue landing
(MegaAdhesive_OnBuffActivate); Insanity Potion's drink; the poison's sizzle (PoisonTrail_OnBuffActivate, kept short and
low: it plays on every cloud's tick). Voice (Play_vo_Singed_): Fling_cast3D; the banks have no line for Mega Adhesive or
Insanity Potion, so W takes Attack2DGeneral and R his laugh (Laugh3DGeneral).
Icons: SingedE = skill (Fling), SingedW = skill2 (Mega Adhesive), SingedR = ult (Insanity Potion), SingedQ = Poison Trail
(league_singed_q), SingedPassive = Noxious Slipstream (league_singed_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/singed/skins/base/singed_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/singed/skins/base/singed_base_vo_"  # same in every language
P = "Play_sfx_Singed_"
V = "Play_vo_Singed_"
C = "league_singed_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Zac's got, the voice as the others', the poison's tick quiet
CLIPS = {
    C + "a": ([P + "SingedBasicAttack_OnCast"], None, 0.7, -8),
    C + "a_hit": ([P + "SingedBasicAttack_OnHit"], None, 0.8, -7),
    C + "e": ([P + "Fling_OnCast"], None, 1.0, -6),
    C + "e_hit": ([P + "Fling_OnHit"], None, 1.0, -6),
    C + "e_root": ([P + "Fling_landg", P + "Fling_land"], None, 1.2, -6),
    C + "q_hit": ([P + "PoisonTrail_OnBuffActivate"], None, 0.5, -16),
    C + "w": ([P + "MegaAdhesive_OnCast"], None, 1.0, -6),
    C + "w_land": ([P + "MegaAdhesive_OnBuffActivate"], None, 1.5, -6),
    C + "r": ([P + "InsanityPotion_OnCast", P + "InsanityPotion_OnBuffActivate"], None, 2.0, -5),
    C + "vo_e": ([V + "Fling_cast3D"], None, 2.5, -6),
    C + "vo_w": ([V + "Attack2DGeneral"], None, 2.5, -6),
    C + "vo_r": ([V + "Laugh3DGeneral"], None, 3.0, -6),
}
I = "assets/characters/singed/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_singed_skill": "singed_e",
    "league_singed_skill2": "singed_w",
    "league_singed_ult": "singed_r",
    "league_singed_q": "singed_q",
    "league_singed_passive": "singed_passive",
}


def icon_path(wad, stem):
    """The WAD path of an icon: hud/icons2d/<stem>.dds or .tex, else the first icons2d entry whose name holds stem's
    letter (Singed's are named after the spells: poisontrail, megaadhesive ...)."""
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
    main_wad = Wad(os.path.join(champs, "Singed.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Singed.{args.lang}.wad.client"))
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
