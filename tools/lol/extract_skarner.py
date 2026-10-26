r"""Pull Skarner's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_skarner.py --lol "D:\WeGameApps\lol" --vgmstream C:\t\ks_tools\vgm\vgmstream-cli.exe

extract_trundle.py's route: reads (never writes) Game/DATA/FINAL/Champions/Skarner.wad.client and
Skarner.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice:
zh_CN. Events (the names his bins carry, Play_sfx_Skarner* / Play_sfx_Skarner_Skarner*): the stinger's swing and hit;
Shattered Earth's pickup, the boulder's empowered hit, Upheaval's throw and landing; Seismic Bastion's quake; Ixtal's
Impact's charge, the grab and the slam; Impale's cast and hit; Quaking's burst (the passive attack's hit). Voice
(Play_vo_Skarner_*): Shattered Earth's, the charge's stun and Impale's casts.
Icons (the champion bin's hud/icons2d): skarner_q = skill, skarner_e = skill2, skarner_r = ult, skarner_passive =
Threads of Vibration (league_skarner_passive), skarner_w = Seismic Bastion (league_skarner_w).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/skarner/skins/base/skarner_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/skarner/skins/base/skarner_base_vo_"  # same in every language
P = "Play_sfx_Skarner"
PS = "Play_sfx_Skarner_Skarner"
V = "Play_vo_Skarner_"
C = "league_skarner_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -8),
    C + "q": ([P + "Q_OnCast"], None, 1.5, -6),
    C + "q_hit": ([P + "QRockAttack_OnHit", P + "QClawAttack_OnHit"], None, 1.0, -6),
    C + "q_toss": ([P + "QRockThrow_OnCast", PS + "QThrow_missilelaunch"], None, 1.0, -7),
    C + "q_land": ([PS + "QThrow_hit", PS + "QThrow_hith"], None, 1.5, -5),
    C + "w": ([PS + "W_OnCast", PS + "W_missilelaunch"], None, 1.8, -5),
    C + "e": ([P + "E_OnCast"], None, 1.5, -6),
    C + "e_hit": ([PS + "EGrab_buffactivate"], None, 1.2, -6),
    C + "e_slam": ([PS + "E_hit"], None, 1.5, -5),
    C + "r": ([PS + "R_cast", PS + "R_missilelaunch"], None, 1.5, -6),
    C + "r_hit": ([PS + "R_hit", PS + "R_hitlocation"], None, 1.8, -5),
    C + "p_burst": ([P + "PassiveAttack_OnHit"], None, 1.2, -7),
    C + "vo_q": ([V + "SkarnerQ_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "Spell3DEStun"], None, 2.5, -6),
    C + "vo_r": ([V + "SkarnerR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/skarner/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_skarner_skill": "skarner_q",
    "league_skarner_skill2": "skarner_e",
    "league_skarner_ult": "skarner_r",
    "league_skarner_w": "skarner_w",
    "league_skarner_passive": "skarner_passive",
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
    main_wad = Wad(os.path.join(champs, "Skarner.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Skarner.{args.lang}.wad.client"))
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
