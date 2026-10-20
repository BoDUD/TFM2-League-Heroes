r"""Pull Zyra's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zyra.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_vex.py: reads (never writes) Game/DATA/FINAL/Champions/Zyra.wad.client and
Zyra.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (named in Zyra.bin and the plants' bins; the plants' sounds sit in Zyra's own bank): ZyraBasicAttack_OnCast /
OnHit, ZyraQ_OnCast / ZyraQ_buffactivate (the spines burst) / ZyraQ_hit, ZyraQPlant_OnBuffActivate (a Thorn Spitter
grows), ZyraThornPlant's ZyraQPlantMissile_OnHit (its strike), ZyraE_OnCast / ZyraEHold_OnBuffActivate (the root),
ZyraEPlant_OnBuffActivate (a Vine Lasher grows), ZyraGraspingPlant's ZyraEPlantAttack_OnHit (its lash), ZyraR_OnCast,
ZyraRSplash_OnMissileLaunch (the thicket), ZyraRKnockUp_hit, ZyraPlantEnrage_OnBuffActivate. Not in the 16.20 bank
(the bins still name them): ZyraQ_hit -> ZyraCritAttack_OnHit, ZyraPlantEnrage_* -> ZyraW_OnBuffActivate (a seed's glow). Voice (Play_vo_Zyra_):
ZyraQ_cast3D, ZyraE_cast3D, ZyraR_cast3D.
Icons (Zyra.bin's): ZyraQ = skill, ZyraE = skill2, ZyraR = ult, ZyraW = W, ZyraP = passive (for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zyra/skins/base/zyra_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zyra/skins/base/zyra_base_vo_"  # same in every language
P = "Play_sfx_Zyra_"
TP = "Play_sfx_ZyraThornPlant_"
GP = "Play_sfx_ZyraGraspingPlant_"
V = "Play_vo_Zyra_"
C = "league_zyra_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "ZyraBasicAttack_OnCast", P + "ZyraBasicAttack_OnMissileLaunch"], None, 0.8, -16),
    C + "a_hit": ([P + "ZyraBasicAttack_OnHit"], None, 0.8, -15),
    C + "q": ([P + "ZyraQ_OnCast"], None, 1.0, -14),
    C + "q_burst": ([P + "ZyraQ_buffactivate"], None, 1.4, -12),
    C + "q_hit": ([P + "ZyraQ_hit", P + "ZyraCritAttack_OnHit"], None, 1.0, -13),
    C + "t_grow": ([P + "ZyraQPlant_OnBuffActivate"], None, 1.4, -14),
    C + "t_hit": ([TP + "ZyraQPlantMissile_OnHit7", TP + "ZyraQPlantMissileOnSpawn_OnHit"], None, 0.8, -16),
    C + "e": ([P + "ZyraE_OnCast", P + "ZyraE_OnMissileLaunch"], None, 1.2, -14),
    C + "e_hit": ([P + "ZyraEHold_OnBuffActivate"], None, 1.4, -13),
    C + "v_grow": ([P + "ZyraEPlant_OnBuffActivate"], None, 1.4, -14),
    C + "v_hit": ([GP + "ZyraEPlantAttack_OnHit7", GP + "ZyraEPlantAttack2_OnHit2"], None, 0.8, -16),
    C + "r": ([P + "ZyraR_OnCast"], None, 1.2, -13),
    C + "r_land": ([P + "ZyraRSplash_OnMissileLaunch"], None, 2.0, -12),
    C + "r_knock": ([P + "ZyraRKnockUp_hit"], None, 1.6, -11),
    C + "r_rage": ([P + "ZyraPlantEnrage_OnBuffActivate", P + "ZyraW_OnBuffActivate"], None, 1.4, -14),
    C + "vo_q": ([V + "ZyraQ_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "ZyraE_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "ZyraR_cast3D"], None, 2.0, -6),
}
I = "assets/characters/zyra/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_zyra_skill": I + "zyraq.dds",
    "league_zyra_skill2": I + "zyrae.dds",
    "league_zyra_ult": I + "zyrar.dds",
    "league_zyra_w": I + "zyraw.dds",
    "league_zyra_passive": I + "zyrap.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zyra.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zyra.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            # (the bins' names can carry a glued character - "OnBuffActivate2", "OnCast0": also try them without it)
            for ev in [e for ev_ in events for e in (ev_, ev_[:-1])]:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else mid
            sr, x = decode(media[m], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event} ({len(variants)} variants)")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
