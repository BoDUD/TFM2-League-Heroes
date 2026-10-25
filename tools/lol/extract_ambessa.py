r"""Pull Ambessa's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ambessa.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Zac route (extract_yorick.py's): reads (never writes) Game/DATA/FINAL/Champions/Ambessa.wad.client and
Ambessa.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice:
zh_CN. Events (prefix Play_sfx_Ambessa_Ambessa, named in her skin and champion bins): the twin blades' swing and hit, the
empowered blow after Drakehound's Step (the crit attack's hit) and the step's dash; Cunning Sweep's cast, its sweep and
its hit; Sundering Slam's cast and its slam; Lacerate's cast, its whirl and its hit; Repudiation's brace, its slam and
its hit; Public Execution's cast, the suppression and the slam. Voice (Play_vo_Ambessa_Ambessa): Cunning Sweep's,
Sundering Slam's, Lacerate's and Public Execution's casts, Repudiation's parry (Play_vo_Ambessa_Spell3DWParry).
Icons (the champion bin's hud/icons2d, Icon_Ambessa_<key>.dds): Cunning Sweep (Q1) = skill, Lacerate = skill2, Public Execution = ult, Drakehound's
Step (league_ambessa_passive), Repudiation (league_ambessa_w), Sundering Slam (league_ambessa_q2).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ambessa/skins/base/ambessa_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ambessa/skins/base/ambessa_base_vo_"  # same in every language
P = "Play_sfx_Ambessa_Ambessa"
V = "Play_vo_Ambessa_Ambessa"
C = "league_ambessa_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -9),
    C + "a_pw": ([P + "CritAttack_OnHit", P + "PassiveChainDragCatchCrit"], None, 0.8, -7),
    C + "st": ([P + "PassiveDash_OnCast"], None, 0.8, -8),
    C + "q": ([P + "Q1_OnCast"], None, 1.0, -7),
    C + "q_sweep": ([P + "Q1_OnHitLocation"], None, 1.0, -7),
    C + "q_hit": ([P + "Q1_hit"], None, 0.8, -8),
    C + "q2": ([P + "Q2_OnCast"], None, 1.0, -7),
    C + "q2_hit": ([P + "Q2_OnHitLocation", P + "Q2_hit"], None, 1.2, -6),
    C + "e": ([P + "E_OnCast"], None, 1.0, -7),
    C + "e_lash": ([P + "E_buffactivate"], None, 1.0, -7),
    C + "e_hit": ([P + "E_hit"], None, 0.8, -8),
    C + "w": ([P + "W_OnCast"], None, 1.0, -7),
    C + "w_slam": ([P + "WRelease_lesser_buffactivate", P + "WRelease_greater_buffactivate"], None, 1.2, -6),
    C + "w_hit": ([P + "WTarget_hit"], None, 0.8, -8),
    C + "r": ([P + "R_OnCast"], None, 1.5, -6),
    C + "r_pin": ([P + "RBuffSuppressing_OnBuffCast"], None, 1.2, -7),
    C + "r_crash": ([P + "RBuffSuppressing_OnBuffDeactivate"], None, 1.5, -5),
    C + "vo_q": ([V + "Q1_cast3D"], None, 2.5, -6),
    C + "vo_q2": ([V + "Q2_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "E_cast3D"], None, 2.5, -6),
    C + "vo_w": (["Play_vo_Ambessa_Spell3DWParry"], None, 2.5, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 3.0, -6),
}
I = "assets/characters/ambessa/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon stems to try (the first found; her bins name Icon_Ambessa_<key>.dds)
    "league_ambessa_skill": ["icon_ambessa_q1"],
    "league_ambessa_skill2": ["icon_ambessa_e"],
    "league_ambessa_ult": ["icon_ambessa_r"],
    "league_ambessa_w": ["icon_ambessa_w"],
    "league_ambessa_passive": ["icon_ambessa_passive"],
    "league_ambessa_q2": ["icon_ambessa_q2"],
}


def icon_path(wad, stems):
    """The WAD path of an icon: hud/icons2d/<stem>.dds / .tex / .png for the first stem found (None when none is)."""
    for stem in stems:
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
    main_wad = Wad(os.path.join(champs, "Ambessa.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ambessa.{args.lang}.wad.client"))
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
    for name, stems in ICONS.items():
        path = over.get(name) or icon_path(main_wad, stems)
        if path is None:
            sys.exit(f"{name}: none of {stems} in {I} - pass --icon {name}=<wad path> (see the WAD's hud/icons2d entries)")
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
