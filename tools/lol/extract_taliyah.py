r"""Pull Taliyah's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_taliyah.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

The Zac route (extract_zac.py): reads (never writes) Game/DATA/FINAL/Champions/Taliyah.wad.client and
Taliyah.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Taliyah_Taliyah, the names her skin bin lists): the pebble's cast and its knock (a rock's hit: BasicAttack_OnHit has no media);
Threaded Volley's rock launch and hit, the Worked Ground boulder's cast and hit; Seismic Shove's cast, the eruption
(WKnockUp_cast) and the heave (WKnockUp_OnBuffCast); Unraveled Earth's cast (the mines thrown) and a mine blowing up
(EMineDash_hit); Weaver's Wall's cast (RDistantSound: R_OnCast7 has no media), the wall rising (RMis_OnMissileLaunch) and the slam against it
(RWallBlowUp_buffactivate). Voice (Play_vo_Taliyah_Taliyah): Q_cast3D, WVC_cast3D, R_cast3D.
Icons: taliyah_q = skill, taliyah_w = skill2, taliyah_r = ult, taliyah_e = Unraveled Earth (league_taliyah_e),
taliyah_passive = Rock Surfing (league_taliyah_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/taliyah/skins/base/taliyah_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/taliyah/skins/base/taliyah_base_vo_"  # same in every language
P = "Play_sfx_Taliyah_Taliyah"
V = "Play_vo_Taliyah_Taliyah"
C = "league_taliyah_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the volley's rocks quieter (five a cast), the voice as the others'
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast", P + "BasicAttack_OnMissileLaunch"], None, 0.6, -9),
    C + "a_hit": ([P + "Q_OnHit"], 3, 0.6, -9),           # no BasicAttack_OnHit media: a rock's knock (another variant)
    C + "q_rock": ([P + "QMis_OnMissileLaunch", P + "Q_OnMissileLaunch"], None, 0.6, -10),
    C + "q_hit": ([P + "QMis_OnHit", P + "Q_OnHit"], None, 0.6, -10),
    C + "q_big": ([P + "QMisBig_cast", P + "QMisBig_missilecast"], None, 1.0, -6),
    C + "q_big_hit": ([P + "QMisBig_hit"], None, 0.9, -6),
    C + "w": ([P + "WVC_OnCast", P + "WSound_cast"], None, 1.0, -6),
    C + "w_erupt": ([P + "WKnockUp_cast"], None, 1.2, -5),
    C + "w_hit": ([P + "WKnockUp_OnBuffCast"], None, 0.9, -7),
    C + "e_land": ([P + "E_cast", P + "ESoundMis_OnMissileLaunch"], None, 1.2, -6),
    C + "e_blast": ([P + "EMineDash_hit", P + "EMineWave_hit"], None, 0.9, -6),
    C + "r": ([P + "RDistantSound_OnBuffCast", P + "RSurfing_OnBuffActivate"], None, 2.0, -5),   # R_OnCast7 has no media
    C + "r_wall": ([P + "RMis_OnMissileLaunch", P + "RMis_OnMissileCast"], None, 2.0, -5),
    C + "r_slam": ([P + "RWallBlowUp_buffactivate", P + "RMis_OnHit"], None, 1.2, -6),
    C + "vo_q": ([V + "Q_cast3D"], None, 2.5, -6),
    C + "vo_w": ([V + "WVC_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 3.0, -6),
}
I = "assets/characters/taliyah/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_taliyah_skill": "taliyah_q",
    "league_taliyah_skill2": "taliyah_w",
    "league_taliyah_ult": "taliyah_r",
    "league_taliyah_e": "taliyah_e",
    "league_taliyah_passive": "taliyah_passive",
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
    main_wad = Wad(os.path.join(champs, "Taliyah.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Taliyah.{args.lang}.wad.client"))
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
