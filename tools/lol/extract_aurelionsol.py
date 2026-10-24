r"""Pull Aurelion Sol's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_aurelionsol.py --lol "D:\WeGameApps\lol" --vgmstream pathgmstream-cli.exe

The Zac route (extract_zac.py, extract_taliyah.py): reads (never writes) Game/DATA/FINAL/Champions/AurelionSol.wad.client
and AurelionSol.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each
event unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/
(git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are
written. Voice: zh_CN. Events (prefix Play_sfx_AurelionSol_AurelionSol, the names his skin bin lists - some carry a
stray byte there, so each is tried as written and without its last character): the star bolt's cast and hit; Breath of
Light's cast and the burn on the one in it; Singularity's cast, the black hole opening and its crushing wave; Falling
Star's cast, the star's impact and its shockwave on those hit; The Skies Descend's giant star and its outer
shockwave; Astral Flight's lift; the Skies charged (RAnnouncement). Voice (Play_vo_AurelionSol): E_cast3D, R_cast3D,
W_cast3D; Breath of Light has no cast line, so the general attack line (Attack2DGeneral).
Icons (the champion bin's hud/icons2d): AurelionSolQ = skill, AurelionSolE = skill2, AurelionSolR1 = ult, AurelionSolW1
= Astral Flight (league_aurelionsol_w), AurelionSolP = Cosmic Creator (league_aurelionsol_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/aurelionsol/skins/base/aurelionsol_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/aurelionsol/skins/base/aurelionsol_base_vo_"  # same in every language
P = "Play_sfx_AurelionSol_AurelionSol"
V = "Play_vo_AurelionSol_"
C = "league_aurelionsol_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the breath's burn quieter (one every 167 ms), the voice as the others'
CLIPS = {
    C + "a": ([P + "Basicattack_cast9", P + "Basicattack_cast"], None, 0.6, -9),
    C + "a_hit": ([P + "Basicattack_OnHitLocation0", P + "Basicattack_OnHitLocation"], None, 0.6, -9),
    C + "q": ([P + "Q_OnCast", P + "Q_missilecast", P + "Q_missilelaunch"], None, 1.5, -6),
    C + "q_hit": ([P + "QDebuff_hit0", P + "QDebuff_hit", P + "QDebuff_hit_loop5"], None, 0.5, -12),
    C + "e": ([P + "E_OnCast6", P + "E_OnCast", P + "E_cast_projectile"], None, 1.0, -6),
    C + "e_hole": ([P + "E_hit_start", P + "E_buffactivate_aoe_other7", P + "E_buffactivate_aoe_other"], None, 1.5, -6),
    C + "e_core": ([P + "E_hit_wave", P + "EDebuff_hit_loop4", P + "EDebuff_hit_loop"], None, 0.9, -8),
    C + "r": ([P + "R_OnCastF", P + "R_OnCast", P + "R_cast_self"], None, 2.0, -5),
    C + "r_land": ([P + "RMissile_hit6", P + "RMissile_hit"], None, 1.5, -4),
    C + "r_hit": ([P + "R_hit_shockwave"], None, 0.9, -7),
    C + "r_sky": ([P + "R2Missile_hit_super", P + "R2_OnCast5", P + "R2_OnCast"], None, 2.0, -3),
    C + "r_wave": ([P + "R2Missile_hit_distant3", P + "R2Missile_hit_distant"], None, 1.5, -6),
    C + "w": ([P + "W_OnCast", "Play_sfx_AurelionSol_Flight3D_buffactivate_swirl"], None, 1.5, -6),
    C + "sky": ([P + "RAnnouncement_ready_buffactivate_self"], None, 1.5, -6),
    C + "vo_q": ([V + "Attack2DGeneral1", V + "Attack2DGeneral", V + "Attack2DDragon"], None, 2.5, -6),
    C + "vo_e": ([V + "AurelionSolE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "AurelionSolR_cast3D"], None, 3.0, -6),
    C + "vo_w": ([V + "AurelionSolW_cast3D"], None, 2.5, -6),
}
I = "assets/characters/aurelionsol/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_aurelionsol_skill": "aurelionsolq",
    "league_aurelionsol_skill2": "aurelionsole",
    "league_aurelionsol_ult": "aurelionsolr1",
    "league_aurelionsol_w": "aurelionsolw1",
    "league_aurelionsol_passive": "aurelionsolp",
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
    main_wad = Wad(os.path.join(champs, "AurelionSol.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"AurelionSol.{args.lang}.wad.client"))
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
