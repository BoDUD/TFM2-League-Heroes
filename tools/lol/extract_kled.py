r"""Pull Kled's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kled.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Zac route (extract_zac.py, extract_sejuani.py): reads (never writes) Game/DATA/FINAL/Champions/Kled.wad.client and
Kled.<lang>.wad.client (one bank for Kled on Skaarl and on foot), resolves the base-skin Wwise events below to their media
(the first variant of each event unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only
the icons are written. Voice: zh_CN. Events (prefix Play_sfx_Kled_Kled; on foot Play_sfx_Kled_KledRider...): the axe's
swing and hit; Violent Tendencies' start, its fourth swing and hit; Bear Trap on a Rope's throw, the hit on a champion and
the yank (the mark's end); Pocket Pistol's shot and hit; Jousting's two dashes (two variants of the cast) and its hit;
Chaaaaaaaarge!!!'s cast, the ram and its hit; Skaarl fleeing and coming back. Voice (Play_vo_Kled_): the trap's hit, W's
cast, E's cast, R's cast, an attack line for the pistol, the dismount and the remount.
Icons (the champion bin's hud/icons2d): kled_q1 = skill, kled_e1 = skill2, kled_r = ult, kled_w = Violent Tendencies
(league_kled_w), kled_p = Skaarl (league_kled_passive), kled_q2 = Pocket Pistol (league_kled_pistol).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kled/skins/base/kled_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kled/skins/base/kled_base_vo_"  # same in every language
P = "Play_sfx_Kled_Kled"
V = "Play_vo_Kled_"
C = "league_kled_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -9),
    C + "w": ([P + "W_buffactivate", P + "WActive_OnBuffActivate"], None, 1.2, -7),
    C + "w_last": ([P + "WAttack4_OnCast"], None, 0.8, -8),
    C + "w_hit": ([P + "WAttack4_OnHit"], None, 0.9, -6),
    C + "q": ([P + "QMissile_OnMissileLaunch", P + "Q_OnCast"], None, 1.0, -7),
    C + "q_hit": ([P + "QMissile_champ_hit"], None, 1.0, -6),
    C + "q_yank": ([P + "QMark_buffdeactivate"], None, 1.0, -6),
    C + "p": ([P + "RiderQMissile_OnMissileLaunch", P + "RiderQ_OnCast"], None, 1.0, -6),
    C + "p_hit": ([P + "RiderQMissile_OnHit"], None, 0.8, -7),
    C + "e": ([P + "EDash_OnCast"], None, 1.0, -7),
    C + "e2": ([P + "EDash_OnCast"], 1, 1.0, -7),
    C + "e_hit": ([P + "EDash_hit"], None, 0.8, -7),
    C + "r": ([P + "R_cast"], None, 1.8, -6),
    C + "r_crash": ([P + "RDash_hit"], None, 1.5, -5),
    C + "r_hit": ([P + "CritAttack_OnHit"], None, 0.8, -7),
    C + "dismount": ([P + "DismountDash_OnBuffCast"], None, 1.5, -6),
    C + "remount": ([P + "RemountDash_explosion", P + "RemounttDash_explosion", P + "MountReturn_buffactivate"],
                    None, 1.5, -6),
    C + "vo_q": ([V + "KledQMissile_hit3D"], None, 2.5, -6),
    C + "vo_w": ([V + "KledWAttack_OnCast"], None, 2.5, -6),
    C + "vo_e": ([V + "KledEDash_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "KledR_cast3D"], None, 3.0, -6),
    C + "vo_p": ([V + "Attack2DGeneral"], None, 2.5, -6),
    C + "vo_off": ([V + "Spell3DPDismount"], None, 3.0, -6),
    C + "vo_mount": ([V + "Spell3DPRemount"], None, 3.0, -6),
}
I = "assets/characters/kled/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_kled_skill": "kled_q1",
    "league_kled_skill2": "kled_e1",
    "league_kled_ult": "kled_r",
    "league_kled_w": "kled_w",
    "league_kled_passive": "kled_p",
    "league_kled_pistol": "kled_q2",
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
    main_wad = Wad(os.path.join(champs, "Kled.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kled.{args.lang}.wad.client"))
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
