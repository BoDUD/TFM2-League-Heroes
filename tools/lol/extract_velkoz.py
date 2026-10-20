r"""Pull Vel'Koz's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_velkoz.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_zyra.py: reads (never writes) Game/DATA/FINAL/Champions/Velkoz.wad.client and
Velkoz.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event,
or the one named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (named in Velkoz.bin): VelkozBasicAttack_OnCast / OnHit, VelkozQ_OnCast / VelkozQ_hit (the bolt),
VelkozQSplitMis_missilelaunch / VelkozQSplitExplosion_buffactivate (the split), VelkozW_OnCast / VelkozWTar_hit (the
rift's first burst) / VelkozWTarPersist_hit (its second; WExplode_* are not in the 16.20 bank), VelkozE_OnCast / VelkozE_explo / VelkozEStun_OnBuffActivate
(the knock-up), VelkozR_OnCast / VelkozR_OnBuffActivate (the beam) / VelkozR_hit / VelkozR_hit_researched (true damage) /
VelkozRBeamEnd_buffactivate, VelkozP1/P2_buffactivate_champ (stacks 1, 2) and VelkozPFull_buffactivate_champ (the
third: Organic Deconstruction). Voice: his spells have no lines of their own in the bank; Play_vo_Velkoz_Attack2DGeneral's
22 lines give three (vo_q / vo_e / vo_r, picked by index).
Icons (Velkoz.bin's): velkoz_q1 = skill, velkoz_e = skill2, velkoz_r = ult, velkoz_w = W (the attack's rift),
velkoz_passive = passive, velkoz_q2 = the split (for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/velkoz/skins/base/velkoz_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/velkoz/skins/base/velkoz_base_vo_"  # same in every language
P = "Play_sfx_Velkoz_Velkoz"
V = "Play_vo_Velkoz_"
C = "league_velkoz_sfx_"

# clip name -> ([events to try, first that resolves], index among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "q": ([P + "Q_OnCast2", P + "Q_missilelaunch"], None, 1.0, -14),
    C + "q_hit": ([P + "Q_hit"], None, 1.0, -13),
    C + "q_split": ([P + "QSplitMis_missilelaunch"], None, 0.8, -15),
    C + "q_split_hit": ([P + "QSplitExplosion_buffactivate"], None, 1.0, -14),
    C + "w": ([P + "W_OnCast4", P + "W_buffactivate"], None, 1.0, -14),
    C + "w_hit": ([P + "WTar_hit"], None, 1.0, -14),
    C + "w_boom": ([P + "WExplode_buffactivate", P + "WExplosionAlt_buffactivate", P + "WTarPersist_hit", P + "W_buffactivate"], None, 1.4, -12),
    C + "e": ([P + "E_OnCast", P + "EMissile_missilelaunch"], None, 1.0, -14),
    C + "e_boom": ([P + "E_explo"], None, 1.6, -11),
    C + "e_air": ([P + "EStun_OnBuffActivate"], None, 1.2, -13),
    C + "r": ([P + "R_OnCast"], None, 1.2, -13),
    C + "r_beam": ([P + "R_OnBuffActivate"], None, 2.6, -12),
    C + "r_hit": ([P + "R_hit"], None, 0.6, -16),
    C + "r_true": ([P + "R_hit_researched"], None, 0.6, -15),
    C + "r_end": ([P + "RBeamEnd_buffactivate"], None, 1.2, -14),
    C + "p_1": ([P + "P1_buffactivate_champ"], None, 0.8, -16),
    C + "p_2": ([P + "P2_buffactivate_champ"], None, 0.8, -16),
    C + "p_full": ([P + "PFull_buffactivate_champ"], None, 1.4, -12),
    C + "vo_q": ([V + "Attack2DGeneral"], 0, 2.4, -6),
    C + "vo_e": ([V + "Attack2DGeneral"], 7, 2.4, -6),
    C + "vo_r": ([V + "Attack2DGeneral"], 14, 2.4, -6),
}
I = "assets/characters/velkoz/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_velkoz_skill": I + "velkoz_q1.dds",
    "league_velkoz_skill2": I + "velkoz_e.dds",
    "league_velkoz_ult": I + "velkoz_r.dds",
    "league_velkoz_w": I + "velkoz_w.dds",
    "league_velkoz_passive": I + "velkoz_passive.dds",
    "league_velkoz_q2": I + "velkoz_q2.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Velkoz.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Velkoz.{args.lang}.wad.client"))
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
            m = variants[0] if mid is None else variants[mid % len(variants)]
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
