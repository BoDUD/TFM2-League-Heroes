r"""Pull Rumble's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_rumble.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

extract_yorick.py's way: reads (never writes) Game/DATA/FINAL/Champions/Rumble.wad.client and Rumble.<lang>.wad.client,
resolves the base-skin Wwise events below to their media (the first variant of each event unless a variant is named),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.
Events (prefix Play_sfx_Rumble_Rumble, read from his bins 2026-10-25): the ball's swing and hit, the overheated hit
(PAttack); Flamespitter's roar (Q_OnBuffActivate: the 4.9 s burst, cut to the kit's 1.5 s) and a burn on each one hit
(REffect_hit, another variant); the harpoon's launch, the Danger Zone one for the second, its hit; Scrap Shield's cast;
the Danger Zone's vent (P_OnBuffDeactivate: the steam's hiss, 8 kHz) and Overheat (P_OnBuffActivate); The Equalizer's
cast, the line's burning (REffect_buffactivate) and its burn on each one in it (REffect_hit). Voice (Play_vo_Rumble_):
Flamespitter's and The Equalizer's (CarpetBomb) casts, Overheat's (Spell3DPCast); League has none for the harpoon or the
shield: two of his attack barks (Attack2DGeneral).
Icons (hud/icons2d): Rumble_Flamespitter = skill, Rumble_ElectroHarpoon = skill2, Rumble_R = ult, Rumble_JunkyardTitan1 =
the Junkyard Titan (league_rumble_passive), Rumble_ScrapShield = Scrap Shield (league_rumble_w).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/rumble/skins/base/rumble_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/rumble/skins/base/rumble_base_vo_"  # same in every language
P = "Play_sfx_Rumble_Rumble"
V = "Play_vo_Rumble_"
C = "league_rumble_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -9),
    C + "oh_hit": ([P + "PAttack_OnHit"], 3, 0.6, -8),
    C + "q": ([P + "Q_OnBuffActivate", P + "Q_OnCast"], None, 1.6, -6),
    C + "q_hit": ([P + "REffect_hit"], 2, 0.5, -12),
    C + "e": ([P + "EMissile_OnMissileLaunch", P + "E_OnCast"], None, 0.9, -7),
    C + "e2": ([P + "EMissileDangerZone_OnMissileLaunch"], 1, 0.9, -6),
    C + "e_hit": ([P + "EMissile_hit"], None, 1.0, -7),
    C + "w": ([P + "W_OnCast"], None, 1.0, -7),
    C + "dz": ([P + "P_OnBuffDeactivate"], None, 1.5, -8),
    C + "oh": ([P + "P_OnBuffActivate"], None, 2.0, -6),
    C + "r": ([P + "R_OnCast"], None, 1.4, -6),
    C + "r_fall": ([P + "REffect_buffactivate"], None, 2.5, -6),
    C + "r_hit": ([P + "REffect_hit"], None, 0.6, -11),
    C + "vo_q": ([V + "RumbleFlameThrowerVO_cast3D"], None, 2.8, -6),
    C + "vo_r": ([V + "RumbleCarpetBomb_cast3D"], None, 2.0, -6),
    C + "vo_oh": ([V + "Spell3DPCast"], None, 2.0, -6),
    C + "vo_e": ([V + "Attack2DGeneral"], 1, 2.0, -6),
    C + "vo_w": ([V + "Attack2DGeneral"], 3, 2.0, -6),
}
I = "assets/characters/rumble/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_rumble_skill": "rumble_flamespitter",
    "league_rumble_skill2": "rumble_electroharpoon",
    "league_rumble_ult": "rumble_r",
    "league_rumble_passive": "rumble_junkyardtitan1",
    "league_rumble_w": "rumble_scrapshield",
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
    main_wad = Wad(os.path.join(champs, "Rumble.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Rumble.{args.lang}.wad.client"))
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
