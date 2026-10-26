r"""Pull Locke's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_locke.py --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

The Zac route (extract_trundle.py's): reads (never writes) Game/DATA/FINAL/Champions/Locke.wad.client and
Locke.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice:
zh_CN. Events (prefix Play_sfx_Locke_Locke, the names his bins carry): the stab's swing and hit; each nail's launch,
its hit and the nails popped by a stab (the medium detonation); Ashen Pursuit's poof, the pursuit's dash and the reset
after a takedown (E's ready warning); Soul Ignition's cast; Purgatory's cast, the case let go, its landing, the mark put on a champion and
the artifact picked up. Voice (Play_vo_Locke_Locke): Ritual Nails', Soul Ignition's, Ashen Pursuit's and Purgatory's
casts.
Icons (the champion bin's hud/icons2d): locke_q = skill, locke_e = skill2, locke_r = ult, locke_passive = Silver Stake
(league_locke_passive), locke_w = Soul Ignition (league_locke_w).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/locke/skins/base/locke_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/locke/skins/base/locke_base_vo_"  # same in every language
P = "Play_sfx_Locke_Locke"
V = "Play_vo_Locke_Locke"
C = "league_locke_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -8),
    C + "q_throw": ([P + "QMissile_OnMissileLaunch", P + "QMissile_OnCast"], None, 0.8, -8),
    C + "q_hit": ([P + "QMissile_hit"], None, 0.8, -7),
    C + "q_pop": ([P + "Q_detonate_medium", P + "Q_detonate_large"], None, 1.0, -6),
    C + "e_blink": ([P + "E_cast_poof", P + "E_cast_poofn"], None, 1.2, -6),
    C + "e_dash": ([P + "EAttackReady_dash_cast"], None, 1.0, -6),
    C + "reset": ([P + "E_cast_warning"], None, 1.0, -8),   # E ready again (its _buffactivate_fs: footsteps)
    C + "w": ([P + "W_cast", P + "W_OnBuffActivate"], None, 1.8, -6),
    C + "r": ([P + "R_OnCast"], None, 1.5, -6),
    C + "r_throw": ([P + "R_OnMissileLaunch"], None, 1.2, -7),
    C + "r_land": ([P + "R_OnHitLocation"], None, 2.0, -5),
    C + "r_hit": ([P + "RExecuteTracker_timer_buffcast_target", P + "R_buffactivate"], None, 1.2, -7),
    C + "r_seal": ([P + "RPickUp_collect", P + "RSuckIn_execute_soul_missilelaunch"], None, 1.8, -6),
    C + "vo_q": ([V + "Q_cast3D"], None, 2.5, -6),
    C + "vo_w": ([V + "W_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "E_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 3.0, -6),
}
I = "assets/characters/locke/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_locke_skill": "locke_q",
    "league_locke_skill2": "locke_e",
    "league_locke_ult": "locke_r",
    "league_locke_w": "locke_w",
    "league_locke_passive": "locke_passive",
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
    main_wad = Wad(os.path.join(champs, "Locke.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Locke.{args.lang}.wad.client"))
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
