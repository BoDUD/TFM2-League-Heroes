r"""Pull Sejuani's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_sejuani.py --lol "D:\WeGameApps\lol" --vgmstream pathgmstream-cli.exe

The Zac route (extract_zac.py, extract_aurelionsol.py): reads (never writes) Game/DATA/FINAL/Champions/Sejuani.wad.client
and Sejuani.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each
event unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/
(git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are
written. Voice: zh_CN. Events (prefix Play_sfx_Sejuani_Sejuani, the names her skin bin lists - some carry a stray digit
there, so each is tried as written and without it): the flail's swing and hit; Arctic Assault's charge and its hit;
Winter's Wrath's cast, the sweep's swing (the flail attack W's cast), the slam's hit and the hit on each one; the
freeze (EStack4); the shatter (the passive's hit); Glacial Prison's cast, the bola's launch, the prison and the storm
(its second hit). Voice (Play_vo_Sejuani): SejuaniQ_cast3D, SejuaniW_cast3D, SejuaniR_cast3D.
Icons (the champion bin's hud/icons2d): sejuani_q = skill, sejuani_w = skill2, sejuani_r = ult, sejuani_e = Permafrost
(league_sejuani_e), sejuani_passive = Fury of the North (league_sejuani_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/sejuani/skins/base/sejuani_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/sejuani/skins/base/sejuani_base_vo_"  # same in every language
P = "Play_sfx_Sejuani_Sejuani"
V = "Play_vo_Sejuani_"
C = "league_sejuani_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -9),
    C + "q": ([P + "Q_OnCast"], None, 1.5, -6),
    C + "q_hit": ([P + "Q_hit"], None, 0.9, -7),
    C + "w": ([P + "W_OnCast"], None, 1.0, -7),
    C + "w_sweep": ([P + "BasicAttackW_OnCast"], None, 0.8, -8),
    C + "w_slam": ([P + "W2_hit"], None, 1.0, -6),
    C + "w_hit": ([P + "W1_hit"], None, 0.6, -9),
    C + "e_freeze": ([P + "EStack4_hit", P + "E2_OnHit"], None, 1.2, -6),
    C + "sh_hit": ([P + "P_hit5", P + "P_hit"], None, 0.9, -6),
    C + "r": ([P + "R_OnCast"], None, 1.5, -6),
    C + "r_throw": ([P + "RMissile_OnMissileLaunch"], None, 1.2, -7),
    C + "r_hit": ([P + "R_hit"], None, 1.5, -5),
    C + "r_storm": ([P + "R_hit2", P + "R_hit_close"], None, 1.8, -7),
    C + "vo_q": ([V + "SejuaniQ_cast3D"], None, 2.5, -6),
    C + "vo_w": ([V + "SejuaniW_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "SejuaniR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/sejuani/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_sejuani_skill": "sejuani_q",
    "league_sejuani_skill2": "sejuani_w",
    "league_sejuani_ult": "sejuani_r",
    "league_sejuani_e": "sejuani_e",
    "league_sejuani_passive": "sejuani_passive",
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
    main_wad = Wad(os.path.join(champs, "Sejuani.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Sejuani.{args.lang}.wad.client"))
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
